"""Train annotation helpers from a hash-bound crop dataset in a fresh run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import sys
import tempfile
import time
import importlib.metadata
import fcntl

import numpy as np
from PIL import Image
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T

REPO = Path(__file__).resolve().parents[1]
CLASSES = ['background', 'hair', 'face', 'upper', 'lower']
PROMPTS = ['hair', 'face', 'shirt, top, upper clothes',
           'pants, trousers, shorts, lower clothes']
# Native SOLIDER LIP labels exhaustively partitioned into the helper output.
LIP_GROUPS = [[0, 1, 3, 4, 6, 8, 10, 11, 14, 15, 16, 17, 18, 19],
              [2], [13], [5, 7], [9, 12]]


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
        temp = stream.name
    os.replace(temp, path)


def atomic_weights(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = stream.name
    torch.save(value, temp)
    with open(temp, 'rb') as stream:
        os.fsync(stream.fileno())
    os.replace(temp, path)


def sam_decoder_state(model):
    return {key: value.detach().cpu().clone() for key, value in model.state_dict().items()
            if not key.startswith('backbone.')}


def save_sam_training_state(path, helper, optimizer, schedule, binding_sha256,
                            epoch, record, best_state):
    numpy_state = np.random.get_state()
    atomic_weights(path, {
        'format_version': 1, 'binding_sha256': binding_sha256,
        'epoch_completed': epoch, 'epoch_record': record,
        'state_dict': sam_decoder_state(helper.model),
        'optimizer': optimizer.state_dict(), 'scheduler': schedule.state_dict(),
        'best_state': best_state,
        'python_rng': random.getstate(),
        'numpy_rng': (numpy_state[0], numpy_state[1].tolist(), *numpy_state[2:]),
        'torch_rng': torch.get_rng_state(),
        'cuda_rng': torch.cuda.get_rng_state_all() if helper.device.type == 'cuda' else [],
    })
    return {'epoch_completed': epoch, 'path': str(path), 'sha256': file_hash(path),
            'binding_sha256': binding_sha256,
            'resume_policy': 'Restore full state at the last completed epoch; repeat any uncommitted partial epoch'}


def restore_sam_training_state(path, helper, optimizer, schedule, binding_sha256):
    state = torch.load(path, map_location='cpu', weights_only=True)
    if state['format_version'] != 1 or state['binding_sha256'] != binding_sha256:
        raise ValueError('Training checkpoint binding mismatch')
    expected = set(sam_decoder_state(helper.model))
    if set(state['state_dict']) != expected or set(state['best_state']['state_dict']) != expected:
        raise ValueError('Training checkpoint decoder keys mismatch')
    loaded = helper.model.load_state_dict(state['state_dict'], strict=False)
    if loaded.unexpected_keys or any(not key.startswith('backbone.') for key in loaded.missing_keys):
        raise ValueError('Training checkpoint decoder readback failed')
    optimizer.load_state_dict(state['optimizer'])
    schedule.load_state_dict(state['scheduler'])
    random.setstate(state['python_rng'])
    numpy_state = state['numpy_rng']
    np.random.set_state((numpy_state[0], np.asarray(numpy_state[1], dtype=np.uint32),
                         *numpy_state[2:]))
    torch.set_rng_state(state['torch_rng'])
    if state['cuda_rng']:
        torch.cuda.set_rng_state_all(state['cuda_rng'])
    return state


def append_epoch_record(path, record):
    records = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    existing = [row for row in records if row['epoch'] == record['epoch']]
    if existing:
        if existing != [record]:
            raise ValueError('Conflicting committed epoch record')
        return
    if len(records) != record['epoch']-1:
        raise ValueError('Epoch history is incomplete or out of order')
    with path.open('a') as stream:
        stream.write(json.dumps(record, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def bind_parent_feature_cache(parent, binding):
    parent = Path(parent).resolve(strict=True)
    previous = json.loads((parent/'BINDING.json').read_text())
    for key in ['dataset', 'checkpoint_sha256', 'warmstart_sha256', 'model_source_sha256']:
        if previous[key] != binding[key]:
            raise ValueError(f'Parent feature cache binding mismatch: {key}')
    # This audited producer uses the same frozen-backbone RGB/1008 float-resize recipe.
    producer = parent.parent/'source_frozen/train_annotation_helper.py'
    approved = '8791132941ef7a8ba1be7e6c9fb9e4f1c18e85ea4091cef585b3c4736607926d'
    if previous['script_sha256'] != approved or file_hash(producer) != approved:
        raise ValueError('Unsupported parent feature-cache producer')
    return {'parent': str(parent), 'binding_sha256': file_hash(parent/'BINDING.json'),
            'producer_sha256': approved, 'mode': 'READ_ONLY',
            'compatibility': 'same backbone, source, warmstart, dataset and RGB float-resize recipe'}


def tree_hash(root):
    files = sorted(Path(root).rglob('*.py'))
    if not files:
        raise ValueError(f'Missing Python source tree: {root}')
    values = {str(p.relative_to(root)): file_hash(p) for p in files}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def source_file(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe dataset path')
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('Dataset path escapes its root')
    return path


def bind_data(dataset, membership):
    dataset = Path(dataset).resolve(strict=True)
    import csv
    with Path(membership).open(encoding='utf-8-sig') as stream:
        members = {r['candidate_id']: r for r in csv.DictReader(stream)}
    manifest_path = dataset/'MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    bindings, groups = {}, {}
    all_sample_ids = set()
    for split, expected in [('train', 'HELPER_TRAIN_INITIAL'), ('val', 'HELPER_VALIDATION_FIXED')]:
        sample_ids = set()
        groups[split] = set()
        if not manifest[split]:
            raise ValueError('Empty training or validation dataset')
        for item in manifest[split]:
            if item['sample_id'] in all_sample_ids:
                raise ValueError('Duplicate sample ID')
            sample_ids.add(item['sample_id'])
            all_sample_ids.add(item['sample_id'])
            member = members[item['candidate_id']]
            if member['helper_role'] != expected:
                raise ValueError('Wrong helper membership')
            groups[split].add(member['time_block_id'])
            for field in ['img_path', 'mask_path']:
                path = source_file(dataset, item[field])
                bindings[item[field]] = file_hash(path)
            with Image.open(source_file(dataset, item['mask_path'])) as image:
                mask_size = image.size
                values = set(np.unique(np.asarray(image)).tolist())
                if not values <= {0, 1, 2, 3, 4, 255}:
                    raise ValueError('Invalid target IDs')
            with Image.open(source_file(dataset, item['img_path'])) as image:
                if image.size != mask_size or image.size != (384, 576):
                    raise ValueError('Crop image/mask geometry mismatch')
    if groups['train'] & groups['val']:
        raise ValueError('Training/validation block leakage')
    return manifest, {'manifest_sha256': file_hash(manifest_path),
                      'membership_sha256': file_hash(membership), 'files': bindings}


class Crops(Dataset):
    def __init__(self, root, items, hashes, training=False, image_size=None):
        self.root, self.items, self.hashes = root, items, hashes
        self.training = training
        self.image_size = image_size
        self.jitter = T.ColorJitter(brightness=.2, contrast=.2, saturation=.2)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        item = self.items[index]
        for field in ['img_path', 'mask_path']:
            if file_hash(self.root/item[field]) != self.hashes[item[field]]:
                raise ValueError('Dataset changed after launch')
        with Image.open(self.root/item['img_path']) as image:
            image = image.convert('RGB')
        with Image.open(self.root/item['mask_path']) as mask:
            target = np.asarray(mask, dtype=np.int64).copy()
        if self.training:
            if random.random() < .5:
                image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                target = target[:, ::-1].copy()
            image = self.jitter(image)
        if self.image_size:
            image = image.resize(self.image_size, Image.Resampling.BILINEAR)
        return T.functional.to_tensor(image), torch.from_numpy(target), index


def semantic_loss(logits, target):
    valid = target != 255
    if not valid.any():
        return logits.sum()*0
    ce = F.cross_entropy(logits, target, ignore_index=255)
    probabilities = logits.softmax(1)*valid[:, None]
    dice = []
    for label in range(5):
        truth = (target == label).float()
        prediction = probabilities[:, label]
        intersection = (prediction*truth).sum((1, 2))*2
        denominator = prediction.square().sum((1, 2))+truth.square().sum((1, 2))
        dice.append(1-(intersection+1e-5)/(denominator+1e-5))
    return ce + torch.stack(dice).mean()


def prompt_loss(masks, scores, presence, target, valid):
    """Match the single target during training and supervise other queries as negatives."""
    if not valid.any():
        return (masks.sum()+scores.sum()+presence.sum())*0
    truth = target.float()[valid]
    selected = masks[:, valid]
    probabilities = selected.sigmoid()
    labels = torch.zeros_like(scores)
    has_target = bool(target[valid].any())
    matched_loss = masks.sum()*0
    unmatched = torch.ones(len(scores), dtype=torch.bool, device=scores.device)
    if has_target:
        dice = 1-(2*(probabilities*truth).sum(1)+1e-5)/(probabilities.square().sum(1)+truth.square().sum()+1e-5)
        best = int(dice.detach().argmin())
        labels[best] = 1
        unmatched[best] = False
        matched_loss = F.binary_cross_entropy_with_logits(selected[best], truth)+2*dice[best]
    weight = scores.new_tensor(float(len(scores)) if has_target else 1.)
    score_loss = F.binary_cross_entropy_with_logits(scores, labels, pos_weight=weight)
    presence_loss = F.binary_cross_entropy_with_logits(presence, torch.full_like(presence, float(has_target)))
    candidates = torch.where(unmatched)[0]
    negative_loss = masks.sum()*0
    if len(candidates):
        top = candidates[scores[candidates].detach().topk(min(4, len(candidates))).indices]
        negative_loss = F.softplus(selected[top]).mean()
    return matched_loss+score_loss+presence_loss+.1*negative_loss


def project_lip(logits):
    return torch.stack([torch.logsumexp(logits[:, ids], 1) for ids in LIP_GROUPS], 1)


def initialize_b5_classifier(model):
    """Initialize a five-target head without altering the cached pretrained model."""
    expected = {0: 'background', 2: 'hair', 4: 'upper-clothes', 5: 'skirt', 6: 'pants', 11: 'face'}
    if model.config.num_labels != 18 or model.config.depths != [3, 6, 40, 3]:
        raise ValueError('Selected B5 checkpoint has an unexpected architecture/head')
    if any(model.config.id2label[i].lower()!=name for i, name in expected.items()):
        raise ValueError('B5 native labels differ from the reviewed checkpoint')
    native = model.decode_head.classifier
    head = nn.Conv2d(native.in_channels, 5, kernel_size=1)
    with torch.no_grad():
        for target, source in enumerate([[0], [2], [11], [4], [5, 6]]):
            head.weight[target].copy_(native.weight[source].mean(0))
            head.bias[target].copy_(native.bias[source].mean(0))
    model.decode_head.classifier = head
    model.config.num_labels = 5
    model.config.id2label = dict(enumerate(CLASSES))
    model.config.label2id = {label: i for i, label in enumerate(CLASSES)}
    model.config.semantic_loss_ignore_index = 255


class DenseHelper:
    def __init__(self, args, device):
        self.kind, self.device = args.model, device
        if args.model in ['b4', 'b5']:
            from transformers import SegformerForSemanticSegmentation
            self.model = SegformerForSemanticSegmentation.from_pretrained(args.checkpoint, local_files_only=True)
            if args.model=='b5':
                initialize_b5_classifier(self.model)
            if self.model.config.num_labels != 5:
                raise ValueError('SegFormer helper requires a five-class checkpoint/head')
            if [self.model.config.id2label[i].lower() for i in range(5)] != CLASSES:
                raise ValueError('SegFormer class ordering differs from annotation targets')
            self.mean, self.std = [0.485, .456, .406], [.229, .224, .225]
        else:
            sys.path.insert(0, str(Path(args.source).resolve()))
            from networks import init_model
            self.model = init_model('swin_small', num_classes=20, pretrained=None)
            state = torch.load(args.checkpoint, map_location='cpu', weights_only=True)
            state = state.get('state_dict', state)
            state = {k.removeprefix('module.'): v for k, v in state.items()}
            self.model.load_state_dict(state, strict=True)
            self.input_space = self.model.input_space
            if self.input_space != 'RGB':
                raise ValueError('Selected Swin-Small source contradicts its reviewed RGB contract')
            self.mean, self.std = self.model.mean, self.model.std
            if self.mean != [.485, .456, .406] or self.std != [.229, .224, .225]:
                raise ValueError('Selected Swin-Small normalization differs from the reviewed source')
        self.model.to(device)

    def logits(self, image):
        if self.kind == 'b5' and image.shape[-2:] != (512, 512):
            raise ValueError('B5 images must pass the reviewed PIL512 preprocessing')
        if self.kind == 'solider':
            image = F.interpolate(image, size=(572, 384), mode='bilinear', align_corners=False)
        mean = image.new_tensor(self.mean)[None, :, None, None]
        std = image.new_tensor(self.std)[None, :, None, None]
        output = self.model((image-mean)/std)
        if self.kind in ['b4', 'b5']:
            logits = output.logits
        else:
            logits = project_lip(output[0][-1])
        return F.interpolate(logits, size=(576, 384), mode='bilinear', align_corners=False)

    def optimizer(self, args):
        backbone, head = [], []
        for name, parameter in self.model.named_parameters():
            is_backbone = name.startswith('segformer.') if self.kind in ['b4', 'b5'] else name.startswith(
                ('patch_embed.', 'stages.', 'norm', 'semantic_embed', 'absolute_pos_embed'))
            (backbone if is_backbone else head).append(parameter)
        return torch.optim.AdamW([{'params': backbone, 'lr': args.lr_backbone},
                                  {'params': head, 'lr': args.lr_head}], weight_decay=1e-4)


class PromptHelper:
    def __init__(self, args, device, cache, bindings):
        source = Path(args.source).resolve()
        sys.path.insert(0, str(source/'src'))
        sys.path.insert(0, str(source/'third_party/sam3'))
        from sam31_labeling import build_detector
        from sam3.model.data_misc import FindStage
        self.model, self.load_binding = build_detector(Path(args.checkpoint), device)
        self.model.backbone.requires_grad_(False)
        if args.warmstart:
            state = torch.load(args.warmstart, map_location='cpu', weights_only=True)['state_dict']
            expected = {k for k in self.model.state_dict() if not k.startswith('backbone.')}
            if set(state) != expected:
                raise ValueError('Incomplete decoder warmstart')
            result = self.model.load_state_dict(state, strict=False)
            if result.unexpected_keys or any(not k.startswith('backbone.') for k in result.missing_keys):
                raise ValueError('Invalid decoder warmstart')
        self.device, self.cache, self.bindings = device, cache, bindings
        cache.mkdir(exist_ok=args.resume_training)
        self.parent_cache = Path(args.feature_cache_parent)/'features' if args.feature_cache_parent else None
        self.shared_position = None
        self.stage = FindStage(img_ids=torch.tensor([0], device=device),
                               text_ids=torch.tensor([0], device=device),
                               input_boxes=None, input_boxes_mask=None, input_boxes_label=None,
                               input_points=None, input_points_mask=None)
        self.geometry = self.model._get_dummy_prompt()
        with torch.no_grad():
            self.text = [self.model.backbone.forward_text([prompt], device=device) for prompt in PROMPTS]

    def features(self, image, item):
        path = self.cache/(item['sample_id']+'.pt')
        position_path = self.cache/'SHARED_POSITION.pt'
        if self.parent_cache and (self.parent_cache/path.name).exists():
            path = self.parent_cache/path.name
            position_path = self.parent_cache/'SHARED_POSITION.pt'
        key = self.bindings['files'][item['img_path']]
        if not path.exists():
            guard(self.cache, self.device)
            self.model.backbone.eval()
            image = F.interpolate(image.to(self.device), size=(1008, 1008), mode='bilinear',
                                  align_corners=False, antialias=True)
            with torch.inference_mode():
                output = self.model.backbone.forward_image((image-.5)/.5)
                fpn = [value.cpu() for value in output['backbone_fpn']]
                position = [value.cpu() for value in output['vision_pos_enc']]
                if self.shared_position is None:
                    self.shared_position = position
                    atomic_weights(self.cache/'SHARED_POSITION.pt', position)
                elif any(not torch.equal(a, b) for a, b in zip(position, self.shared_position)):
                    raise ValueError('Positional encodings vary across identical input grids')
                vision = output['vision_features']
                vision = fpn[-1] if torch.equal(vision, output['backbone_fpn'][-1]) else vision.cpu()
                atomic_weights(path, {'image_sha256': key, 'vision_features': vision,
                                      'backbone_fpn': fpn,
                                      'vision_mask': output['vision_mask'].cpu() if output.get('vision_mask') is not None else None})
        data = torch.load(path, map_location='cpu', weights_only=True)
        if data.pop('image_sha256') != key:
            raise ValueError('Feature cache image identity mismatch')
        position = torch.load(position_path, map_location='cpu', weights_only=True)
        data['vision_pos_enc'] = [value.to(self.device) for value in position]
        data['vision_features'] = data['vision_features'].to(self.device)
        data['backbone_fpn'] = [value.to(self.device) for value in data['backbone_fpn']]
        if data['vision_mask'] is not None:
            data['vision_mask'] = data['vision_mask'].to(self.device)
        return data

    def forward(self, features, label):
        data = dict(features)
        data.update(self.text[label-1])
        output = self.model.forward_grounding(backbone_out=data, find_input=self.stage,
                                              geometric_prompt=self.geometry, find_target=None)
        masks = F.interpolate(output['pred_masks'].squeeze(0)[:, None], size=(576, 384),
                              mode='bilinear', align_corners=False)[:, 0]
        return masks, output['pred_logits'].reshape(-1), output['presence_logit_dec'].reshape(-1)

    def optimizer(self, args):
        parameters = [p for p in self.model.parameters() if p.requires_grad]
        return torch.optim.AdamW(parameters, lr=args.lr_head, weight_decay=1e-4)


def guard(output, device):
    import shutil
    if shutil.disk_usage(output).free < 50*1024**3:
        raise RuntimeError('Free disk guard below 50 GiB')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA device required by this training recipe')


def evaluate(helper, dataset, output=None):
    helper.model.eval()
    cm = np.zeros((5, 5), dtype=np.int64)
    for index in range(len(dataset)):
        image, target, _ = dataset[index]
        with torch.no_grad():
            if isinstance(helper, PromptHelper):
                features = helper.features(image[None], dataset.items[index])
                planes = []
                for label in range(1, 5):
                    masks, scores, presence = helper.forward(features, label)
                    # Helper policy consumes joint logits once. Native Sam3Processor
                    # applies a further presence factor and keeps multiple queries.
                    confidence = scores.sigmoid()
                    best = int(confidence.argmax())
                    probability = masks[best].sigmoid()
                    planes.append(torch.where((confidence[best]>.2) & (probability>.5),
                                               probability*confidence[best], 0.))
                planes = torch.stack(planes)
                prediction = planes.argmax(0)+1
                prediction[planes.max(0).values==0] = 0
            else:
                prediction = helper.logits(image[None].to(helper.device)).argmax(1)[0]
        pred = prediction.cpu().numpy().astype('uint8')
        truth = target.numpy()
        valid = truth != 255
        cm += np.bincount(truth[valid]*5+pred[valid], minlength=25).reshape(5, 5)
        if output:
            with tempfile.NamedTemporaryFile('wb', dir=output, delete=False) as stream:
                Image.fromarray(pred).save(stream, format='PNG')
                stream.flush()
                os.fsync(stream.fileno())
                temporary = Path(stream.name)
            temporary.replace(output/(dataset.items[index]['sample_id']+'.png'))
    return metrics_from_confusion(cm, len(dataset))


def metrics_from_confusion(cm, crop_count):
    iou, statistics = [], {}
    for label in range(5):
        tp = int(cm[label, label])
        support, predicted = int(cm[label].sum()), int(cm[:, label].sum())
        union = support+predicted-tp
        iou.append(float(cm[label, label]/union) if union else None)
        statistics[CLASSES[label]] = {'tp': tp, 'fp': predicted-tp, 'fn': support-tp,
                                      'gt_pixels': support, 'prediction_pixels': predicted,
                                      'union': union, 'precision': tp/predicted if predicted else None,
                                      'recall': tp/support if support else None,
                                      'f1_dice': 2*tp/(support+predicted) if support+predicted else None}
    foreground = [v for v in iou[1:] if v is not None]
    return {'per_class_iou': dict(zip(CLASSES, iou)),
            'miou4': sum(foreground)/len(foreground) if foreground else None,
            'per_class_statistics': statistics,
            'confusion_axes': 'rows=GT; columns=prediction; background,hair,face,upper,lower',
            'confusion': cm.tolist(), 'crop_count': crop_count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['b4', 'b5', 'solider', 'sam31'], required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--membership', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--warmstart')
    parser.add_argument('--source')
    parser.add_argument('--output', required=True)
    parser.add_argument('--weights-directory', required=True)
    parser.add_argument('--repository-root', default=str(REPO))
    parser.add_argument('--epochs', type=int, required=True)
    parser.add_argument('--batch-size', type=int, default=2)
    parser.add_argument('--lr-backbone', type=float, default=1e-5)
    parser.add_argument('--lr-head', type=float, default=1e-4)
    parser.add_argument('--seed', type=int, default=20261112)
    parser.add_argument('--amp', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--save-training-state', action='store_true')
    parser.add_argument('--resume-training', action='store_true')
    parser.add_argument('--feature-cache-parent', type=Path)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or min(args.lr_backbone, args.lr_head)<=0:
        parser.error('Invalid training budget')
    if args.model=='sam31' and args.amp:
        parser.error('The cached SAM3.1 recipe uses FP32')
    if args.model=='sam31' and args.batch_size != 1:
        parser.error('SAM3.1 cached decoder training uses batch size one')
    if (args.save_training_state or args.resume_training or args.feature_cache_parent) and args.model!='sam31':
        parser.error('Training-state resume and parent feature cache are supported for SAM3.1')
    if args.resume_training and (not args.save_training_state or args.preflight):
        parser.error('Resume requires --save-training-state and a real training invocation')
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    manifest, bindings = bind_data(args.dataset, args.membership)
    output = Path(args.output).resolve()
    if output.exists() and not args.resume_training:
        raise ValueError('Choose a fresh attempt directory')
    if output.is_relative_to(Path(args.repository_root).resolve()) or output.is_relative_to(Path(args.dataset).resolve()):
        raise ValueError('Training outputs must be outside source and repository')
    output.mkdir(parents=True, exist_ok=args.resume_training)
    weights_directory = Path(args.weights_directory).resolve()
    if weights_directory.exists() and not args.resume_training:
        raise ValueError('Choose a fresh weights directory')
    binding = {'arguments': vars(args), 'dataset': bindings,
               'script_sha256': file_hash(__file__),
               'checkpoint_sha256': file_hash(Path(args.checkpoint)/'model.safetensors') if args.model in ['b4', 'b5'] else file_hash(args.checkpoint),
               'warmstart_sha256': file_hash(args.warmstart) if args.warmstart else None,
               'model_source_sha256': tree_hash(args.source) if args.source else None,
               'torch_version': torch.__version__, 'python': sys.version,
               'packages': {name: importlib.metadata.version(name) for name in
                            (['torch', 'torchvision', 'numpy', 'Pillow']+
                             (['transformers'] if args.model in ['b4','b5'] else []))},
               'checkpoint_config_sha256': file_hash(Path(args.checkpoint)/'config.json') if args.model in ['b4', 'b5'] else None,
               'train_crops': len(manifest['train']), 'val_crops': len(manifest['val']),
               'selection_metric_role': 'helper_diagnostic; inspect_saved_drafts_for_correction_effort',
               'initial_metrics_role': 'B5 head-initialized diagnostic, separate from native zero-shot' if args.model=='b5' else 'recipe-specific starting checkpoint diagnostic',
               'created_at_utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
    if args.feature_cache_parent:
        binding['feature_cache_reuse'] = bind_parent_feature_cache(args.feature_cache_parent, binding)
    if args.resume_training:
        if json.loads((output/'STATUS.json').read_text())['state']=='COMPLETE':
            raise ValueError('This training run already completed')
        previous = json.loads((output/'BINDING.json').read_text())
        current = json.loads(json.dumps(binding, default=str))
        for value in [previous, current]:
            value.pop('created_at_utc', None)
            value['arguments'].pop('resume_training', None)
        if current != previous:
            raise ValueError('Resume changed source, data, environment or training configuration')
    else:
        # argparse's optional cache path is serialized explicitly, alongside the other paths.
        binding['arguments']['feature_cache_parent'] = str(args.feature_cache_parent) if args.feature_cache_parent else None
        atomic_json(output/'BINDING.json', binding)
    binding_sha256 = file_hash(output/'BINDING.json')
    if args.preflight:
        atomic_json(output/'STATUS.json', {'state': 'CPU_INPUT_PREFLIGHT_PASS', 'model_calls': 0})
        return
    weights_directory.mkdir(parents=True, exist_ok=args.resume_training)
    def stop_requested(signum, frame):
        raise InterruptedError(f'Training received signal {signum}')
    signal.signal(signal.SIGTERM, stop_requested)
    helper = None
    worker_lock = (output/'WORKER.lock').open('a')
    fcntl.flock(worker_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        device = torch.device('cuda:0')
        guard(output, device)
        torch.cuda.set_device(device)
        torch.cuda.reset_peak_memory_stats(device)
        atomic_json(output/'STATUS.json', {'state': 'LOADING', 'pid': os.getpid()})
        helper = (PromptHelper(args, device, output/'features', bindings) if args.model=='sam31'
                  else DenseHelper(args, device))
        contract = {'color_order': 'RGB', 'model': args.model,
                    'native_processor_equivalence_claim': False}
        if args.model == 'sam31':
            contract.update({'mean': [.5]*3, 'std': [.5]*3, 'input_hw': [1008, 1008],
                             'resize': 'float bilinear, align_corners=False, antialias=True',
                             'selection': 'one highest joint-score query per target; threshold0.2',
                             'native_differences': 'uint8 resize quantization; extra presence factor; query retention'})
        else:
            contract.update({'mean': helper.mean, 'std': helper.std,
                             'input_hw': [572, 384] if args.model=='solider' else ([512, 512] if args.model=='b5' else [576, 384]),
                             'output': 'grouped native logits' if args.model=='solider' else 'five-class logits'})
        atomic_json(output/'EFFECTIVE_INPUT_OUTPUT_CONTRACT.json', contract)
        root = Path(args.dataset).resolve()
        image_size = (512, 512) if args.model=='b5' else None
        train = Crops(root, manifest['train'], bindings['files'], training=args.model!='sam31', image_size=image_size)
        validation = Crops(root, manifest['val'], bindings['files'], image_size=image_size)
        optimizer = helper.optimizer(args)
        schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs)
        scaler = torch.amp.GradScaler('cuda', enabled=args.amp, init_scale=1024.)
        first_epoch = 1
        if args.resume_training:
            resumed = restore_sam_training_state(weights_directory/'LAST.pt', helper,
                                                   optimizer, schedule, binding_sha256)
            best_state = resumed['best_state']
            first_epoch = resumed['epoch_completed']+1
            if resumed['epoch_record']:
                append_epoch_record(output/'HISTORY.jsonl', resumed['epoch_record'])
            history_path = output/'HISTORY.jsonl'
            history = [json.loads(line) for line in history_path.read_text().splitlines()] if history_path.exists() else []
            if [row['epoch'] for row in history] != list(range(1, first_epoch)):
                raise ValueError('History does not match the recoverable checkpoint')
            atomic_weights(weights_directory/'BEST.pt', best_state)
        else:
            initial = evaluate(helper, validation)
            atomic_json(output/'INITIAL_METRICS.json', initial)
            state = {k: v.cpu() for k, v in helper.model.state_dict().items()
                     if args.model!='sam31' or not k.startswith('backbone.')}
            best_state = {'epoch': 0, 'model': args.model, 'state_dict': state, 'metrics': initial}
            atomic_weights(weights_directory/'BEST.pt', best_state)
            if args.save_training_state:
                recovery = save_sam_training_state(weights_directory/'LAST.pt', helper, optimizer,
                                                   schedule, binding_sha256, 0, None, best_state)
                atomic_json(output/'RECOVERY.json', recovery)
        best = best_state['metrics']['miou4'] if best_state['metrics']['miou4'] is not None else -1.
        with (output/'ATTEMPTS.jsonl').open('a') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'time_utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                                      'resume': args.resume_training, 'first_epoch': first_epoch,
                                      'binding_sha256': binding_sha256,
                                      'training_state_sha256': file_hash(weights_directory/'LAST.pt') if args.save_training_state else None})+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        for epoch in range(first_epoch, args.epochs+1):
            guard(output, device)
            # SAM multiplex training mode invokes its own target matcher and DAC.
            # This helper uses external prompt losses with gradients enabled.
            helper.model.train(args.model!='sam31')
            if args.model=='solider':
                # Keep pretrained running statistics for the small crop batches.
                for module in helper.model.modules():
                    if isinstance(module, nn.modules.batchnorm._BatchNorm):
                        module.eval()
            total, steps, skipped_updates = 0., 0, 0
            start = time.time()
            if args.model=='sam31':
                helper.model.backbone.eval()
                order = list(range(len(train)))
                random.shuffle(order)
                for index in order:
                    image, target, _ = train[index]
                    target = target.to(device)
                    features = helper.features(image[None], train.items[index])
                    optimizer.zero_grad(set_to_none=True)
                    for label in range(1, 5):
                        masks, scores, presence = helper.forward(features, label)
                        loss = prompt_loss(masks, scores, presence, target==label, target!=255)/4
                        if not torch.isfinite(loss):
                            raise ValueError('Nonfinite loss')
                        loss.backward()
                        total += float(loss.detach())
                    torch.nn.utils.clip_grad_norm_(helper.model.parameters(), 1., error_if_nonfinite=True)
                    optimizer.step()
                    steps += 1
                    if steps % 20 == 0:
                        atomic_json(output/'STATUS.json', {'state': 'TRAINING', 'pid': os.getpid(),
                                   'epoch': epoch, 'epochs': args.epochs, 'crops_completed': steps,
                                   'crops_expected': len(train)})
            else:
                loader = DataLoader(train, batch_size=args.batch_size, shuffle=True, num_workers=0, drop_last=False)
                for image, target, _ in loader:
                    optimizer.zero_grad(set_to_none=True)
                    with torch.autocast('cuda', dtype=torch.float16, enabled=args.amp):
                        logits = helper.logits(image.to(device))
                        loss = semantic_loss(logits.float(), target.to(device))
                    if not torch.isfinite(loss):
                        raise ValueError('Nonfinite loss')
                    scaler.scale(loss).backward()
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(helper.model.parameters(), 1., error_if_nonfinite=not args.amp)
                    previous_scale = scaler.get_scale()
                    scaler.step(optimizer)
                    scaler.update()
                    skipped_updates += int(scaler.get_scale() < previous_scale)
                    total += float(loss.detach())
                    steps += 1
                    if steps % 20 == 0:
                        atomic_json(output/'STATUS.json', {'state': 'TRAINING', 'pid': os.getpid(),
                                   'epoch': epoch, 'epochs': args.epochs, 'batches_completed': steps,
                                   'batches_expected': len(loader)})
            if steps == skipped_updates:
                raise ValueError('No optimizer updates completed in this epoch')
            schedule.step()
            metrics = evaluate(helper, validation)
            score = metrics['miou4']
            record = {'epoch': epoch, 'loss': total/max(1, steps), 'validation': metrics,
                      'optimizer_updates': steps-skipped_updates, 'amp_skipped_updates': skipped_updates,
                      'seconds': time.time()-start,
                      'peak_allocated_bytes': torch.cuda.max_memory_allocated(device)}
            if score is not None and score>best:
                best = score
                state = {k: v.cpu() for k, v in helper.model.state_dict().items()
                         if args.model!='sam31' or not k.startswith('backbone.')}
                best_state = {'epoch': epoch, 'model': args.model, 'state_dict': state, 'metrics': metrics}
                atomic_weights(weights_directory/'BEST.pt', best_state)
            if args.save_training_state:
                recovery = save_sam_training_state(weights_directory/'LAST.pt', helper, optimizer,
                                                   schedule, binding_sha256, epoch, record, best_state)
                atomic_json(output/'RECOVERY.json', recovery)
            append_epoch_record(output/'HISTORY.jsonl', record)
            atomic_json(output/'STATUS.json', {'state': 'RUNNING', 'pid': os.getpid(),
                                               'epoch_completed': epoch, 'epochs': args.epochs,
                                               'best_diagnostic_miou4': best})
            print(json.dumps(record, allow_nan=False), flush=True)
        best_state = torch.load(weights_directory/'BEST.pt', map_location='cpu', weights_only=True)
        loaded = helper.model.load_state_dict(best_state['state_dict'], strict=args.model!='sam31')
        if args.model=='sam31' and (loaded.unexpected_keys or any(not k.startswith('backbone.') for k in loaded.missing_keys)):
            raise ValueError('Saved decoder readback failed')
        if args.model in ['b4', 'b5']:
            helper.model.save_pretrained(weights_directory/'huggingface')
        predictions = output/'validation_predictions'
        predictions.mkdir(exist_ok=args.resume_training)
        final = evaluate(helper, validation, predictions)
        atomic_json(output/'METRICS.json', final)
        atomic_json(output/'STATUS.json', {'state': 'COMPLETE', 'pid': os.getpid(),
                                           'epochs': args.epochs, 'best_epoch': best_state['epoch'],
                                           'checkpoint': str(weights_directory/'BEST.pt'),
                                           'checkpoint_sha256': file_hash(weights_directory/'BEST.pt'),
                                           'predictions': len(validation), 'metrics': final})
    except BaseException as error:
        import traceback
        (output/'TRACEBACK.txt').write_text(traceback.format_exc())
        atomic_json(output/'STATUS.json', {'state': 'FAILED', 'pid': os.getpid(),
                                           'error_type': type(error).__name__, 'message': str(error)})
        raise
    finally:
        worker_lock.close()


if __name__ == '__main__':
    main()
