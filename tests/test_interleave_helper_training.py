"""CPU subprocess fixtures for temporary pause and guaranteed normal cleanup."""
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1]/'scripts/interleave_helper_training.py'
SPEC = importlib.util.spec_from_file_location('interleave', SOURCE)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PauseResumeRequirements(unittest.TestCase):
    def test_resume_on_success_and_worker_failure(self):
        for success in [True, False]:
            with self.subTest(success=success), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                parents = [subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)']) for _ in range(2)]
                try:
                    output = root/'rgb'
                    bgr = root/'bgr'
                    bgr.mkdir()
                    dataset = root/'dataset'
                    dataset.mkdir()
                    Image.frombytes('L', (2, 2), bytes([1, 2, 3, 4])).save(dataset/'gt.png')
                    items = [{'sample_id': str(i), 'mask_path': 'gt.png'} for i in range(77)]
                    (dataset/'MANIFEST.json').write_text(json.dumps({'val': items}))
                    cm = [[77 if i==j and i>0 else 0 for j in range(5)] for i in range(5)]
                    metrics = {'per_class_iou': dict.fromkeys(['hair', 'face', 'upper', 'lower'], 1.),
                               'miou4': 1., 'confusion': cm}
                    for name in ['INITIAL_METRICS.json', 'METRICS.json']:
                        (bgr/name).write_text(json.dumps(metrics))
                    code = f'''from pathlib import Path
import json
p=Path({str(output)!r});p.mkdir()
(p/'STATUS.json').write_text(json.dumps({{'state':'COMPLETE','predictions':77}}))
for name in ['INITIAL_METRICS.json','METRICS.json']:
 (p/name).write_text({json.dumps(metrics)!r})
(p/'validation_predictions').mkdir()
for i in range(77):
 (p/'validation_predictions'/(str(i)+'.png')).write_bytes(Path({str(dataset/'gt.png')!r}).read_bytes())
'''
                    if not success:
                        code += '\nraise SystemExit(3)\n'
                    config = {'parent': dict(zip(['worker', 'controller'], [module.identity(p.pid) for p in parents])),
                              'command': [sys.executable, '-c', code], 'output': str(output),
                              'bgr_output': str(bgr), 'repository': str(root), 'input_sha256': {},
                              'dataset': str(dataset),
                              'physical_gpu': '0', 'min_free_vram_mib': 0, 'max_pause_seconds': 60,
                              'pause_settle_seconds': .1, 'health_interval_seconds': .05}
                    manifest = root/'manifest.json'
                    manifest.write_text(json.dumps(config))
                    original_handlers = {s: signal.getsignal(s) for s in [signal.SIGTERM, signal.SIGINT]}
                    try:
                        with mock.patch.object(sys, 'argv', ['interleave', str(manifest)]), \
                             mock.patch.object(module.subprocess, 'check_output', return_value='15000\n'):
                            if success:
                                module.main()
                            else:
                                with self.assertRaises(RuntimeError):
                                    module.main()
                    finally:
                        for sig, handler in original_handlers.items():
                            signal.signal(sig, handler)
                    self.assertEqual(json.loads((root/'RESUMED.json').read_text())['state'], 'RESUMED')
                    self.assertEqual((root/'REPORT_TH.md').exists(), success)
                    for parent in parents:
                        state = Path(f'/proc/{parent.pid}/stat').read_text().rsplit(') ', 1)[1].split()[0]
                        self.assertNotIn(state, ['T', 't'])
                finally:
                    for parent in parents:
                        parent.send_signal(signal.SIGCONT)
                        parent.terminate()
                        parent.wait(timeout=5)

    def test_pid_reuse_identity_rejected(self):
        entry = module.identity(__import__('os').getpid())
        entry['start_ticks'] = 'wrong'
        self.assertFalse(module.matches(entry))

    def test_watchdog_resumes_stopped_processes_if_supervisor_is_gone(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            parents = [subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)']) for _ in range(2)]
            try:
                config = {'parent': dict(zip(['worker', 'controller'], [module.identity(p.pid) for p in parents])),
                          'command': ['unused-command-for-fixture']}
                manifest = root/'manifest.json'
                manifest.write_text(json.dumps(config))
                dead = dict(config['parent']['worker'], start_ticks='gone')
                (root/'SUPERVISOR.json').write_text(json.dumps({'identity': dead, 'deadline_monotonic': 0}))
                for parent in parents:
                    parent.send_signal(signal.SIGSTOP)
                with mock.patch.object(sys, 'argv', ['interleave', str(manifest), '--watchdog']):
                    module.main()
                self.assertEqual(json.loads((root/'RESUMED.json').read_text())['state'], 'RESUMED')
            finally:
                for parent in parents:
                    parent.send_signal(signal.SIGCONT)
                    parent.terminate()
                    parent.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
