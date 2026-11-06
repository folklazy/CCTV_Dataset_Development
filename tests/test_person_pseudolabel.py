"""Independent tiny fixtures: requirements, not model quality/GPU acceptance."""
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import person_pseudolabel as core
import sam3_person_draft as driver


class FixtureBackend:
    def encode(self,image):return image.size

    def predict(self,size,prompt):
        w,h=size;mask=Image.new('L',size)
        if prompt=='person':
            # 8x6 visible envelope, preserved hole and disconnected corner pixel.
            for y in range(1,7):
                for x in range(2,10):mask.putpixel((x,y),255)
            mask.putpixel((4,3),0);mask.putpixel((11,8),255)
            return [{'mask':mask,'box':[2,1,12,9],'score':0.8}]
        if prompt in ('hair','face'):
            # Deliberately same support: conflict must be kept, not assigned a winner.
            mask.putpixel((0,0),255);mask.putpixel((3,2),255)
            return [{'mask':mask,'box':[0,0,4,3],'score':0.6}]
        return []


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_full_packet_preserves_hole_component_raw_other_owner_and_conflict(self):
        path=self.root/'packet';core.run_frame(Image.new('RGB',(14,10)),FixtureBackend(),path)
        check=core.verify_packet(path)
        self.assertEqual(check['state'],'PACKET_READBACK_PASS_NOT_GT')
        person=Image.open(path/'persons/0000.png')
        self.assertEqual(person.getpixel((4,3)),0)
        self.assertEqual(person.getpixel((11,8)),255)
        self.assertEqual(person.histogram()[255],48)
        doc=core.load(path/'PACKET.json');p=doc['people'][0]
        self.assertIsNone(doc['human_acceptance']);self.assertFalse(doc['no_proposals_is_verified_negative'])
        self.assertEqual(set(p['parts']),set(core.TARGETS)|{'CrossZoneProbe'})
        self.assertGreater(p['target_conflict_px'],0)
        self.assertEqual(p['parts']['Upper']['raw_geometry']['area_px'],0)
        self.assertEqual(p['parts']['Upper']['empty_means'],'NO_PROPOSAL_NOT_ABSENCE')
        # Crop [0,0,14,10], pixel0 is outside person: raw retained, owned proposal removes it.
        self.assertEqual(Image.open(path/'person_0000/Hair.raw_union.png').getpixel((0,0)),255)
        self.assertEqual(Image.open(path/'person_0000/Hair.owned_proposal.png').getpixel((0,0)),0)
        core.preview(path,self.root/'preview.png')
        self.assertTrue((self.root/'preview.png').is_file())

    def test_asymmetric_crop_original_grid(self):
        mask=Image.new('L',(3,2));mask.putpixel((2,0),255)
        out=core.map_back(mask,[4,3,7,5],(11,8))
        self.assertEqual(out.getbbox(),(6,3,7,4))
        self.assertEqual(out.histogram()[255],1)
        with self.assertRaises(ValueError):core.map_back(mask,[4,3,8,5],(11,8))

    def test_human_box_crop_rescues_without_text_detection(self):
        class BoxBackend(FixtureBackend):
            def predict(self,size,prompt):
                if prompt=='person':raise AssertionError('Text detector must not gate human boxes')
                return []
            def predict_box(self,state,box,size):
                im=Image.new('L',size);im.putpixel((1,1),255)
                return [{'mask':im,'box':[0,0,2,2],'score':0.5}]
        path=self.root/'packet'
        core.run_frame(Image.new('RGB',(20,12)),BoxBackend(),path,[[8,4,12,8]])
        doc=core.load(path/'PACKET.json')
        self.assertEqual(doc['person_proposal_mode'],'human-box-crops')
        self.assertEqual(doc['person_proposals'],1)
        # Context expands [8,4,12,8] to [7,3,13,9]; local1,1 maps to8,4.
        with Image.open(path/'persons/0000.png') as im:self.assertEqual(im.getbbox(),(8,4,9,5))
        core.verify_packet(path)

    def test_prepare_actual_contract_uses_ledger_byte_join_and_six_blind_roles(self):
        root=self.root/'images';root.mkdir();rows=[];ledger=[]
        for i in range(12):
            file=root/f'{i}.png';Image.new('RGB',(3,2)).save(file)
            md5=__import__('hashlib').md5(file.read_bytes()).hexdigest()
            rows.append({'candidate_id':str(i),'filename':file.name,'byte_md5':md5,
                         'pixel_sha256':'upstream-encoding','site':'fixture','camera_name':str(i%3)})
            ledger.append({'candidate_id':str(i),'filename':file.name,'relative_path':f'images/{file.name}',
                           'md5':md5,'sha256':core.file_hash(file),'canonical_pixel_sha256':'server-encoding',
                           'verification':'fixture','width':3,'height':2})
        manifest=self.root/'manifest.csv'
        with manifest.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        led=self.root/'ledger.json';core.write(led,ledger)
        binding=self.root/'binding.json';core.write(binding,{'manifest_path':str(manifest),
            'manifest_sha256':core.file_hash(manifest),'file_ledger_path':str(led),
            'file_ledger_sha256':core.file_hash(led),'image_root':str(root)})
        out=self.root/'queue';q=core.prepare(binding,out,12)
        self.assertEqual(sum(r['role']=='human_first' for r in q['selected']),6)
        self.assertEqual(core.queue(out)['population'],12)
        Image.new('RGB',(3,2),(1,2,3)).save(root/q['selected'][0]['source']['filename'])
        with self.assertRaises(ValueError):core.image_read(q,q['selected'][0])

    def test_rle_column_order_and_holes_independent_expected_counts(self):
        mask=Image.new('L',(3,2));mask.putpixel((0,1),255);mask.putpixel((2,0),255)
        self.assertEqual(core.rle(mask),{'size':[2,3],'counts':[1,1,2,1,1]})

    def test_no_person_is_empty_draft_not_verified_negative(self):
        class Empty(FixtureBackend):
            def predict(self,*args):return []
        path=self.root/'packet';core.run_frame(Image.new('RGB',(14,10)),Empty(),path)
        self.assertEqual(core.load(path/'PACKET.json')['person_proposals'],0)
        self.assertFalse(core.load(path/'PACKET.json')['no_proposals_is_verified_negative'])
        core.verify_packet(path)

    def test_size_tags_do_not_delete_lying_person_or_invent_distance(self):
        mask=Image.new('L',(100,20))
        for x in range(2,82):mask.putpixel((x,4),255)
        m=core.mask_info(mask);self.assertEqual(m['size_review_band'],'50to99')
        self.assertEqual(m['long_side_px'],80);self.assertIsNone(m['distance_m'])
        self.assertEqual(m['area_px'],80)

    def test_invalid_palette_and_readback_tampering(self):
        with self.assertRaises(ValueError):core.binary(Image.new('L',(2,3),3),(2,3))
        with self.assertRaises(ValueError):core.binary(Image.new('RGB',(2,3)),(2,3))
        path=self.root/'packet';core.run_frame(Image.new('RGB',(14,10)),FixtureBackend(),path)
        Image.new('L',(14,10)).save(path/'persons/0000.png')
        with self.assertRaises(ValueError):core.verify_packet(path)

    def test_selection_disjoint_round_robin_deterministic(self):
        rows=[{'candidate_id':str(i),'site':'demo','camera_name':str(i%3)} for i in range(18)]
        a=core.select_camera_round_robin(rows,12,5);b=core.select_camera_round_robin(rows,12,5)
        self.assertEqual(a,b);self.assertEqual(len(set(x['candidate_id'] for x in a)),12)
        self.assertEqual(len(set(x['camera_name'] for x in a[:3])),3)

    def test_source_escape_and_fresh_output(self):
        root=self.root/'images';root.mkdir();(root/'source.png').write_bytes(b'x')
        with self.assertRaises(ValueError):core.safe_source(root,{'relative_path':'images/../outside'})
        with self.assertRaises(ValueError):core.fresh_external(root/'outputs',root)
        link=self.root/'alias';link.symlink_to(root)
        with self.assertRaises(ValueError):core.fresh_external(link/'out',root)

    def test_call_budget_before_second_forward_and_failure_history(self):
        class CUDA:
            def mem_get_info(self,*args):return (100*1024**3,100*1024**3)
            def synchronize(self,*args):pass
            def max_memory_allocated(self,*args):return 0
            def max_memory_reserved(self,*args):return 0
        from contextlib import nullcontext
        class Torch:
            cuda=CUDA()
            inference_mode=lambda self:nullcontext()
            autocast=lambda self,*args,**kwargs:nullcontext()
        from unittest.mock import patch
        b=driver.Backend(Torch(),None,self.root,1,'cuda:0',0)
        with patch.object(driver.shutil,'disk_usage',return_value=type('D',(),{'free':100*1024**3})()):
            with self.assertRaises(RuntimeError):b.call('fixture',lambda:(_ for _ in ()).throw(RuntimeError('synthetic failure')))
            with self.assertRaises(ValueError):b.call('must_not_execute',lambda:self.fail('budget ignored'))
        events=[json.loads(x) for x in (self.root/'CALLS.jsonl').read_text().splitlines()]
        self.assertEqual([e['state'] for e in events],['STARTED','FAILED'])

    def test_human_first_requires_real_bound_artifacts(self):
        row={'id':'DEMO','source':{'sha256':'example'}}
        with self.assertRaises(ValueError):driver.receipt(None,row)
        path=self.root/'receipt.json';core.write(path,{'image_id':'DEMO','source_sha256':'example',
            'before_ai_draft':True,'reviewer':'fixture','completed_at':'fixture','artifacts':[]})
        with self.assertRaises(ValueError):driver.receipt(path,row)

    def test_partial_checkpoint_is_fatal_even_when_upstream_only_warns(self):
        from types import SimpleNamespace
        class Module:
            def load_state_dict(self,*args,**kwargs):
                return SimpleNamespace(missing_keys=['mask_head.weight'],unexpected_keys=[])
        torch=SimpleNamespace(nn=SimpleNamespace(Module=Module))
        def build():
            m=Module();m.load_state_dict({});return m
        with self.assertRaises(ValueError):driver.strict_checkpoint_load(torch,build)
        # A builder that bypasses loading is also rejected.
        with self.assertRaises(ValueError):driver.strict_checkpoint_load(torch,lambda:Module())

    def test_publish_preserves_partial_history_and_never_overwrites_commit(self):
        partial=self.root/'packet.partial';final=self.root/'packet'
        core.run_frame(Image.new('RGB',(14,10)),FixtureBackend(),partial)
        before=(partial/'persons/0000.png').read_bytes()
        core.commit_directory(partial,final)
        self.assertEqual((final/'persons/0000.png').read_bytes(),before)
        second=self.root/'new.partial';second.mkdir();(second/'evidence').write_text('keep')
        with self.assertRaises(ValueError):core.commit_directory(second,final)
        self.assertEqual((second/'evidence').read_text(),'keep')


if __name__=='__main__':unittest.main()
