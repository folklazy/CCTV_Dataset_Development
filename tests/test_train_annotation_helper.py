"""CPU requirement fixtures for the annotation-helper training revision."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace
import json
import sys

import numpy as np
from PIL import Image
import torch

SOURCE = Path(__file__).resolve().parents[1]/'scripts/train_annotation_helper.py'
SPEC = importlib.util.spec_from_file_location('helper_training', SOURCE)
trainer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trainer)
BATCH_SPEC = importlib.util.spec_from_file_location('helper_batch', SOURCE.with_name('run_helper_training_batch.py'))
batch = importlib.util.module_from_spec(BATCH_SPEC)
BATCH_SPEC.loader.exec_module(batch)


class TrainingRequirements(unittest.TestCase):
    def test_absent_prompt_supervises_false_positive_and_scores(self):
        masks = torch.ones(3, 2, 2, requires_grad=True)
        scores = torch.ones(3, requires_grad=True)
        presence = torch.ones(1, requires_grad=True)
        loss = trainer.prompt_loss(masks, scores, presence,
                                   torch.zeros(2, 2, dtype=torch.bool),
                                   torch.ones(2, 2, dtype=torch.bool))
        loss.backward()
        self.assertGreater(loss.item(), 0)
        for value in (masks, scores, presence):
            self.assertTrue(torch.all(value.grad > 0))

    def test_present_prompt_supervises_selected_and_rejected_queries(self):
        masks = torch.zeros(3, 2, 2, requires_grad=True)
        scores = torch.zeros(3, requires_grad=True)
        presence = torch.zeros(1, requires_grad=True)
        target = torch.tensor([[True, False], [False, False]])
        trainer.prompt_loss(masks, scores, presence, target, torch.ones_like(target)).backward()
        self.assertLess(scores.grad[0].item(), 0)
        self.assertTrue(torch.all(scores.grad[1:] > 0))
        self.assertLess(presence.grad.item(), 0)
        self.assertLess(masks.grad[0, 0, 0].item(), 0)

    def test_void_changes_neither_dense_nor_prompt_loss(self):
        truth = torch.tensor([[[1, 255], [0, 2]]])
        logits = torch.zeros(1, 5, 2, 2)
        changed = logits.clone()
        changed[:, :, 0, 1] = 500
        torch.testing.assert_close(trainer.semantic_loss(logits, truth),
                                   trainer.semantic_loss(changed, truth))
        target, valid = truth[0] == 1, truth[0] != 255
        masks = torch.zeros(3, 2, 2)
        changed_masks = masks.clone()
        changed_masks[:, 0, 1] = 500
        scores, presence = torch.zeros(3), torch.zeros(1)
        torch.testing.assert_close(trainer.prompt_loss(masks, scores, presence, target, valid),
                                   trainer.prompt_loss(changed_masks, scores, presence, target, valid))

    def test_all_void_is_differentiable_finite_zero(self):
        logits = torch.zeros(1, 5, 2, 2, requires_grad=True)
        loss = trainer.semantic_loss(logits, torch.full((1, 2, 2), 255))
        loss.backward()
        self.assertEqual(loss.item(), 0)
        self.assertEqual(logits.grad.abs().sum().item(), 0)
        masks = torch.zeros(3, 2, 2, requires_grad=True)
        scores = torch.zeros(3, requires_grad=True)
        presence = torch.zeros(1, requires_grad=True)
        loss = trainer.prompt_loss(masks, scores, presence, torch.ones(2, 2, dtype=torch.bool),
                                   torch.zeros(2, 2, dtype=torch.bool))
        loss.backward()
        self.assertEqual(loss.item(), 0)

    def test_native_projection_is_exhaustive_probability_union(self):
        ids = [label for group in trainer.LIP_GROUPS for label in group]
        self.assertEqual(sorted(ids), list(range(20)))
        logits = torch.zeros(1, 20, 1, 1)
        probability = trainer.project_lip(logits).softmax(1).flatten()
        torch.testing.assert_close(probability, torch.tensor([14, 1, 1, 2, 2])/20)

    def test_solider_swin_receives_native_rgb_normalization(self):
        class Capture(torch.nn.Module):
            def forward(self, image):
                self.received = image
                return [[torch.zeros(1, 20, 2, 2)], []]
        helper = trainer.DenseHelper.__new__(trainer.DenseHelper)
        helper.kind, helper.device = 'solider', torch.device('cpu')
        helper.model = Capture()
        helper.input_space = 'RGB'
        helper.mean, helper.std = [.485, .456, .406], [.229, .224, .225]
        image = torch.tensor([.9, .5, .1]).reshape(1, 3, 1, 1)
        output = helper.logits(image)
        expected = (torch.tensor([.9, .5, .1])-torch.tensor(helper.mean))/torch.tensor(helper.std)
        torch.testing.assert_close(helper.model.received[0, :, 100, 100], expected)
        self.assertEqual(output.shape, (1, 5, 576, 384))

    def test_global_confusion_counts_absent_false_positives(self):
        class Samples:
            items = [{'sample_id': 'synthetic'}]
            def __len__(self):
                return 1
            def __getitem__(self, index):
                return torch.zeros(3, 2, 2), torch.tensor([[1, 0], [2, 255]]), index
        class Model:
            def eval(self):
                return self
        def logits(image):
            predicted = torch.tensor([[[1, 1], [0, 4]]])
            return torch.nn.functional.one_hot(predicted, 5).permute(0, 3, 1, 2).float()
        helper = SimpleNamespace(model=Model(), device='cpu', logits=logits)
        with tempfile.TemporaryDirectory() as folder:
            report = trainer.evaluate(helper, Samples(), Path(folder))
            self.assertEqual(report['confusion'], [[0, 1, 0, 0, 0], [0, 1, 0, 0, 0],
                                                  [1, 0, 0, 0, 0], [0]*5, [0]*5])
            self.assertEqual(report['per_class_iou']['hair'], .5)
            self.assertEqual(report['per_class_iou']['face'], 0)
            self.assertIsNone(report['per_class_iou']['upper'])
            self.assertEqual(report['miou4'], .25)
            self.assertEqual(np.asarray(Image.open(Path(folder)/'synthetic.png'))[0, 1], 1)

    def test_paths_cannot_escape_dataset(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                trainer.source_file(Path(folder), '../secret')

    def test_sam_joint_score_is_not_multiplied_by_presence_twice(self):
        class Samples:
            items = [{'sample_id': 'synthetic'}]
            def __len__(self):
                return 1
            def __getitem__(self, index):
                return torch.zeros(3, 2, 2), torch.ones(2, 2, dtype=torch.long), index
        helper = trainer.PromptHelper.__new__(trainer.PromptHelper)
        helper.model = torch.nn.Identity()
        helper.features = lambda image, item: {}
        def forward(features, label):
            joint_score = torch.logit(torch.tensor([.3 if label==1 else .01]))
            return torch.full((1, 2, 2), 10.), joint_score, torch.tensor([-10.])
        helper.forward = forward
        report = trainer.evaluate(helper, Samples())
        self.assertEqual(report['per_class_iou']['hair'], 1.)

    def test_controller_runs_sequentially_and_stops_after_failure(self):
        for first_succeeds in (True, False):
            with self.subTest(first_succeeds=first_succeeds), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                jobs = []
                for index in range(2):
                    output = root/str(index)
                    body = ('from pathlib import Path; import json; '
                            f'p=Path({str(output)!r}); p.mkdir(); '
                            '(p/"STATUS.json").write_text(json.dumps({"state":"COMPLETE"})); '
                            '(p/"METRICS.json").write_text("{}")')
                    if index==0 and not first_succeeds:
                        body = 'raise SystemExit(3)'
                    jobs.append({'model': str(index), 'output': str(output),
                                 'input_sha256': {}, 'command': [sys.executable, '-c', body]})
                config = {'jobs': jobs, 'lock_path': str(root/'lock'), 'repository': str(root),
                          'physical_gpu': '0', 'min_free_gib': 0, 'min_free_vram_mib': 0,
                          'max_hours_per_model': 1, 'max_output_gib_per_model': 1,
                          'health_interval_seconds': .01}
                manifest = root/'manifest.json'
                manifest.write_text(json.dumps(config))
                with mock.patch.object(sys, 'argv', ['batch', str(manifest)]), \
                     mock.patch.object(batch.subprocess, 'check_output', return_value='15000\n'):
                    if first_succeeds:
                        batch.main()
                    else:
                        with self.assertRaises(RuntimeError):
                            batch.main()
                status = json.loads((root/'STATUS.json').read_text())
                self.assertEqual(status['state'], 'COMPLETE' if first_succeeds else 'STOPPED')
                self.assertEqual((root/'1').exists(), first_succeeds)


if __name__ == '__main__':
    unittest.main()
