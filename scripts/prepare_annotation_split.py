"""Prepare private time-block memberships before annotation-helper training."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from person_pseudolabel import (
    file_hash, fresh_external, load, packed, safe_source,
    select_camera_round_robin, write,
)

VERSION = 'annotation-time-block-split-1'


def camera(row):
    return row['site'], row['camera_name']


def timestamp(row):
    value = datetime.strptime(row['incident_timestamp'], '%Y-%m-%d %H:%M:%S.%f %z')
    return value.astimezone(timezone(timedelta(hours=7)))


def stable(value, seed):
    return hashlib.sha256((str(seed) + packed(value)).encode()).hexdigest()


def time_groups(rows, guard_hours):
    """Keep site/calendar days together, linking close cross-midnight observations."""
    parents = {row['candidate_id']: row['candidate_id'] for row in rows}

    def root(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    def join(left, right):
        left, right = sorted((root(left), root(right)))
        parents[right] = left

    days, cameras, duplicates = {}, defaultdict(list), {}
    for row in rows:
        identifier = row['candidate_id']
        day = row['site'], timestamp(row).date().isoformat()
        if day in days:
            join(identifier, days[day])
        days[day] = identifier
        cameras[camera(row)].append(row)
        for field in ('dhash_hex', 'pixel_sha256'):
            key = field, row[field]
            if not row[field]:
                raise ValueError('Missing duplicate-screening metadata')
            if key in duplicates:
                join(identifier, duplicates[key])
            duplicates[key] = identifier
    for observations in cameras.values():
        ordered = sorted(observations, key=lambda r: (timestamp(r), r['candidate_id']))
        for left, right in zip(ordered, ordered[1:]):
            if timestamp(right) - timestamp(left) < timedelta(hours=guard_hours):
                join(left['candidate_id'], right['candidate_id'])
    hashes = []
    for row in rows:
        raw = row['dhash_hex']
        if len(raw) != 64:
            raise ValueError('Expected supplied 256-bit dHash encoding')
        value = int(raw, 16)
        for prior, identifier in hashes:
            if (value ^ prior).bit_count() <= 4:
                join(row['candidate_id'], identifier)
        hashes.append((value, row['candidate_id']))
    groups = defaultdict(list)
    for row in rows:
        groups[root(row['candidate_id'])].append(row)
    return dict(groups)


def allocate(groups, pilot_ids, fraction, seed):
    """Keep pilot groups in development and require development for every test camera."""
    membership = defaultdict(set)
    for key, rows in groups.items():
        for row in rows:
            membership[camera(row)].add(key)
    locked = {key for key, rows in groups.items()
              if any(row['candidate_id'] in pilot_ids for row in rows)
              or any(len(membership[camera(row)]) < 2 for row in rows)}
    target = round(sum(map(len, groups.values())) * fraction)
    heldout, covered, count = set(), set(), 0
    while count < target:
        options = []
        for key, rows in groups.items():
            if key in locked or key in heldout:
                continue
            cams = {camera(row) for row in rows}
            if any(not (membership[cam] - heldout - {key}) for cam in cams):
                continue
            options.append(((-len(cams - covered), abs(count + len(rows) - target),
                             stable(key, seed)), key, cams))
        if not options:
            break
        _, key, cams = min(options)
        if abs(count + len(groups[key]) - target) >= abs(count - target):
            break
        heldout.add(key)
        covered.update(cams)
        count += len(groups[key])
    if not heldout:
        raise ValueError('No same-camera held-out time blocks can be allocated')
    return heldout, locked, target


def prepare(args):
    binding_path, pilot_path = Path(args.binding).resolve(), Path(args.parent_pilot).resolve()
    binding, pilot = load(binding_path), load(pilot_path)
    for path_key, hash_key in [('manifest_path', 'manifest_sha256'),
                               ('file_ledger_path', 'file_ledger_sha256')]:
        if file_hash(binding[path_key]) != binding[hash_key]:
            raise ValueError('Changed source binding')
    if (pilot['binding_sha256'] != file_hash(binding_path)
            or pilot['manifest_sha256'] != binding['manifest_sha256']):
        raise ValueError('Parent pilot has different scientific inputs')
    with Path(binding['manifest_path']).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    ledger = load(binding['file_ledger_path'])
    by_id = {row['candidate_id']: row for row in rows}
    sources = {row['candidate_id']: row for row in ledger}
    if (len(rows) != args.expected_count or len(by_id) != len(rows)
            or len(sources) != len(ledger) or set(by_id) != set(sources)):
        raise ValueError('Population mismatch or duplicate IDs')
    for row in rows:
        source = sources[row['candidate_id']]
        if row['filename'] != source['filename'] or row['byte_md5'] != source['md5']:
            raise ValueError('Manifest/ledger identity mismatch')
        safe_source(binding['image_root'], source)
    selected = pilot['selected']
    pilot_ids = {row['id'] for row in selected}
    if len(selected) != 24 or len(pilot_ids) != 24 or not pilot_ids <= set(by_id):
        raise ValueError('Parent pilot must contain 24 unique population members')
    for row in selected:
        if row['source'] != sources[row['id']]:
            raise ValueError('Parent pilot source differs from accepted ledger')
    groups = time_groups(rows, args.guard_hours)
    heldout, locked, target = allocate(groups, pilot_ids, args.heldout_fraction, args.seed)
    development = [row for key, members in groups.items() if key not in heldout for row in members]
    if not len(pilot_ids) <= args.seed_count <= len(development):
        raise ValueError('Development cannot support requested annotation seed')
    remaining = [row for row in development if row['candidate_id'] not in pilot_ids]
    seed_ids = pilot_ids | {row['candidate_id'] for row in select_camera_round_robin(
        remaining, args.seed_count - len(pilot_ids), args.seed)}
    group_of = {row['candidate_id']: key for key, members in groups.items() for row in members}
    roles = {row['id']: row['role'] for row in selected}
    records = []
    for row in rows:
        identifier, key = row['candidate_id'], group_of[row['candidate_id']]
        split = 'HELDOUT_TEST_CANDIDATE' if key in heldout else 'DEVELOPMENT'
        records.append({**row, 'time_block_id': key, 'split': split,
                        'annotation_seed': identifier in seed_ids,
                        'pilot_role': roles.get(identifier, ''),
                        'source_relative_path': sources[identifier]['relative_path']})
    test_cameras = {camera(r) for r in records if r['split'] == 'HELDOUT_TEST_CANDIDATE'}
    dev_cameras = {camera(r) for r in records if r['split'] == 'DEVELOPMENT'}
    assert test_cameras <= dev_cameras
    assert not any(r['split'] != 'DEVELOPMENT' for r in records if r['annotation_seed'])
    output = fresh_external(args.output, binding['image_root'])
    output.mkdir(parents=True)
    with (output / 'MEMBERSHIP.csv').open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    write(output / 'PILOT_BINDING.json', {
        'parent_queue_path': str(pilot_path), 'parent_queue_sha256': file_hash(pilot_path),
        'membership_sha256': file_hash(output / 'MEMBERSHIP.csv'),
        'selected': selected, 'state': 'DEVELOPMENT_BOUND_VISUAL_COVERAGE_PENDING',
        'helper_train_validation': 'GROUP_SPLIT_AFTER_VERIFIED_SEED_BEFORE_TRAINING',
    })
    counts = Counter(r['split'] for r in records)
    summary = {
        'version': VERSION, 'created_at': datetime.now(timezone.utc).isoformat(),
        'state': 'TIME_BLOCK_MEMBERSHIP_MATERIALIZED_EVENT_REVIEW_PENDING',
        'binding_path': str(binding_path), 'binding_sha256': file_hash(binding_path),
        'script_sha256': file_hash(__file__),
        'shared_selection_source_sha256': file_hash(Path(__file__).with_name('person_pseudolabel.py')),
        'launch_commit': subprocess.check_output(
            ['git', '-C', str(Path(__file__).resolve().parents[1]), 'rev-parse', 'HEAD'], text=True).strip(),
        'parameters': vars(args), 'population': len(records), 'groups': len(groups),
        'near_duplicate_guard': {'supplied_dhash_bits': 256, 'maximum_hamming_distance': 4},
        'split_counts': counts, 'requested_heldout_count': target,
        'annotation_seed': len(seed_ids), 'pilot_count': len(pilot_ids),
        'pilot_roles': Counter(roles.values()), 'development_only_cameras': len(dev_cameras-test_cameras),
        'development_cameras': len(dev_cameras), 'heldout_cameras': len(test_cameras),
        'locked_development_groups': len(locked),
        'limitations': [
            'Site/calendar-day blocks and a same-camera time guard approximate event separation.',
            'Timestamp and exact supplied hash matching do not prove event or identity independence.',
            'Near duplicates, camera clock errors and long events need source-context review.',
            'Pilot membership preserves prior candidates; visual/person-size coverage remains pending.',
            'Membership is separate from GT acceptance and final execution freeze.',
        ],
        'artifact_sha256': {name: file_hash(output/name) for name in ['MEMBERSHIP.csv', 'PILOT_BINDING.json']},
    }
    write(output / 'SUMMARY.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', required=True)
    parser.add_argument('--parent-pilot', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--heldout-fraction', type=float, default=0.2)
    parser.add_argument('--seed-count', type=int, default=300)
    parser.add_argument('--seed', type=int, default=20261110)
    parser.add_argument('--guard-hours', type=float, default=4)
    parser.add_argument('--expected-count', type=int, default=2200)
    args = parser.parse_args()
    if not 0 < args.heldout_fraction < 1 or not 0 < args.guard_hours <= 24:
        parser.error('Heldout fraction must be between 0 and 1; time guard must be in (0,24]')
    result = prepare(args)
    print(json.dumps({k: result[k] for k in [
        'state', 'population', 'groups', 'split_counts', 'annotation_seed',
        'pilot_count', 'development_cameras', 'heldout_cameras', 'development_only_cameras',
    ]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
