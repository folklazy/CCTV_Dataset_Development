"""Evaluate pretrained annotation helpers on the fixed, hash-bound crop split."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time

import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms as T

from train_annotation_helper import atomic_json, bind_data, file_hash, guard, metrics_from_confusion, tree_hash


def project_native(native, mapping):
    native = np.asarray(native)
    if not np.issubdtype(native.dtype, np.integer) or native.min()<0 or native.max()>=len(mapping):
        raise ValueError('Unknown or noninteger native prediction IDs')
    return np.asarray(mapping, dtype=np.uint8)[native]


def native_fashn_input(image):
    resized = cv2.resize(np.asarray(image), (384, 576), interpolation=cv2.INTER_AREA)
    normalized = (resized.astype(np.float32)/255-np.array([.485,.456,.406], np.float32))/np.array([.229,.224,.225], np.float32)
    return torch.from_numpy(normalized.transpose(2, 0, 1).copy())[None]


def query_plane(probabilities, scores, threshold=.5):
    if len(scores)==0:
        return probabilities.new_zeros(probabilities.shape[-2:])
    return torch.where(probabilities>threshold, probabilities*scores[:, None, None], 0.).amax(0)


def atomic_image(path, array):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        Image.fromarray(array).save(stream, format='PNG')
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)


def atomic_npz(path, **arrays):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        np.savez_compressed(stream, **arrays)
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)


class NativeDense:
    def __init__(self, args, contract, dataset, items, device):
        self.kind, self.device, self.mapping = args.model, device, contract['target_map']
        self.processor = None
        if args.model in ['b4', 'b5']:
            from transformers import AutoImageProcessor, SegformerForSemanticSegmentation
            self.model = SegformerForSemanticSegmentation.from_pretrained(args.checkpoint, local_files_only=True)
            labels = [self.model.config.id2label[i] for i in range(self.model.config.num_labels)]
            if [s.lower() for s in labels] != [s.lower() for s in contract['native_labels']]:
                raise ValueError('Native checkpoint labels differ from the frozen mapping')
            expected = [3, 8, 27, 3] if args.model=='b4' else [3, 6, 40, 3]
            if self.model.config.depths != expected:
                raise ValueError('Wrong SegFormer architecture')
            if args.model=='b5':
                self.processor = AutoImageProcessor.from_pretrained(args.checkpoint, local_files_only=True, use_fast=False)
                if self.processor.size != {'height':512,'width':512} or self.processor.do_reduce_labels:
                    raise ValueError('B5 processor contract differs')
        else:
            sys.path.insert(0, str(Path(args.source).resolve()))
            from networks import init_model
            from datasets.simple_extractor_dataset import SimpleFolderDataset
            from utils.transforms import BGR2RGB_transform, transform_logits
            self.model = init_model('swin_small', num_classes=20, pretrained=None)
            value = torch.load(args.checkpoint, map_location='cpu', weights_only=True)
            state = value.get('state_dict', value)
            self.model.load_state_dict({k.removeprefix('module.'):v for k,v in state.items()}, strict=True)
            if self.model.input_space!='RGB' or self.model.mean != [.485,.456,.406] or self.model.std != [.229,.224,.225]:
                raise ValueError('Native Swin RGB metadata differs')
            folders = {(dataset/item['img_path']).parent for item in items}
            if len(folders)!=1:
                raise ValueError('Official folder reader requires one crop folder')
            self.reader = SimpleFolderDataset(root=str(folders.pop()), input_size=[572,384],
                transform=T.Compose([T.ToTensor(),BGR2RGB_transform(),T.Normalize(self.model.mean,self.model.std)]))
            self.reader.file_list = [Path(item['img_path']).name for item in items]
            self.transform_logits = transform_logits
        self.model.to(device).eval()

    def predict(self, image, index):
        geometry = {'original_hw': [image.height, image.width]}
        if self.kind=='solider':
            tensor, meta = self.reader[index]
            logits = self.model(tensor[None].to(self.device))[0][-1]
            if not torch.isfinite(logits).all():
                raise ValueError('Nonfinite native logits')
            up = F.interpolate(logits,size=(572,384),mode='bilinear',align_corners=True)[0].permute(1,2,0).cpu().numpy()
            restored = self.transform_logits(up,meta['center'],meta['scale'],meta['width'],meta['height'],input_size=[572,384])
            native = restored.argmax(2).astype(np.uint8)
            geometry.update({'input_hw':[572,384],'center':meta['center'].tolist(),'scale':meta['scale'].tolist(),
                             'resize':'source affine + inverse-affine logits; align_cornersTrue'})
        else:
            tensor = native_fashn_input(image) if self.kind=='b4' else self.processor(images=image,return_tensors='pt')['pixel_values']
            logits = self.model(tensor.to(self.device)).logits
            if not torch.isfinite(logits).all():
                raise ValueError('Nonfinite native logits')
            native = F.interpolate(logits,size=(image.height,image.width),mode='bilinear',align_corners=False).argmax(1)[0].cpu().numpy().astype(np.uint8)
            geometry.update({'input_hw':list(tensor.shape[-2:]),'resize':'source preprocessing; bilinear original-grid logits; align_cornersFalse'})
        return native, project_native(native,self.mapping), geometry, None


class NativePrompt:
    def __init__(self, args, contract, device):
        source = Path(args.source).resolve()
        sys.path.insert(0,str(source/'src'))
        sys.path.insert(0,str(source/'third_party/sam3'))
        from sam31_labeling import build_detector
        from sam3.model.sam3_image_processor import Sam3Processor
        self.model,self.loading = build_detector(Path(args.checkpoint),device)
        self.processor = Sam3Processor(self.model,resolution=1008,device=device,
                                        confidence_threshold=contract['confidence_threshold'])
        self.contract,self.device = contract,device

    def predict(self, image, index):
        state = self.processor.set_image(image)
        planes, candidates, scores, labels, boxes = [], [], [], [], []
        for label,prompt in enumerate(self.contract['prompts'],1):
            self.processor.reset_all_prompts(state)
            output = self.processor.set_text_prompt(prompt=prompt,state=state)
            probability = output['masks_logits'][:,0]
            confidence = output['scores'].reshape(-1)
            if not torch.isfinite(probability).all() or not torch.isfinite(confidence).all():
                raise ValueError('Nonfinite native SAM outputs')
            if ((probability<0)|(probability>1)).any():
                raise ValueError('Native processor mask probabilities out of range')
            planes.append(query_plane(probability,confidence,self.contract['mask_threshold']))
            candidates.append(output['masks'][:,0].cpu().numpy())
            scores.append(confidence.cpu().numpy())
            labels.append(np.full(len(confidence),label,dtype=np.uint8))
            boxes.append(output['boxes'].cpu().numpy())
        planes = torch.stack(planes)
        prediction = planes.argmax(0)+1
        prediction[planes.amax(0)==0] = 0
        common = prediction.cpu().numpy().astype(np.uint8)
        arrays = {'masks':np.concatenate(candidates).astype(bool),'scores':np.concatenate(scores),
                  'class_ids':np.concatenate(labels),'boxes_xyxy':np.concatenate(boxes),
                  'composed_class_strength':planes.cpu().numpy()}
        geometry = {'original_hw':[image.height,image.width],'input_hw':[1008,1008],
                    'resize':'native uint8 processor; original-grid probability map-back',
                    'output_contract':'prompt instance candidates + derived categorical0..4'}
        return None,common,geometry,arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=['b4','b5','solider','sam31'],required=True)
    for name in ['dataset','membership','checkpoint','protocol','output']:
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--source')
    parser.add_argument('--repository-root',default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--preflight',action='store_true')
    args = parser.parse_args()
    if args.model in ['solider','sam31'] and not args.source:
        parser.error('The selected model requires its bound source directory')
    protocol = json.loads(Path(args.protocol).read_text())
    contract = protocol['models'][args.model]
    if args.model!='sam31':
        if len(contract['target_map'])!=len(contract['native_labels']) or not set(contract['target_map'])<={0,1,2,3,4}:
            raise ValueError('Native mapping is incomplete')
    data = Path(args.dataset).resolve()
    manifest,binding = bind_data(data,args.membership)
    items = manifest['val']
    out = Path(args.output).resolve()
    if out.is_relative_to(data) or out.is_relative_to(Path(args.repository_root).resolve()):
        raise ValueError('Outputs must be outside the dataset and source repository')
    if out.exists():
        raise ValueError('Choose a fresh zero-shot output directory')
    out.mkdir(parents=True)
    weights = Path(args.checkpoint)/'model.safetensors' if args.model in ['b4','b5'] else Path(args.checkpoint)
    source_binding = {'protocol_sha256':file_hash(args.protocol),'script_sha256':file_hash(__file__),
        'shared_metrics_source_sha256':file_hash(Path(__file__).with_name('train_annotation_helper.py')),
        'checkpoint_sha256':file_hash(weights),'dataset':binding,'arguments':vars(args),
        'native_source_sha256':tree_hash(args.source) if args.source else None,
        'checkpoint_config_sha256':file_hash(Path(args.checkpoint)/'config.json') if args.model in ['b4','b5'] else None,
        'processor_config_sha256':file_hash(Path(args.checkpoint)/'preprocessor_config.json') if args.model=='b5' else None,
        'created_at_utc':datetime.now(timezone.utc).isoformat(),'weights_role':'PRETRAINED_NO_CCTV_FINETUNING',
        'precision':'FP32/noAMP/batch1/noextraTTA','contract':contract,
        'packages':{k:importlib.metadata.version(k) for k in
                    (['torch','torchvision','numpy','Pillow']+(['transformers'] if args.model in ['b4','b5'] else []))}}
    atomic_json(out/'BINDING.json',source_binding)
    if args.preflight:
        atomic_json(out/'STATUS.json',{'state':'CPU_INPUT_PREFLIGHT_PASS','model_calls':0})
        return
    def interrupted(signum,frame):
        raise InterruptedError(f'Zero-shot worker received signal {signum}')
    signal.signal(signal.SIGTERM,interrupted)
    sample_id = None
    try:
        device = torch.device('cuda:0')
        guard(out,device)
        torch.cuda.set_device(device)
        torch.cuda.reset_peak_memory_stats(device)
        atomic_json(out/'STATUS.json',{'state':'LOADING','pid':os.getpid(),'expected':len(items)})
        model = NativePrompt(args,contract,device) if args.model=='sam31' else NativeDense(args,contract,data,items,device)
        folders = {name:out/name for name in ['predictions','metadata','native','candidates']}
        for path in folders.values():path.mkdir()
        cm = np.zeros((5,5),dtype=np.int64)
        for index,item in enumerate(items):
            guard(out,device)
            sample_id = item['sample_id']
            if Path(sample_id).name!=sample_id:raise ValueError('Unsafe sample ID')
            start = time.perf_counter()
            with Image.open(data/item['img_path']) as image:image = image.convert('RGB')
            truth = np.asarray(Image.open(data/item['mask_path']),dtype=np.int64)
            read_end = time.perf_counter()
            with torch.inference_mode():native,common,geometry,arrays = model.predict(image,index)
            predicted_at = time.perf_counter()
            if common.shape!=truth.shape or not set(np.unique(common))<={0,1,2,3,4}:
                raise ValueError('Invalid projected prediction geometry or labels')
            paths = {'common':folders['predictions']/(sample_id+'.png')}
            atomic_image(paths['common'],common)
            if native is not None:
                paths['native']=folders['native']/(sample_id+'.png');atomic_image(paths['native'],native)
            if arrays is not None:
                paths['candidates']=folders['candidates']/(sample_id+'.npz');atomic_npz(paths['candidates'],**arrays)
            valid = truth!=protocol['gt_void']
            cm += np.bincount(truth[valid]*5+common[valid],minlength=25).reshape(5,5)
            packet = {'sample_id':sample_id,'input_sha256':binding['files'][item['img_path']],
                      'gt_sha256':binding['files'][item['mask_path']],'geometry':geometry,
                      'protocol_sha256':source_binding['protocol_sha256'],'checkpoint_sha256':source_binding['checkpoint_sha256'],
                      'files':{k:{'path':str(p.relative_to(out)),'sha256':file_hash(p)} for k,p in paths.items()},
                      'timing_seconds':{'read':read_end-start,'native_route':predicted_at-read_end,'save_score':time.perf_counter()-predicted_at},
                      'timing_role':'adapter diagnostic; native SOLIDER folder I/O lies inside native_route',
                      'candidate_contract':'SAM stores selected query hard masks/scores/boxes and composed strength; full per-query logits and rejected queries are absent',
                      'crop_box_original':item['crop_box_original'],'pad_meta':item['pad_meta']}
            atomic_json(folders['metadata']/(sample_id+'.json'),packet)
            with (out/'LEDGER.jsonl').open('a') as stream:
                stream.write(json.dumps({'sample_id':sample_id,'state':'COMMITTED','metadata_sha256':file_hash(folders['metadata']/(sample_id+'.json'))})+'\n');stream.flush();os.fsync(stream.fileno())
            atomic_json(out/'STATUS.json',{'state':'EVALUATING','pid':os.getpid(),'completed':index+1,'expected':len(items)})
            print(json.dumps({'completed':index+1,'expected':len(items),'sample_id':sample_id}),flush=True)
        expected = {item['sample_id']+'.png' for item in items}
        if {p.name for p in folders['predictions'].glob('*.png')}!=expected:
            raise ValueError('Exact validation membership mismatch')
        independent = np.zeros((5,5),dtype=np.int64)
        for item in items:
            truth=np.array(Image.open(data/item['mask_path']),dtype=np.int64)
            pred=np.array(Image.open(folders['predictions']/(item['sample_id']+'.png')),dtype=np.int64)
            valid=truth!=255;np.add.at(independent,(truth[valid],pred[valid]),1)
        if not np.array_equal(cm,independent):raise ValueError('Saved-mask scorer agreement failed')
        metrics=metrics_from_confusion(cm,len(items))
        atomic_json(out/'METRICS.json',metrics)
        atomic_json(out/'AUDIT.json',{'state':'PASS','exact_ids':len(items),'saved_mask_confusion':'EXACT_MATCH','failed':0,'invalid':0,'missing':0,
                                    'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),
                                    'peak_reserved_bytes':torch.cuda.max_memory_reserved(device)})
        atomic_json(out/'STATUS.json',{'state':'COMPLETE','pid':os.getpid(),'predictions':len(items),'metrics':metrics,'weights_role':'PRETRAINED_NO_CCTV_FINETUNING'})
    except BaseException as error:
        import traceback
        (out/'TRACEBACK.txt').write_text(traceback.format_exc())
        atomic_json(out/'STATUS.json',{'state':'FAILED','pid':os.getpid(),'sample_id':sample_id,'error_type':type(error).__name__,'message':str(error),'primary':None})
        raise


if __name__=='__main__':main()
