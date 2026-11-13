"""Membership isolation and lossless seed-export fixtures for annotation packs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
SPEC = importlib.util.spec_from_file_location('annotation_workset', ROOT/'scripts/prepare_annotation_workset.py')
workset = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workset)


class WorksetRequirements(unittest.TestCase):
    def membership(self):
        rows = []
        for role, (_, count, _) in workset.ROLES.items():
            for _ in range(count):
                rows.append({'candidate_id': f'CAND_{len(rows)+1:04d}',
                             'helper_role': role, 'time_block_id': role})
        return rows

    def test_existing_roles_and_population_are_preserved(self):
        rows = self.membership()
        workset.validate_membership(rows)
        rows[-1]['candidate_id'] = rows[0]['candidate_id']
        with self.assertRaisesRegex(ValueError, 'unique'):
            workset.validate_membership(rows)

    def test_validation_and_test_time_blocks_cannot_enter_training(self):
        for protected in ['HELPER_VALIDATION_FIXED', 'HELDOUT_TEST']:
            rows = self.membership()
            next(row for row in rows if row['helper_role'] == 'HELPER_TRAIN_BOOST')['time_block_id'] = protected
            with self.assertRaisesRegex(ValueError, 'protected time block'):
                workset.validate_membership(rows)

    def test_seed_export_preserves_shapes_owner_flags_and_acceptance_fields(self):
        annotation = {'imagePath': 'old.jpg', 'imageWidth': 2, 'imageHeight': 3,
                      'checked': False, 'imageData': None, 'flags': {'review_note': True},
                      'shapes': [{'label': 'Hair', 'points': [[0., 0.], [1., 0.], [1., 2.]],
                                  'group_id': 7, 'flags': {'component': 2}}]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, target = root/'source.json', root/'target.json'
            source.write_text(json.dumps(annotation))
            original = source.read_bytes()
            digest = hashlib.sha256(original).hexdigest()
            _, changed = workset.export_seed_annotation(source, digest, target, 'new.jpg', (2, 3))
            self.assertTrue(changed)
            expected = {**annotation, 'imagePath': 'new.jpg'}
            self.assertEqual(json.loads(target.read_text()), expected)
            self.assertEqual(source.read_bytes(), original)
            with self.assertRaisesRegex(ValueError, 'acceptance receipt'):
                workset.export_seed_annotation(source, 'wrong', root/'invalid.json', 'new.jpg', (2, 3))

    def test_seed_geometry_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'source.json'
            source.write_text(json.dumps({'imagePath': 'a.jpg', 'imageWidth': 2, 'imageHeight': 3}))
            with self.assertRaisesRegex(ValueError, 'geometry'):
                workset.export_seed_annotation(source, hashlib.sha256(source.read_bytes()).hexdigest(),
                                               Path(folder)/'out.json', 'a.jpg', (3, 2))


if __name__ == '__main__':
    unittest.main()
