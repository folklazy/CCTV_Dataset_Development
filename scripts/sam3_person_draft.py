"""Local SAM3 driver; explicit bounded execution, no downloads, AMP or GT acceptance."""
import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback

import person_pseudolabel as core


def source_binding(root):
    root=Path(root).resolve(strict=True)
    source=root/'app/models/sam3'
    paths=sorted(source.rglob('*.py'))
    if not paths or not (source/'model_builder.py').is_file():
        raise ValueError('Expected local X-AnyLabeling SAM3 source checkout')
    vocab=source/'assets/bpe_simple_vocab_16e6.txt.gz'
    if not vocab.is_file():raise ValueError('Missing local vocabulary; will not download')
    files={str(p.relative_to(source)):core.file_hash(p) for p in paths+[vocab]}
    head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    return {'root':str(source),'git_head':head,'source_files_sha256':files,
            'source_tree_sha256':core.digest(core.packed(files).encode()),'vocab':str(vocab)}


def receipt(path,row):
    if not path:raise ValueError('Human-first image requires a saved human-first receipt before AI exposure')
    r=core.load(path)
    if (r.get('image_id')!=row['id'] or r.get('source_sha256')!=row['source']['sha256']
        or r.get('before_ai_draft') is not True or not r.get('reviewer') or not r.get('completed_at')):
        raise ValueError('Human-first receipt binding incomplete')
    root=Path(path).resolve().parent
    refs=r.get('artifacts',[])
    if not refs:raise ValueError('Human-first receipt needs actual annotation artifacts, not a checkbox')
    for a in refs:
        f=(root/a['path']).resolve()
        if not f.is_relative_to(root) or core.file_hash(f)!=a['sha256']:
            raise ValueError('Human-first artifact missing or changed')
    return {'path':str(Path(path).resolve()),'sha256':core.file_hash(path)}


def strict_checkpoint_load(torch,build,**kwargs):
    """The local builder prints missing keys with strict=False; make that fatal."""
    from unittest.mock import patch
    native=torch.nn.Module.load_state_dict;events=[]
    def audited(module,*args,**kw):
        result=native(module,*args,**kw)
        events.append({'missing':list(result.missing_keys),'unexpected':list(result.unexpected_keys)})
        return result
    with patch.object(torch.nn.Module,'load_state_dict',audited):model=build(**kwargs)
    if not events or any(e['missing'] or e['unexpected'] for e in events):
        raise ValueError('Incomplete/unexpected checkpoint keys; refusing partially initialized model: '+core.packed(events))
    return model,events


class Backend:
    def __init__(self,torch,processor,run,max_calls,device,min_free_gib):
        self.torch=torch;self.processor=processor;self.run=run;self.max_calls=max_calls
        self.device=device;self.min_free_gib=min_free_gib;self.calls=0

    def event(self,value):
        with (self.run/'CALLS.jsonl').open('a') as f:
            f.write(core.packed({'at':core.now(),**value})+'\n');f.flush();os.fsync(f.fileno())

    def call(self,kind,fn):
        if self.calls>=self.max_calls:raise ValueError('STOP: explicit call budget exhausted; no retry')
        if shutil.disk_usage(self.run).free < 50*1024**3:
            raise ValueError('STOP: 50 GiB disk guard')
        free,_=self.torch.cuda.mem_get_info(self.device)
        if free < self.min_free_gib*1024**3:raise ValueError('STOP: declared free-VRAM guard')
        self.calls+=1;self.event({'call':self.calls,'kind':kind,'state':'STARTED'})
        t=time.perf_counter()
        try:
            with self.torch.inference_mode(),self.torch.autocast('cuda',enabled=False):
                result=fn()
            self.torch.cuda.synchronize(self.device)
        except Exception as e:
            self.event({'call':self.calls,'kind':kind,'state':'FAILED','error_type':type(e).__name__})
            raise
        self.event({'call':self.calls,'kind':kind,'state':'COMPLETED',
                    'diagnostic_seconds':time.perf_counter()-t,
                    'peak_allocated_bytes':self.torch.cuda.max_memory_allocated(self.device),
                    'peak_reserved_bytes':self.torch.cuda.max_memory_reserved(self.device)})
        return result

    def encode(self,image):
        return self.call(f'encode_image:{image.width}x{image.height}',lambda:self.processor.set_image(image))

    def predict(self,state,prompt):
        def forward():
            self.processor.reset_all_prompts(state)
            out=self.processor.set_text_prompt(prompt,state)
            return self.convert(out)
        return self.call('prompt:'+prompt,forward)

    def convert(self,out):
        masks=out['masks'].detach().cpu()
        boxes=out['boxes'].detach().float().cpu()
        scores=out['scores'].detach().float().cpu()
        if masks.ndim!=4 or masks.shape[1]!=1 or masks.shape[0]!=scores.numel() or boxes.shape!=(scores.numel(),4):
            raise ValueError('Unexpected SAM3 output geometry')
        if not self.torch.isfinite(boxes).all() or not self.torch.isfinite(scores).all():
            raise ValueError('Nonfinite SAM3 output')
        from PIL import Image
        return [{'mask':Image.fromarray(m[0].numpy().astype('uint8')*255),
                 'box':b.tolist(),'score':float(s)} for m,b,s in zip(masks,boxes,scores)]

    def predict_box(self,state,box,size):
        def forward():
            self.processor.reset_all_prompts(state)
            a,b,c,d=box;w,h=size
            norm=[(a+c)/(2*w),(b+d)/(2*h),(c-a)/w,(d-b)/h]
            return self.convert(self.processor.add_geometric_prompt(norm,True,state))
        return self.call('human_positive_box',forward)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue',required=True);p.add_argument('--id',required=True)
    p.add_argument('--source-checkout',required=True);p.add_argument('--checkpoint',required=True)
    p.add_argument('--output',required=True);p.add_argument('--execute',action='store_true')
    p.add_argument('--human-first-receipt');p.add_argument('--device',default='cuda:0')
    p.add_argument('--person-boxes',help='Human-drawn boxes JSON, linked by source SHA; never YOLO predictions')
    p.add_argument('--max-calls',type=int,default=64)
    p.add_argument('--confidence',type=float,default=0.25)
    p.add_argument('--min-free-gib',type=float,default=0,
                   help='Operational reserve, not a prediction of peak demand; 0 disables this extra guard')
    args=p.parse_args()
    if not 0<args.confidence<1 or not 2<=args.max_calls<=256 or args.min_free_gib<0:
        raise ValueError('Invalid explicit budget/threshold')
    q=core.queue(args.queue)
    rows=[r for r in q['selected'] if r['id']==args.id]
    if len(rows)!=1:raise ValueError('ID must be in the frozen candidate queue')
    row=rows[0]
    image=core.image_read(q,row)
    manual_boxes=None
    if args.person_boxes:
        mb=core.load(args.person_boxes)
        if (mb.get('image_id')!=args.id or mb.get('source_sha256')!=row['source']['sha256']
            or mb.get('provenance')!='human_drawn_before_model_draft' or not mb.get('reviewer')):
            raise ValueError('Human-box source/provenance binding incomplete')
        manual_boxes=mb['boxes_xyxy_exclusive']
        if not isinstance(manual_boxes,list):raise ValueError('Boxes must be a list')
        for box in manual_boxes:core.context_crop(box,image.size,0)
    sb=source_binding(args.source_checkout)
    checkpoint=Path(args.checkpoint).resolve(strict=True)
    cb={'path':str(checkpoint),'bytes':checkpoint.stat().st_size,'sha256':core.file_hash(checkpoint)}
    import torch
    config={'version':core.VERSION,'created_at':core.now(),'mode':'PRECHECK_ONLY',
            'image_id':args.id,'image_source_sha256':row['source']['sha256'],
            'queue_sha256':core.file_hash(Path(args.queue)/'QUEUE.json'),
            'source':sb,'checkpoint':cb,'device':args.device,
            'precision':'FP32','amp':False,'tf32':False,'batch':1,'resolution':1008,
            'preprocess':'official Sam3Processor RGB square1008 normalize mean/std0.5',
            'person_prompt':'person','part_prompts':core.PROMPTS,'crop_context_fraction':0.15,
            'map_back':'official logits bilinear original crop then binary0.5 then crop-offset',
            'no_pixel_minimum_deletion':True,'max_calls':args.max_calls,'confidence':args.confidence,
            'min_free_gib':args.min_free_gib,'disk_guard_free_gib':50,
            'auto_retries':0,'resource_policy':'ANNOTATION_HELPER_NOT_BENCHMARK',
            'environment':{'python':platform.python_version(),'torch':torch.__version__,
                           'cuda':torch.version.cuda,'packages':{}},
            'execute_requested':args.execute}
    config['annotation_repo_head']=subprocess.check_output(['git','-C',str(core.REPO),'rev-parse','HEAD'],text=True).strip()
    config['driver_source_sha256']=core.file_hash(__file__)
    config['core_source_sha256']=core.file_hash(core.__file__)
    config['manual_box_binding']=({'path':str(Path(args.person_boxes).resolve()),
                                  'sha256':core.file_hash(args.person_boxes)} if args.person_boxes else None)
    for name in ('torchvision','numpy','Pillow','timm','einops'):
        config['environment']['packages'][name]=importlib.metadata.version(name)
    if torch.cuda.is_available():
        config['gpu']={'name':torch.cuda.get_device_name(args.device),
                       'free_bytes':torch.cuda.mem_get_info(args.device)[0]}
    sys.path.insert(0,str(Path(args.source_checkout).resolve()/'app/models'))
    from sam3.model_builder import build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor
    config['cpu_imports_passed']=True
    output=core.fresh_external(args.output,q['image_root']);output.mkdir(parents=True)
    core.write(output/'CONFIG.json',config)
    if not args.execute:
        core.write(output/'STATUS.json',{'state':'PRECHECK_PASS_NOT_GPU_VALIDATED',
                   'model_calls':0,'checkpoint_loading_validated':False,
                   'current_input_verified':True,'human_first_draft_exposure':False})
        print(core.packed({'state':'PRECHECK_PASS_NOT_GPU_VALIDATED','output':str(output)}));return
    # Serialize all drafts from this queue; any prior attempt for this ID needs reconciliation.
    with (Path(args.queue)/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        attempts=Path(args.queue)/'ATTEMPTS';attempts.mkdir(exist_ok=True)
        claim=attempts/(args.id+'.json')
        # open x is atomic. No deletion/reset/retry command is provided.
        human=receipt(args.human_first_receipt,row) if row['role']=='human_first' else None
        with claim.open('x') as f:
            f.write(core.packed({'at':core.now(),'output':str(output),'id':args.id}));f.flush();os.fsync(f.fileno())
        core.sync_dir(attempts)
        config['mode']='EXECUTION';config['human_first_receipt']=human
        config['driver_source_sha256']=core.file_hash(__file__)
        config['core_source_sha256']=core.file_hash(core.__file__)
        core.write(output/'CONFIG.json',config)
        core.write(output/'STATUS.json',{'state':'LOADING','model_calls':0})
        backend=None
        try:
            if not args.device.startswith('cuda') or not torch.cuda.is_available():
                raise ValueError('Explicit CUDA device unavailable; CPU fallback forbidden')
            if shutil.disk_usage(output).free<50*1024**3:raise ValueError('Disk guard')
            free,_=torch.cuda.mem_get_info(args.device)
            if free<args.min_free_gib*1024**3:raise ValueError('Declared VRAM guard')
            torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
            torch.cuda.reset_peak_memory_stats(args.device)
            # Direct builder avoids the server adapter global BF16/fallback and contour conversion.
            model,load_events=strict_checkpoint_load(torch,build_sam3_image_model,
                                         checkpoint_path=str(checkpoint),load_from_HF=False,
                                         bpe_path=sb['vocab'],device=args.device,eval_mode=True,
                                         image_size=1008,compile=False)
            model=model.float().eval()
            core.write(output/'CHECKPOINT_LOAD.json',{'state':'ALL_LOADED_KEYS_MATCH','events':load_events})
            if any(t.is_floating_point() and t.dtype!=torch.float32 for t in model.parameters()):
                raise ValueError('Effective weights are not FP32')
            processor=Sam3Processor(model,resolution=1008,device=args.device,
                                    confidence_threshold=args.confidence)
            backend=Backend(torch,processor,output,args.max_calls,args.device,args.min_free_gib)
            core.write(output/'STATUS.json',{'state':'RUNNING_DRAFT','model_calls':0})
            core.run_frame(image,backend,output/'packet.partial',manual_boxes)
            verification=core.verify_packet(output/'packet.partial')
            core.write(output/'packet.partial'/'READBACK.json',verification)
            manifest={str(f.relative_to(output/'packet.partial')):core.file_hash(f)
                      for f in sorted((output/'packet.partial').rglob('*')) if f.is_file()}
            core.write(output/'packet.partial'/'FILES.json',manifest)
            core.commit_directory(output/'packet.partial',output/'packet')
            core.preview(output/'packet',output/'PREVIEW.png')
            core.write(output/'STATUS.json',{'state':'DRAFT_COMPLETE_REQUIRES_HUMAN_REVIEW',
                       'completed_at':core.now(),'model_calls':backend.calls,
                       'checkpoint_loading_validated':True,'accepted_gt':False,
                       'preview':'PREVIEW.png','packet':'packet'})
        except Exception as e:
            (output/'TRACEBACK.txt').write_text(traceback.format_exc())
            core.write(output/'STATUS.json',{'state':'STOPPED_FAILED_NO_RETRY','at':core.now(),
                       'error_type':type(e).__name__,'message':str(e),
                       'model_calls':backend.calls if backend else 0,'accepted_gt':False,
                       'partial_artifacts_preserved':True})
            raise
    print(core.packed({'state':'DRAFT_COMPLETE_REQUIRES_HUMAN_REVIEW','output':str(output)}))


if __name__=='__main__':main()
