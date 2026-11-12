"""Read-only progress viewer for a sequential helper-training run."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import time
from zoneinfo import ZoneInfo


def read_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def render(root):
    config = read_json(root/'BATCH_MANIFEST.json')
    if not config:
        raise ValueError('BATCH_MANIFEST.json is missing from the selected run')
    batch = read_json(root/'STATUS.json')
    lines = [datetime.now(ZoneInfo('Asia/Bangkok')).isoformat(timespec='seconds'),
             f'Run {root.name} | Batch {batch.get("state", "PENDING")}']
    for job in config['jobs']:
        output = Path(job['output'])
        status = read_json(output/'STATUS.json')
        state = status.get('state', 'PENDING')
        description = state
        if state == 'COMPLETE':
            if 'epochs' in status:
                description += f' | epochs {status["epochs"]}'
            description += f' | saved predictions {status["predictions"]}'
        elif state == 'EVALUATING':
            description += f' | crops {status["completed"]}/{status["expected"]}'
        elif state == 'LOADING':
            initial = (output/'INITIAL_METRICS.json').exists()
            if initial:
                description = 'INITIAL_EVALUATION_COMPLETE / FIRST_TRAINING_STEPS'
            elif (output/'features').exists():
                description = 'INITIAL_EVALUATION_AND_FEATURE_CACHE'
            if job['model'] == 'sam31':
                command = job['command']
                dataset = Path(command[command.index('--dataset')+1])
                manifest = read_json(dataset/'MANIFEST.json')
                cached = {p.stem for p in (output/'features').glob('*.pt')}
                counts = []
                for split in ['val', 'train']:
                    expected = {item['sample_id'] for item in manifest[split]}
                    counts.append(f'{split} feature cache {len(cached & expected)}/{len(expected)}')
                description += ' | '+ ' | '.join(counts)
                description += ' | training counter is written every 20 crops'
        elif state in ['TRAINING', 'RUNNING']:
            description += f' | epoch {status.get("epoch", status.get("epoch_completed"))}/{status["epochs"]}'
            if 'batches_completed' in status:
                description += f' | batches {status["batches_completed"]}/{status["batches_expected"]}'
            if 'crops_completed' in status:
                description += f' | crops {status["crops_completed"]}/{status["crops_expected"]}'
        elif state == 'FAILED':
            description += f' | {status.get("error_type")}: {status.get("message")}'
        pid = status.get('pid')
        if pid and state not in ['COMPLETE', 'FAILED']:
            proc = Path(f'/proc/{pid}')
            live = proc.exists()
            if live:
                try:
                    process_state = (proc/'stat').read_text().rsplit(') ', 1)[1].split()[0]
                    if process_state in ['T', 't']:
                        description = 'PAUSED_IN_MEMORY | '+description
                except FileNotFoundError:
                    live = False
            description += f' | PID {pid} '+('alive' if live else 'exited; inspect controller/log')
        lines.append(f'{job["model"]}: {description}')
    if batch.get('state') == 'STOPPED':
        lines.append(f'Stop reason: {batch.get("reason")}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, default=Path.cwd())
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    try:
        while True:
            if args.watch:
                print('\033[2J\033[H', end='')
            print(render(args.run_dir.resolve()), flush=True)
            if not args.watch:
                return
            time.sleep(2)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
