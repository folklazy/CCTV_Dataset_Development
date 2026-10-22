"""Exercise migrated commands on a tiny synthetic package from a different cwd."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / 'scripts'))
from workspace_paths import validate_config


class WorkspaceSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.work = self.root / 'work'
        self.source.mkdir()
        self.work.mkdir()
        self.rows = [dict(filename=f'fixture_{i}.jpg', site='synthetic_site',
                          camera_name=f'fixture_camera_{i}', category='synthetic_category',
                          incident_timestamp='2025-01-02 15:00:00.000 +0700',
                          curate_status=status, curate_note='', remark='synthetic fixture')
                     for i, status in enumerate(['pending', 'flagged'])]
        fields = list(self.rows[0])
        with (self.source / 'metadata.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(self.rows)
        (self.source / 'metadata.json').write_text(json.dumps(self.rows))
        sheet_rows = []
        for row_number, row in enumerate([fields] + [list(r.values()) for r in self.rows], 1):
            cells = ''.join(f'<c r="{chr(65+i)}{row_number}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
                            for i, value in enumerate(row))
            sheet_rows.append(f'<row r="{row_number}">{cells}</row>')
        xml = ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
               '<sheetData>' + ''.join(sheet_rows) + '</sheetData></worksheet>')
        with zipfile.ZipFile(self.source / 'metadata.xlsx', 'w') as archive:
            archive.writestr('xl/worksheets/sheet1.xml', xml)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            for row in self.rows:
                archive.writestr('images/' + row['filename'], b'synthetic non-image bytes')
        payload = buffer.getvalue()
        for i, start in enumerate(range(0, len(payload), 67), 1):
            (self.source / f'fixture_part{i:02d}.zip.{i:03d}').write_bytes(payload[start:start+67])
        self.config = {'dataset_root': str(self.source), 'work_root': str(self.work),
                       **{f'metadata_{ext}': str(self.source / f'metadata.{ext}') for ext in ['csv','json','xlsx']},
                       'source_read_only': True, 'inspect_images': False, 'run_models': False}
        self.config_path = self.root / 'local.json'
        self.config_path.write_text(json.dumps(self.config))

    def command(self, script, *extra):
        result = subprocess.run([sys.executable, '-B', str(REPOSITORY / 'scripts' / script),
                                 '--config', str(self.config_path), *extra], cwd=self.root,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_package_audit_is_external_readonly_and_cwd_independent(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        result = self.command('audit_package.py')
        run = Path(result.stdout.strip().splitlines()[-1])
        self.assertTrue(run.is_relative_to(self.work))
        audit = json.loads((run / 'metadata_audit.json').read_text())
        self.assertEqual(audit['records'], 2)
        self.assertEqual(audit['linkage_status_counts'], {'matched': 2})
        self.assertEqual(audit['raw_curation_status_counts'], {'pending': 1, 'flagged': 1})
        self.assertIsNone(audit['readable_images'])
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()})
        self.assertFalse(json.loads((run/'package_status.json').read_text())['image_pixels_decoded'])
        formats = json.loads((run/'format_comparison.json').read_text())
        self.assertTrue(all(row['same_record_multiset'] for row in formats.values()))

    def test_config_check_does_not_create_runs(self):
        result = self.command('audit_package.py', '--check-config')
        self.assertFalse(json.loads(result.stdout)['package_contents_read'])
        self.assertFalse((self.work / 'runs').exists())

    def test_document_command_uses_external_output(self):
        run = Path(self.command('prepare_handoff.py').stdout.strip())
        self.assertTrue(run.is_relative_to(self.work))
        inventory = json.loads((run/'document_inventory.json').read_text())
        self.assertTrue(all(not Path(r['path']).is_absolute() for r in inventory))
        self.assertEqual(json.loads((run/'preparation_status.json').read_text())['images_inspected_by_this_command'],0)

    def test_overlap_and_relative_paths_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_config({**self.config, 'work_root': str(self.source)})
        with self.assertRaises(ValueError):
            validate_config({**self.config, 'dataset_root': 'relative/source'})
        with self.assertRaises(ValueError):
            validate_config(self.config, repository=self.root)


if __name__ == '__main__':
    unittest.main()
