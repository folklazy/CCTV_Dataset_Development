"""Pause a resident helper, run one bounded training job, then resume it."""
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


def atomic_json(path, value):
    temp = path.with_suffix('.tmp')
    with temp.open('w') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def identity(pid):
    proc = Path('/proc')/str(pid)
    try:
        fields = (proc/'stat').read_text().rsplit(') ', 1)[1].split()
        return {'pid': pid, 'start_ticks': fields[19],
                'command_sha256': hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()}
    except FileNotFoundError:
        return None


def matches(entry):
    return identity(entry['pid']) == entry


def stamp(state, **values):
    return {'time_utc': datetime.now(timezone.utc).isoformat(), 'state': state, **values}


def stop_owned_rgb(config):
    expected = config['command']
    # Also covers a supervisor interruption between spawning and writing its PID.
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():
            continue
        try:
            args = [s.decode() for s in (proc/'cmdline').read_bytes().split(b'\0') if s]
            if args != expected:
                continue
            entry = identity(int(proc.name))
            if entry:
                os.kill(entry['pid'], signal.SIGTERM)
                deadline = time.monotonic()+30
                while matches(entry) and time.monotonic() < deadline:
                    time.sleep(.2)
                if matches(entry):
                    os.kill(entry['pid'], signal.SIGKILL)
        except (FileNotFoundError, ProcessLookupError):
            pass


def resume(root, config, reason):
    with (root/'resume.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (root/'RESUMED.json').exists():
            return
        stop_owned_rgb(config)
        resumed = []
        missing = []
        for name in ['worker', 'controller']:
            entry = config['parent'][name]
            if matches(entry):
                os.kill(entry['pid'], signal.SIGCONT)
                resumed.append(name)
            else:
                missing.append(name)
        atomic_json(root/'RESUMED.json', stamp('RESUMED' if not missing else 'RESUME_REQUIRES_REVIEW',
                                             reason=reason, resumed=resumed, identity_missing=missing))


def report(root, config):
    import numpy as np
    from PIL import Image
    new = Path(config['output'])
    dataset = Path(config['dataset'])
    items = json.loads((dataset/'MANIFEST.json').read_text())['val']
    expected = {item['sample_id']+'.png' for item in items}
    if {p.name for p in (new/'validation_predictions').glob('*.png')} != expected:
        raise ValueError('RGB validation prediction membership mismatch')
    cm = np.zeros((5, 5), dtype=np.int64)
    for item in items:
        truth = np.array(Image.open(dataset/item['mask_path']), dtype=np.int64)
        pred = np.array(Image.open(new/'validation_predictions'/(item['sample_id']+'.png')), dtype=np.int64)
        if pred.shape != truth.shape or not set(np.unique(pred)) <= {0, 1, 2, 3, 4}:
            raise ValueError('RGB saved-mask geometry or labels failed')
        valid = truth != 255
        np.add.at(cm, (truth[valid], pred[valid]), 1)
    if cm.tolist() != json.loads((new/'METRICS.json').read_text())['confusion']:
        raise ValueError('Independent RGB saved-mask confusion differs')
    atomic_json(root/'RGB_SAVED_MASK_AUDIT.json', {'state': 'PASS', 'predictions': len(items),
                                                 'confusion': cm.tolist(), 'method': 'np.add.at'})
    rows = []
    for name, path in [('BGR', Path(config['bgr_output'])), ('RGB', new)]:
        for stage, file in [('ก่อนฝึก CCTV', 'INITIAL_METRICS.json'), ('หลังฝึก CCTV', 'METRICS.json')]:
            values = json.loads((path/file).read_text())
            scores = [values['per_class_iou'][label]*100 for label in ['hair', 'face', 'upper', 'lower']]
            scores.append(values['miou4']*100)
            rows.append('| '+name+' | '+stage+' | '+' | '.join(f'{v:.2f}' for v in scores)+' |')
    text = '# ผล SOLIDER BGR และ RGB สำหรับ annotation helper\n\n'
    text += 'ประเมิน validation77personcrops จาก56ภาพ ใช้GTcropชุดเดิม เปรียบเทียบconfigurationของhelperที่ใช้groupedlogits คะแนนใช้วิเคราะห์ร่างประกอบกับภาระการแก้จริง\n\n'
    text += '| Recipe | ช่วง | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % |\n| --- | --- | --- | --- | --- | --- | --- |\n'
    text += '\n'.join(rows)+'\n\n'
    text += 'BGR parent '+str(config['bgr_output'])+'\n\nRGB output '+str(new)+'\n\n'
    selected = json.loads((new/'STATUS.json').read_text()).get('best_epoch')
    text += 'RGB selected best epoch '+str(selected)+'; epoch0หมายถึงเลือกinitialweightsก่อนอัปเดตtraining รวมไว้เป็นcandidateตามกติกาเดิม\n\n'
    text += 'ทั้งสองเริ่มจากpretrainedLIP20checkpointเดียวกัน ใช้25epochs/AMPbatch2/loss/learningrates/seedเดียวกัน Source revisionและresource residencyระบุในmanifest RGBใช้nativeSwinRGB; BGRเก็บเป็นcustomrecipe การฝึก/วัดร่วมกับprocessที่พักไว้ไม่ใช้จัดอันดับความเร็ว\n\n'
    text += 'Savedmasksอยู่validation_predictionsของแต่ละrun ส่วนcheckpoint/GT/source/input hashesอยู่BINDINGและSTATUS ข้อสรุปว่าตัวใดลดงานแก้ได้มากกว่าต้องดูdraftsจริง คะแนนนี้ยังไม่ใช่เวลาคนแก้ที่วัดแล้ว\n'
    (root/'REPORT_TH.md').write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--watchdog', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    if args.resume:
        resume(root, config, 'Manual controlled resume')
        return
    if args.watchdog:
        started = json.loads((root/'SUPERVISOR.json').read_text())
        while not (root/'RESUMED.json').exists():
            if not matches(started['identity']) or time.monotonic()>started['deadline_monotonic']:
                resume(root, config, 'Supervisor exited or pause deadline reached')
                return
            time.sleep(5)
        return

    def interrupted(signum, frame):
        raise InterruptedError(f'Supervisor received signal {signum}')

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    with (root/'supervisor.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for path, expected in config['input_sha256'].items():
            digest = hashlib.sha256()
            with open(path, 'rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''):
                    digest.update(block)
            if digest.hexdigest() != expected:
                raise ValueError(f'Input binding changed: {Path(path).name}')
        if not all(matches(entry) for entry in config['parent'].values()):
            raise RuntimeError('Parent process identity changed before pause')
        if Path(config['output']).exists():
            raise ValueError('RGB output already exists; reconcile before launching')
        atomic_json(root/'SUPERVISOR.json', {'identity': identity(os.getpid()),
                    'deadline_monotonic': time.monotonic()+config['max_pause_seconds']})
        with (root/'watchdog.log').open('xb') as log:
            watchdog = subprocess.Popen([sys.executable, __file__, str(args.manifest.resolve()), '--watchdog'],
                                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        atomic_json(root/'WATCHDOG.json', {'pid': watchdog.pid})
        child = None
        outcome = 'STOPPED'
        try:
            os.kill(config['parent']['controller']['pid'], signal.SIGSTOP)
            os.kill(config['parent']['worker']['pid'], signal.SIGSTOP)
            atomic_json(root/'PAUSED.json', stamp('SAM_PAUSED', parent=config['parent']))
            time.sleep(config.get('pause_settle_seconds', 2))
            for entry in config['parent'].values():
                state = Path(f'/proc/{entry["pid"]}/stat').read_text().rsplit(') ', 1)[1].split()[0]
                if state not in ['T', 't']:
                    raise RuntimeError('Parent process did not enter stopped state')
            free = int(subprocess.check_output(['nvidia-smi', '-i', config['physical_gpu'],
                '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).strip())
            if free < config['min_free_vram_mib']:
                raise RuntimeError('Free VRAM below the interleave admission guard')
            if shutil.disk_usage(root).free < 50*1024**3:
                raise RuntimeError('Free disk below 50 GiB')
            atomic_json(root/'STATUS.json', stamp('RGB_STARTING_SAM_PAUSED', free_vram_mib=free))
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=config['physical_gpu'])
            with (root/'solider.log').open('xb') as log:
                child = subprocess.Popen(config['command'], stdout=log, stderr=subprocess.STDOUT,
                                         env=env, cwd=config['repository'], start_new_session=True)
                atomic_json(root/'RGB_WORKER.json', identity(child.pid))
                atomic_json(root/'STATUS.json', stamp('RGB_TRAINING_SAM_PAUSED', worker_pid=child.pid))
                while child.poll() is None:
                    if (root/'RESUMED.json').exists():
                        raise RuntimeError('Pause watchdog resumed parent before RGB completion')
                    if time.monotonic()>json.loads((root/'SUPERVISOR.json').read_text())['deadline_monotonic']:
                        raise RuntimeError('Maximum pause budget reached')
                    if shutil.disk_usage(root).free < 50*1024**3:
                        raise RuntimeError('Free disk below 50 GiB')
                    size = sum(p.stat().st_size for p in Path(config['output']).rglob('*') if p.is_file())
                    if size > 80*1024**3:
                        raise RuntimeError('RGB output exceeds 80 GiB')
                    time.sleep(config.get('health_interval_seconds', 10))
                if child.returncode:
                    raise RuntimeError(f'RGB worker exited {child.returncode}')
            status = json.loads((Path(config['output'])/'STATUS.json').read_text())
            if status['state']!='COMPLETE' or status['predictions']!=77:
                raise RuntimeError('RGB completion contract failed')
            report(root, config)
            outcome = 'RGB_COMPLETE'
        except BaseException as error:
            atomic_json(root/'FAILURE.json', stamp('STOPPED', error_type=type(error).__name__, reason=str(error)))
            raise
        finally:
            try:
                if child and child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
            finally:
                resume(root, config, outcome)
                resumed = json.loads((root/'RESUMED.json').read_text())
                state = outcome+'_SAM_RESUMED' if resumed['state']=='RESUMED' else 'RESUME_REQUIRES_REVIEW'
                atomic_json(root/'STATUS.json', stamp(state, resume_record=str(root/'RESUMED.json')))
                try:
                    watchdog.wait(timeout=7)
                except subprocess.TimeoutExpired:
                    watchdog.terminate()
                    watchdog.wait(timeout=5)


if __name__ == '__main__':
    main()
