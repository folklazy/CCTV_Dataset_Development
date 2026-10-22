"""Resolve this repository and validate isolated, local-only data/work paths."""
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

REPOSITORY = Path(__file__).resolve().parents[1]


def overlaps(left, right):
    left, right = Path(left).resolve(), Path(right).resolve()
    return left == right or left in right.parents or right in left.parents


def validate_config(config, repository=REPOSITORY):
    result = dict(config)
    for key in ("dataset_root", "work_root", "metadata_csv", "metadata_json", "metadata_xlsx"):
        value = result.get(key)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError(f"{key} must be an absolute path in local config")
        result[key] = str(Path(value).resolve(strict=True))
    source, work = Path(result["dataset_root"]), Path(result["work_root"])
    if not source.is_dir() or not work.is_dir():
        raise ValueError("dataset_root and work_root must be existing directories")
    if overlaps(source, repository) or overlaps(work, repository) or overlaps(source, work):
        raise ValueError("Repository, source and work directories must be disjoint")
    for key in ("metadata_csv", "metadata_json", "metadata_xlsx"):
        path = Path(result[key])
        if path.parent != source or not path.is_file():
            raise ValueError(f"{key} must be a file directly under dataset_root")
    if len({result[k] for k in ("metadata_csv", "metadata_json", "metadata_xlsx")}) != 3:
        raise ValueError("Metadata formats must reference three distinct files")
    if (result.get("source_read_only") is not True or result.get("inspect_images") is not False
            or result.get("run_models") is not False):
        raise ValueError("Only read-only metadata/document audit is supported")
    return result


def load_local_config(path=None):
    path = Path(path) if path else REPOSITORY / "config/local.json"
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def create_run(config, kind):
    root = Path(config["work_root"]) / "runs"
    # Resolve again to reject a changed output-root symlink before writing.
    if overlaps(root, REPOSITORY) or overlaps(root, config["dataset_root"]):
        raise ValueError("Output root overlaps source or repository")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run = root / f"{kind}-{stamp}-{uuid4().hex[:8]}"
    run.mkdir(parents=True, exist_ok=False)
    return run
