"""Synthetic whole-export scope and decode/deduplication workflow checks."""
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from dataset_review import check_files, context, make_sheets
from workspace_paths import load_dataset_review_scope


class WholeExportScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.work, self.repo = [self.root / x for x in ('source', 'work', 'repo')]
        for p in (self.source, self.work, self.repo): p.mkdir()
        self.run = self.work / 'run'; self.run.mkdir()
        self.rows = [{'filename': f'demo{i}.png', 'site': 'synthetic', 'camera_name': 'cam',
                      'category': 'record-only', 'incident_timestamp': 'synthetic time',
                      'curate_status': 'pending'} for i in range(40)]
        self.part = self.source / 'part.zip.001'; self.part.write_bytes(b'not opened by scope loader')
        self.config = {'dataset_root': str(self.source), 'work_root': str(self.work),
                       **{'metadata_'+e: str(self.source / ('metadata.'+e)) for e in ('csv','json','xlsx')},
                       'phase': 'dataset_inventory_and_visual_review', 'source_read_only': True,
                       'inspect_images': True, 'run_models': False, 'annotation_enabled': False,
                       'training_enabled': False, 'benchmark_enabled': False,
                       'dataset_review_scope': {'manifest_path': str(self.run/'scope.json')}}
        for e in ('json','xlsx'): (self.source/('metadata.'+e)).write_text('synthetic placeholder')
        self.cp = self.root / 'local.json'; self.save()

    def save(self):
        with (self.source/'metadata.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(self.rows[0])); w.writeheader(); w.writerows(self.rows)
        self.manifest = {'authorization':'user_authorized_current_dataset_read_only_review',
                         'metadata_sha256':hashlib.sha256((self.source/'metadata.csv').read_bytes()).hexdigest(),
                         'records':[{'record_id':f'R{i:05d}','metadata':r,'archive_member':r['filename']} for i,r in enumerate(self.rows,1)],
                         'archive_parts':[{'name':self.part.name,'size_mtime_ns':[self.part.stat().st_size,self.part.stat().st_mtime_ns]}]}
        self.pin()

    def pin(self):
        mp=self.run/'scope.json';mp.write_text(json.dumps(self.manifest))
        self.config['dataset_review_scope'].update(manifest_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),approved_count=len(self.rows))
        self.cp.write_text(json.dumps(self.config))

    def test_explicit_whole_export_over_32_without_pixels(self):
        _,m=load_dataset_review_scope(self.cp,repository=self.repo)
        self.assertEqual(len(m['records']),40)
        self.assertEqual(self.part.read_bytes(),b'not opened by scope loader')

    def test_scope_metadata_part_drift_and_other_capabilities_rejected(self):
        for key,value in [('run_models',True),('annotation_enabled',True),('training_enabled',True),
                          ('benchmark_enabled',True),('phase','bounded_visual_exploration')]:
            changed={**self.config,key:value};self.cp.write_text(json.dumps(changed))
            with self.assertRaises(ValueError): load_dataset_review_scope(self.cp,repository=self.repo)
        self.pin(); self.part.write_bytes(b'changed')
        with self.assertRaises(ValueError): load_dataset_review_scope(self.cp,repository=self.repo)
        self.save();self.manifest['records'][0]['metadata']['category']='wrong';self.pin()
        with self.assertRaises(ValueError): load_dataset_review_scope(self.cp,repository=self.repo)

    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Existing Pillow needed for invented PNGs')
    def test_byte_vs_pixel_duplicates_and_unreadable_are_distinct(self):
        from PIL import Image
        self.rows=self.rows[:4]
        a,b=io.BytesIO(),io.BytesIO(); image=Image.new('RGB',(16,12),(30,60,90))
        image.save(a,format='PNG',compress_level=0);image.save(b,format='PNG',compress_level=9)
        with zipfile.ZipFile(self.part,'w') as z:
            for row,data in zip(self.rows,[a.getvalue(),b.getvalue(),a.getvalue(),b'not an image']):
                z.writestr(row['filename'],data)
        self.save();before=self.part.read_bytes()
        cfg,manifest,run,db=context(self.cp,self.run)
        try:
            with self.assertRaises(ValueError):
                make_sheets(run,db,1,20261027)
            check_files(cfg,manifest,run,db,workers=2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM files WHERE decode_status='READABLE'").fetchone()[0],3)
            self.assertEqual(db.execute("SELECT COUNT(DISTINCT byte_sha),COUNT(DISTINCT pixel_sha) FROM files WHERE decode_status='READABLE'").fetchone(),(2,1))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM files WHERE decode_status='UNREADABLE'").fetchone()[0],1)
            make_sheets(run,db,1,20261027)
            make_sheets(run,db,1,20261027)  # Same frozen order can resume.
            with self.assertRaises(ValueError):
                make_sheets(run,db,1,20261028)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sheets WHERE viewed_at IS NOT NULL').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM observations').fetchone()[0],0)
            self.assertEqual(self.part.read_bytes(),before)
        finally: db.close()


if __name__=='__main__': unittest.main()
