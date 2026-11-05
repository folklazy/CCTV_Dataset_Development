import importlib.util
from pathlib import Path
import tempfile
import unittest
from PIL import Image

spec = importlib.util.spec_from_file_location('scale',Path(__file__).resolve().parents[1]/'scripts/annotation_scale.py')
scale = importlib.util.module_from_spec(spec); spec.loader.exec_module(scale)


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'fixture.png'

    def test_disconnected_pixels_area_and_extent_are_distinct(self):
        im=Image.new('L',(10,8));im.putpixel((2,1),255);im.putpixel((7,5),255);im.save(self.path)
        before=self.path.read_bytes();r=scale.measure_scale(self.path,[10,8],'human_reviewed')
        self.assertEqual(r['visible_area_px'],2)
        self.assertEqual(r['visible_bbox_xyxy_exclusive'],[2,1,8,6])
        self.assertEqual(r['visible_area_fraction'],2/80)
        self.assertEqual(r['bbox_height_fraction'],5/8)
        self.assertIsNone(r['distance_m']);self.assertFalse(r['acceptance_granted_by_measurement'])
        self.assertEqual(self.path.read_bytes(),before)

    def test_hole_not_filled(self):
        im=Image.new('L',(5,5),1);im.putpixel((2,2),0);im.save(self.path)
        r=scale.measure_scale(self.path,[5,5],'draft');self.assertEqual(r['visible_area_px'],24)

    def test_empty_is_not_absent_or_zero_distance(self):
        Image.new('L',(4,7)).save(self.path);r=scale.measure_scale(self.path,[4,7],'draft')
        self.assertEqual(r['visible_area_px'],0);self.assertIsNone(r['visible_bbox_xyxy_exclusive'])
        self.assertIsNone(r['bbox_height_px']);self.assertEqual(r['extent_state'],'empty_support_not_absence')

    def test_geometry_palette_and_invalid_labels_rejected(self):
        Image.new('L',(4,7),2).save(self.path)
        with self.assertRaises(ValueError):scale.measure_scale(self.path,[4,7],'draft')
        Image.new('L',(4,7),255).save(self.path)
        with self.assertRaises(ValueError):scale.measure_scale(self.path,[7,4],'draft')
        Image.new('RGB',(4,7)).save(self.path)
        with self.assertRaises(ValueError):scale.measure_scale(self.path,[4,7],'draft')


if __name__ == '__main__':unittest.main()
