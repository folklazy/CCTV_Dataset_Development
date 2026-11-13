"""Prepare a reversible editor view and overlap-review queue from saved Boost drafts."""
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from person_pseudolabel import file_hash, fresh_external, load, write
from generate_boost_drafts import polygon_view, editor_shape

POLICY = {'version': 'boost-plan-triage-view-3', 'minimum_person_score': .50, 'clean_person_score': .85,
          'size_cutoff_px': 50, 'borderline_px': [45, 55], 'editable_parts': 'RAW4PARTS_WITH_OWNERSHIP_WARNINGS', 'near_duplicate_mask_iou': .85,
          'near_duplicate_box_iou': .5, 'review_box_iou': .3, 'review_box_iomin': .8,
          'review_mask_iomin': .9, 'priority': 'SAM score descending, original person ID ascending',
          'role': 'PROVISIONAL_DRAFT_VIEW_NOT_GT', 'fragment_filter': 'NONE'}


def box_overlap(a, b):
    intersection = max(0., min(a[2], b[2])-max(a[0], b[0]))*max(0., min(a[3], b[3])-max(a[1], b[1]))
    area_a = (a[2]-a[0])*(a[3]-a[1])
    area_b = (b[2]-b[0])*(b[3]-b[1])
    return intersection/(area_a+area_b-intersection), intersection/min(area_a, area_b)


def compare_masks(a, b):
    if a.shape != b.shape or a.dtype != bool or b.dtype != bool:
        raise ValueError('Expected original-grid binary person masks')
    intersection = int((a & b).sum())
    area_a, area_b = int(a.sum()), int(b.sum())
    if not min(area_a, area_b):
        raise ValueError('Empty person extent')
    return {'mask_iou': intersection/(area_a+area_b-intersection),
            'mask_iomin': intersection/min(area_a, area_b),
            'coverage_a': intersection/area_a, 'coverage_b': intersection/area_b}


def select_people(people, pairs):
    """Greedy proposal preference only; nearby/contained extents remain distinct."""
    lookup = {frozenset([p['person_a'], p['person_b']]): p for p in pairs}
    kept, suppressed = [], {}
    for person in sorted(people, key=lambda p: (-p['detector_score'], p['person_id'])):
        identifier = person['person_id']
        match = None
        for existing in kept:
            pair = lookup.get(frozenset([identifier, existing]))
            if pair and pair['mask_iou'] >= POLICY['near_duplicate_mask_iou'] and pair['box_iou'] >= POLICY['near_duplicate_box_iou']:
                match = existing
                break
        if match is None:
            kept.append(identifier)
        else:
            suppressed[identifier] = match
    return set(kept), suppressed


def long_side(box):
    return max(box[2]-box[0], box[3]-box[1])


def size_state(box, envelope):
    model_side, mask_side = long_side(box), long_side(envelope)
    straddles = (model_side < 50) != (mask_side < 50)
    borderline = straddles or any(45 <= value <= 55 for value in [model_side, mask_side])
    return {'model_long_side_px': model_side, 'mask_long_side_px': mask_side,
            'below50_draft': max(model_side, mask_side) < 50,
            'check50': borderline, 'measurement_source': 'original-grid model bbox and mask envelope',
            'human_size_confirmation': 'PENDING'}


def draft_action(score, size):
    if not np.isfinite(score) or not 0 <= score <= 1:
        raise ValueError('Invalid SAM person score')
    if score < POLICY['minimum_person_score']:
        return 'LOW_SCORE_HIDDEN'
    if size['below50_draft']:
        return 'IGNORE_CANDIDATE'
    return 'PARTS_DRAFT'


def plan_view(annotation, people, pairs, envelopes, raw_labels):
    sizes = {p['person_id']: size_state(p['bbox_xyxy'], envelopes[p['person_id']]) for p in people}
    actions = {p['person_id']: draft_action(p['detector_score'], sizes[p['person_id']]) for p in people}
    candidates = [p for p in people if actions[p['person_id']] != 'LOW_SCORE_HIDDEN']
    kept, suppressed = select_people(candidates, pairs)
    for identifier in suppressed:
        actions[identifier] = 'DUPLICATE_ALTERNATIVE_HIDDEN'
    shapes, audits, flags = [], [], []
    retained = [p for p in people if p['person_id'] in kept and actions[p['person_id']] == 'PARTS_DRAFT']
    for person in people:
        identifier = person['person_id']
        action = actions[identifier]
        tags = []
        box = person['bbox_xyxy']
        x1, y1, x2, y2 = box
        tag = f"Person #{identifier}; SAM person score={person['detector_score']:.3f}; bbox_long_side={long_side(box):.1f}px"
        if sizes[identifier]['check50']:
            tags.append('CHECK_50PX')
        if action == 'PARTS_DRAFT':
            if person['detector_score'] < POLICY['clean_person_score']:
                tags.append('LOW_PERSON_SCORE_FOR_CLEAN_QUEUE')
            if any(box_overlap(box, q['bbox_xyxy'])[0] > 0 for q in retained if q['person_id'] != identifier):
                tags.append('CHECK_CROWD_OWNERSHIP')
            bbox = editor_shape('bbox', 'rectangle', [[x1,y1],[x2,y1],[x2,y2],[x1,y2]], identifier, person['detector_score'])
            regions, diagnostics = polygon_view(raw_labels[identifier], identifier)
            if any(d['mask_pixels'] == 0 for d in diagnostics.values()):
                tags.append('EMPTY_PART_PROPOSAL')
            if any(d['holes'] for d in diagnostics.values()):
                tags.append('CHECK_POLYGON_HOLES')
            for shape in [bbox, *regions]:
                shape['description'] = '['+(','.join(tags) if tags else 'NO_AUTO_FLAGS')+'] '+tag
            shapes.extend([bbox, *regions])
        elif action == 'IGNORE_CANDIDATE':
            # A coarse exclusion must not be painted over an eligible-person candidate.
            if any(box_overlap(box, q['bbox_xyxy'])[0] > 0 for q in retained):
                tags.append('CHECK_SMALL_IGNORE_OVERLAP_ELIGIBLE')
            else:
                shape = editor_shape('ignore', 'rectangle', [[x1,y1],[x2,y1],[x2,y2],[x1,y2]], None)
                shape['description'] = '[SMALL_IGNORE_DRAFT_REQUIRES_SIZE_CONFIRMATION] '+tag
                shapes.append(shape)
            tags.append('SMALL_IGNORE_REVIEW')
        else:
            tags.append(action)
        flags.extend(tags)
        audits.append({'person_id': identifier, 'action': action, 'sam_person_score': person['detector_score'],
                       'size': sizes[identifier], 'flags': tags, 'suppressed_to': suppressed.get(identifier),
                       'raw_labels': person['raw_labels'], 'owned_labels': person['owned_labels'],
                       'outside_helper_person_pixels_warning': person['outside_person_target_pixels'],
                       'polygon_diagnostics': diagnostics if action == 'PARTS_DRAFT' else None})
    if not retained:
        flags.append('NO_ELIGIBLE_PARTS_DRAFT_CHECK_FULL_IMAGE')
    result = json.loads(json.dumps(annotation))
    result['shapes'] = shapes
    result['description'] = 'Boost plan triage revision3; raw parts; automatic draft; full-image human review pending'
    result['checked'] = False
    result.setdefault('flags', {})['draft_not_gt'] = True
    return result, audits, sorted(set(flags)), suppressed


def csv_write(path, records):
    if not records:
        return
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def protected_membership(rows, receipt):
    batches = set(receipt['batches'])
    allowed = {f'batch_{n:02d}' for n in range(1, 12)}
    if not batches or not batches <= allowed:
        raise ValueError('Invalid reviewed batch names')
    expected = {r['candidate_id'] for r in rows if Path(r['work_pack']).name in batches}
    files = receipt['files']
    protected = {r['candidate_id']: r for r in files}
    if set(protected) != expected or len(protected) != len(files) or len(expected) != 50*len(batches):
        raise ValueError('Reviewed receipt membership differs from the declared complete batches')
    return protected


def prepare(parent, output, plan, preserve_receipt):
    parent = Path(parent).resolve()
    output = fresh_external(output, parent)
    config, completion = load(parent/'CONFIG.json'), load(parent/'COMPLETION.json')
    config_sha = file_hash(parent/'CONFIG.json')
    if config_sha != (parent/'CONFIG.sha256').read_text().strip() or config_sha != completion['protocol_sha256']:
        raise ValueError('Parent config binding changed')
    rows = config['rows']
    if len(rows) != 550 or len({r['candidate_id'] for r in rows}) != 550 or completion['completed'] != 550:
        raise ValueError('Parent needs exact550 completed images')
    if {p.name for p in (parent/'packets').iterdir()} != {r['candidate_id'] for r in rows}:
        raise ValueError('Parent packet membership mismatch')
    receipt = load(preserve_receipt)
    protected = protected_membership(rows, receipt)
    output.mkdir(parents=True)
    shutil.copyfile(plan, output/'MASTER_PLAN_INPUT.md')
    all_pairs, manifest, person_audits, image_index = [], [], [], []
    counts = Counter()
    for row in rows:
        packet_dir = parent/'packets'/row['candidate_id']
        packet = load(packet_dir/'PACKET.json')
        if (packet['protocol_sha256'] != config_sha or packet['candidate_id'] != row['candidate_id'] or
                packet['input_sha256'] != row['image_sha256']):
            raise ValueError('Parent packet binding mismatch')
        people = packet['people']
        masks, envelopes, raw = {}, {}, {}
        for person in people:
            identifier = person['person_id']
            for key in ['person_mask', 'raw_labels']:
                path = packet_dir/person[key]
                if file_hash(path) != packet['artifact_sha256'][person[key]]:
                    raise ValueError('Referenced canonical mask changed')
                with Image.open(path) as image:
                    image.load()
                    if image.size != (int(row['width']), int(row['height'])):
                        raise ValueError('Original-grid geometry mismatch')
                    array = np.array(image)
                    allowed = {0,255} if key == 'person_mask' else set(range(5))
                    if not set(np.unique(array)) <= allowed:
                        raise ValueError('Mask labels invalid')
                    if key == 'person_mask':
                        masks[identifier], envelopes[identifier] = array > 0, image.getbbox()
                    else:
                        raw[identifier] = array
        pairs = []
        for index, a in enumerate(people):
            for b in people[index+1:]:
                box_iou, box_iomin = box_overlap(a['bbox_xyxy'], b['bbox_xyxy'])
                if box_iou < POLICY['review_box_iou'] and box_iomin < POLICY['review_box_iomin']:
                    continue
                pair = {'candidate_id': row['candidate_id'], 'person_a': a['person_id'], 'person_b': b['person_id'],
                        'box_iou': box_iou, 'box_iomin': box_iomin,
                        **compare_masks(masks[a['person_id']], masks[b['person_id']])}
                pairs.append(pair)
        source_image = parent/'xanylabeling'/Path(row['work_pack']).name/'images'/Path(row['export_image']).name
        source_annotation = source_image.with_suffix('.json')
        source_bytes = source_annotation.read_bytes()
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        annotation = json.loads(source_bytes)
        human_modified = source_sha != packet['artifact_sha256']['annotation.json']
        user_reviewed = row['candidate_id'] in protected
        if user_reviewed and source_sha != protected[row['candidate_id']]['sha256']:
            raise ValueError('User-reviewed file changed after receipt; preserve and reconcile')
        if human_modified or user_reviewed:
            derived, audits, flags, suppressed = annotation, [], ['EXISTING_EDITOR_CHANGES_PRESERVED'], {}
            counts['editor_inputs_preserved'] += 1
            counts['modified_editor_inputs_preserved'] += human_modified
            counts['user_reviewed_images_preserved'] += user_reviewed
        else:
            derived, audits, flags, suppressed = plan_view(annotation, people, pairs, envelopes, raw)
        bucket = '00_reviewed' if user_reviewed else '02_needs_edit' if flags else '01_clean_ready'
        if user_reviewed:
            flags = ['USER_REPORTED_REVIEW_COMPLETED']
        for audit in audits:
            audit['candidate_id'] = row['candidate_id']
            counts[audit['action']] += 1
        person_audits.extend(audits)
        all_pairs.extend(pairs)
        if file_hash(source_image) != row['image_sha256']:
            raise ValueError('Source editor image changed')
        destination = output/bucket/Path(row['work_pack']).name/'images'/source_image.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_image, destination)
        write(destination.with_suffix('.json'), derived)
        if file_hash(destination) != row['image_sha256'] or load(destination.with_suffix('.json')) != derived:
            raise ValueError('Editor copy readback failed')
        boxes = sum(s['label']=='bbox' for s in derived['shapes'])
        ignores = sum(s['label']=='ignore' for s in derived['shapes'])
        counts[bucket] += 1
        counts['editor_bbox_shapes'] += boxes
        counts['editor_ignore_shapes'] += ignores
        manifest.append({'candidate_id': row['candidate_id'], 'parent_packet_sha256': file_hash(packet_dir/'PACKET.json'),
                         'source_editor_json_sha256': source_sha,
                         'output_json': str(destination.with_suffix('.json').relative_to(output)),
                         'output_json_sha256': file_hash(destination.with_suffix('.json')),
                         'suppressed_to_kept': suppressed, 'editor_changes_preserved': human_modified,
                         'user_reviewed_preserved': user_reviewed})
        image_index.append({'candidate_id': row['candidate_id'], 'queue': bucket,
                            'annotation': str(destination.with_suffix('.json').relative_to(output)),
                            'bbox_shapes': boxes, 'ignore_shapes': ignores, 'flags': '|'.join(flags)})
    csv_write(output/'OVERLAP_REVIEW.csv', all_pairs)
    csv_write(output/'IMAGE_INDEX.csv', image_index)
    write(output/'MANIFEST.json', manifest)
    write(output/'PERSON_AUDIT.json', person_audits)
    summary = {'state': 'PLAN_ALIGNED_DRAFT_VIEW_REQUIRES_HUMAN_REVIEW', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
               'images': len(manifest), 'parent': str(parent), 'parent_config_sha256': config_sha,
               'master_plan': str(Path(plan).resolve()), 'master_plan_sha256': file_hash(plan),
               'preserve_receipt': str(Path(preserve_receipt).resolve()), 'preserve_receipt_sha256': file_hash(preserve_receipt),
               'policy': POLICY, 'counts': dict(counts), 'original_person_proposals': completion['persons'],
               'overlap_candidate_pairs': len(all_pairs), 'model_calls': 0, 'source_files_modified': 0,
               'script_sha256': file_hash(__file__), 'manifest_sha256': file_hash(output/'MANIFEST.json')}
    write(output/'SUMMARY.json', summary)
    return summary


def assemble_editor_batches(prepared, output):
    """Use one editable JSON per image; queue manifests reference that same file."""
    prepared = Path(prepared).resolve()
    output = fresh_external(output, prepared)
    summary = load(prepared/'SUMMARY.json')
    if file_hash(prepared/'MANIFEST.json') != summary['manifest_sha256']:
        raise ValueError('Prepared view manifest changed')
    parent = Path(summary['parent'])
    rows = {r['candidate_id']: r for r in load(parent/'CONFIG.json')['rows']}
    manifest = load(prepared/'MANIFEST.json')
    if len(manifest) != 550 or {r['candidate_id'] for r in manifest} != set(rows):
        raise ValueError('Prepared view membership mismatch')
    output.mkdir(parents=True)
    final, queues = [], {'00_reviewed': [], '01_clean_ready': [], '02_needs_edit': []}
    for record in manifest:
        row = rows[record['candidate_id']]
        source = prepared/record['output_json']
        current = parent/'xanylabeling'/Path(row['work_pack']).name/'images'/Path(row['export_image']).with_suffix('.json').name
        if file_hash(current) != record['source_editor_json_sha256']:
            raise ValueError('Parent editor changed during export; reconcile current edits')
        if file_hash(source) != record['output_json_sha256']:
            raise ValueError('Prepared annotation changed')
        image = source.with_suffix(Path(row['export_image']).suffix)
        destination = output/'xanylabeling'/Path(row['work_pack']).name/'images'/image.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        annotation_source = current if record['user_reviewed_preserved'] or record['editor_changes_preserved'] else source
        expected_json_sha = file_hash(annotation_source)
        shutil.copyfile(image, destination)
        shutil.copyfile(annotation_source, destination.with_suffix('.json'))
        if file_hash(destination) != row['image_sha256'] or file_hash(destination.with_suffix('.json')) != expected_json_sha:
            raise ValueError('Final editor batch copy changed')
        queue = Path(record['output_json']).parts[0]
        entry = {**record, 'prepared_json': str(source), 'queue': queue,
                 'prepared_json_sha256': record['output_json_sha256'], 'output_json_sha256': expected_json_sha,
                 'output_json': str(destination.with_suffix('.json').relative_to(output))}
        final.append(entry)
        queues[queue].append({'candidate_id': record['candidate_id'], 'annotation': entry['output_json']})
    write(output/'MANIFEST.json', final)
    for name, entries in queues.items():
        directory = output/name
        directory.mkdir()
        csv_write(directory/'QUEUE.csv', entries)
    result = {**summary, 'prepared_view': str(prepared), 'prepared_summary_sha256': file_hash(prepared/'SUMMARY.json'),
              'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'layout': 'One editable batch tree; three queue manifests refer to the same JSON files',
              'queue_counts': {name: len(entries) for name, entries in queues.items()},
              'manifest_sha256': file_hash(output/'MANIFEST.json'), 'assembly_source_sha256': file_hash(__file__)}
    write(output/'SUMMARY.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--parent', type=Path)
    mode.add_argument('--assemble-from', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--preserve-receipt', type=Path)
    args = parser.parse_args()
    if args.assemble_from:
        result = assemble_editor_batches(args.assemble_from, args.output)
    else:
        if not args.plan or not args.preserve_receipt:
            parser.error('Preparing requires --plan and --preserve-receipt')
        result = prepare(args.parent, args.output, args.plan, args.preserve_receipt)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
