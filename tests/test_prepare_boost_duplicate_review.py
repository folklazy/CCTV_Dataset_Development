"""Protect overlapping people and disconnected visible parts during duplicate review."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
SPEC = importlib.util.spec_from_file_location('review', ROOT/'scripts/prepare_boost_duplicate_review.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class DuplicateReviewRequirements(unittest.TestCase):
    def test_display_cleanup_preserves_ids_geometry_scores_and_manual_notes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            editor = root/'editor'
            path = editor/'batch_01/images/example.json'
            path.parent.mkdir(parents=True)
            source = {'checked': True, 'shapes': [
                {'label': 'bbox', 'group_id': 3, 'points': [[1,2],[4,6]], 'score': .9,
                 'description': '[CHECK_50PX] Person #3; SAM person score=0.900; bbox_long_side=51.0px'},
                {'label': 'upper', 'group_id': None, 'points': [[1,2],[4,2],[4,5]],
                 'description': 'operator note about visible sleeve'}]}
            path.write_text(json.dumps(source))
            original_bytes = path.read_bytes()
            result = review.shorten_editor_descriptions(editor, root/'backup')
            expected = json.loads(json.dumps(source))
            expected['shapes'][0]['description'] = ''
            self.assertEqual(review.load(path), expected)
            self.assertEqual(result['shape_descriptions_removed'], 1)
            self.assertEqual((root/'backup/originals/batch_01/images/example.json').read_bytes(), original_bytes)
            self.assertEqual(review.shorten_editor_descriptions(editor, root/'backup2')['files_updated'], 0)

    def fixture(self, box, score=.9, envelope=None):
        person = {'person_id': 1, 'bbox_xyxy': box, 'detector_score': score,
                  'raw_labels': 'raw.png', 'owned_labels': 'owned.png',
                  'outside_person_target_pixels': 5}
        labels = np.zeros((80, 100), dtype='uint8')
        labels[2:6, 2:6] = 1
        labels[6:10, 2:6] = 2
        labels[10:20, 2:6] = 3
        labels[21:30, 2:6] = 4
        return review.plan_view({'description': '', 'shapes': [], 'checked': False},
                                [person], [], {1: envelope or box}, {1: labels})

    def test_49_is_ignore_without_parts_and_50_is_person(self):
        annotation, audits, flags, _ = self.fixture([0, 0, 20, 49])
        self.assertEqual({s['label'] for s in annotation['shapes']}, {'ignore'})
        self.assertIsNone(annotation['shapes'][0]['group_id'])
        self.assertEqual(audits[0]['action'], 'IGNORE_CANDIDATE')
        self.assertIn('CHECK_50PX', flags)
        annotation, audits, flags, _ = self.fixture([0, 0, 20, 50])
        self.assertEqual({s['label'] for s in annotation['shapes']}, {'bbox', 'hair', 'face', 'upper', 'lower'})
        self.assertEqual(audits[0]['action'], 'PARTS_DRAFT')

    def test_lying_person_long_side_and_straddling_size(self):
        annotation, audits, _, _ = self.fixture([0, 0, 70, 25])
        self.assertEqual(audits[0]['action'], 'PARTS_DRAFT')
        annotation, audits, flags, _ = self.fixture([0, 0, 20, 48], envelope=[0, 0, 20, 60])
        self.assertEqual(audits[0]['action'], 'PARTS_DRAFT')
        self.assertIn('CHECK_50PX', flags)

    def test_low_score_hide_is_separate_from_ignore_and_clean_threshold(self):
        annotation, audits, _, _ = self.fixture([0, 0, 20, 70], score=.4999)
        self.assertEqual(annotation['shapes'], [])
        self.assertEqual(audits[0]['action'], 'LOW_SCORE_HIDDEN')
        annotation, audits, flags, _ = self.fixture([0, 0, 20, 70], score=.50)
        self.assertEqual(audits[0]['action'], 'PARTS_DRAFT')
        self.assertIn('LOW_PERSON_SCORE_FOR_CLEAN_QUEUE', flags)
        annotation, audits, flags, _ = self.fixture([0, 0, 20, 70], score=.85)
        self.assertNotIn('LOW_PERSON_SCORE_FOR_CLEAN_QUEUE', flags)

    def test_empty_proposals_require_full_image_review(self):
        annotation, audits, flags, _ = review.plan_view({'shapes': []}, [], [], {}, {})
        self.assertFalse(annotation['checked'])
        self.assertIn('NO_ELIGIBLE_PARTS_DRAFT_CHECK_FULL_IMAGE', flags)

    def test_ignore_draft_cannot_cover_retained_person(self):
        people = [{'person_id': identifier, 'bbox_xyxy': box, 'detector_score': .9,
                   'raw_labels': 'raw', 'owned_labels': 'owned', 'outside_person_target_pixels': 0}
                  for identifier, box in [(1, [0, 0, 30, 70]), (2, [1, 1, 10, 20])]]
        raw = {i: np.full((80, 100), 3, dtype='uint8') for i in [1, 2]}
        annotation, audits, flags, _ = review.plan_view({'shapes': []}, people, [],
                                                       {p['person_id']: p['bbox_xyxy'] for p in people}, raw)
        self.assertNotIn('ignore', {s['label'] for s in annotation['shapes']})
        self.assertIn('CHECK_SMALL_IGNORE_OVERLAP_ELIGIBLE', flags)
        self.assertEqual(audits[1]['action'], 'IGNORE_CANDIDATE')

    def test_equal_boxes_do_not_remove_disjoint_people(self):
        a = np.array([[True, False], [True, False]])
        b = ~a
        stats = review.compare_masks(a, b)
        self.assertEqual(stats['mask_iou'], 0)
        people = [{'person_id': 1, 'detector_score': .9}, {'person_id': 2, 'detector_score': .8}]
        kept, removed = review.select_people(people, [{'person_a': 1, 'person_b': 2, 'box_iou': 1., **stats}])
        self.assertEqual(kept, {1, 2})
        self.assertEqual(removed, {})

    def test_contained_occluded_extent_is_retained(self):
        a = np.ones((4, 4), dtype=bool)
        b = np.zeros((4, 4), dtype=bool)
        b[0] = True
        stats = review.compare_masks(a, b)
        self.assertEqual(stats['mask_iomin'], 1.)
        self.assertEqual(stats['mask_iou'], .25)
        people = [{'person_id': 1, 'detector_score': .9}, {'person_id': 2, 'detector_score': .8}]
        kept, removed = review.select_people(people, [{'person_a': 1, 'person_b': 2, 'box_iou': .5, **stats}])
        self.assertEqual(kept, {1, 2})

    def test_near_identical_proposals_prefer_score_and_keep_all_parts_of_selected_owner(self):
        people = [{'person_id': 1, 'detector_score': .4}, {'person_id': 2, 'detector_score': .8}]
        kept, removed = review.select_people(people, [{'person_a': 1, 'person_b': 2, 'box_iou': .8, 'mask_iou': .95}])
        self.assertEqual(kept, {2})
        self.assertEqual(removed, {1: 2})
        people = [{'person_id': i, 'detector_score': score, 'bbox_xyxy': [0, 0, 20, 70],
                   'raw_labels': 'raw', 'owned_labels': 'owned', 'outside_person_target_pixels': 0}
                  for i, score in [(1, .7), (2, .8)]]
        raw = np.zeros((80, 100), dtype='uint8')
        raw[10:15, 2:5] = 3
        raw[20:25, 2:5] = 3
        source = {'description': '', 'shapes': [], 'checked': False}
        result, _, _, _ = review.plan_view(source, people,
            [{'person_a': 1, 'person_b': 2, 'box_iou': .8, 'mask_iou': .95}],
            {1: [0, 0, 20, 70], 2: [0, 0, 20, 70]}, {1: raw, 2: raw})
        self.assertEqual([s['label'] for s in result['shapes']], ['bbox', 'upper', 'upper'])
        self.assertTrue(all(s['group_id'] == 2 for s in result['shapes']))
        self.assertEqual(source['shapes'], [])

    def test_declared_reviewed_batches_have_exact_membership(self):
        rows = [{'candidate_id': str(n), 'work_pack': f'role/batch_{n//50+1:02d}'} for n in range(550)]
        files = [{'candidate_id': str(n), 'sha256': 'example'} for n in range(100)]
        receipt = {'batches': ['batch_01', 'batch_02'], 'files': files}
        self.assertEqual(len(review.protected_membership(rows, receipt)), 100)
        with self.assertRaises(ValueError):
            review.protected_membership(rows, {**receipt, 'files': files[:-1]})

    def test_normal_export_preserves_reviewed_unchanged_checked_false_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            parent = root/'parent'
            (parent/'packets').mkdir(parents=True)
            rows, protected = [], []
            for n in range(550):
                batch = f'batch_{n//50+1:02d}'
                directory = parent/'xanylabeling'/batch/'images'
                directory.mkdir(parents=True, exist_ok=True)
                image = directory/f'C{n}.png'
                Image.new('RGB', (2, 3)).save(image)
                annotation = {'imagePath': image.name, 'shapes': [], 'checked': False}
                if n < 100:
                    annotation['shapes'] = [{'label': 'ignore', 'group_id': None, 'points': [[0,0],[1,2]]}]
                review.write(image.with_suffix('.json'), annotation)
                row = {'candidate_id': f'C{n}', 'work_pack': 'role/'+batch, 'export_image': image.name,
                       'image_sha256': review.file_hash(image), 'width': 2, 'height': 3}
                rows.append(row)
                packet = parent/'packets'/row['candidate_id']
                packet.mkdir()
                document = {'candidate_id': row['candidate_id'], 'input_sha256': row['image_sha256'],
                            'people': [], 'artifact_sha256': {'annotation.json': review.file_hash(image.with_suffix('.json'))}}
                review.write(packet/'PACKET.json', document)
                if n < 100:
                    protected.append({'candidate_id': row['candidate_id'], 'sha256': review.file_hash(image.with_suffix('.json'))})
            review.write(parent/'CONFIG.json', {'rows': rows})
            sha = review.file_hash(parent/'CONFIG.json')
            (parent/'CONFIG.sha256').write_text(sha)
            review.write(parent/'COMPLETION.json', {'completed': 550, 'persons': 0, 'protocol_sha256': sha})
            for packet in (parent/'packets').iterdir():
                document = review.load(packet/'PACKET.json')
                review.write(packet/'PACKET.json', {**document, 'protocol_sha256': sha})
            receipt = root/'receipt.json'
            review.write(receipt, {'batches': ['batch_01', 'batch_02'], 'files': protected})
            plan = root/'plan.md'
            plan.write_text('fixture')
            result = review.prepare(parent, root/'output', plan, receipt)
            self.assertEqual(result['counts']['00_reviewed'], 100)
            self.assertEqual(result['counts']['02_needs_edit'], 450)
            self.assertEqual(result['counts']['editor_ignore_shapes'], 100)
            copied = review.load(root/'output/00_reviewed/batch_01/images/C0.json')
            self.assertEqual(copied, review.load(parent/'xanylabeling/batch_01/images/C0.json'))
            self.assertFalse(copied['checked'])
            assembled = review.assemble_editor_batches(root/'output', root/'ready')
            self.assertEqual(assembled['queue_counts']['00_reviewed'], 100)
            self.assertEqual(assembled['queue_counts']['02_needs_edit'], 450)
            self.assertEqual(review.load(root/'ready/xanylabeling/batch_01/images/C0.json'), copied)
            self.assertEqual((root/'ready/xanylabeling/batch_01/images/C0.json').read_bytes(),
                             (parent/'xanylabeling/batch_01/images/C0.json').read_bytes())
            self.assertEqual(len(list((root/'ready/xanylabeling').glob('*/images/*.json'))), 550)

    def test_duplicate_chains_do_not_merge_dissimilar_endpoints(self):
        people = [{'person_id': n, 'detector_score': 1.-n*.1} for n in [1, 2, 3]]
        pairs = [{'person_a': 1, 'person_b': 2, 'box_iou': 1., 'mask_iou': .9},
                 {'person_a': 2, 'person_b': 3, 'box_iou': 1., 'mask_iou': .9},
                 {'person_a': 1, 'person_b': 3, 'box_iou': 1., 'mask_iou': .7}]
        kept, removed = review.select_people(people, pairs)
        self.assertEqual(kept, {1, 3})
        self.assertEqual(removed, {2: 1})


if __name__ == '__main__':
    unittest.main()
