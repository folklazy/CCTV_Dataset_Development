"""Synthetic contract/geometry checks; no company data or actual annotations."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from annotation_contract import safe_output, synthetic_roundtrip, transform_point, validate_contract


class AnnotationContractTests(unittest.TestCase):
    def test_nonuniform_transform_inverse_and_invalid_scale(self):
        t = {"crop_xyxy": [11, 7, 80, 40], "scale_xy": [1.5, 2.25], "padding_left_top": [3, 8]}
        point = (39.5, 28.25)
        back = transform_point(transform_point(point, t), t, inverse=True)
        for actual, expected in zip(back, point):
            self.assertAlmostEqual(actual, expected)
        with self.assertRaises(ValueError):
            transform_point(point, {**t, "scale_xy": [0, 1]})

    def test_unsafe_output_or_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = {"work_root": str(root / "work"), "dataset_root": str(root / "source")}
            for p in [root / "source" / "new", root / "repo" / "new", root / "elsewhere"]:
                with self.assertRaises(ValueError):
                    safe_output(p, cfg, repository=root / "repo")

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Existing Pillow required for PNG fixture")
    def test_real_png_and_json_roundtrip_and_failure_detection(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "synthetic"
            report = synthetic_roundtrip(output)
            self.assertTrue(report["validity_unknown_ignore_preserved"])
            doc = json.loads((output / "export.json").read_text())
            broken = copy.deepcopy(doc)
            broken["regions"][0]["person_id"] = "lost-owner"
            with self.assertRaises(ValueError):
                validate_contract(broken)
            broken = copy.deepcopy(doc)
            broken["attributes"][0]["value"] = "absent"
            with self.assertRaises(ValueError):
                validate_contract(broken)
            with self.assertRaises(ValueError):
                validate_contract(doc, {"bad_mask": (12, 9)})
            with self.assertRaises(FileExistsError):
                synthetic_roundtrip(output)


if __name__ == "__main__":
    unittest.main()
