#!/usr/bin/env python3
"""Audit delivered files, metadata and ZIP directory; never decode CCTV images."""

import argparse
import bisect
import collections
import csv
import hashlib
import io
import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from workspace_paths import REPOSITORY, load_local_config, create_run
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def now():
    return datetime.now(timezone.utc).isoformat()


def signature(path):
    st = path.stat()
    return st.st_size, st.st_mtime_ns, st.st_ino


def stable_bytes(path):
    for _ in range(3):
        before = signature(path)
        data = path.read_bytes()
        if before == signature(path):
            return data
    raise RuntimeError(f"Source changed during three read attempts: {path.name}")


def save_json(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def save_csv(path, rows, fields):
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class SplitArchive(io.RawIOBase):
    """Seekable read-only concatenation; no merged ZIP or image extraction."""

    def __init__(self, paths):
        super().__init__()
        self.paths = paths
        self.starts = [0]
        for path in paths:
            self.starts.append(self.starts[-1] + path.stat().st_size)
        self.position = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=os.SEEK_SET):
        base = {os.SEEK_SET: 0, os.SEEK_CUR: self.position,
                os.SEEK_END: self.starts[-1]}[whence]
        target = base + offset
        if target < 0:
            raise ValueError("Negative seek")
        self.position = target
        return target

    def read(self, size=-1):
        if self.closed:
            raise ValueError("Read on closed archive")
        remaining = max(0, self.starts[-1] - self.position)
        size = remaining if size is None or size < 0 else min(size, remaining)
        pieces = []
        while size:
            index = bisect.bisect_right(self.starts, self.position) - 1
            take = min(size, self.starts[index + 1] - self.position)
            with self.paths[index].open("rb") as handle:
                handle.seek(self.position - self.starts[index])
                part = handle.read(take)
            if len(part) != take:
                raise OSError("Split archive changed or was truncated")
            pieces.append(part)
            self.position += take
            size -= take
        return b"".join(pieces)


def spreadsheet_rows(data):
    """Read the delivered XLSX strings directly with stdlib; reject formulas."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        sheets = [n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)]
        if len(sheets) != 1:
            raise ValueError("Expected one worksheet; inspect workbook mapping before reuse")
        shared = []
        if "xl/sharedStrings.xml" in names:
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(item.itertext()) for item in shared_root.findall("s:si", NS)]
        sheet = ET.fromstring(archive.read(sheets[0]))
    result = []
    for row in sheet.findall(".//s:sheetData/s:row", NS):
        values = {}
        for cell in row.findall("s:c", NS):
            if cell.find("s:f", NS) is not None:
                raise ValueError("Formula encountered; values are not treated as source truth")
            letters = re.match(r"[A-Z]+", cell.attrib["r"])[0]
            column = 0
            for letter in letters:
                column = column * 26 + ord(letter) - ord("A") + 1
            kind = cell.get("t")
            value = cell.findtext("s:v", default="", namespaces=NS)
            if kind == "inlineStr":
                inline = cell.find("s:is", NS)
                value = "".join(inline.itertext()) if inline is not None else ""
            elif kind == "s":
                value = shared[int(value)]
            values[column - 1] = value
        if values:
            result.append([values.get(i, "") for i in range(max(values) + 1)])
    columns = result[0]
    if len(columns) != len(set(columns)):
        raise ValueError("Duplicate spreadsheet columns")
    records = []
    for row in result[1:]:
        if len(row) > len(columns):
            raise ValueError("Spreadsheet row exceeds header")
        records.append(dict(zip(columns, row + [""] * (len(columns) - len(row)))))
    return columns, records


def canonical(records, columns):
    return collections.Counter(tuple("" if row.get(c) is None else str(row[c])
                                     for c in columns) for row in records)


def parse_timestamp(value):
    # Delivered export uses a space before a numeric UTC offset, not ISO 8601.
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f %z")
    except ValueError:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


def file_role(path, metadata_names):
    if re.fullmatch(r".+_part\d+\.zip\.\d+", path.name):
        return "required_split_archive_piece"
    if path.name == metadata_names[0]:
        return "primary_metadata_export"
    if path.name == metadata_names[1]:
        return "metadata_crosscheck_export"
    if path.name == metadata_names[2]:
        return "human_readable_metadata_crosscheck"
    if path.name.startswith("CCTV_") and path.suffix == ".md":
        return "delivered_foundation_copy"
    if path.name == "merge_files.bat":
        return "windows_assembly_reference_do_not_execute_on_linux"
    return "unclassified_review_required"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPOSITORY / "config/local.json")
    parser.add_argument("--check-config", action="store_true", help="Validate paths only; do not read package contents")
    args = parser.parse_args()
    config = load_local_config(args.config)
    source = Path(config["dataset_root"])
    if args.check_config:
        print(json.dumps({"configuration": "valid", "source_read_only": True,
                          "work_outside_repository": True, "package_contents_read": False}))
        return
    started = now()
    run = create_run(config, "package-audit")
    save_json(run / "audit_configuration.json", {
        "source_root": str(source),
        "script_path": Path(__file__).resolve().relative_to(REPOSITORY).as_posix(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "metadata_formats_and_archive_central_directory_no_image_decode",
    })
    files = sorted(source.iterdir())
    if any(not p.is_file() or p.is_symlink() for p in files):
        raise ValueError("Unexpected directory or symlink; inspect package scope first")
    initial = {p.name: signature(p) for p in files}
    metadata_names = [Path(config[key]).name for key in ("metadata_csv", "metadata_json", "metadata_xlsx")]
    payloads = {name: stable_bytes(source / name) for name in metadata_names}
    reader = csv.DictReader(io.StringIO(payloads[metadata_names[0]].decode("utf-8-sig")))
    columns = reader.fieldnames
    if not columns or len(columns) != len(set(columns)):
        raise ValueError("Missing or duplicate CSV headers")
    records = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in records):
        raise ValueError("Malformed CSV row")
    json_records = json.loads(payloads[metadata_names[1]].decode("utf-8-sig"))
    if not isinstance(json_records, list) or any(not isinstance(r, dict) for r in json_records):
        raise ValueError("Expected JSON record list")
    xlsx_columns, xlsx_records = spreadsheet_rows(payloads[metadata_names[2]])
    comparisons = {}
    for label, other_columns, other_records in (
        ("json", sorted({k for row in json_records for k in row}), json_records),
        ("xlsx", xlsx_columns, xlsx_records),
    ):
        same_schema = set(columns) == set(other_columns)
        comparisons[label] = {"records": len(other_records), "same_column_set": same_schema,
            "same_record_multiset": same_schema and canonical(records, columns) == canonical(
                other_records, columns), "comparison": "all columns; null normalized to empty string"}
    save_json(run / "format_comparison.json", comparisons)
    parts = []
    for path in files:
        match = re.fullmatch(r".+_part(\d+)\.zip\.(\d+)", path.name)
        if match:
            if int(match[1]) != int(match[2]):
                raise ValueError("Archive part labels disagree")
            parts.append((int(match[1]), path))
    parts.sort()
    if not parts or [n for n, _ in parts] != list(range(1, len(parts) + 1)):
        raise ValueError("Missing archive parts or inconsistent numbering")
    archive_rows = []
    with SplitArchive([p for _, p in parts]) as stream, zipfile.ZipFile(stream) as archive:
        for index, info in enumerate(archive.infolist(), 1):
            path = PurePosixPath(info.filename)
            archive_rows.append({"archive_member_id": f"M{index:05d}",
                "member_path": info.filename, "basename": path.name,
                "is_directory": info.is_dir(), "uncompressed_bytes": info.file_size,
                "compressed_bytes": info.compress_size, "header_crc32": f"{info.CRC:08x}",
                "is_image_by_suffix": not info.is_dir() and path.suffix.lower() in IMAGE_SUFFIXES,
                "unsafe_path": path.is_absolute() or ".." in path.parts or "\\" in info.filename})
    save_csv(run / "archive_inventory.csv", archive_rows, list(archive_rows[0]))
    images = [r for r in archive_rows if r["is_image_by_suffix"]]
    by_path, by_name = collections.defaultdict(list), collections.defaultdict(list)
    for member in images:
        by_path[member["member_path"]].append(member)
        by_name[member["basename"]].append(member)
    linkage, matched = [], set()
    for index, record in enumerate(records, 2):
        filename = record["filename"]
        candidates = by_path.get(filename, [])
        method = "exact_member_path"
        if not candidates and PurePosixPath(filename).name == filename:
            candidates = by_name.get(filename, [])
            method = "basename_checked_for_uniqueness"
        status = "matched" if len(candidates) == 1 else ("ambiguous" if candidates else "unmatched")
        if status == "matched":
            matched.add(candidates[0]["archive_member_id"])
        linkage.append({"csv_row_locator": index, "filename": filename, "match_status": status,
            "match_method": method, "candidate_count": len(candidates),
            "archive_member_id": candidates[0]["archive_member_id"] if len(candidates) == 1 else ""})
    save_csv(run / "metadata_linkage.csv", linkage, list(linkage[0]))
    timestamps, source_times, invalid_time, naive_time = [], [], 0, 0
    for record in records:
        try:
            value = parse_timestamp(record["incident_timestamp"])
            if value.utcoffset() is None:
                naive_time += 1
            else:
                source_times.append(value)
                timestamps.append(value.astimezone(timezone.utc))
        except (ValueError, TypeError):
            invalid_time += 1
    audit = {"records": len(records), "columns": columns,
        "missing_values": {c: sum(not r[c].strip() for r in records) for c in columns},
        "unique_filenames": len({r["filename"] for r in records}),
        "site_count": len({r["site"] for r in records}),
        "site_unknown_literal_count": sum(r["site"] == "Unknown" for r in records),
        "site_count_excluding_unknown_literal": len({r["site"] for r in records if r["site"] != "Unknown"}),
        "camera_name_count": len({r["camera_name"] for r in records}),
        "site_camera_pair_count": len({(r["site"], r["camera_name"]) for r in records}),
        "raw_curation_status_counts": dict(collections.Counter(r["curate_status"] for r in records)),
        "curation_status_mapping": None,
        "category_counts_record_level_only": dict(collections.Counter(r["category"] for r in records)),
        "timestamp_invalid": invalid_time, "timestamp_without_offset": naive_time,
        "timestamp_min_utc": min(timestamps).isoformat() if timestamps else None,
        "timestamp_max_utc": max(timestamps).isoformat() if timestamps else None,
        "timestamp_source_offset_counts": dict(collections.Counter(v.strftime("%z") for v in source_times)),
        "timestamp_min_source": min(source_times).isoformat() if source_times else None,
        "timestamp_max_source": max(source_times).isoformat() if source_times else None,
        "calendar_dates_with_records_source_offset": len({v.date() for v in source_times}),
        "archive_member_count_including_directories": len(archive_rows),
        "archive_image_members_by_suffix": len(images),
        "archive_duplicate_image_basenames": sum(len(v) > 1 for v in by_name.values()),
        "archive_duplicate_member_paths": len(archive_rows) - len({r["member_path"] for r in archive_rows}),
        "archive_unsafe_path_count": sum(r["unsafe_path"] for r in archive_rows),
        "linkage_status_counts": dict(collections.Counter(r["match_status"] for r in linkage)),
        "orphan_archive_image_members": len(images) - len(matched),
        "readable_images": None, "unique_image_content_hashes": None,
        "image_crc_verification": "NOT_RUN", "images_visually_inspected": 0}
    save_json(run / "metadata_audit.json", audit)
    save_json(run / "stratified_record_counts.json", {
        "denominator_records": len(records), "unit": "metadata_record_not_person",
        "by_site_raw": dict(collections.Counter(r["site"] for r in records)),
        "by_site_camera_raw": [{"site": site, "camera_name": camera, "records": count}
            for (site, camera), count in sorted(collections.Counter(
                (r["site"], r["camera_name"]) for r in records).items())],
        "by_source_calendar_date": dict(sorted(collections.Counter(
            v.date().isoformat() for v in source_times).items())),
        "by_raw_curation_status": audit["raw_curation_status_counts"],
    })
    source_rows = []
    for path in files:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                digest.update(block)
        st = path.stat()
        source_rows.append({"filename": path.name, "role": file_role(path, metadata_names),
            "size_bytes": st.st_size, "mtime_utc": datetime.fromtimestamp(
                st.st_mtime, timezone.utc).isoformat(), "sha256_file_bytes": digest.hexdigest(),
            "stable_since_start": initial[path.name] == signature(path),
            "action": "preserve_read_only"})
        # Append progress rather than overwrite any previous checkpoint or run record.
        with (run / "hash_progress.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(source_rows[-1], ensure_ascii=False) + "\n")
        print(f"Hashed {len(source_rows)}/{len(files)}: {path.name}", flush=True)
    save_csv(run / "source_files.csv", source_rows, list(source_rows[0]))
    stable = (all(r["stable_since_start"] for r in source_rows)
              and all(initial[p.name] == signature(p) for p in files)
              and sorted(p.name for p in source.iterdir()) == sorted(initial))
    save_json(run / "package_status.json", {"started_at_utc": started, "completed_at_utc": now(),
        "source_root": str(source), "source_snapshot_stable": stable,
        "phase": "metadata_and_archive_directory_only", "archive_part_count": len(parts),
        "archive_total_bytes": sum(p.stat().st_size for _, p in parts),
        "source_file_count": len(files), "archive_extracted": False,
        "image_pixels_decoded": False, "models_run": False,
        "related_study_outputs_used": False})
    if not stable:
        raise RuntimeError("Source changed during audit; do not treat this run as one stable snapshot")
    print(run.as_posix())


if __name__ == "__main__":
    main()
