"""Synthetic tests for explicit, bounded visual authorization; no image data."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from workspace_paths import load_visual_scope, require_visual_ids, validate_config


class VisualScopeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.work, self.repo = [self.root / n for n in ("source", "work", "repo")]
        for p in (self.source, self.work, self.repo):
            p.mkdir()
        columns = ["filename", "site", "camera_name", "incident_timestamp", "curate_status"]
        with (self.source / "metadata.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerow(dict(zip(columns, ["synthetic.jpg", "demo", "cam", "synthetic time", "pending"])))
        for ext in ("json", "xlsx"):
            (self.source / ("metadata." + ext)).write_text("synthetic placeholder")
        self.manifest = {"input_refs": {"metadata_sha256": hashlib.sha256(
            (self.source / "metadata.csv").read_bytes()).hexdigest()}, "records": [{
                "filename": "synthetic.jpg", "exploration_id": "demo-1", "proposed_order": 1,
                "site": "demo", "camera_name": "cam", "incident_timestamp_raw": "synthetic time",
                "curation_status_raw_unchanged": "pending"}]}
        self.mp = self.work / "proposal.json"
        self.config = {"dataset_root": str(self.source), "work_root": str(self.work),
                       **{"metadata_" + e: str(self.source / ("metadata." + e)) for e in ("csv", "json", "xlsx")},
                       "source_read_only": True, "inspect_images": True, "run_models": False,
                       "annotation_enabled": False, "training_enabled": False, "benchmark_enabled": False,
                       "phase": "bounded_visual_exploration", "visual_scope": {
                           "manifest_path": str(self.mp), "approved_count": 1}}
        self.cp = self.root / "local.json"
        self.save()

    def save(self):
        self.mp.write_text(json.dumps(self.manifest))
        self.config["visual_scope"]["manifest_sha256"] = hashlib.sha256(self.mp.read_bytes()).hexdigest()
        self.cp.write_text(json.dumps(self.config))

    def load(self):
        return load_visual_scope(self.cp, repository=self.repo)

    def test_explicit_scope_loads_without_opening_images(self):
        before = (self.source / "metadata.csv").read_bytes()
        _, manifest = self.load()
        self.assertEqual(require_visual_ids(manifest, ["demo-1"])[0]["filename"], "synthetic.jpg")
        self.assertFalse((self.source / "synthetic.jpg").exists())
        self.assertEqual(before, (self.source / "metadata.csv").read_bytes())

    def test_wrong_capabilities_and_phase_rejected(self):
        for key, value in [("run_models", True), ("annotation_enabled", True),
                           ("training_enabled", True), ("benchmark_enabled", True),
                           ("source_read_only", False), ("phase", "workspace_setup_only")]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_config({**self.config, key: value}, repository=self.repo, purpose="bounded_visual")
        with self.assertRaises(ValueError):
            validate_config(self.config, repository=self.repo)
        with self.assertRaises(ValueError):
            validate_config(self.config, repository=self.repo, purpose="inference")
        missing = dict(self.config)
        del missing["annotation_enabled"]
        with self.assertRaises(ValueError):
            validate_config(missing, repository=self.repo, purpose="bounded_visual")

    def test_manifest_and_metadata_drift_rejected(self):
        self.mp.write_text(self.mp.read_text() + " ")
        with self.assertRaises(ValueError):
            self.load()
        self.save()
        with (self.source / "metadata.csv").open("a") as f:
            f.write("unexpected change\n")
        with self.assertRaises(ValueError):
            self.load()

    def test_scope_count_unsafe_name_and_join_drift_rejected(self):
        self.config["visual_scope"]["approved_count"] = 33
        self.save()
        with self.assertRaises(ValueError):
            self.load()
        self.config["visual_scope"]["approved_count"] = 1
        for key, value in [("filename", "../outside.jpg"),
                           ("exploration_id", "../unsafe-id"), ("site", "different")]:
            old = self.manifest["records"][0][key]
            self.manifest["records"][0][key] = value
            self.save()
            with self.assertRaises(ValueError):
                self.load()
            self.manifest["records"][0][key] = old

    def test_outside_and_repeated_requests_rejected(self):
        _, manifest = self.load()
        for requested in ([], ["outside"], ["demo-1", "demo-1"]):
            with self.assertRaises(ValueError):
                require_visual_ids(manifest, requested)

    def test_public_or_source_manifest_and_symlink_rejected(self):
        for parent in (self.repo, self.source):
            candidate = parent / "proposal.json"
            candidate.write_bytes(self.mp.read_bytes())
            self.config["visual_scope"]["manifest_path"] = str(candidate)
            self.cp.write_text(json.dumps(self.config))
            with self.assertRaises(ValueError):
                self.load()
        link = self.work / "linked.json"
        link.symlink_to(self.mp)
        self.config["visual_scope"]["manifest_path"] = str(link)
        self.cp.write_text(json.dumps(self.config))
        with self.assertRaises(ValueError):
            self.load()


if __name__ == "__main__":
    unittest.main()
