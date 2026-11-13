"""Timing scope, aggregation and live-encoder contract fixtures without a GPU."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
from PIL import Image
import torch

SOURCE = Path(__file__).resolve().parents[1]/'scripts/benchmark_helper_inference.py'
SPEC = importlib.util.spec_from_file_location('helper_timing', SOURCE)
timing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(timing)


class InferenceTimingRequirements(unittest.TestCase):
    def test_summary_uses_all_measured_roi_calls(self):
        result = timing.summarize([{'total_ms': value} for value in [10., 20., 90.]])
        self.assertEqual(result, {'mean_ms_per_roi': 40., 'median_ms_per_roi': 20.,
                                  'total_measured_ms': 120., 'measured_calls': 3})
        for values in [[], [{'total_ms': 0}], [{'total_ms': float('nan')}]]:
            with self.assertRaises(ValueError):
                timing.summarize(values)

    def test_total_contains_input_parser_and_readback_with_sync(self):
        helper = SimpleNamespace(device=torch.device('cpu'))
        helper.logits = lambda image: torch.tensor([0., 2., 0., 0., 0.]).reshape(1, 5, 1, 1).expand(1, 5, 2, 2)
        ticks = iter([0., .002, .007, .008])
        syncs = []
        prediction, record = timing.timed_prediction(helper, 'b4', Image.new('RGB', (2, 2)),
                                                      synchronize=lambda: syncs.append(True),
                                                      clock=lambda: next(ticks))
        np.testing.assert_array_equal(prediction, np.ones((2, 2), dtype=np.uint8))
        self.assertEqual(len(syncs), 4)
        self.assertEqual(record['input_prepare_h2d_ms'], 2.)
        self.assertEqual(record['parser_route_ms'], 5.)
        self.assertEqual(record['cpu_readback_ms'], 1.)
        self.assertEqual(record['total_ms'], 8.)

    def test_sam_recomputes_rgb_encoder_and_composes_four_prompts(self):
        class Backbone:
            def forward_image(self, image):
                self.received = image
                return {'vision_features': image, 'backbone_fpn': [image], 'vision_pos_enc': [image]}
        backbone = Backbone()
        labels = []
        def forward(features, label):
            labels.append(label)
            score = torch.logit(torch.tensor([.9 if label == 1 else .1]))
            return torch.full((1, 2, 2), 10.), score, torch.zeros(1)
        helper = SimpleNamespace(device=torch.device('cpu'), model=SimpleNamespace(backbone=backbone), forward=forward)
        prediction, _ = timing.timed_prediction(helper, 'sam31', Image.new('RGB', (2, 2), (0, 128, 255)),
                                                synchronize=lambda: None)
        self.assertEqual(labels, [1, 2, 3, 4])
        self.assertEqual(backbone.received.shape, (1, 3, 1008, 1008))
        torch.testing.assert_close(backbone.received[0, :, 0, 0],
                                   (torch.tensor([0., 128/255., 1.])-.5)/.5)
        np.testing.assert_array_equal(prediction, np.ones((2, 2), dtype=np.uint8))


if __name__ == '__main__':
    unittest.main()
