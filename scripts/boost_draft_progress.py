"""Read-only progress for the Boost550 annotation draft worker."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import time
from zoneinfo import ZoneInfo


def show(root):
    status = json.loads((root/'STATUS.json').read_text())
    pid = status.get('pid')
    alive = False
    if pid:
        try:
            os.kill(pid, 0)
            alive = True
        except ProcessLookupError:
            pass
    print(datetime.now(ZoneInfo('Asia/Bangkok')).isoformat(timespec='seconds'))
    print(f"Boost550 | {status['state']} | {status.get('completed', 0)}/550 images")
    print(f"PID {pid} | {'alive' if alive else 'exited/not found'} | latest {status.get('latest_image')}")
    print(f"Phase {status.get('phase', '-')} | editable files {root/'xanylabeling'}")
    if status.get('message'):
        print(status['message'])
    return status['state']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    while True:
        state = show(args.run_dir)
        if not args.watch or state in ['FAILED', 'DRAFTS_COMPLETE_REQUIRES_HUMAN_REVIEW']:
            return
        time.sleep(5)


if __name__ == '__main__':
    main()
