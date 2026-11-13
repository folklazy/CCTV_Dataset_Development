"""Independent geometry, ownership and editor-export requirements for Boost drafts."""
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
SPEC = importlib.util.spec_from_file_location('boost', ROOT/'scripts/generate_boost_drafts.py')
boost = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boost)


class BoostDraftRequirements(unittest.TestCase):
    def test_training_round_context_letterbox_and_rgb(self):
        image = Image.new('RGB', (100, 80), (200, 10, 30))
        canvas, geometry = boost.image_crop(image, [20, 10, 60, 70])
        self.assertEqual(geometry['crop_xyxy'], [14, 1, 66, 79])
        self.assertEqual(geometry['resized_wh'], [384, 576])
        self.assertEqual(canvas.size, (384, 576))
        self.assertEqual(canvas.getpixel((50, 50)), (200, 10, 30))

    def test_asymmetric_unpad_and_original_offset(self):
        geometry = {'crop_xyxy': [2, 1, 6, 3], 'pad_xy': [0, 192],
                    'resized_wh': [384, 192]}
        plane = np.zeros((576, 384), dtype='uint8')
        plane[192:288, :192] = 1
        plane[192:288, 192:] = 2
        plane[288:384, :192] = 3
        plane[288:384, 192:] = 4
        actual = boost.original_labels(plane, geometry, (8, 5))
        expected = np.zeros((5, 8), dtype='uint8')
        expected[1:3, 2:6] = [[1, 1, 2, 2], [3, 3, 4, 4]]
        np.testing.assert_array_equal(actual, expected)

    def test_components_and_holes_remain_auditable(self):
        labels = np.zeros((12, 16), dtype='uint8')
        labels[1:10, 1:10] = 3
        labels[3:6, 3:6] = 0
        labels[10, 14] = 3
        shapes, stats = boost.polygon_view(labels, 7)
        self.assertEqual(stats['upper']['mask_pixels'], 73)
        self.assertEqual(stats['upper']['components'], 2)
        self.assertEqual(stats['upper']['holes'], 1)
        self.assertEqual(stats['upper']['polygon_added_pixels'], 9)
        self.assertEqual(stats['upper']['polygon_missing_pixels'], 0)
        self.assertEqual(len(shapes), 2)
        self.assertTrue(all(s['group_id'] == 7 and s['score'] is None for s in shapes))

    def test_no_people_export_is_review_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'packets').mkdir()
            source = root/'original.png'
            image = Image.new('RGB', (8, 5))
            image.save(source)
            row = {'candidate_id': 'CAND_TEST', 'width': '8', 'height': '5',
                   'export_image': 'original.png', 'work_pack': 'role/batch_01',
                   'image_sha256': boost.file_hash(source)}
            boost.write(root/'CONFIG.json', {'workset': str(root)})
            result = boost.export_frame(root, {'schema': 'test'}, 'proto', row, image, [], None, None)
            self.assertFalse(result['accepted_gt'])
            self.assertEqual(result['people'], [])
            self.assertEqual(result['no_proposals_means'], 'HUMAN_PERSON_INVENTORY_REQUIRED')
            annotation = boost.load(root/'xanylabeling/batch_01/images/original.json')
            self.assertEqual(annotation['shapes'], [])
            self.assertFalse(annotation['checked'])

    def test_actual_packet_editor_flow_keeps_raw_and_owned_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'packets').mkdir()
            source = root/'original.png'
            image = Image.new('RGB', (4, 6))
            image.save(source)
            row = {'candidate_id': 'CAND_TEST', 'width': '4', 'height': '6',
                   'export_image': 'original.png', 'work_pack': 'role/batch_01',
                   'image_sha256': boost.file_hash(source)}
            boost.write(root/'CONFIG.json', {'workset': str(root)})
            mask = np.zeros((6, 4), dtype=bool)
            mask[:, :2] = True
            def infer(*args):
                return np.full((576, 384), 3, dtype='uint8'), {'total_ms': 10.0}
            packet = boost.export_frame(root, {'schema': 'test'}, 'proto', row, image,
                                        [([0., 0., 4., 6.], mask, .8)], None, infer)
            person = packet['people'][0]
            self.assertEqual(person['outside_person_target_pixels'], 12)
            self.assertEqual(person['parts']['upper']['mask_pixels'], 12)
            final = root/'packets/CAND_TEST'
            raw = np.array(Image.open(final/person['raw_labels']))
            owned = np.array(Image.open(final/person['owned_labels']))
            np.testing.assert_array_equal(raw, np.full((6, 4), 3))
            np.testing.assert_array_equal(owned, np.array([[3, 3, 0, 0]]*6))
            self.assertFalse(boost.verify_packet(final, row, 'proto')['accepted_gt'])
            editor = root/'xanylabeling/batch_01/images/original.json'
            annotation = boost.load(editor)
            self.assertEqual({s['label'] for s in annotation['shapes']}, {'bbox', 'upper'})
            annotation['description'] = 'human edit'
            boost.write(editor, annotation)
            with self.assertRaisesRegex(ValueError, 'already edited'):
                boost.publish_editor(root, row, final)

    def test_invalid_label_is_contract_failure(self):
        with self.assertRaises(ValueError):
            boost.original_labels(np.full((576, 384), 255), {}, (4, 6))


if __name__ == '__main__':
    unittest.main()
