"""Measure selected helper checkpoints on fixed, decoded validation person crops."""
import argparse
import hashlib
import importlib.util
import importlib.metadata
import json
import os
from pathlib import Path
import statistics
import time
from types import SimpleNamespace

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision.transforms.functional import to_tensor


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summarize(records):
    values = [record['total_ms'] for record in records]
    if not values or any(not np.isfinite(value) or value <= 0 for value in values):
        raise ValueError('Missing or invalid inference durations')
    return {'mean_ms_per_roi': statistics.mean(values),
            'median_ms_per_roi': statistics.median(values),
            'total_measured_ms': sum(values), 'measured_calls': len(values)}


def live_features(helper, image):
    # Same RGB/float resize and normalization as PromptHelper.features, kept on GPU.
    image = F.interpolate(image, size=(1008, 1008), mode='bilinear',
                          align_corners=False, antialias=True)
    features = helper.model.backbone.forward_image((image-.5)/.5)
    return {key: features[key] for key in ['vision_features', 'backbone_fpn', 'vision_pos_enc']} | {
        'vision_mask': features.get('vision_mask')}


def timed_prediction(helper, kind, image, synchronize=torch.cuda.synchronize,
                     clock=time.perf_counter):
    synchronize()
    started = clock()
    prepared = image.resize((512, 512), Image.Resampling.BILINEAR) if kind == 'b5' else image
    tensor = to_tensor(prepared)[None].to(helper.device)
    synchronize()
    prepared_at = clock()
    with torch.no_grad():
        if kind == 'sam31':
            features = live_features(helper, tensor)
            planes = []
            for label in range(1, 5):
                masks, scores, _ = helper.forward(features, label)
                confidence = scores.sigmoid()
                best = int(confidence.argmax())
                probability = masks[best].sigmoid()
                planes.append(torch.where((confidence[best] > .2) & (probability > .5),
                                           probability*confidence[best], 0.))
            planes = torch.stack(planes)
            prediction = planes.argmax(0)+1
            prediction[planes.max(0).values == 0] = 0
        else:
            prediction = helper.logits(tensor).argmax(1)[0]
    synchronize()
    predicted_at = clock()
    result = prediction.cpu().numpy().astype('uint8')
    synchronize()
    finished = clock()
    if result.shape != (image.height, image.width) or not set(np.unique(result)) <= set(range(5)):
        raise ValueError('Prediction geometry or labels violate the helper contract')
    return result, {'input_prepare_h2d_ms': (prepared_at-started)*1000,
                    'parser_route_ms': (predicted_at-prepared_at)*1000,
                    'cpu_readback_ms': (finished-predicted_at)*1000,
                    'total_ms': (finished-started)*1000}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--configuration', required=True)
    cli = parser.parse_args()
    config = json.loads(cli.manifest.read_text())
    root = cli.manifest.resolve().parent
    job = next(job for job in config['jobs'] if job['model'] == cli.configuration)
    output = Path(job['output'])
    output.mkdir()
    source_output = Path(job['source_output'])
    binding = json.loads((source_output/'BINDING.json').read_text())
    selected = json.loads((source_output/'STATUS.json').read_text())
    source = Path(job['helper_source'])
    def status(state, **values):
        path = output/'STATUS.json'
        temporary = output/'STATUS.tmp'
        temporary.write_text(json.dumps({'state': state, 'pid': os.getpid(), **values}, indent=2)+'\n')
        temporary.replace(path)
    status('LOADING')
    try:
        if selected['state'] != 'COMPLETE' or sha256(selected['checkpoint']) != selected['checkpoint_sha256']:
            raise ValueError('Selected checkpoint completion/hash mismatch')
        if sha256(source) != binding['script_sha256']:
            raise ValueError('Helper source binding mismatch')
        if torch.__version__ != binding['torch_version']:
            raise ValueError('PyTorch runtime differs from the selected result')
        packages = {key: importlib.metadata.version(key) for key in binding['packages']}
        if packages != binding['packages']:
            raise ValueError('Package versions differ from the selected result')
        if not torch.cuda.is_available():
            raise ValueError('CUDA is required by this timing protocol')
        spec = importlib.util.spec_from_file_location('frozen_helper', source)
        trainer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(trainer)
        args = SimpleNamespace(**binding['arguments'])
        args.warmstart, args.resume_training, args.feature_cache_parent = None, False, None
        if args.source and trainer.tree_hash(args.source) != binding['model_source_sha256']:
            raise ValueError('Model source tree differs from its binding')
        device = torch.device('cuda:0')
        torch.cuda.set_device(device)
        torch.manual_seed(args.seed)
        helper = (trainer.PromptHelper(args, device, output/'unused_cache', binding['dataset'])
                  if args.model == 'sam31' else trainer.DenseHelper(args, device))
        weights = torch.load(selected['checkpoint'], map_location='cpu', weights_only=True)
        loaded = helper.model.load_state_dict(weights['state_dict'], strict=args.model != 'sam31')
        if loaded.unexpected_keys or any(not key.startswith('backbone.') for key in loaded.missing_keys):
            raise ValueError('Selected checkpoint keys differ from the model')
        helper.model.eval()
        if any(parameter.is_floating_point() and parameter.dtype != torch.float32
               for parameter in helper.model.parameters()):
            raise ValueError('Expected FP32 parameters')
        dataset = Path(config['dataset'])
        items = json.loads((dataset/'MANIFEST.json').read_text())['val'][:3]
        images = []
        for item in items:
            path = dataset/item['img_path']
            if sha256(path) != binding['dataset']['files'][item['img_path']]:
                raise ValueError('Input image changed')
            with Image.open(path) as image:
                images.append(image.convert('RGB'))
        records = []
        torch.cuda.reset_peak_memory_stats(device)
        for repeat in range(config['measured_repeats']+1):
            for item, image in zip(items, images):
                prediction, timing = timed_prediction(helper, args.model, image)
                expected_path = source_output/'validation_predictions'/(item['sample_id']+'.png')
                with Image.open(expected_path) as expected_image:
                    expected = np.array(expected_image)
                if not np.array_equal(prediction, expected):
                    raise ValueError(f'Saved-mask parity failed: {item["sample_id"]}')
                if repeat:
                    record = {'sample_id': item['sample_id'], 'repeat': repeat, **timing}
                    records.append(record)
                    with (output/'LEDGER.jsonl').open('a') as stream:
                        stream.write(json.dumps(record, allow_nan=False)+'\n')
                        stream.flush()
                        os.fsync(stream.fileno())
                    status('EVALUATING', completed=len(records), expected=3*config['measured_repeats'])
        metrics = {**summarize(records), 'configuration': cli.configuration,
                   'unique_crops': len(items), 'warmup_calls': len(items),
                   'checkpoint_sha256': selected['checkpoint_sha256'],
                   'source_binding_sha256': sha256(source_output/'BINDING.json'),
                   'helper_source_sha256': sha256(source), 'all_saved_mask_parity': 'EXACT',
                   'protocol_sha256': sha256(root/'TIMING_PROTOCOL.json'),
                   'packages': packages,
                   'torch_version': torch.__version__, 'device': torch.cuda.get_device_name(device),
                   'peak_allocated_bytes': torch.cuda.max_memory_allocated(device),
                   'sam_live_encoder': args.model == 'sam31',
                   'timing_role': 'Decoded GT-person ROI to CPU hard mask; input prepare/H2D, fresh parser, projection/composition/D2H. Excludes disk/model load/warmup/GT/scoring/YOLO. SAM encoder recomputed; no feature cache.'}
        (output/'METRICS.json').write_text(json.dumps(metrics, indent=2)+'\n')
        status('COMPLETE', predictions=len(items), measured_calls=len(records))
    except BaseException as error:
        import traceback
        (output/'TRACEBACK.txt').write_text(traceback.format_exc())
        status('FAILED', error_type=type(error).__name__, message=str(error))
        raise


if __name__ == '__main__':
    main()
