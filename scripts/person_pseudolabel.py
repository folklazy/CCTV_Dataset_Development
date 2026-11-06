"""Bounded, lossless person/part draft generation. Never promotes model output to GT."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

from PIL import Image, ImageChops, ImageDraw

VERSION = 'person-parts-draft-1'
TARGETS = ('Hair', 'Face', 'Upper', 'Lower')
PROMPTS = {'Hair': 'hair', 'Face': 'face', 'Upper': 'upper body clothing',
           'Lower': 'lower body clothing', 'CrossZoneProbe': 'dress'}
REPO = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def write(path, value):
    """Atomic JSON; callers must choose fresh artifact paths."""
    path = Path(path)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     suffix='.tmp', delete=False) as f:
        f.write(packed(value) + '\n'); f.flush(); os.fsync(f.fileno())
        tmp = f.name
    os.replace(tmp, path)
    sync_dir(path.parent)


def sync_dir(path):
    fd=os.open(path,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def commit_directory(partial, final):
    """Flush staged files before publishing a whole packet by directory rename."""
    partial,final=Path(partial),Path(final)
    if final.exists():raise ValueError('Committed packet already exists')
    for file in partial.rglob('*'):
        if file.is_file():
            with file.open('rb') as stream:os.fsync(stream.fileno())
    for directory in sorted([p for p in partial.rglob('*') if p.is_dir()],reverse=True):
        sync_dir(directory)
    sync_dir(partial)
    os.rename(partial,final);sync_dir(final.parent)


def safe_source(root, row):
    root = Path(root).resolve(strict=True)
    rel = Path(row['relative_path'])
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] != root.name:
        raise ValueError('Unsafe source path')
    raw = root.parent / rel
    if any(p.is_symlink() for p in [raw, *raw.parents]):
        raise ValueError('Source symlinks are forbidden')
    path = raw.resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Source is outside image root')
    return path


def fresh_external(path, source_root=None):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError('Output symlinks are forbidden')
    path = path.resolve()
    roots = [REPO] + ([Path(source_root).resolve()] if source_root else [])
    if path.exists() or any(path.is_relative_to(p) or p.is_relative_to(path) for p in roots):
        raise ValueError('Choose a fresh directory outside source/repository')
    return path


def select_camera_round_robin(rows, count, seed):
    """Metadata diversity only; deliberately does not claim visual/size coverage."""
    groups = {}
    for row in rows:
        key = (row.get('site', ''), row.get('camera_name', ''))
        groups.setdefault(key, []).append(row)
    order = lambda value: digest((str(seed) + packed(value)).encode())
    queues = [sorted(groups[k], key=lambda r: order(r['candidate_id']))
              for k in sorted(groups, key=order)]
    selected = []
    while len(selected) < count:
        for q in queues:
            if q and len(selected) < count:
                selected.append(q.pop(0))
        if not any(queues) and len(selected) < count:
            raise ValueError('Not enough candidates')
    return selected


def prepare(binding, output, count=24, seed=20261106):
    b = load(binding)
    for key, hk in [('manifest_path', 'manifest_sha256'),
                    ('file_ledger_path', 'file_ledger_sha256')]:
        if file_hash(b[key]) != b[hk]:
            raise ValueError('Intake binding changed')
    with Path(b['manifest_path']).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    ledger = load(b['file_ledger_path'])
    by_id = {x['candidate_id']: x for x in ledger}
    ids = [r['candidate_id'] for r in rows]
    if len(ids) != len(set(ids)) or len(by_id) != len(ledger) or set(ids) != set(by_id):
        raise ValueError('Duplicate or mismatched population')
    if not 12 <= count <= len(rows):
        raise ValueError('Need at least 12 images to preserve calibration/human-first roles')
    chosen = select_camera_round_robin(rows, count, seed)
    records = []
    for i, row in enumerate(chosen):
        a = by_id[row['candidate_id']]
        # Uploaded pixel_sha256 and server canonical_pixel_sha256 use different
        # encodings. Reuse accepted intake join (filename + byte MD5 + ledger),
        # and verify actual byte SHA256 again at image read time.
        if row['filename'] != a['filename'] or row['byte_md5'] != a['md5'] or not a.get('verification'):
            raise ValueError('Metadata and intake ledger disagree')
        safe_source(b['image_root'], a)
        role = 'calibration' if i < 6 else 'human_first' if i < 12 else 'workflow'
        records.append({'id': row['candidate_id'], 'source': a, 'role': role,
                        'metadata': {k: row.get(k) for k in ('site', 'camera_name', 'incident_timestamp')},
                        'coverage_state': 'CANDIDATE_NOT_VISUALLY_CONFIRMED'})
    output = fresh_external(output, b['image_root']); output.mkdir(parents=True)
    config = {'version': VERSION, 'created_at': now(), 'state': 'PREPARED_NOT_ANNOTATED',
              'image_root': b['image_root'], 'population': len(rows), 'selected': records,
              'binding_path': str(Path(binding).resolve()), 'binding_sha256': file_hash(binding),
              'manifest_sha256': b['manifest_sha256'], 'ledger_sha256': b['file_ledger_sha256'],
              'selection': {'seed': seed, 'method': 'camera-round-robin-hash',
                            'not_random_population_sample': True, 'visual_confirmation_required': True},
              'person_min_pixels_for_deletion': None,
              'long_side_review_bins_px': [20, 50, 100],
              'size_bins_are_review_tags_not_exclusion': True,
              'targets': list(TARGETS), 'prompts': PROMPTS,
              'requires_human_review_every_image': True}
    write(output/'QUEUE.json', config)
    write(output/'QUEUE.sha256.json', {'sha256': file_hash(output/'QUEUE.json')})
    return config


def queue(path):
    path = Path(path)
    if file_hash(path/'QUEUE.json') != load(path/'QUEUE.sha256.json')['sha256']:
        raise ValueError('Queue fingerprint changed')
    q = load(path/'QUEUE.json')
    if q['version'] != VERSION or file_hash(q['binding_path']) != q['binding_sha256']:
        raise ValueError('Queue/input binding changed')
    b = load(q['binding_path'])
    if file_hash(b['manifest_path']) != q['manifest_sha256'] or file_hash(b['file_ledger_path']) != q['ledger_sha256']:
        raise ValueError('Source manifest/ledger changed')
    return q


def image_read(q, row):
    path = safe_source(q['image_root'], row['source'])
    raw = path.read_bytes()
    if digest(raw) != row['source']['sha256']:
        raise ValueError('Source bytes changed')
    import io
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if im.size != (row['source']['width'], row['source']['height']):
            raise ValueError('Source geometry changed')
        if im.getexif().get(274, 1) != 1:
            raise ValueError('Nontrivial EXIF orientation needs an explicit coordinate binding')
        return im.convert('RGB')


def binary(mask, size):
    if not isinstance(mask, Image.Image) or mask.mode not in ('L', '1') or mask.size != size:
        raise ValueError('Require original-grid, single-channel binary mask')
    values = {v for _, v in mask.getcolors(maxcolors=256)}
    if not values.issubset({0, 1}) and not values.issubset({0, 255}):
        raise ValueError('Reject probability/overlay/multiclass mask')
    return mask.convert('L').point(lambda x: 255 if x else 0)


def mask_info(mask):
    b = mask.getbbox(); area = mask.histogram()[255]
    long_side = max(b[2]-b[0], b[3]-b[1]) if b else None
    band = None if b is None else 'under20' if long_side < 20 else '20to49' if long_side < 50 else '50to99' if long_side < 100 else '100plus'
    return {'area_px': area, 'bbox_xyxy_exclusive': list(b) if b else None,
            'long_side_px': long_side, 'size_review_band': band,
            'empty_is_absent': False, 'distance_m': None,
            'bbox_mask_parsing_color_eligibility': 'HUMAN_REVIEW_REQUIRED'}


def map_back(mask, crop, size):
    x1, y1, x2, y2 = crop
    if not (0 <= x1 < x2 <= size[0] and 0 <= y1 < y2 <= size[1]):
        raise ValueError('Crop outside source')
    mask = binary(mask, (x2-x1, y2-y1))
    out = Image.new('L', size); out.paste(mask, (x1, y1)); return out


def context_crop(box, size, fraction=0.15):
    if len(box) != 4 or not all(math.isfinite(x) for x in box):
        raise ValueError('Invalid box')
    a,b,c,d = box; w,h = c-a,d-b
    if not (0 <= a < c <= size[0] and 0 <= b < d <= size[1]):
        raise ValueError('Box outside source')
    return [max(0,math.floor(a-w*fraction)), max(0,math.floor(b-h*fraction)),
            min(size[0],math.ceil(c+w*fraction)), min(size[1],math.ceil(d+h*fraction))]


def save_predictions(folder, image, results, crop=None):
    """All native candidate planes remain distinct, including holes and overlaps."""
    folder.mkdir()
    crop = crop or [0,0,*image.size]
    records = []
    for i, item in enumerate(results):
        score = float(item['score'])
        if not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError('Invalid score')
        mask = map_back(item['mask'], crop, image.size)
        # Validate model-regressed box but retain mask-derived geometry separately.
        box = item['box']
        if len(box) != 4 or not all(math.isfinite(x) for x in box) or box[0]>=box[2] or box[1]>=box[3]:
            raise ValueError('Invalid regressed box')
        path = folder/f'{i:04}.png'; mask.save(path)
        records.append({'mask': path.name, 'sha256': file_hash(path), 'score': score,
                        'model_bbox_xyxy_local': item['box'],
                        'model_bbox_xyxy_original': [item['box'][0]+crop[0],item['box'][1]+crop[1],
                                                     item['box'][2]+crop[0],item['box'][3]+crop[1]],
                        'geometry': mask_info(mask), 'crop_xyxy': crop,
                        'state': 'DRAFT_NOT_GT', 'target_presence': 'NOT_HUMAN_ASSESSED'})
    write(folder/'INDEX.json',records)
    return records


def rle(mask):
    """COCO uncompressed RLE, column-major; lossless through holes/components."""
    counts=[]; value=0; length=0; pixels=mask.load()
    for x in range(mask.width):
        for y in range(mask.height):
            v=int(pixels[x,y]>0)
            if v==value: length+=1
            else: counts.append(length);length=1;value=v
    counts.append(length)
    return {'size':[mask.height,mask.width], 'counts':counts}


def run_frame(image, backend, folder, manual_boxes=None):
    """No GT or benchmark predictions are accepted by this interface."""
    folder.mkdir()
    if manual_boxes is None:
        state=backend.encode(image)
        people=backend.predict(state, 'person')
    else:
        # Human boxes rescue persons omitted by text detection. Cropping happens
        # in ORIGINAL pixels; these annotation prompts are not benchmark inputs.
        people=[]
        for box in manual_boxes:
            crop=context_crop(box,image.size)
            roi=image.crop(crop); state=backend.encode(roi)
            local=[box[0]-crop[0],box[1]-crop[1],box[2]-crop[0],box[3]-crop[1]]
            for result in backend.predict_box(state,local,roi.size):
                item=dict(result)
                item['mask']=map_back(result['mask'],crop,image.size)
                b=result['box'];item['box']=[b[0]+crop[0],b[1]+crop[1],b[2]+crop[0],b[3]+crop[1]]
                people.append(item)
    persons=save_predictions(folder/'persons',image,people)
    output=[]
    for i,p in enumerate(persons):
        box=p['geometry']['bbox_xyxy_exclusive']
        if box is None:
            raise ValueError('Person proposal has empty mask; keep attempt, stop for inspection')
        crop=context_crop(box,image.size); roi=image.crop(crop)
        state=backend.encode(roi)
        person_mask=Image.open(folder/'persons'/p['mask']).convert('L')
        part_dir=folder/f'person_{i:04}';part_dir.mkdir()
        parts={}; unions={}
        for target,prompt in PROMPTS.items():
            raw=backend.predict(state,prompt)
            parts[target]=save_predictions(part_dir/target,image,raw,crop)
            union=Image.new('L',image.size)
            for item in parts[target]:
                with Image.open(part_dir/target/item['mask']) as im:
                    union=ImageChops.lighter(union,im.convert('L'))
            owned=ImageChops.darker(union,person_mask)
            union.save(part_dir/f'{target}.raw_union.png')
            owned.save(part_dir/f'{target}.owned_proposal.png')
            parts[target]={'candidates':parts[target], 'raw_union':f'{target}.raw_union.png',
                           'owned_proposal':f'{target}.owned_proposal.png',
                           'outside_person_px':union.histogram()[255]-owned.histogram()[255],
                           'raw_geometry':mask_info(union), 'owned_geometry':mask_info(owned),
                           'status':'DRAFT_REVIEW_CLASS_BOUNDARY_OWNER',
                           'empty_means':'NO_PROPOSAL_NOT_ABSENCE'}
            unions[target]=union
        conflict=Image.new('L',image.size)
        for a,ta in enumerate(TARGETS):
            for tb in TARGETS[a+1:]:
                conflict=ImageChops.lighter(conflict,ImageChops.darker(unions[ta],unions[tb]))
        conflict.save(part_dir/'target_conflicts.png')
        output.append({'person_proposal':i,'person_mask_ref':f'persons/{p["mask"]}',
                       'crop_xyxy':crop,'parts':parts,
                       'target_conflict_px':conflict.histogram()[255],
                       'ownership':'PERSON_MASK_INTERSECTION_IS_DRAFT_ONLY',
                       'cross_zone_probe_is_not_semantic_truth':True})
    # A convenient bbox file for the existing editor; canonical planes stay PNG.
    shapes=[]
    for i,p in enumerate(persons):
        x1,y1,x2,y2=p['geometry']['bbox_xyxy_exclusive']
        shapes.append({'label':'person','shape_type':'rectangle','group_id':i+1,
                       'points':[[x1,y1],[x2,y2]],'score':p['score'],
                       'flags':{'draft_not_gt':True},'description':'Visible mask envelope; review against source'})
    write(folder/'bbox_draft.xany.json',{'version':VERSION,'flags':{},'shapes':shapes,
          'imagePath':'source.png','imageData':None,'imageWidth':image.width,'imageHeight':image.height})
    image.save(folder/'source.png')
    write(folder/'PACKET.json',{'schema':VERSION,'state':'DRAFT_NOT_GT','people':output,
                              'person_proposals':len(people),'no_proposals_is_verified_negative':False,
                              'coordinates':'original_encoded_pixels_xyxy_exclusive',
                              'person_proposal_mode':'text-person' if manual_boxes is None else 'human-box-crops',
                              'manual_boxes':manual_boxes,
                              'human_acceptance':None})


def verify_packet(folder):
    folder=Path(folder);packet=load(folder/'PACKET.json')
    with Image.open(folder/'source.png') as source:
        size=source.size
    files=[]
    for path in sorted(folder.rglob('*.png')):
        if path.name=='source.png': continue
        with Image.open(path) as im: binary(im,size)
        files.append({'path':str(path.relative_to(folder)),'sha256':file_hash(path)})
    for path in folder.rglob('INDEX.json'):
        for row in load(path):
            if file_hash(path.parent/row['mask'])!=row['sha256']:
                raise ValueError('Saved native candidate changed')
    if (folder/'FILES.json').exists():
        for rel,expected in load(folder/'FILES.json').items():
            path=(folder/rel).resolve()
            if not path.is_relative_to(folder.resolve()) or file_hash(path)!=expected:
                raise ValueError('Committed packet fingerprint changed')
    if packet['state']!='DRAFT_NOT_GT' or packet['human_acceptance'] is not None:
        raise ValueError('Model must not grant human acceptance')
    return {'state':'PACKET_READBACK_PASS_NOT_GT','png_files':len(files),'files':files}


def preview(folder, output):
    folder=Path(folder);verify_packet(folder)
    with Image.open(folder/'source.png') as source:
        src=source.convert('RGB')
    p=load(folder/'PACKET.json')
    cols=[(src.copy(),'Original'),(src.copy(),'Person bbox/mask')]
    colors={'Hair':(240,170,30),'Face':(70,160,240),'Upper':(0,180,130),'Lower':(180,80,210)}
    people=load(folder/'persons/INDEX.json')
    for row in people:
        mask=Image.open(folder/'persons'/row['mask']).convert('L')
        cols[1][0].paste(Image.blend(src,Image.new('RGB',src.size,(0,190,160)),0.4),mask=mask)
        ImageDraw.Draw(cols[1][0]).rectangle(row['geometry']['bbox_xyxy_exclusive'],outline='yellow',width=2)
    for target,color in colors.items():
        plane=Image.new('L',src.size)
        for i,_ in enumerate(p['people']):
            plane=ImageChops.lighter(plane,Image.open(folder/f'person_{i:04}'/f'{target}.raw_union.png'))
        panel=src.copy();panel.paste(Image.blend(src,Image.new('RGB',src.size,color),0.45),mask=plane)
        cols.append((panel,target+' RAW DRAFT'))
    tile_w=min(640,src.width);tile_h=round(src.height*tile_w/src.width)
    sheet=Image.new('RGB',(tile_w*3,(tile_h+26)*2),'white');draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(cols):
        x=(i%3)*tile_w;y=(i//3)*(tile_h+26)
        sheet.paste(im.resize((tile_w,tile_h)),(x,y+26));draw.text((x+8,y+6),label,fill='black')
    output=Path(output)
    if output.exists():raise ValueError('Do not overwrite previous preview')
    sheet.save(output)


def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    a=subs.add_parser('prepare');a.add_argument('--binding',required=True);a.add_argument('--output',required=True)
    a.add_argument('--count',type=int,default=24);a.add_argument('--seed',type=int,default=20261106)
    a=subs.add_parser('check');a.add_argument('--packet',required=True)
    a=subs.add_parser('preview');a.add_argument('--packet',required=True);a.add_argument('--output',required=True)
    args=p.parse_args()
    if args.command=='prepare':
        q=prepare(args.binding,args.output,args.count,args.seed)
        print(packed({'state':q['state'],'population':q['population'],'selected':len(q['selected']),
                      'human_first':sum(r['role']=='human_first' for r in q['selected'])}))
    elif args.command=='check':print(packed(verify_packet(args.packet)))
    else:preview(args.packet,args.output)


if __name__=='__main__':main()
