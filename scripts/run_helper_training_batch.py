"""Run a bounded, sequential annotation-helper batch from a private manifest."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    status_path = root/'STATUS.json'
    history_path = root/'BATCH_EVENTS.jsonl'
    child = None

    def event(state, **details):
        record = {'time_utc': datetime.now(timezone.utc).isoformat(),
                  'state': state, 'controller_pid': os.getpid(), **details}
        with history_path.open('a') as stream:
            stream.write(json.dumps(record, allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
        write_json(status_path, record)

    def terminate(signum, frame):
        raise InterruptedError(f'Controller received signal {signum}')

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    lock_path = Path(config['lock_path'])
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        event('STARTING', order=[job['model'] for job in config['jobs']])
        try:
            for job in config['jobs']:
                for path, expected in job['input_sha256'].items():
                    if sha256(path) != expected:
                        raise RuntimeError(f'Launch binding changed: {Path(path).name}')
                if shutil.disk_usage(root).free < config['min_free_gib']*1024**3:
                    raise RuntimeError('Free disk guard failed before launch')
                query = subprocess.check_output([
                    'nvidia-smi', '-i', config['physical_gpu'],
                    '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True)
                required_vram = job.get('min_free_vram_mib', config['min_free_vram_mib'])
                if int(query.strip()) < required_vram:
                    raise RuntimeError('GPU free-memory admission failed before launch')
                output = Path(job['output'])
                if output.exists():
                    raise RuntimeError('Attempt output already exists; reconcile before a new attempt')
                env = dict(os.environ)
                env['CUDA_VISIBLE_DEVICES'] = config['physical_gpu']
                with (root/(job['model']+'.log')).open('xb') as log:
                    child = subprocess.Popen(job['command'], stdout=log, stderr=subprocess.STDOUT,
                                             cwd=config['repository'], env=env, start_new_session=True)
                    event(config.get('execution_state', 'TRAINING'), model=job['model'], worker_pid=child.pid,
                          output=str(output), command=job['command'])
                    started = time.monotonic()
                    while child.poll() is None:
                        elapsed = time.monotonic()-started
                        if elapsed > config['max_hours_per_model']*3600:
                            raise RuntimeError('Per-model execution time cap exceeded')
                        if shutil.disk_usage(root).free < config['min_free_gib']*1024**3:
                            raise RuntimeError('Free disk guard failed during training')
                        size = sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
                        if size > config['max_output_gib_per_model']*1024**3:
                            raise RuntimeError('Per-model output cap exceeded')
                        time.sleep(config['health_interval_seconds'])
                    if child.returncode:
                        raise RuntimeError(f'{job["model"]} worker exited {child.returncode}')
                    result = json.loads((output/'STATUS.json').read_text())
                    if result['state'] != 'COMPLETE':
                        raise RuntimeError('Worker exit without COMPLETE artifact')
                    event('MODEL_COMPLETE', model=job['model'], output=str(output),
                          metrics_sha256=sha256(output/'METRICS.json'))
                    child = None
            event('COMPLETE', models=[job['model'] for job in config['jobs']],
                  next_action='Inspect saved validation drafts and correction burden before choosing helper')
        except BaseException as error:
            if child and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            event('STOPPED', error_type=type(error).__name__, reason=str(error),
                  retry_count=0, next_action='Inspect failure evidence; preserve previous completed models')
            raise


if __name__ == '__main__':
    main()
