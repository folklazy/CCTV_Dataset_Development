"""Requirement fixtures with independently known pixels and state transitions."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/assisted_coverage.py'
spec = importlib.util.spec_from_file_location('assisted', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AssistedCoverage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.images = self.root / 'package/images'
        self.images.mkdir(parents=True)
        self.evidence = self.root / 'evidence'
        self.evidence.mkdir()
        self.run = self.root / 'new_run'
        rows, ledger = [], []
        for i, val in enumerate((0,255)):
            path = self.images / f'{i}.png'
            Image.new('RGB', (13,7), (val,val,val)).save(path)
            rows.append({'candidate_id': f'C{i}', 'filename': path.name,
                         'byte_md5': __import__('hashlib').md5(path.read_bytes()).hexdigest(),
                         'site': 'synthetic', 'camera_name': 'fixture'})
            ledger.append({'candidate_id': f'C{i}', 'filename': path.name,
                           'relative_path': 'images/'+path.name, 'sha256': m.sha(path.read_bytes()),
                           'md5': rows[-1]['byte_md5'], 'width': 13, 'height': 7,
                           'verification': 'SYNTHETIC_KNOWN_PIXELS'})
        self.manifest = self.evidence / 'manifest.csv'
        with self.manifest.open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.ledger = self.evidence / 'ledger.json'
        self.ledger.write_text(json.dumps(ledger))
        self.binding = self.evidence / 'binding.json'
        self.binding.write_text(json.dumps({'image_root': str(self.images),
            'manifest_path': str(self.manifest), 'manifest_sha256': m.sha(self.manifest.read_bytes()),
            'file_ledger_path': str(self.ledger), 'file_ledger_sha256': m.sha(self.ledger.read_bytes())}))

    def init(self):
        return m.initialize(self.binding,self.run)

    def test_known_pixels_and_no_semantic_claim(self):
        self.init(); result = m.analyze(self.run)
        self.assertEqual(result['cpu_measured'],2)
        self.assertEqual(result['operator_coverage_complete'],0)
        self.assertEqual(result['annotation_accepted'],0)
        items = {x['id']:x for x in m.snapshot(self.run)}
        black = items['C0']['measurement']; white=items['C1']['measurement']
        self.assertEqual(black['luma_mean'],0); self.assertEqual(white['luma_mean'],255)
        self.assertEqual(black['dark_fraction'],1); self.assertEqual(white['bright_fraction'],1)
        self.assertEqual(black['edge_mean'],0); self.assertEqual(white['edge_mean'],0)
        self.assertEqual(black['analysis_size'],[13,7])
        self.assertTrue(all(x['review'] is None for x in items.values()))

    def test_resume_reuses_committed_rows_and_never_overwrites(self):
        self.init(); m.analyze(self.run,limit=1)
        with m.connect(self.run) as db:
            before=db.execute('SELECT content FROM measurements WHERE id="C0"').fetchone()[0]
        self.assertEqual(m.analyze(self.run)['cpu_measured'],2)
        with m.connect(self.run) as db:
            after=db.execute('SELECT content FROM measurements WHERE id="C0"').fetchone()[0]
        self.assertEqual(before,after)
        with self.assertRaises(ValueError): self.init()

    def test_source_change_records_failure_and_stops_no_retry(self):
        self.init()
        (self.images/'0.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'SHA256'): m.analyze(self.run)
        self.assertEqual(m.summary(self.run)['measurement_failures'],1)
        # Explicit subsequent analyze never retries the failed row.
        m.analyze(self.run)
        s=m.summary(self.run)
        self.assertEqual((s['cpu_measured'],s['measurement_failures']),(1,1))

    def test_changed_control_and_completed_source_are_blocked(self):
        self.init();m.analyze(self.run,limit=1)
        (self.images/'0.png').write_bytes(b'other')
        with self.assertRaisesRegex(ValueError,'stat changed'): m.analyze(self.run)
        self.manifest.write_text('changed')
        with self.assertRaisesRegex(ValueError,'Pinned control'):m.verify_config(self.run)

    def test_symlinks_and_traversal_rejected(self):
        self.init(); c=m.verify_config(self.run)
        with self.assertRaises(ValueError):m.source_path(c,{'relative_path':'images/../0.png'})
        (self.images/'link.png').symlink_to(self.images/'0.png')
        with self.assertRaises(ValueError):m.source_path(c,{'relative_path':'images/link.png'})

    def test_operator_review_requires_loaded_source_and_records_revisions(self):
        self.init()
        p={'id':'C0','actor':'fixture-reviewer','view_token':'loaded-fixture',
           'confirmed_image_loaded':True,
           'fields':{k:{'state':'uncertain','note':'Synthetic boundary intentionally not provided'} for k in m.AXES+m.TARGETS}}
        with self.assertRaisesRegex(ValueError,'Load source'):m.save_review(self.run,p)
        with m.connect(self.run) as db:
            actual_sha=m.sha((self.images/'0.png').read_bytes())
            db.execute('INSERT INTO views VALUES(?,?,?,?)',('loaded-fixture','C0',actual_sha,m.now()))
        m.save_review(self.run,p)
        self.assertEqual(m.summary(self.run)['operator_coverage_complete'],1)
        p['fields']['Face']={'state':'not_assessed','note':''}
        m.save_review(self.run,p)
        s=m.summary(self.run)
        self.assertEqual(s['operator_coverage_records'],1)
        self.assertEqual(s['operator_coverage_complete'],0)
        self.assertEqual(s['annotation_accepted'],0)
        with m.connect(self.run) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0],2)

    def test_malformed_partial_and_unsupported_fields_fail(self):
        self.init()
        for fields in ({}, {'Face':{'state':'observed','note':'face'}}):
            with self.assertRaises(ValueError):m.save_review(self.run,{'actor':'fixture','fields':fields})
        fields={k:{'state':'observed','note':''} for k in m.AXES+m.TARGETS}
        with self.assertRaisesRegex(ValueError,'concrete observation'):m.save_review(self.run,{'actor':'fixture','fields':fields})


if __name__ == '__main__':
    unittest.main()
