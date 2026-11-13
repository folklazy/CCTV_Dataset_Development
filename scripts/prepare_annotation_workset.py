"""Materialize existing annotation memberships as private, hash-verified work packs."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import time

from PIL import Image

from person_pseudolabel import file_hash, fresh_external, load, safe_source, write

ROLES = {
    'HELPER_TRAIN_INITIAL': ('01_seed_train_240', 240, 'EXISTING_SEED_RECEIPT'),
    'HELPER_VALIDATION_FIXED': ('02_fixed_validation_60', 60, 'FIXED_VALIDATION_NO_TRAINING'),
    'HELPER_TRAIN_BOOST': ('03_boost_550', 550, 'NEXT_AFTER_HELPER_SELECTION'),
    'DEVELOPMENT_AFTER_FREEZE': ('04_after_helper_freeze_910', 910, 'AFTER_HELPER_V2_FREEZE'),
    'HELDOUT_TEST': ('05_heldout_test_440', 440, 'HELDOUT_AFTER_HELPER_V2_FREEZE'),
}


def validate_membership(rows):
    ids = [row['candidate_id'] for row in rows]
    if len(ids) != 2200 or len(set(ids)) != 2200:
        raise ValueError('Expected exact 2200 unique membership IDs')
    counts = Counter(row['helper_role'] for row in rows)
    if counts != Counter({role: values[1] for role, values in ROLES.items()}):
        raise ValueError('Membership role counts differ from the accepted split')
    test_groups = {row['time_block_id'] for row in rows if row['helper_role'] == 'HELDOUT_TEST'}
    development_groups = {row['time_block_id'] for row in rows if row['helper_role'] != 'HELDOUT_TEST'}
    validation_groups = {row['time_block_id'] for row in rows if row['helper_role'] == 'HELPER_VALIDATION_FIXED'}
    training_groups = {row['time_block_id'] for row in rows if row['helper_role'] in
                       ['HELPER_TRAIN_INITIAL', 'HELPER_TRAIN_BOOST']}
    if test_groups & development_groups or validation_groups & training_groups:
        raise ValueError('Membership leaks a protected time block')


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def export_seed_annotation(source, expected_sha256, destination, image_name, image_size):
    if file_hash(source) != expected_sha256:
        raise ValueError('Seed annotation changed since its human acceptance receipt')
    annotation = load(source)
    if (annotation['imageWidth'], annotation['imageHeight']) != image_size:
        raise ValueError('Seed annotation geometry differs from its source image')
    original = json.loads(json.dumps(annotation))
    changed = annotation['imagePath'] != image_name
    if changed:
        annotation['imagePath'] = image_name
        write(destination, annotation)
    else:
        shutil.copyfile(source, destination)
    readback = load(destination)
    original['imagePath'] = image_name
    if readback != original:
        raise ValueError('Derived annotation readback changed fields beyond imagePath')
    return file_hash(destination), changed


def prepare(membership_path, seed_receipt, output, pack_size=50):
    started = time.monotonic()
    membership_path, seed_receipt = Path(membership_path), Path(seed_receipt)
    if pack_size <= 0:
        raise ValueError('Work-pack size must be positive')
    summary = load(membership_path.parent/'SUMMARY.json')
    if file_hash(membership_path) != summary['artifact_sha256']['MEMBERSHIP.csv']:
        raise ValueError('Accepted membership hash changed')
    binding_path = Path(summary['binding_path'])
    if file_hash(binding_path) != summary['binding_sha256']:
        raise ValueError('Scientific source binding changed')
    binding = load(binding_path)
    for key, hash_key in [('manifest_path', 'manifest_sha256'), ('file_ledger_path', 'file_ledger_sha256')]:
        if file_hash(binding[key]) != binding[hash_key]:
            raise ValueError('Scientific manifest or file ledger changed')
    with membership_path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    validate_membership(rows)
    ledger = load(binding['file_ledger_path'])
    sources = {row['candidate_id']: row for row in ledger}
    if len(sources) != len(ledger) or set(sources) != {row['candidate_id'] for row in rows}:
        raise ValueError('File ledger population differs from membership')
    receipt = load(seed_receipt)
    annotation_binding_path = seed_receipt.parent/receipt['annotation_binding']
    if file_hash(annotation_binding_path) != receipt['annotation_binding_sha256']:
        raise ValueError('Human acceptance binding changed')
    annotation_binding = load(annotation_binding_path)
    if annotation_binding['membership_sha256'] != file_hash(membership_path):
        raise ValueError('Human receipt uses another membership')
    annotations = {item['candidate_id']: item for item in annotation_binding['annotation_files']}
    seed_ids = {row['candidate_id'] for row in rows if row['helper_role'] in
                ['HELPER_TRAIN_INITIAL', 'HELPER_VALIDATION_FIXED']}
    if set(annotations) != seed_ids or len(annotations) != 300:
        raise ValueError('Expected seed receipt for the same 300 IDs')
    output = fresh_external(output, binding['image_root'])
    output.mkdir(parents=True)
    work_rows, batch_rows, manifests = [], [], {}
    copied_bytes = 0
    try:
        for role, (folder, _, stage) in ROLES.items():
            ordered = sorted((row for row in rows if row['helper_role'] == role),
                             key=lambda row: (row['site'], row['camera_name'],
                                              row['incident_timestamp'], row['candidate_id']))
            for offset in range(0, len(ordered), pack_size):
                pack = output/folder/f'batch_{offset//pack_size+1:02d}'
                images = pack/'images'
                images.mkdir(parents=True)
                records = []
                for member in ordered[offset:offset+pack_size]:
                    identifier = member['candidate_id']
                    source = sources[identifier]
                    if (source['relative_path'] != member['source_relative_path'] or
                            source['filename'] != member['filename'] or source['md5'] != member['byte_md5']):
                        raise ValueError('Source identity differs from membership')
                    if Path(identifier).name != identifier or Path(source['filename']).name != source['filename']:
                        raise ValueError('Unsafe export filename')
                    path = safe_source(binding['image_root'], source)
                    raw = path.read_bytes()
                    if hashlib.sha256(raw).hexdigest() != source['sha256']:
                        raise ValueError('Source image changed')
                    if hashlib.md5(raw).hexdigest() != source['md5']:
                        raise ValueError('Source MD5 differs from its ledger')
                    with Image.open(io.BytesIO(raw)) as image:
                        image.load()
                        size = image.size
                    if size != (source['width'], source['height']):
                        raise ValueError('Source decode dimensions changed')
                    name = identifier+'_'+source['filename']
                    destination = images/name
                    destination.write_bytes(raw)
                    if file_hash(destination) != source['sha256']:
                        raise ValueError('Copied image readback hash mismatch')
                    copied_bytes += len(raw)
                    annotation_path, annotation_sha, changed = '', '', False
                    if identifier in annotations:
                        accepted = annotations[identifier]
                        target = destination.with_suffix('.json')
                        annotation_sha, changed = export_seed_annotation(
                            accepted['path'], accepted['sha256'], target, name, size)
                        annotation_path = target.relative_to(output).as_posix()
                    record = {**member, 'work_pack': pack.relative_to(output).as_posix(),
                              'stage': stage, 'export_image': destination.relative_to(output).as_posix(),
                              'source_image': str(path), 'image_sha256': source['sha256'],
                              'width': size[0], 'height': size[1], 'image_bytes': len(raw),
                              'seed_annotation': annotation_path, 'seed_annotation_sha256': annotation_sha,
                              'seed_annotation_source': annotations[identifier]['path'] if identifier in annotations else '',
                              'seed_image_path_adjusted': changed,
                              'new_annotation_state': 'EXISTING_SEED_RECEIPT' if annotation_path else 'NOT_ANNOTATED'}
                    records.append(record)
                    work_rows.append(record)
                manifest = pack/'MANIFEST.csv'
                write_csv(manifest, records)
                manifests[manifest.relative_to(output).as_posix()] = file_hash(manifest)
                batch_rows.append({'work_pack': pack.relative_to(output).as_posix(), 'helper_role': role,
                                   'stage': stage, 'images': len(records),
                                   'sites': len({row['site'] for row in records}),
                                   'cameras': len({(row['site'], row['camera_name']) for row in records})})
            write(output/'PROGRESS.json', {'state': 'PREPARING', 'copied_images': len(work_rows),
                                           'total_images': len(rows), 'completed_role': role})
        write_csv(output/'WORKSET.csv', work_rows)
        write_csv(output/'BATCHES.csv', batch_rows)
        result = {'state': 'WORKSET_PREPARED_SOURCE_VERIFIED',
                  'created_at_utc': datetime.now(timezone.utc).isoformat(),
                  'images': len(work_rows), 'work_packs': len(batch_rows), 'pack_size_limit': pack_size,
                  'role_counts': dict(Counter(row['helper_role'] for row in work_rows)),
                  'seed_annotation_copies': sum(bool(row['seed_annotation']) for row in work_rows),
                  'unannotated_images': sum(not row['seed_annotation'] for row in work_rows),
                  'image_bytes': copied_bytes, 'elapsed_seconds': time.monotonic()-started,
                  'membership_path': str(membership_path.resolve()), 'membership_sha256': file_hash(membership_path),
                  'source_binding_path': str(binding_path), 'source_binding_sha256': file_hash(binding_path),
                  'seed_receipt': str(seed_receipt.resolve()), 'seed_receipt_sha256': file_hash(seed_receipt),
                  'batch_manifest_hashes': manifests,
                  'artifact_sha256': {name: file_hash(output/name) for name in ['WORKSET.csv', 'BATCHES.csv']},
                  'source_files_modified': 0, 'model_calls': 0,
                  'audit_scope': 'Membership/byte hashes/strict decode/dimensions/seed JSON roundtrip; no new visual or GT acceptance',
                  'person_mask_role': 'Automatic helper only; full-person GT mask not required'}
        write(output/'SUMMARY.json', result)
        write(output/'PROGRESS.json', {'state': 'COMPLETE', 'copied_images': len(work_rows), 'total_images': len(rows)})
        return result
    except BaseException as error:
        write(output/'PROGRESS.json', {'state': 'STOPPED', 'copied_images': len(work_rows),
                                       'total_images': len(rows), 'error': str(error)})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--membership', type=Path, required=True)
    parser.add_argument('--seed-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pack-size', type=int, default=50)
    args = parser.parse_args()
    result = prepare(args.membership, args.seed_receipt, args.output, args.pack_size)
    print(json.dumps({key: value for key, value in result.items()
                      if key in ['state', 'images', 'work_packs', 'seed_annotation_copies',
                                 'unannotated_images', 'image_bytes', 'elapsed_seconds']}))


if __name__ == '__main__':
    main()
