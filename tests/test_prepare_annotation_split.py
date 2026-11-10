"""Independent small cases for annotation time-block separation."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_annotation_split import allocate, time_groups, helper_partitions


def observation(identifier, site, camera, when, image_hash):
    return {'candidate_id': identifier, 'site': site, 'camera_name': camera,
            'incident_timestamp': when, 'dhash_hex': format(image_hash, '064x'),
            'pixel_sha256': identifier}


class TimeBlockTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            observation('a', 'S', 'C', '2026-01-01 23:00:00.000 +0700', 0),
            observation('b', 'S', 'C', '2026-01-02 01:00:00.000 +0700', 2**128-1),
            observation('c', 'S', 'D', '2026-01-02 12:00:00.000 +0700', 2**256-1),
            observation('d', 'S', 'C', '2026-01-04 12:00:00.000 +0700', int('aa'*32, 16)),
            observation('e', 'S', 'C', '2026-01-05 12:00:00.000 +0700', int('55'*32, 16)),
            observation('f', 'T', 'SINGLE', '2026-01-06 12:00:00.000 +0700', int('cc'*32, 16)),
        ]

    def test_day_and_cross_midnight_blocks(self):
        groups = time_groups(self.rows, 4)
        actual = {frozenset(r['candidate_id'] for r in g) for g in groups.values()}
        self.assertEqual(actual, {frozenset('abc'), frozenset('d'), frozenset('e'), frozenset('f')})

    def test_pilot_and_single_group_camera_stay_in_development(self):
        heldout, locked, _ = allocate(time_groups(self.rows, 4), {'a'}, .3, 42)
        self.assertTrue(heldout)
        self.assertTrue(heldout <= {'d', 'e'})
        self.assertTrue({'a', 'f'} <= locked)

    def test_allocation_is_independent_of_iteration_order(self):
        groups = time_groups(self.rows, 4)
        self.assertEqual(allocate(groups, {'a'}, .3, 42),
                         allocate(dict(reversed(list(groups.items()))), {'a'}, .3, 42))

    def test_near_duplicate_cross_site_is_linked(self):
        self.rows.append(observation('z', 'OTHER', 'OTHER',
                                     '2026-02-01 12:00:00.000 +0700', int('aa'*32, 16)^1))
        groups = time_groups(self.rows, 4)
        self.assertIn(frozenset({'d', 'z'}),
                      {frozenset(r['candidate_id'] for r in g) for g in groups.values()})

    def test_impossible_same_camera_holdout_stops(self):
        with self.assertRaises(ValueError):
            allocate(time_groups(self.rows, 4), set('adef'), .3, 42)

    def test_invalid_hash_encoding_stops(self):
        self.rows[0]['dhash_hex'] = 'abc'
        with self.assertRaises(ValueError):
            time_groups(self.rows, 4)

    def test_site_targets_take_priority_over_large_camera_blocks(self):
        groups = {}
        for site in ['A', 'B']:
            for index in range(10):
                key = f'{site}-{index}'
                groups[key] = [dict(candidate_id=f'{key}-{n}', site=site,
                                    camera_name=site, diurnal_period='day')
                               for n in range(10)]
        heldout, _, target = allocate(groups, set(), .2, 42)
        self.assertEqual(target, 40)
        for site in ['A', 'B']:
            self.assertEqual(sum(len(groups[key]) for key in heldout if key.startswith(site)), 20)

    def test_linked_cross_site_block_requests_review(self):
        groups = {'mixed': [dict(site='A', camera_name='C', candidate_id='a'),
                            dict(site='B', camera_name='C', candidate_id='b')]}
        with self.assertRaisesRegex(ValueError, 'Cross-site'):
            allocate(groups, set(), .2, 42)

    def test_helper_validation_siblings_cannot_enter_boost(self):
        rows, groups = [], {}
        for index in range(1500):
            row = dict(candidate_id=str(index), site='A', camera_name=str(index % 10),
                       diurnal_period='day' if index % 3 == 0 else 'night')
            key = str(index-300 if 300 <= index < 600 else index)
            groups.setdefault(key, []).append(row)
            rows.append(row)
        seed = {str(n) for n in range(300)}
        pilot = {str(n) for n in range(24)}
        roles, validation_groups = helper_partitions(rows, seed, pilot, groups, 42)
        self.assertEqual(sum(v == 'HELPER_TRAIN_INITIAL' for v in roles.values()), 240)
        self.assertEqual(sum(v == 'HELPER_VALIDATION_FIXED' for v in roles.values()), 60)
        self.assertEqual(sum(v == 'HELPER_TRAIN_BOOST' for v in roles.values()), 550)
        self.assertTrue(all(roles[key] == 'HELPER_TRAIN_INITIAL' for key in pilot))
        for key in validation_groups:
            self.assertEqual({roles[row['candidate_id']] for row in groups[key]},
                             {'HELPER_VALIDATION_FIXED', 'DEVELOPMENT_AFTER_FREEZE'})


if __name__ == '__main__':
    unittest.main()
