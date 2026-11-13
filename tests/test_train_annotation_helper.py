"""CPU requirement fixtures for the annotation-helper training revision."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace
import json
import sys
import random
import contextlib
import io
import math

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
    def test_class_weights_change_only_ce_and_preserve_void(self):
        logits = torch.zeros(1, 5, 1, 3)
        logits[0, 0, 0, 0] = math.log(4)
        target = torch.tensor([[[0, 1, 255]]])
        weights = torch.tensor([1., 3., 1., 1., 1.])
        expected_delta = (math.log(2)+3*math.log(5))/4-(math.log(2)+math.log(5))/2
        actual_delta = trainer.semantic_loss(logits, target, weights)-trainer.semantic_loss(logits, target)
        self.assertAlmostEqual(actual_delta.item(), expected_delta, places=6)
        changed = logits.clone()
        changed[:, :, :, 2] = 500
        torch.testing.assert_close(trainer.semantic_loss(logits, target, weights),
                                   trainer.semantic_loss(changed, target, weights))

    def test_dense_warmstart_strictly_loads_the_selected_full_model(self):
        def make_model():
            model = torch.nn.Linear(2, 2)
            model.config = SimpleNamespace(num_labels=5, id2label=dict(enumerate(trainer.CLASSES)))
            return model
        factory = SimpleNamespace(from_pretrained=lambda *args, **kwargs: make_model())
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'BEST.pt'
            selected = make_model()
            with torch.no_grad():
                selected.weight.fill_(.7)
                selected.bias.fill_(.1)
            torch.save({'model': 'b4', 'state_dict': selected.state_dict()}, path)
            args = SimpleNamespace(model='b4', checkpoint='local_fixture', warmstart=str(path))
            with mock.patch.dict(sys.modules, {'transformers': SimpleNamespace(SegformerForSemanticSegmentation=factory)}):
                helper = trainer.DenseHelper(args, torch.device('cpu'))
                for key, value in helper.model.state_dict().items():
                    torch.testing.assert_close(value, selected.state_dict()[key], rtol=0, atol=0)
                torch.save({'model': 'b5', 'state_dict': selected.state_dict()}, path)
                with self.assertRaisesRegex(ValueError, 'model identity mismatch'):
                    trainer.DenseHelper(args, torch.device('cpu'))

    def test_dense_resume_preserves_backbone_and_amp_scaler(self):
        class DenseModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = torch.nn.Linear(2, 2)
                self.head = torch.nn.Linear(2, 1)
            def forward(self, image):
                return self.head(self.backbone(image).tanh())
        def make_helper(scale):
            helper = SimpleNamespace(model=DenseModel(), kind='b5', device=torch.device('cpu'))
            optimizer = torch.optim.AdamW(helper.model.parameters(), lr=.01)
            schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 4)
            scaler = torch.amp.GradScaler('cpu', init_scale=scale, growth_interval=2)
            return helper, optimizer, schedule, scaler
        def update(helper, optimizer, schedule, scaler):
            optimizer.zero_grad(set_to_none=True)
            loss = (helper.model(torch.rand(1, 2))-torch.rand(1, 1)).square().mean()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            schedule.step()
        torch.manual_seed(42)
        helper, optimizer, schedule, scaler = make_helper(32.)
        for _ in range(2):
            update(helper, optimizer, schedule, scaler)
        best = {'epoch': 2, 'model': 'b5', 'state_dict': trainer.model_training_state(helper.model),
                'metrics': {'miou4': .5}}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'LAST.pt'
            trainer.save_training_state(path, helper, optimizer, schedule, 'dense', 2, {'epoch': 2}, best, scaler=scaler)
            for _ in range(2):
                update(helper, optimizer, schedule, scaler)
            expected = trainer.model_training_state(helper.model)
            resumed, new_optimizer, new_schedule, new_scaler = make_helper(1.)
            trainer.restore_training_state(path, resumed, new_optimizer, new_schedule, 'dense', scaler=new_scaler)
            self.assertEqual(new_scaler.get_scale(), 64.)
            for _ in range(2):
                update(resumed, new_optimizer, new_schedule, new_scaler)
            self.assertEqual(new_scaler.state_dict(), scaler.state_dict())
            for key, value in resumed.model.state_dict().items():
                torch.testing.assert_close(value, expected[key], rtol=0, atol=0)

    def test_normal_entry_resume_releases_lock_and_preserves_history(self):
        class TinyModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = torch.nn.Identity()
                self.head = torch.nn.Linear(1, 1)

        class TinyHelper:
            def __init__(self, args, device, cache, bindings):
                self.model, self.device = TinyModel(), torch.device('cpu')
            def optimizer(self, args):
                return torch.optim.AdamW(self.model.parameters(), lr=args.lr_head)
            def features(self, image, item):
                return {}
            def forward(self, features, label):
                value = self.model.head(torch.ones(1, 1)).reshape(1)
                return value[:, None, None].expand(1, 2, 2), value, value

        original_to = torch.Tensor.to
        def cpu_to(tensor, *args, **kwargs):
            if args and isinstance(args[0], torch.device) and args[0].type == 'cuda':
                args = (torch.device('cpu'), *args[1:])
            return original_to(tensor, *args, **kwargs)

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root/'data'
            data.mkdir()
            Image.new('RGB', (2, 2), (30, 80, 120)).save(data/'image.png')
            Image.new('L', (2, 2), 1).save(data/'mask.png')
            items = {split: [{'sample_id': split, 'img_path': 'image.png', 'mask_path': 'mask.png'}]
                     for split in ['train', 'val']}
            bindings = {'manifest_sha256': 'fixture', 'membership_sha256': 'fixture',
                        'files': {path.name: trainer.file_hash(path) for path in data.iterdir()}}
            checkpoint = root/'base.pt'
            checkpoint.write_bytes(b'base fixture')
            arguments = ['trainer', '--model', 'sam31', '--dataset', str(data),
                         '--membership', str(root/'membership.csv'), '--checkpoint', str(checkpoint),
                         '--output', str(root/'output'), '--weights-directory', str(root/'weights'),
                         '--repository-root', str(root/'source'), '--epochs', '2',
                         '--batch-size', '1', '--save-training-state']
            with mock.patch.object(trainer, 'PromptHelper', TinyHelper), \
                 mock.patch.object(trainer, 'bind_data', return_value=(items, bindings)), \
                 mock.patch.object(torch.Tensor, 'to', cpu_to), \
                 mock.patch.object(torch.cuda, 'set_device'), \
                 mock.patch.object(torch.cuda, 'reset_peak_memory_stats'), \
                 mock.patch.object(torch.cuda, 'max_memory_allocated', return_value=0), \
                 contextlib.redirect_stdout(io.StringIO()):
                with mock.patch.object(sys, 'argv', arguments), \
                     mock.patch.object(trainer, 'guard', side_effect=[None, None, InterruptedError('fixture')]):
                    with self.assertRaises(InterruptedError):
                        trainer.main()
                saved = torch.load(root/'weights/LAST.pt', map_location='cpu', weights_only=True)
                self.assertEqual(saved['epoch_completed'], 1)
                previous_history = (root/'output/HISTORY.jsonl').read_text()
                with mock.patch.object(sys, 'argv', arguments+['--resume-training']), \
                     mock.patch.object(trainer, 'guard'):
                    trainer.main()
            history = [json.loads(line) for line in (root/'output/HISTORY.jsonl').read_text().splitlines()]
            self.assertEqual([row['epoch'] for row in history], [1, 2])
            self.assertTrue((root/'output/HISTORY.jsonl').read_text().startswith(previous_history))
            self.assertEqual(json.loads((root/'output/STATUS.json').read_text())['state'], 'COMPLETE')
            attempts = [json.loads(line) for line in (root/'output/ATTEMPTS.jsonl').read_text().splitlines()]
            self.assertEqual([(row['resume'], row['first_epoch']) for row in attempts], [(False, 1), (True, 2)])

    def test_sam_full_state_resume_matches_uninterrupted_cpu_updates(self):
        def make_helper():
            helper = SimpleNamespace(model=torch.nn.Linear(2, 1), device=torch.device('cpu'))
            optimizer = torch.optim.AdamW(helper.model.parameters(), lr=.01)
            schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 4)
            return helper, optimizer, schedule

        def update(helper, optimizer, schedule):
            image = torch.rand(1, 2)
            target = torch.tensor([[random.random()+float(np.random.random())]])
            optimizer.zero_grad(set_to_none=True)
            (helper.model(image)-target).square().mean().backward()
            optimizer.step()
            schedule.step()

        random.seed(13)
        np.random.seed(13)
        torch.manual_seed(13)
        original, optimizer, schedule = make_helper()
        for _ in range(2):
            update(original, optimizer, schedule)
        best = {'epoch': 1, 'model': 'sam31', 'state_dict': trainer.model_training_state(original.model),
                'metrics': {'miou4': .5}}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'LAST.pt'
            trainer.save_training_state(path, original, optimizer, schedule, 'bound', 2,
                                             {'epoch': 2}, best)
            for _ in range(2):
                update(original, optimizer, schedule)
            expected = trainer.model_training_state(original.model)
            expected_next = (random.random(), np.random.random(), torch.rand(1))
            resumed, new_optimizer, new_schedule = make_helper()
            state = trainer.restore_training_state(path, resumed, new_optimizer, new_schedule, 'bound')
            self.assertEqual(state['epoch_completed'], 2)
            self.assertEqual(new_schedule.last_epoch, 2)
            for _ in range(2):
                update(resumed, new_optimizer, new_schedule)
            for key, value in resumed.model.state_dict().items():
                torch.testing.assert_close(value, expected[key], rtol=0, atol=0)
            self.assertEqual(random.random(), expected_next[0])
            self.assertEqual(np.random.random(), expected_next[1])
            torch.testing.assert_close(torch.rand(1), expected_next[2], rtol=0, atol=0)
            with self.assertRaisesRegex(ValueError, 'binding mismatch'):
                trainer.restore_training_state(path, resumed, new_optimizer, new_schedule, 'changed')
            state['state_dict'] = {}
            torch.save(state, path)
            with self.assertRaisesRegex(ValueError, 'decoder keys mismatch'):
                trainer.restore_training_state(path, resumed, new_optimizer, new_schedule, 'bound')

    def test_epoch_commit_reconciles_once_and_rejects_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'HISTORY.jsonl'
            trainer.append_epoch_record(path, {'epoch': 1, 'loss': .7})
            trainer.append_epoch_record(path, {'epoch': 1, 'loss': .7})
            self.assertEqual(len(path.read_text().splitlines()), 1)
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                trainer.append_epoch_record(path, {'epoch': 1, 'loss': .5})
            with self.assertRaisesRegex(ValueError, 'out of order'):
                trainer.append_epoch_record(path, {'epoch': 3, 'loss': .5})

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

    def test_sam_helper_uses_single_joint_score_policy(self):
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
