"""Generate reviewable SAM3.1-box / SOLIDER drafts from a bound Boost550 workset."""
import argparse
import csv
from datetime import datetime, timezone
import fcntl
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace

import cv2
import numpy as np
from PIL import Image, ImageDraw

from person_pseudolabel import commit_directory, file_hash, fresh_external, load, write

LABELS = {1: 'hair', 2: 'face', 3: 'upper', 4: 'lower'}
PALETTE = {1: (245, 190, 30), 2: (30, 190, 240), 3: (245, 65, 100), 4: (45, 200, 110)}


def now():
    return datetime.now(timezone.utc).isoformat()


def event(root, **value):
    with (root/'ATTEMPTS.jsonl').open('a') as stream:
        stream.write(json.dumps({'at_utc': now(), **value}, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def image_crop(image, box):
    """Reproduce the reviewed training producer's round, context and letterbox."""
    x1, y1, x2, y2 = box
    if not np.isfinite(box).all() or not (0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height):
        raise ValueError('Invalid original-grid bbox')
    width, height = x2-x1, y2-y1
    crop = [max(0, round(x1-.15*width)), max(0, round(y1-.15*height)),
            min(image.width, round(x2+.15*width)), min(image.height, round(y2+.15*height))]
    roi = image.crop(crop)
    scale = min(384/roi.width, 576/roi.height)
    nw, nh = max(1, round(roi.width*scale)), max(1, round(roi.height*scale))
    px, py = (384-nw)//2, (576-nh)//2
    canvas = Image.new('RGB', (384, 576))
    canvas.paste(roi.resize((nw, nh), Image.Resampling.BILINEAR), (px, py))
    return canvas, {'crop_xyxy': crop, 'resized_wh': [nw, nh], 'pad_xy': [px, py],
                    'canvas_wh': [384, 576], 'rgb_resize': 'PIL_BILINEAR',
                    'mask_mapback': 'argmax576; unpad; PIL_NEAREST; crop offset'}


def original_labels(prediction, geometry, size):
    prediction = np.asarray(prediction)
    if prediction.shape != (576, 384) or not set(np.unique(prediction)) <= set(range(5)):
        raise ValueError('Parser output shape or native helper IDs invalid')
    x1, y1, x2, y2 = geometry['crop_xyxy']
    px, py = geometry['pad_xy']
    nw, nh = geometry['resized_wh']
    unpadded = prediction[py:py+nh, px:px+nw].astype('uint8')
    canvas = Image.new('L', size)
    canvas.paste(Image.fromarray(unpadded).resize((x2-x1, y2-y1), Image.Resampling.NEAREST), (x1, y1))
    return np.asarray(canvas).copy()


def editor_shape(label, kind, points, person_id, score=None, difficult=False):
    return {'label': label, 'shape_type': kind, 'points': points, 'group_id': person_id,
            'score': score, 'difficult': difficult, 'flags': {'draft_not_gt': True},
            'description': '',
            'attributes': {}, 'kie_linking': []}


def polygon_view(labels, person_id):
    """Keep every component; record raster differences and holes against raw masks."""
    shapes, diagnostics = [], {}
    for label, name in LABELS.items():
        binary = (labels == label).astype('uint8')
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        raster = Image.new('L', (labels.shape[1], labels.shape[0]))
        drawing = ImageDraw.Draw(raster)
        holes = 0 if hierarchy is None else int(sum(item[3] >= 0 for item in hierarchy[0]))
        components = 0
        for index, contour in enumerate(contours):
            if hierarchy[0][index][3] >= 0:
                continue
            components += 1
            points = cv2.approxPolyDP(contour, .5, True).reshape(-1, 2).astype(float).tolist()
            kind = 'polygon'
            if len(points) < 3:
                x, y, w, h = cv2.boundingRect(contour)
                points = [[x, y], [x+w-1, y], [x+w-1, y+h-1], [x, y+h-1]]
                kind = 'rectangle'
            shapes.append(editor_shape(name, kind, points, person_id, difficult=holes > 0))
            drawing.polygon([tuple(point) for point in points], fill=1)
        exported = np.asarray(raster).astype(bool)
        truth = binary.astype(bool)
        diagnostics[name] = {'mask_pixels': int(truth.sum()), 'components': components, 'holes': holes,
                             'polygon_added_pixels': int((exported & ~truth).sum()),
                             'polygon_missing_pixels': int((truth & ~exported).sum()),
                             'target_state': 'PROPOSAL_REQUIRES_REVIEW' if truth.any() else 'NO_PROPOSAL_NOT_ABSENCE'}
    return shapes, diagnostics


def verify_packet(folder, row, protocol_sha256):
    packet = load(folder/'PACKET.json')
    if packet['candidate_id'] != row['candidate_id'] or packet['protocol_sha256'] != protocol_sha256:
        raise ValueError('Packet identity or protocol mismatch')
    if packet['input_sha256'] != row['image_sha256'] or packet['accepted_gt'] is not False:
        raise ValueError('Packet input or draft status mismatch')
    expected_size = (int(row['width']), int(row['height']))
    for name, digest in packet['artifact_sha256'].items():
        path = folder/name
        if file_hash(path) != digest:
            raise ValueError('Packet artifact hash mismatch')
        if path.suffix == '.png':
            with Image.open(path) as image:
                image.load()
                if image.size != expected_size:
                    raise ValueError('Packet mask geometry mismatch')
                allowed = {0, 255} if name.endswith('_person.png') else set(range(5))
                if not set(np.unique(np.asarray(image))) <= allowed:
                    raise ValueError('Packet mask labels invalid')
    return packet


def prepare(workset, selected, sam_source, sam_checkpoint, output):
    workset, selected = Path(workset).resolve(), Path(selected).resolve()
    summary = load(workset/'SUMMARY.json')
    if file_hash(workset/'WORKSET.csv') != summary['artifact_sha256']['WORKSET.csv']:
        raise ValueError('Workset identity changed')
    with (workset/'WORKSET.csv').open() as stream:
        rows = [row for row in csv.DictReader(stream) if row['helper_role'] == 'HELPER_TRAIN_BOOST']
    if len(rows) != 550 or len({row['candidate_id'] for row in rows}) != 550:
        raise ValueError('Expected exact550 Boost membership')
    selection = load(selected)['families']['SOLIDER_RGB']
    if selection['configuration'] != 'SOLIDER_RGB_B':
        raise ValueError('Requested SOLIDER_RGB_B selection changed')
    binding = load(Path(selection['metrics']['metrics_path']).parent/'BINDING.json')
    helper_source = selected.parent/'source_frozen/train_annotation_helper.py'
    if file_hash(helper_source) != binding['script_sha256']:
        raise ValueError('Selected trainer source changed')
    sam_source, sam_checkpoint = Path(sam_source).resolve(), Path(sam_checkpoint).resolve()
    files = {str(helper_source): file_hash(helper_source), str(selected): file_hash(selected),
             str(workset/'WORKSET.csv'): file_hash(workset/'WORKSET.csv'),
             selection['checkpoint']: selection['checkpoint_sha256'],
             binding['arguments']['checkpoint']: binding['checkpoint_sha256']}
    dataset = Path(binding['arguments']['dataset'])
    parity_sample = load(dataset/'MANIFEST.json')['val'][0]
    parity_image = dataset/parity_sample['img_path']
    files[str(parity_image)] = binding['dataset']['files'][parity_sample['img_path']]
    parity_prediction = Path(selection['metrics']['metrics_path']).parent/'validation_predictions'/(parity_sample['sample_id']+'.png')
    files[str(parity_prediction)] = file_hash(parity_prediction)
    trees = [Path(binding['arguments']['source']), sam_source/'third_party/sam3/sam3', sam_source/'src']
    for tree in trees:
        for path in sorted(tree.rglob('*.py')):
            files[str(path)] = file_hash(path)
    from train_annotation_helper import tree_hash
    if tree_hash(binding['arguments']['source']) != binding['model_source_sha256']:
        raise ValueError('Selected SOLIDER architecture source changed')
    sam_digest = file_hash(sam_checkpoint)
    if sam_digest != '0567debeec80ba4ac6369540c6c248025283cb3ff2b92827509e57e2b3541cb6':
        raise ValueError('SAM3.1 pretrained checkpoint identity mismatch')
    files[str(sam_checkpoint)] = sam_digest
    for path, digest in files.items():
        if file_hash(path) != digest:
            raise ValueError('Dependency changed during preparation')
    for row in rows:
        path = workset/row['export_image']
        if file_hash(path) != row['image_sha256']:
            raise ValueError('Boost input changed')
        with Image.open(path) as image:
            image.load()
            if image.size != (int(row['width']), int(row['height'])):
                raise ValueError('Boost input dimensions changed')
    output = fresh_external(output, workset)
    output.mkdir(parents=True)
    frozen = output/'source_frozen'
    frozen.mkdir()
    for name in ['generate_boost_drafts.py', 'person_pseudolabel.py', 'boost_draft_progress.py',
                 'benchmark_helper_inference.py']:
        source = Path(__file__).parent/name
        shutil.copyfile(source, frozen/name)
        files[str(frozen/name)] = file_hash(source)
    config = {'schema': 'boost550-sam31-solider-rgb-b-v1', 'created_at_utc': now(),
              'workset': str(workset), 'rows': rows, 'selection': selection,
              'helper_source': str(helper_source), 'helper_arguments': binding['arguments'],
              'parity_image': str(parity_image), 'parity_prediction': str(parity_prediction),
              'sam_source': str(sam_source), 'sam_checkpoint': str(sam_checkpoint),
              'source_files_sha256': files, 'expected': 550, 'batch_size': 1,
              'precision': 'FP32', 'amp': False, 'tf32': False, 'extra_tta': False,
              'person_prompt': 'person', 'person_score_threshold': .25,
              'person_order': 'original bbox y1,x1,y2,x2,descending score; one-based local IDs',
              'crop_context_fraction': .15, 'letterbox_wh': [384, 576],
              'ownership': 'SAM person-mask intersection for editable draft; preserve raw parser planes',
              'polygon': 'all external components, epsilon0.5px, holes/raster differences reported',
              'small_person': 'retain proposals and parts; flag predicted longest bbox side<50 for human scope review',
              'resource_policy': 'SHARED_GPU_QUALITY_ONLY_ANNOTATION_HELPER',
              'admission_free_vram_gib': 10, 'disk_free_gib': 50, 'output_cap_gib': 20,
              'max_execution_seconds': 7200, 'max_persons_per_image': 100, 'automatic_retries': 0,
              'visual_gate_after_images': 3, 'packages': binding['packages'],
              'torch_version': binding['torch_version'],
              'annotation_repository_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    write(output/'CONFIG.json', config)
    (output/'CONFIG.sha256').write_text(file_hash(output/'CONFIG.json')+'\n')
    write(output/'STATUS.json', {'state': 'PREPARED', 'expected': 550, 'completed': 0})
    return output


def bindings(root):
    if file_hash(root/'CONFIG.json') != (root/'CONFIG.sha256').read_text().strip():
        raise ValueError('Frozen run configuration changed')
    config = load(root/'CONFIG.json')
    for path, digest in config['source_files_sha256'].items():
        if file_hash(path) != digest:
            raise ValueError('Bound source, model or workset changed')
    return config, file_hash(root/'CONFIG.json')


def import_helper(path):
    spec = importlib.util.spec_from_file_location('selected_boost_helper', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_preview(image, owned, people, path):
    rgb = np.asarray(image).copy()
    for plane in owned:
        for label, color in PALETTE.items():
            pixels = plane == label
            rgb[pixels] = (rgb[pixels]*.5+np.array(color)*.5).astype('uint8')
    overlay = Image.fromarray(rgb)
    draw = ImageDraw.Draw(overlay)
    for person in people:
        draw.rectangle(person['bbox_xyxy'], outline='cyan', width=2)
        draw.text(tuple(person['bbox_xyxy'][:2]), str(person['person_id']), fill='cyan')
    result = Image.new('RGB', (image.width*2, image.height))
    result.paste(image, (0, 0))
    result.paste(overlay, (image.width, 0))
    result.thumbnail((2400, 1200))
    result.save(path)


def export_frame(root, config, protocol_sha, row, image, proposals, parser, infer):
    identifier = row['candidate_id']
    partial = root/'packets'/(identifier+'.partial')
    partial.mkdir()
    shapes, people, owned_planes = [], [], []
    for index, proposal in enumerate(proposals, 1):
        box, person_mask, score = proposal
        canvas, geometry = image_crop(image, box)
        predicted, timing = infer(parser, 'solider', canvas)
        raw = original_labels(predicted, geometry, image.size)
        owned = np.where(person_mask, raw, 0).astype('uint8')
        owned_planes.append(owned)
        stem = f'person_{index:03}'
        Image.fromarray(person_mask.astype('uint8')*255).save(partial/(stem+'_person.png'))
        Image.fromarray(raw).save(partial/(stem+'_raw.png'))
        Image.fromarray(owned).save(partial/(stem+'_owned.png'))
        x1, y1, x2, y2 = box
        shapes.append(editor_shape('bbox', 'rectangle', [[x1, y1], [x2, y1], [x2, y2], [x1, y2]], index, score))
        regions, diagnostics = polygon_view(owned, index)
        shapes.extend(regions)
        people.append({'person_id': index, 'bbox_xyxy': box, 'detector_score': score,
                       'predicted_under50_review': max(x2-x1, y2-y1) < 50,
                       'geometry': geometry, 'parsing_timing': timing,
                       'person_mask': stem+'_person.png', 'raw_labels': stem+'_raw.png',
                       'owned_labels': stem+'_owned.png', 'parts': diagnostics,
                       'outside_person_target_pixels': int(((raw > 0) & ~person_mask).sum()),
                       'colors': {'upper': 'NOT_ASSESSED', 'lower': 'NOT_ASSESSED'}})
    annotation = {'version': '4.3.2', 'flags': {'draft_not_gt': True}, 'checked': False,
                  'shapes': shapes, 'imagePath': Path(row['export_image']).name, 'imageData': None,
                  'imageWidth': image.width, 'imageHeight': image.height,
                  'description': 'SAM3.1 pretrained person boxes + SOLIDER_RGB_B; human review pending'}
    write(partial/'annotation.json', annotation)
    render_preview(image, owned_planes, people, partial/'PREVIEW.jpg')
    overlap = np.zeros((image.height, image.width), dtype='uint16')
    for plane in owned_planes:
        overlap += plane > 0
    hashes = {path.name: file_hash(path) for path in partial.iterdir() if path.is_file()}
    packet = {'schema': config['schema'], 'candidate_id': identifier, 'input_sha256': row['image_sha256'],
              'protocol_sha256': protocol_sha, 'accepted_gt': False, 'people': people,
              'cross_owner_overlap_pixels': int((overlap > 1).sum()), 'artifact_sha256': hashes,
              'no_proposals_means': 'HUMAN_PERSON_INVENTORY_REQUIRED', 'created_at_utc': now()}
    write(partial/'PACKET.json', packet)
    verify_packet(partial, row, protocol_sha)
    final = root/'packets'/identifier
    commit_directory(partial, final)
    publish_editor(root, row, final)
    return packet


def publish_editor(root, row, packet):
    destination = root/'xanylabeling'/Path(row['work_pack']).name/'images'
    destination.mkdir(parents=True, exist_ok=True)
    image = destination/Path(row['export_image']).name
    annotation = image.with_suffix('.json')
    if image.exists() and file_hash(image) != row['image_sha256']:
        raise ValueError('Editor image changed')
    if annotation.exists() and file_hash(annotation) != file_hash(packet/'annotation.json'):
        raise ValueError('Editor annotations already edited; preserve user changes')
    if not image.exists():
        source = Path(load(root/'CONFIG.json')['workset'])/row['export_image']
        temporary = image.with_suffix(image.suffix+'.tmp')
        shutil.copyfile(source, temporary)
        if file_hash(temporary) != row['image_sha256']:
            raise ValueError('Editor image copy mismatch')
        os.replace(temporary, image)
    if not annotation.exists():
        write(annotation, load(packet/'annotation.json'))


def run(root):
    import torch
    root = Path(root).resolve()
    # One active Boost generation process across all fresh attempts.
    lock_path = root.parent.parent/'boost550_generation.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config, protocol_sha = bindings(root)
        prior = load(root/'STATUS.json')
        if prior['state'] in ['FAILED', 'STOPPED_RESOURCE']:
            raise ValueError('Failed attempt requires controlled review before another model attempt')
        pid = os.getpid()
        started = time.monotonic()
        completed = 0
        phase, identifier = 'LOADING', None
        def status(state, **extra):
            write(root/'STATUS.json', {'state': state, 'at_utc': now(), 'pid': pid,
                                      'completed': completed, 'expected': 550,
                                      'latest_image': identifier, **extra})
        def guard(admission=False):
            if time.monotonic()-started > config['max_execution_seconds']:
                raise RuntimeError('Execution time budget reached')
            if shutil.disk_usage(root).free < config['disk_free_gib']*1024**3:
                raise RuntimeError('Disk free-space guard')
            if admission and torch.cuda.mem_get_info()[0] < config['admission_free_vram_gib']*1024**3:
                raise RuntimeError('GPU memory admission guard')
            size = sum(path.stat().st_size for path in root.rglob('*') if path.is_file())
            if size > config['output_cap_gib']*1024**3:
                raise RuntimeError('Output size guard')
        status('LOADING')
        event(root, state='PROCESS_START', pid=pid, config_sha256=protocol_sha)
        try:
            if not torch.cuda.is_available() or torch.__version__ != config['torch_version']:
                raise ValueError('CUDA/runtime binding mismatch')
            for name, version in config['packages'].items():
                if importlib.metadata.version(name) != version:
                    raise ValueError('Environment package binding mismatch')
            guard(admission=True)
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            torch.manual_seed(20261113)
            torch.cuda.reset_peak_memory_stats()
            sys.path.insert(0, str(Path(config['sam_source'])/'src'))
            from sam31_labeling import build_detector
            detector, detector_binding = build_detector(config['sam_checkpoint'], 'cuda:0')
            from sam3.model.sam3_image_processor import Sam3Processor
            detector = detector.float().eval()
            processor = Sam3Processor(detector, resolution=1008, device='cuda:0',
                                      confidence_threshold=config['person_score_threshold'])
            helper = import_helper(config['helper_source'])
            arguments = SimpleNamespace(**config['helper_arguments'])
            arguments.warmstart = config['selection']['checkpoint']
            parser = helper.DenseHelper(arguments, torch.device('cuda:0'))
            parser.model.float().eval()
            sys.path.insert(0, str(Path(__file__).parent))
            # The accepted timing adapter uses the same logits path as validation.
            timing_source = Path(__file__).parent/'benchmark_helper_inference.py'
            timing = import_helper(timing_source)
            with Image.open(config['parity_image']) as img:
                parity_image = img.convert('RGB')
            with torch.inference_mode():
                predicted, _ = timing.timed_prediction(parser, 'solider', parity_image)
            with Image.open(config['parity_prediction']) as img:
                expected = np.asarray(img)
            if not np.array_equal(predicted, expected):
                raise ValueError('Selected parser saved-mask parity failed')
            write(root/'READINESS.json', {'state': 'PASS', 'detector_load': detector_binding,
                  'parser_validation_parity': 'EXACT_ONE_FIXED_CROP', 'parser_warmup_calls': 1,
                  'gpu': torch.cuda.get_device_name(), 'precision': 'FP32',
                  'packages': config['packages'], 'at_utc': now()})
            (root/'packets').mkdir(exist_ok=True)
            expected_ids = {row['candidate_id'] for row in config['rows']}
            if any(path.name not in expected_ids for path in (root/'packets').iterdir() if path.is_dir()):
                raise ValueError('Partial/orphan directory requires controlled reconciliation')
            status('RUNNING')
            phase = 'INFERENCE'
            for row in config['rows']:
                identifier = row['candidate_id']
                final = root/'packets'/identifier
                if final.exists():
                    verify_packet(final, row, protocol_sha)
                    publish_editor(root, row, final)
                    completed += 1
                    event(root, state='REUSED_COMMITTED_PACKET', candidate_id=identifier)
                    continue
                guard()
                source = Path(config['workset'])/row['export_image']
                if file_hash(source) != row['image_sha256']:
                    raise ValueError('Input changed before inference')
                with Image.open(source) as img:
                    image = img.convert('RGB')
                event(root, state='IMAGE_STARTED', candidate_id=identifier)
                status('RUNNING', phase='SAM31_PERSON', persons_completed=0)
                begun = time.perf_counter()
                with torch.inference_mode(), torch.autocast('cuda', enabled=False):
                    state = processor.set_image(image)
                    state = processor.set_text_prompt('person', state)
                    masks = state['masks'].detach().cpu().numpy()
                    boxes = state['boxes'].detach().float().cpu().numpy()
                    scores = state['scores'].detach().float().cpu().numpy()
                torch.cuda.synchronize()
                if (masks.shape != (len(scores), 1, image.height, image.width) or
                    boxes.shape != (len(scores), 4) or not np.isfinite(boxes).all() or
                    not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)) or
                    len(scores) > config['max_persons_per_image']):
                    raise ValueError('SAM3.1 output contract failed')
                proposals = []
                for box, mask, score in zip(boxes, masks[:, 0], scores):
                    box = [float(np.clip(box[0], 0, image.width)), float(np.clip(box[1], 0, image.height)),
                           float(np.clip(box[2], 0, image.width)), float(np.clip(box[3], 0, image.height))]
                    if not (box[2] > box[0] and box[3] > box[1]) or not mask.any():
                        raise ValueError('Empty SAM3.1 person extent')
                    proposals.append((box, mask.astype(bool), float(score)))
                proposals.sort(key=lambda p: (p[0][1], p[0][0], p[0][3], p[0][2], -p[2]))
                event(root, state='PERSON_PROPOSALS_COMPLETED', candidate_id=identifier,
                      persons=len(proposals), seconds=time.perf_counter()-begun)
                del state, masks, boxes, scores
                def infer(model, kind, canvas):
                    with torch.inference_mode():
                        return timing.timed_prediction(model, kind, canvas)
                status('RUNNING', phase='SOLIDER_AND_EXPORT', proposed_persons=len(proposals))
                packet = export_frame(root, config, protocol_sha, row, image, proposals, parser, infer)
                completed += 1
                event(root, state='IMAGE_COMMITTED', candidate_id=identifier, persons=len(packet['people']),
                      packet_sha256=file_hash(final/'PACKET.json'))
                status('RUNNING', phase='IMAGE_COMMITTED', persons=len(packet['people']))
                if completed == config['visual_gate_after_images'] and not (root/'EXPORT_CHECK.json').exists():
                    status('WAITING_EXPORT_CHECK')
                    while not (root/'EXPORT_CHECK.json').exists():
                        guard()
                        time.sleep(2)
                    check = load(root/'EXPORT_CHECK.json')
                    if check.get('state') != 'PASS' or check.get('protocol_sha256') != protocol_sha:
                        raise ValueError('Export check rejected or binding mismatch')
            phase = 'CLOSURE'
            packets = [verify_packet(root/'packets'/row['candidate_id'], row, protocol_sha) for row in config['rows']]
            if {p.name for p in (root/'packets').iterdir()} != expected_ids:
                raise ValueError('Final exact-ID membership mismatch')
            result = {'state': 'DRAFTS_COMPLETE_REQUIRES_HUMAN_REVIEW', 'expected': 550,
                      'completed': len(packets), 'missing': 0, 'duplicate': 0, 'invalid': 0,
                      'failed_this_attempt': 0, 'persons': sum(len(p['people']) for p in packets),
                      'zero_proposal_images': sum(not p['people'] for p in packets),
                      'accepted_gt_images': 0, 'protocol_sha256': protocol_sha, 'at_utc': now(),
                      'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
                      'peak_reserved_bytes': torch.cuda.max_memory_reserved()}
            write(root/'COMPLETION.json', result)
            status(result['state'], persons=result['persons'])
            event(root, state='BATCH_COMPLETE', completed=completed)
        except BaseException as error:
            (root/'TRACEBACK.txt').write_text(traceback.format_exc())
            event(root, state='FAILED', phase=phase, candidate_id=identifier,
                  error_type=type(error).__name__, message=str(error))
            status('FAILED', phase=phase, error_type=type(error).__name__, message=str(error))
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--workset', type=Path)
    parser.add_argument('--selected', type=Path)
    parser.add_argument('--sam-source', type=Path)
    parser.add_argument('--sam-checkpoint', type=Path)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.prepare:
        print(prepare(args.workset, args.selected, args.sam_source, args.sam_checkpoint, args.run_dir))
    else:
        run(args.run_dir)


if __name__ == '__main__':
    main()
