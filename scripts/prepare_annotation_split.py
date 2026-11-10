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

VERSION = 'annotation-time-block-split-2'


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
    """Allocate whole blocks toward per-site targets with metadata balance.

    Dynamic programming retains one metadata-balanced candidate per image count.
    The result is deterministic, with protected development observations per camera.
    """
    membership = defaultdict(set)
    site_groups = defaultdict(dict)
    for key, rows in groups.items():
        sites = {row['site'] for row in rows}
        if len(sites) != 1:
            raise ValueError('Cross-site linked block requires allocation review')
        site_groups[next(iter(sites))][key] = rows
        for row in rows:
            membership[camera(row)].add(key)
    locked = {key for key, rows in groups.items()
              if any(row['candidate_id'] in pilot_ids for row in rows)
              or any(len(membership[camera(row)]) < 2 for row in rows)}
    for cam in sorted(membership, key=lambda value: stable(value, seed)):
        if not membership[cam] & locked:
            anchor = min(membership[cam], key=lambda key: (len(groups[key]), stable(key, seed)))
            locked.add(anchor)
    total = sum(map(len, groups.values()))
    target = round(total * fraction)
    combined = {0: (0.0, ())}
    for site in sorted(site_groups):
        blocks = site_groups[site]
        size = sum(map(len, blocks.values()))
        site_target = size * fraction
        limit = min(size, round(site_target) + max(map(len, blocks.values())))
        states = {0: ()}
        for key in sorted(blocks, key=lambda value: stable(value, seed)):
            if key in locked:
                continue
            for count, selected in list(states.items()):
                new_count = count + len(blocks[key])
                if new_count > limit:
                    continue
                candidate = selected + (key,)
                previous = states.get(new_count)
                if previous is None or balance_cost(candidate, blocks, fraction) < balance_cost(previous, blocks, fraction):
                    states[new_count] = candidate
        updated = {}
        for count, (cost, selected) in combined.items():
            for site_count, keys in states.items():
                new_count = count + site_count
                if new_count > target + max(map(len, groups.values())):
                    continue
                new_cost = (cost + (site_count-site_target)**2/max(1, site_target)
                            + balance_cost(keys, blocks, fraction))
                candidate = new_cost, selected + keys
                if new_count not in updated or candidate < updated[new_count]:
                    updated[new_count] = candidate
        combined = updated
    count = min(combined, key=lambda n: (combined[n][0] + 4*(n-target)**2/max(1, target),
                                         abs(n-target), combined[n][1]))
    heldout = set(combined[count][1])
    if not heldout:
        raise ValueError('No same-camera held-out time blocks can be allocated')
    return heldout, locked, target


def balance_cost(selected, groups, fraction):
    """Secondary costs for camera, day/night and time-block representation."""
    all_rows = [row for key in sorted(groups) for row in groups[key]]
    chosen = [row for key in selected for row in groups[key]]
    cost = 0.0
    for weight, feature in [(0.05, camera), (0.1, lambda row: row.get('diurnal_period', 'unknown'))]:
        totals = Counter(feature(row) for row in all_rows)
        counts = Counter(feature(row) for row in chosen)
        cost += weight * sum((counts[key]-fraction*n)**2/max(1, fraction*n)
                             for key, n in sorted(totals.items()))
    return cost + 0.02*(len(selected)-fraction*len(groups))**2/max(1, fraction*len(groups))


def helper_partitions(development, seed_ids, pilot_ids, groups, seed):
    """Keep pilot in training and reserve complete validation blocks from both rounds."""
    pilot_groups = {key for key, rows in groups.items()
                    if any(row['candidate_id'] in pilot_ids for row in rows)}
    training_counts = Counter(camera(row) for row in development if row['candidate_id'] in seed_ids)
    validation, selected_groups = [], set()
    seen_sites, seen_cameras = set(), set()
    seed_rows = [row for row in development if row['candidate_id'] in seed_ids]
    day_fraction = sum(row.get('diurnal_period') == 'day' for row in seed_rows) / len(seed_rows)
    while len(validation) < 60:
        options = []
        for key, rows in groups.items():
            chosen = [row for row in rows if row['candidate_id'] in seed_ids]
            counts = Counter(camera(row) for row in chosen)
            if (not chosen or key in pilot_groups | selected_groups
                    or len(validation)+len(chosen) > 60
                    or any(training_counts[cam] <= n for cam, n in counts.items())):
                continue
            sites = {row['site'] for row in chosen}
            cameras = set(counts)
            day = sum(row.get('diurnal_period') == 'day' for row in validation+chosen)
            score = (-len(sites-seen_sites), -len(cameras-seen_cameras),
                     abs(day-(len(validation)+len(chosen))*day_fraction),
                     len(rows)-len(chosen), stable(key, seed))
            options.append((score, key, chosen, counts, sites, cameras))
        if not options:
            raise ValueError('Cannot form validation60 while preserving pilot and training cameras')
        _, key, chosen, counts, sites, cameras = min(options)
        validation.extend(chosen)
        selected_groups.add(key)
        training_counts.subtract(counts)
        seen_sites.update(sites)
        seen_cameras.update(cameras)
    val_ids = {row['candidate_id'] for row in validation}
    blocked_ids = {row['candidate_id'] for key in selected_groups for row in groups[key]}
    candidates = [row for row in development
                  if row['candidate_id'] not in seed_ids | blocked_ids]
    boost_ids = {row['candidate_id'] for row in select_camera_round_robin(candidates, 550, seed)}
    roles = {row['candidate_id']: 'DEVELOPMENT_AFTER_FREEZE' for row in development}
    roles.update({identifier: 'HELPER_TRAIN_INITIAL' for identifier in seed_ids-val_ids})
    roles.update({identifier: 'HELPER_VALIDATION_FIXED' for identifier in val_ids})
    roles.update({identifier: 'HELPER_TRAIN_BOOST' for identifier in boost_ids})
    return roles, selected_groups


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
    parent_path = Path(args.parent_membership).resolve()
    parent_summary = load(parent_path.parent / 'SUMMARY.json')
    if (file_hash(parent_path) != parent_summary['artifact_sha256']['MEMBERSHIP.csv']
            or parent_summary['binding_sha256'] != file_hash(binding_path)):
        raise ValueError('Parent split binding changed')
    with parent_path.open(encoding='utf-8-sig', newline='') as stream:
        parent_rows = list(csv.DictReader(stream))
    parent_ids = {row['candidate_id'] for row in parent_rows}
    if len(parent_ids) != len(parent_rows) or parent_ids != set(by_id):
        raise ValueError('Parent split population differs')
    parent_by_id = {row['candidate_id']: row for row in parent_rows}
    for row in rows:
        if any(parent_by_id[row['candidate_id']][key] != value for key, value in row.items()):
            raise ValueError('Parent metadata differs from source manifest')
    groups = time_groups(rows, args.guard_hours)
    heldout, locked, target = allocate(groups, pilot_ids, args.heldout_fraction, args.seed)
    development = [row for key, members in groups.items() if key not in heldout for row in members]
    if not len(pilot_ids) <= args.seed_count <= len(development):
        raise ValueError('Development cannot support requested annotation seed')
    remaining = [row for row in development if row['candidate_id'] not in pilot_ids]
    seed_ids = pilot_ids | {row['candidate_id'] for row in select_camera_round_robin(
        remaining, args.seed_count - len(pilot_ids), args.seed)}
    dev_groups = {key: members for key, members in groups.items() if key not in heldout}
    helper_roles, validation_groups = helper_partitions(development, seed_ids, pilot_ids,
                                                       dev_groups, args.seed)
    group_of = {row['candidate_id']: key for key, members in groups.items() for row in members}
    roles = {row['id']: row['role'] for row in selected}
    records = []
    for row in rows:
        identifier, key = row['candidate_id'], group_of[row['candidate_id']]
        split = 'HELDOUT_TEST_CANDIDATE' if key in heldout else 'DEVELOPMENT'
        records.append({**row, 'time_block_id': key, 'split': split,
                        'annotation_seed': identifier in seed_ids,
                        'pilot_role': roles.get(identifier, ''),
                        'helper_role': helper_roles.get(identifier, 'HELDOUT_TEST'),
                        'helper_validation_block': key in validation_groups,
                        'train_round1': helper_roles.get(identifier) == 'HELPER_TRAIN_INITIAL',
                        'train_round2': helper_roles.get(identifier) in {'HELPER_TRAIN_INITIAL', 'HELPER_TRAIN_BOOST'},
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
        'helper_train_validation': 'MEMBERSHIP_BOUND_GT_ACCEPTANCE_PENDING',
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
        'allocation_policy': {
            'primary': 'per_site_squared_image_count_error_normalized_by_site_target',
            'secondary_weights': {'camera': 0.05, 'diurnal_period': 0.1, 'group_count': 0.02},
            'overall_count_weight': 4,
            'candidate_search': 'one_metadata_balanced_subset_per_reachable_count_per_site_then_site_combination',
            'development_anchors': 'pilot_and_single_group_camera_blocks_then_smallest_hash_tied_block_per_uncovered_camera',
            'helper_validation': 'whole_blocks_exclude_pilot_preserve_all_seed_training_cameras_greedy_site_camera_day_coverage',
            'counts_are_targets': True,
        },
        'parent_membership_path': str(parent_path),
        'parent_membership_sha256': file_hash(parent_path),
        'parent_summary_sha256': file_hash(parent_path.parent / 'SUMMARY.json'),
        'outer_membership_changed_ids': sum(row['split'] != parent_by_id[row['candidate_id']]['split'] for row in records),
        'seed_membership_changed_ids': sum(str(row['annotation_seed']) != parent_by_id[row['candidate_id']]['annotation_seed'] for row in records),
        'helper_role_counts': Counter(helper_roles.values()),
        'helper_validation_groups': len(validation_groups),
        'validation_block_nonvalidation_images': sum(key in validation_groups for key in group_of.values())-60,
        'per_site': site_statistics(records, args.heldout_fraction),
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


def site_statistics(records, fraction):
    result = []
    for site in sorted({row['site'] for row in records}):
        rows = [row for row in records if row['site'] == site]
        test = [row for row in rows if row['split'] == 'HELDOUT_TEST_CANDIDATE']
        dev = [row for row in rows if row['split'] == 'DEVELOPMENT']
        result.append({
            'site': site, 'total': len(rows), 'development': len(dev), 'test': len(test),
            'target': len(rows)*fraction, 'test_fraction': len(test)/len(rows),
            'groups': len({row['time_block_id'] for row in rows}),
            'test_groups': len({row['time_block_id'] for row in test}),
            'cameras': len({camera(row) for row in rows}),
            'test_cameras': len({camera(row) for row in test}),
            'development_day_night': Counter(row.get('diurnal_period', 'unknown') for row in dev),
            'test_day_night': Counter(row.get('diurnal_period', 'unknown') for row in test),
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', required=True)
    parser.add_argument('--parent-pilot', required=True)
    parser.add_argument('--parent-membership', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--heldout-fraction', type=float, default=0.2)
    parser.add_argument('--seed-count', type=int, default=300)
    parser.add_argument('--seed', type=int, default=20261110)
    parser.add_argument('--guard-hours', type=float, default=4)
    parser.add_argument('--expected-count', type=int, default=2200)
    args = parser.parse_args()
    if not 0 < args.heldout_fraction < 1 or not 0 < args.guard_hours <= 24:
        parser.error('Heldout fraction must be between 0 and 1; time guard must be in (0,24]')
    if args.seed_count != 300:
        parser.error('This revision implements the accepted seed300 / validation60 / boost550 scope')
    result = prepare(args)
    print(json.dumps({k: result[k] for k in [
        'state', 'population', 'groups', 'split_counts', 'annotation_seed',
        'pilot_count', 'development_cameras', 'heldout_cameras', 'development_only_cameras',
    ]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
