# CCTV Human Parsing Evaluation Dataset

This is an independent dataset-development Git repository. Resolve its root from the script or checkout location; never assume the former workspace is its parent.

- Source/configuration/docs/tests/templates belong here. Real images, metadata, annotations, per-image identifiers, private reports, generated outputs and real release manifests stay outside this repository under the absolute paths in ignored `config/local.json`.
- Keep source images/metadata at their current location. Use read-only opens; never rename, rewrite, delete, chmod or alter source curation statuses. `pending` in an export does not invalidate earlier selected/rejected/flagged records.
- Configuration examples contain placeholders only. Do not commit local config, personal paths, credentials, company identifiers, image previews or raw audit evidence. Review the staged paths and contents before each commit.
- Current scope is workspace preparation. Do not start annotation, image review, inference, training or benchmarking from setup work. Do not freeze classes, colors, quality thresholds, splits or evaluation policy.
- Reuse inherited draft methods with their provenance. Record every semantic change and distinguish proposed / reported / observed / measured / accepted. Archived model experiments are separate and must not be modified.
- Python 3.10+ and standard library are sufficient for current tools. Do not install packages/download weights or create/modify environments without authorization. Do not use sudo/system changes. Respect device visibility if later GPU work is authorized.
- Work/source/repository paths must be disjoint. Each execution creates a fresh run under external `work_root/runs`; never overwrite historical results. Do not follow source symlinks or silently expand source scope.
- Keep legacy originals until verification and explicit deletion approval. Back up before migration; keep an old-to-new SHA256 manifest in external provenance. Reversible setup is authorized; pause only an operation that risks overwriting existing work.
- Use local Git only for this setup. Do not create remotes, publish or push without a later instruction. Change VS Code settings only in this repository's workspace file.
