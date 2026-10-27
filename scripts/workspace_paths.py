"""Resolve this repository and validate isolated, local-only data/work paths."""
import json
import csv
import hashlib
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

REPOSITORY = Path(__file__).resolve().parents[1]


def overlaps(left, right):
    left, right = Path(left).resolve(), Path(right).resolve()
    return left == right or left in right.parents or right in left.parents


def validate_config(config, repository=REPOSITORY, purpose="metadata"):
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
    if result.get("source_read_only") is not True or result.get("run_models") is not False:
        raise ValueError("Source must be read-only and models disabled")
    if purpose == "metadata":
        if result.get("inspect_images") is not False:
            raise ValueError("Metadata commands require inspect_images=false")
    elif purpose in {"bounded_visual", "dataset_review"}:
        phase = "bounded_visual_exploration" if purpose == "bounded_visual" else "dataset_inventory_and_visual_review"
        if (result.get("inspect_images") is not True
                or result.get("phase") != phase
                or any(result.get(k) is not False for k in
                       ("annotation_enabled", "training_enabled", "benchmark_enabled"))):
            raise ValueError("Explicit authorized visual phase and disabled other capabilities required")
    else:
        raise ValueError("Unsupported capability")
    if any(result.get(k, False) is not False for k in
           ("annotation_enabled", "training_enabled", "benchmark_enabled")):
        raise ValueError("Annotation, training and benchmark are unsupported")
    return result


def load_local_config(path=None):
    path = Path(path) if path else REPOSITORY / "config/local.json"
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def load_visual_scope(path=None, repository=REPOSITORY):
    """Load an explicitly authorized, hash-pinned proposal; never open image data."""
    path = Path(path) if path else repository / "config/local.json"
    config = validate_config(json.loads(path.read_text(encoding="utf-8")),
                             repository=repository, purpose="bounded_visual")
    scope = config.get("visual_scope", {})
    raw_path = scope.get("manifest_path", "")
    if not raw_path or not Path(raw_path).is_absolute() or Path(raw_path).is_symlink():
        raise ValueError("Visual manifest must be a regular absolute private path")
    manifest_path = Path(raw_path).resolve(strict=True)
    if not manifest_path.is_file() or not manifest_path.is_relative_to(Path(config["work_root"])):
        raise ValueError("Visual manifest must be inside external work_root")
    data = manifest_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != scope.get("manifest_sha256"):
        raise ValueError("Visual manifest checksum differs from authorized proposal")
    manifest = json.loads(data)
    records = manifest.get("records", [])
    count = scope.get("approved_count")
    if type(count) is not int or not 1 <= count <= 32 or len(records) != count:
        raise ValueError("Visual proposal count must match explicit scope, maximum 32")
    names = [row["filename"] for row in records]
    ids = [row["exploration_id"] for row in records]
    if (len(set(names)) != count or len(set(ids)) != count
            or [row["proposed_order"] for row in records] != list(range(1, count + 1))
            or any(not isinstance(x, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", x) is None
                   for x in ids)
            or any(not n or "/" in n or "\\" in n or "\x00" in n or n in {".", ".."} for n in names)):
        raise ValueError("Visual proposal identities/order must be unique and safe")
    metadata_path = Path(config["metadata_csv"])
    before = metadata_path.stat()
    metadata = metadata_path.read_bytes()
    after = metadata_path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Metadata changed during scope validation")
    if hashlib.sha256(metadata).hexdigest() != manifest["input_refs"]["metadata_sha256"]:
        raise ValueError("Metadata snapshot differs from approved proposal")
    rows = list(csv.DictReader(io.StringIO(metadata.decode("utf-8-sig"))))
    by_name = {row["filename"]: row for row in rows}
    if len(by_name) != len(rows):
        raise ValueError("Ambiguous metadata filenames")
    checks = {"site": "site", "camera_name": "camera_name",
              "incident_timestamp_raw": "incident_timestamp",
              "curation_status_raw_unchanged": "curate_status"}
    for row in records:
        source = by_name.get(row["filename"])
        if source is None or any(row[k] != source[v] for k, v in checks.items()):
            raise ValueError("Proposal record no longer matches metadata")
    return config, manifest


def load_dataset_review_scope(path=None, repository=REPOSITORY):
    """Validate an explicitly authorized whole-current-export review, not annotation."""
    path = Path(path) if path else repository / "config/local.json"
    config = validate_config(json.loads(path.read_text(encoding="utf-8")),
                             repository=repository, purpose="dataset_review")
    scope = config.get("dataset_review_scope", {})
    target = Path(scope.get("manifest_path", ""))
    if (not target.is_absolute() or target.is_symlink()
            or not target.resolve(strict=True).is_relative_to(Path(config["work_root"]))):
        raise ValueError("Whole-dataset review manifest must be private and external")
    data = target.read_bytes()
    if hashlib.sha256(data).hexdigest() != scope.get("manifest_sha256"):
        raise ValueError("Whole-dataset review manifest checksum changed")
    manifest = json.loads(data)
    if manifest.get("authorization") != "user_authorized_current_dataset_read_only_review":
        raise ValueError("Explicit current-dataset review authorization required")
    metadata = Path(config["metadata_csv"]).read_bytes()
    if hashlib.sha256(metadata).hexdigest() != manifest.get("metadata_sha256"):
        raise ValueError("Metadata snapshot changed")
    rows = list(csv.DictReader(io.StringIO(metadata.decode("utf-8-sig"))))
    records = manifest.get("records", [])
    if not rows or len(records) != len(rows) or scope.get("approved_count") != len(rows):
        raise ValueError("Whole-export scope must match every metadata record")
    ids = [r["record_id"] for r in records]
    if len(set(ids)) != len(ids) or any(re.fullmatch(r"R\d{5,8}", x) is None for x in ids):
        raise ValueError("Review record IDs must be unique and safe")
    for row, record in zip(rows, records):
        if record["metadata"] != row:
            raise ValueError("Review record differs from approved metadata snapshot")
    source = Path(config["dataset_root"])
    for part in manifest.get("archive_parts", []):
        name = part["name"]
        if Path(name).name != name:
            raise ValueError("Unsafe archive piece path")
        p = source / name
        if p.is_symlink() or not p.is_file():
            raise ValueError("Archive piece unavailable")
        st = p.stat()
        if [st.st_size, st.st_mtime_ns] != part["size_mtime_ns"]:
            raise ValueError("Archive piece changed after review scope creation")
    if not manifest.get("archive_parts"):
        raise ValueError("Archive scope cannot be empty")
    return config, manifest


def require_visual_ids(manifest, requested):
    """Reject additions and repeated requests rather than silently expanding scope."""
    by_id = {row["exploration_id"]: row for row in manifest["records"]}
    if not requested or len(requested) != len(set(requested)) or any(x not in by_id for x in requested):
        raise ValueError("Requested images must be distinct members of the approved proposal")
    return [by_id[x] for x in requested]


def create_run(config, kind):
    root = Path(config["work_root"]) / "runs"
    # Resolve again to reject a changed output-root symlink before writing.
    if overlaps(root, REPOSITORY) or overlaps(root, config["dataset_root"]):
        raise ValueError("Output root overlaps source or repository")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run = root / f"{kind}-{stamp}-{uuid4().hex[:8]}"
    run.mkdir(parents=True, exist_ok=False)
    return run
