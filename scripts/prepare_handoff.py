#!/usr/bin/env python3
"""Record repository-document provenance into external work storage only."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from workspace_paths import REPOSITORY, load_local_config, create_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPOSITORY / "config/local.json")
    args = parser.parse_args()
    config = load_local_config(args.config)
    paths = [REPOSITORY / "AGENTS.md", REPOSITORY / "README.md"]
    paths += sorted((REPOSITORY / "docs").glob("*.md"))
    inventory = []
    for path in paths:
        if path.is_symlink():
            raise ValueError("Document symlinks are not read")
        before = path.stat()
        data = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError("Repository document changed during read; rerun")
        inventory.append({"path": path.relative_to(REPOSITORY).as_posix(),
                          "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    run = create_run(config, "document-preparation")
    (run / "document_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    status = {"completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "repository_documents_only", "document_count": len(inventory),
              "dataset_path_status": "AVAILABLE", "package_contents_read": False,
              "images_inspected_by_this_command": 0}
    (run / "preparation_status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(run)


if __name__ == "__main__":
    main()
