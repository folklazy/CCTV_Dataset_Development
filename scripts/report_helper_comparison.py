"""Summarize completed helper checkpoints and render fixed-sample comparisons."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    data = Path(config['dataset'])
    items = json.loads((data/'MANIFEST.json').read_text())['val']
    rows, sources = [], {}
    reference_support = None
    for entry in config['comparison_entries']:
        out = Path(entry['output'])
        status = json.loads((out/'STATUS.json').read_text()) if (out/'STATUS.json').exists() else {}
        complete = status.get('state')=='COMPLETE' and (out/'METRICS.json').exists()
        metrics = json.loads((out/'METRICS.json').read_text()) if complete else None
        if complete and metrics['crop_count']!=len(items):
            raise ValueError('Completed result has a different crop population')
        if complete:
            existing_binding=json.loads((out/'BINDING.json').read_text())
            if existing_binding['dataset']['manifest_sha256']!=hashlib.sha256((data/'MANIFEST.json').read_bytes()).hexdigest():
                raise ValueError('Completed result uses another dataset manifest')
            support=[sum(row) for row in metrics['confusion']]
            if reference_support is not None and support!=reference_support:
                raise ValueError('GT valid-domain support differs across configurations')
            reference_support=support
            sources[entry['key']]={'metrics_path':str(out/'METRICS.json'),
                'metrics_sha256':hashlib.sha256((out/'METRICS.json').read_bytes()).hexdigest(),
                'binding_sha256':hashlib.sha256((out/'BINDING.json').read_bytes()).hexdigest()}
            if entry['stage']=='ZERO_SHOT':
                binding=json.loads((out/'BINDING.json').read_text())
                if binding['protocol_sha256']!=config['zero_shot_protocol_sha256'] or binding['weights_role']!='PRETRAINED_NO_CCTV_FINETUNING':
                    raise ValueError('Zero-shot protocol mismatch')
        row={'configuration':entry['key'],'stage':entry['stage'],'state':status.get('state','NOT_ATTEMPTED'),
             'crop_count':metrics['crop_count'] if metrics else None,'best_epoch':status.get('best_epoch')}
        for label in ['hair','face','upper','lower']:
            row[label+'_iou']=metrics['per_class_iou'][label] if metrics else None
            for metric in ['precision','recall','f1_dice','gt_pixels','prediction_pixels','union']:
                row[label+'_'+metric]=metrics['per_class_statistics'][label][metric] if metrics else None
        row['miou4']=metrics['miou4'] if metrics else None
        rows.append(row)
    with (root/'COMPARISON.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    def table(stage):
        lines=['| Configuration | State | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % |',
               '| --- | --- | --- | --- | --- | --- | --- |']
        for row in rows:
            if row['stage']!=stage:continue
            values=[row['configuration'],row['state']]+[
                '—' if row[k] is None else f'{row[k]*100:.2f}' for k in ['hair_iou','face_iou','upper_iou','lower_iou','miou4']]
            lines.append('| '+' | '.join(values)+' |')
        return '\n'.join(lines)
    gallery=root/'gallery'
    if gallery.exists():
        raise ValueError('Gallery already exists; preserve it and use a new report directory')
    gallery.mkdir()
    colors={1:(255,200,0),2:(0,220,255),3:(255,50,80),4:(50,220,100)}
    font=ImageFont.load_default()
    gallery_inputs, gallery_outputs={},{}
    def overlay(raw,mask,valid):
        value=np.array(raw).astype(float)
        for label,color in colors.items():value[mask==label]=value[mask==label]*.4+np.array(color)*.6
        value[~valid]=128
        return Image.fromarray(value.astype(np.uint8))
    def tile(image,title):
        canvas=Image.new('RGB',(256,420),'#f5f8fa')
        ImageDraw.Draw(canvas).text((8,8),title,font=font,fill='#17354b')
        if image:canvas.paste(image.resize((256,384),Image.Resampling.LANCZOS),(0,36))
        else:ImageDraw.Draw(canvas).text((25,190),'No completed saved output',font=font,fill='#6c7b89')
        return canvas
    panels=[]
    for item in items[:3]:
        sample=item['sample_id'];raw=Image.open(data/item['img_path']).convert('RGB');gt=np.array(Image.open(data/item['mask_path']));valid=gt!=255
        for p in [data/item['img_path'],data/item['mask_path']]:gallery_inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        for stage in ['ZERO_SHOT','FINE_TUNED']:
            tiles=[tile(raw,'Original crop'),tile(overlay(raw,gt,valid),'GT / gray = VOID')]
            for entry,row in zip(config['comparison_entries'],rows):
                if entry['stage']!=stage:continue
                prediction=None
                p=Path(entry['output'])/entry['mask_folder']/(sample+'.png')
                if row['state']=='COMPLETE':
                    mask=np.array(Image.open(p))
                    if mask.shape!=gt.shape or not set(np.unique(mask))<={0,1,2,3,4}:
                        raise ValueError('Gallery prediction contract mismatch')
                    prediction=overlay(raw,mask,valid)
                    gallery_inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
                tiles.append(tile(prediction,entry['key']))
            canvas=Image.new('RGB',(256*len(tiles),450),'white')
            ImageDraw.Draw(canvas).text((8,7),f'{sample} / {stage} / Hair yellow; Face cyan; Upper red; Lower green',font=font,fill='#17354b')
            for idx,value in enumerate(tiles):canvas.paste(value,(256*idx,30))
            target=gallery/(sample+'_'+stage+'.png');canvas.save(target)
            gallery_outputs[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
            panels.append(f'<h2>{html.escape(sample)} / {stage}</h2><img src="{target.name}">')
    (gallery/'index.html').write_text('<!doctype html><html lang="th"><meta charset="utf-8"><title>Helper comparisons</title><style>body{font-family:Tahoma,Arial,sans-serif;margin:24px;background:#f5f8fa;color:#17354b}img{max-width:100%;height:auto}p{line-height:1.7}</style><h1>ภาพเปรียบเทียบ annotation helpers</h1><p>สามvalidationcropsแรกตามfixedmanifest สีเป็นlegendของคลาส พื้นที่สีเทาคือGT VOID เปรียบเทียบแต่ละconfigurationตามrecipeที่ระบุ ตัวอย่างไม่ได้เลือกจากคะแนน</p>'+''.join(panels))
    (gallery/'MANIFEST.json').write_text(json.dumps({'selection':'first3 fixed validation entries inherited from existing SAM examples','inputs_sha256':gallery_inputs,'outputs_sha256':gallery_outputs},indent=2))
    complete=all(row['state']=='COMPLETE' for row in rows)
    text='# ผลตัวช่วย annotation บน CCTV Seed300\n\n'
    text+=('สถานะ COMPLETE' if complete else 'สถานะ PARTIAL — ดูstateของแต่ละconfiguration')+'\n\n'
    text+='ใช้fixed validation77personcropsจาก56ภาพ แยกจากtrain313crops คะแนนเป็นpixelIoUบนGTvaliddomainร่วมกัน GT255ถูกข้าม predictiontargetบนGT0นับFP ค่าเฉลี่ย4partsคิดจากglobalconfusion ส่วนP/R/F1/support/unionอยู่COMPARISON.csv\n\n'
    text+='## Pretrained zero-shot ก่อนCCTVfine-tune\n\n'+table('ZERO_SHOT')+'\n\n'
    text+='ใช้nativeweights/head B4/B5/SOLIDERก่อนCCTVtraining เก็บnativeclassesก่อนfixedmapping Hair/Face/Upper/Lower Nativeอื่นเป็นbackground/OTHERโดยไม่เพิ่มmodelignore SAMใช้originaldetector+nativeprocessorและfixedprompts ไม่โหลดCCTVdecoder\n\n'
    text+='## หลังรอบ fine-tune\n\n'+table('FINE_TUNED')+'\n\n'
    text+='B5ใช้native18→helper5classifierinitializationแล้วฝึกSeedtrain313crops25epochs batch2 AMP native512RGB มีepoch0เป็นcandidate การเปลี่ยนheadเป็นinitializationไม่ใช่zero-shotผลnative18 Nativezero-shotและFTบางตัวใช้input/outputadapterต่างกัน จึงเป็นผลของconfigurationและน้ำหนักร่วมกัน ตารางแยกตามstageและไม่ใช้ผลต่างอ้างผลของFTอย่างเดียว\n\n'
    text+='SAMfine-tunedเดิมเป็นwarmrestartช่วงepochlabels6–15จากbestepoch3 ใช้optimizerใหม่ พร้อมcustomfloatresize/single-query/jointscore ส่วนzero-shotSAMใช้nativeprocessorพร้อมextra presence factorและหลายqueriesตามcontractเดิม Sourceoftruthของผลเก่ายังเป็นrunเดิม ไม่รวมsubsetที่failedเป็นชุดเต็ม\n\n'
    if complete:
        text+='## คะแนนสูงสุดรายtargetในแต่ละstage\n\n'
        text+='| Stage | Target/metric | Configuration | คะแนน % |\n| --- | --- | --- | --- |\n'
        for stage in ['ZERO_SHOT','FINE_TUNED']:
            candidates=[row for row in rows if row['stage']==stage]
            for metric in ['hair_iou','face_iou','upper_iou','lower_iou','miou4']:
                eligible=[row for row in candidates if row[metric] is not None]
                if eligible:
                    best=max(row[metric] for row in eligible)
                    winners=[row['configuration'] for row in eligible if row[metric]==best]
                    text+=f'| {stage} | {metric} | {", ".join(winners)} | {best*100:.2f} |\n'
                else:
                    text+=f'| {stage} | {metric} | — | — |\n'
        text+='\nใช้full-precisionเลือกค่าสูงสุดก่อนปัดเศษ ตารางนี้ชี้candidateสำหรับดูร่างก่อน และยังไม่วัดเวลาคนแก้หรือstatisticalsignificance\n\n'
    text+='[เปิดภาพเปรียบเทียบ fixed3crops](gallery/index.html)\n\n'
    text+='การเลือกตัวช่วยให้ดูmissing/excess/boundary/ownershipและภาระการแก้ร่างจริงร่วมกับIoU/P/R/F1 ยังไม่มีเวลาผู้ใช้แก้ที่วัดแล้ว การใช้GT-personcropsยังไม่วัดautomaticbboxgenerationทั้ง2200ภาพ Timingที่บันทึกเป็นadapterdiagnostics\n'
    (root/'REPORT_TH.md').write_text(text)
    (root/'RESULT_INDEX.json').write_text(json.dumps({'state':'COMPLETE' if complete else 'PARTIAL','rows':rows,'sources':sources,'gallery':'gallery/index.html','report':'REPORT_TH.md'},indent=2))


if __name__=='__main__':main()
