"""Read-only file checks and checkpointed visual-review assets; never annotation."""
import argparse
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import random
import sqlite3
import struct
import threading
import zipfile

from audit_package import SplitArchive
from workspace_paths import load_dataset_review_scope


def now():
    return datetime.now(timezone.utc).isoformat()


def context(config_path, run):
    config, manifest = load_dataset_review_scope(config_path)
    run = Path(run).resolve(strict=True)
    if (not run.is_relative_to(Path(config['work_root']))
            or run != Path(config['dataset_review_scope']['manifest_path']).parent):
        raise ValueError('Run must own the approved private review manifest')
    db = sqlite3.connect(run / 'review.sqlite3')
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS files (
      record_id TEXT PRIMARY KEY, member TEXT, metadata_json TEXT NOT NULL,
      decode_status TEXT DEFAULT 'NOT_CHECKED', byte_sha TEXT, pixel_sha TEXT,
      width INTEGER, height INTEGER, mode TEXT, orientation INTEGER, cache_path TEXT,
      thumbnail_path TEXT, crc_verified INTEGER, error TEXT, checked_at TEXT,
      representative_id TEXT, dhash TEXT);
    CREATE TABLE IF NOT EXISTS sheets (
      sheet_id TEXT PRIMARY KEY, path TEXT, sha256 TEXT, records_json TEXT,
      created_at TEXT, viewed_at TEXT, notes_json TEXT);
    CREATE TABLE IF NOT EXISTS observations (
      observation_id INTEGER PRIMARY KEY, record_id TEXT, level TEXT,
      observed_json TEXT, inference_json TEXT, needs_review_json TEXT,
      evidence_ref TEXT, actor TEXT, recorded_at TEXT);
    ''')
    db.execute('CREATE INDEX IF NOT EXISTS files_pixel_sha_idx ON files(pixel_sha)')
    db.execute('CREATE INDEX IF NOT EXISTS files_byte_sha_idx ON files(byte_sha)')
    db.executemany('INSERT OR IGNORE INTO files(record_id,member,metadata_json) VALUES(?,?,?)',
                   [(r['record_id'], r['archive_member'], json.dumps(r['metadata'], ensure_ascii=False))
                    for r in manifest['records']])
    db.commit()
    return config, manifest, run, db


def write_once(path, data):
    try:
        with path.open('xb') as handle:
            handle.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError('Cached artifact differs; never overwrite it')


def check_files(config, manifest, run, db, workers=2):
    from PIL import Image, ImageOps
    (run / 'payloads').mkdir(exist_ok=True)
    (run / 'thumbnails').mkdir(exist_ok=True)
    local = threading.local()
    handles = []
    lock = threading.Lock()
    parts = [Path(config['dataset_root']) / p['name'] for p in manifest['archive_parts']]
    todo = db.execute("SELECT record_id,member FROM files WHERE decode_status IN ('NOT_CHECKED','CACHE_ERROR') ORDER BY record_id").fetchall()
    if todo:
        with (run / 'FILE_CHECK_ATTEMPTS.jsonl').open('a') as handle:
            for rid, _ in todo:
                previous = db.execute('SELECT decode_status,error,checked_at FROM files WHERE record_id=?', (rid,)).fetchone()
                handle.write(json.dumps({'record_id': rid, 'attempt_started_at': now(),
                                         'previous_status': previous[0], 'previous_error': previous[1],
                                         'previous_checked_at': previous[2]})+'\n')

    def process(row):
        rid, member = row
        result = dict(record_id=rid, decode_status='UNREADABLE', byte_sha=None, pixel_sha=None,
                      width=None, height=None, mode=None, orientation=None, cache_path=None,
                      thumbnail_path=None, crc_verified=0, error=None, checked_at=now(), dhash=None)
        try:
            if not member:
                raise ValueError('Metadata has no unique archive member')
            if not hasattr(local, 'archive'):
                stream = SplitArchive(parts)
                local.archive = zipfile.ZipFile(stream)
                with lock:
                    handles.append((local.archive, stream))
            data = local.archive.read(member)  # ZipFile checks payload CRC while reading.
            result['crc_verified'] = 1
            result['byte_sha'] = hashlib.sha256(data).hexdigest()
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                result.update(width=image.width, height=image.height, mode=image.mode,
                              orientation=image.getexif().get(274))
                rgba = image.convert('RGBA')
                prefix = b'RGBA_encoded_orientation_v1\0' + struct.pack('<II', *image.size)
                result['pixel_sha'] = hashlib.sha256(prefix + rgba.tobytes()).hexdigest()
                suffix = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}.get(image.format, 'image')
                cache = run / 'payloads' / (result['byte_sha'] + '.' + suffix)
                with lock:
                    write_once(cache, data)
                result['cache_path'] = str(cache.relative_to(run))
                thumb = ImageOps.pad(image.convert('RGB'), (480, 270), color=(20, 20, 20), method=Image.Resampling.LANCZOS)
                target = run / 'thumbnails' / (result['byte_sha'] + '.jpg')
                output = io.BytesIO()
                thumb.save(output, format='JPEG', quality=90)
                with lock:
                    write_once(target, output.getvalue())
                result['thumbnail_path'] = str(target.relative_to(run))
                gray = image.convert('L').resize((9, 8), Image.Resampling.BILINEAR)
                values = list(gray.get_flattened_data()) if hasattr(gray, 'get_flattened_data') else list(gray.getdata())
                bits = [values[y*9+x] > values[y*9+x+1] for y in range(8) for x in range(8)]
                result['dhash'] = f'{sum(int(b) << i for i,b in enumerate(bits)):016x}'
            result['decode_status'] = 'READABLE'
        except Exception as error:
            if result['pixel_sha'] is not None:
                result['decode_status'] = 'CACHE_ERROR'
            result['error'] = type(error).__name__ + ': ' + str(error)
        return result

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for index, result in enumerate(pool.map(process, todo), 1):
                fields = [k for k in result if k != 'record_id']
                db.execute('UPDATE files SET '+','.join(k+'=?' for k in fields)+' WHERE record_id=?',
                           [result[k] for k in fields]+[result['record_id']])
                if index % 25 == 0:
                    db.commit()
                if index % 250 == 0 or index == len(todo):
                    db.commit()
                    print(json.dumps({'file_checks_this_invocation': index, 'remaining_this_invocation': len(todo)-index}), flush=True)
    finally:
        db.commit()
        for archive, stream in handles:
            archive.close()
            stream.close()
    db.execute('''UPDATE files SET representative_id=(SELECT MIN(f.record_id) FROM files f
                WHERE f.pixel_sha=files.pixel_sha AND f.decode_status='READABLE')
                WHERE decode_status='READABLE' ''')
    db.commit()
    status(run, db)


def make_sheets(run, db, limit, seed):
    from PIL import Image, ImageDraw
    if db.execute("SELECT COUNT(*) FROM files WHERE decode_status IN ('NOT_CHECKED','CACHE_ERROR')").fetchone()[0]:
        raise ValueError('Complete file checks before freezing the reproducible sheet order')
    records = db.execute("SELECT record_id,thumbnail_path,metadata_json FROM files WHERE record_id=representative_id ORDER BY record_id").fetchall()
    grouped = defaultdict(list)
    for rid, path, raw in records:
        m = json.loads(raw)
        grouped[(m['site'], m['camera_name'], m['incident_timestamp'][:7], m['category'])].append((rid, path))
    rng = random.Random(seed)
    queues = []
    for key in sorted(grouped):
        rng.shuffle(grouped[key])
        queues.append(deque(grouped[key]))
    order = []
    while any(queues):
        for queue in queues:
            if queue:
                order.append(queue.popleft())
    # Refuse to mix seeds or a changed inventory into previously generated sheets.
    plan = {'method': 'seeded_within_strata_round_robin_v1', 'seed': seed,
            'tile_count': 16, 'ordered_record_ids': [rid for rid, _ in order]}
    write_once(run / 'sheet_plan.json', (json.dumps(plan, sort_keys=True)+'\n').encode())
    folder = run / 'sheets'
    folder.mkdir(exist_ok=True)
    for start in range(0, len(order), 16):
        number = start // 16 + 1
        if limit and number > limit:
            break
        sid = f'S{number:04d}'
        if db.execute('SELECT 1 FROM sheets WHERE sheet_id=?', (sid,)).fetchone():
            continue
        batch = order[start:start+16]
        sheet = Image.new('RGB', (1920, 1210), (30, 30, 30))
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 8), f'{sid} | OVERVIEW ONLY / NOT GT | 16 or fewer unique decoded-pixel representatives', fill='white')
        for i, (rid, path) in enumerate(batch):
            x, y = (i % 4)*480, 38+(i//4)*293
            draw.text((x+7, y), rid, fill=(255, 230, 30))
            with Image.open(run / path) as image:
                sheet.paste(image, (x, y+21))
        path = folder / (sid+'.jpg')
        data = io.BytesIO()
        sheet.save(data, format='JPEG', quality=94)
        write_once(path, data.getvalue())
        db.execute('INSERT INTO sheets VALUES(?,?,?,?,?,?,?)',
                   (sid, str(path.relative_to(run)), hashlib.sha256(data.getvalue()).hexdigest(),
                    json.dumps([r[0] for r in batch]), now(), None, None))
    db.commit()
    status(run, db)


def status(run, db):
    counts = dict(db.execute('SELECT decode_status,COUNT(*) FROM files GROUP BY decode_status').fetchall())
    report = {'recorded_at_utc': now(), 'file_status': counts,
              'byte_unique': db.execute("SELECT COUNT(DISTINCT byte_sha) FROM files WHERE decode_status='READABLE'").fetchone()[0],
              'byte_unique_accessible_payloads': db.execute('SELECT COUNT(DISTINCT byte_sha) FROM files').fetchone()[0],
              'pixel_unique': db.execute("SELECT COUNT(DISTINCT pixel_sha) FROM files WHERE decode_status='READABLE'").fetchone()[0],
              'sheets_generated': db.execute('SELECT COUNT(*) FROM sheets').fetchone()[0],
              'sheets_recorded_reviewed': db.execute('SELECT COUNT(*) FROM sheets WHERE viewed_at IS NOT NULL AND notes_json IS NOT NULL').fetchone()[0],
              'representatives_with_current_observations': db.execute('SELECT COUNT(DISTINCT record_id) FROM observations').fetchone()[0],
              'generated_is_not_reviewed': True, 'annotation_performed': False, 'models_run': False}
    report['byte_unique_strict_readable_payloads'] = report['byte_unique']
    current = db.execute('''SELECT DISTINCT f.pixel_sha,o.level FROM observations o
                         JOIN files f ON f.record_id=o.record_id WHERE f.pixel_sha IS NOT NULL''').fetchall()
    current_hashes = {h for h, _ in current}
    detail_hashes = {h for h, level in current if level == 'DETAIL_NATIVE'}
    prior_hashes = set()
    prior_path = run / 'PRIOR_VISUAL_RECONCILIATION_PRIVATE.json'
    if prior_path.is_file():
        prior = json.loads(prior_path.read_text())
        for item in prior['linked_records']:
            row = db.execute('SELECT pixel_sha FROM files WHERE record_id=?', (item['current_record_id'],)).fetchone()
            if item['sha256_matches_previous_open'] and row and row[0]:
                prior_hashes.add(row[0])
    covered = current_hashes | prior_hashes
    report.update(current_reviewed_unique_pixels=len(current_hashes),
                  current_native_detail_unique_pixels=len(detail_hashes),
                  previous_detail_unique_pixels=len(prior_hashes),
                  combined_reviewed_unique_pixels=len(covered),
                  combined_detail_unique_pixels=len(detail_hashes | prior_hashes),
                  readable_unique_pixels_not_reviewed=report['pixel_unique']-len(covered),
                  all_readable_unique_pixels_reviewed=bool(report['pixel_unique'])
                  and not counts.get('NOT_CHECKED', 0) and not counts.get('CACHE_ERROR', 0)
                  and len(covered)==report['pixel_unique'])
    (run / 'CHECKPOINT.json').write_text(json.dumps(report, indent=2)+'\n')
    with (run / 'CHECKPOINT_HISTORY.jsonl').open('a') as handle:
        handle.write(json.dumps(report)+'\n')
    print(json.dumps(report), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('command', choices=['check-files', 'make-sheets', 'status', 'next-batch'])
    parser.add_argument('--workers', type=int, choices=[1, 2, 3, 4], default=2)
    parser.add_argument('--limit-sheets', type=int, default=0)
    parser.add_argument('--seed', type=int, default=20261027)
    parser.add_argument('--batch-sheets', type=int, default=4)
    args = parser.parse_args()
    config, manifest, run, db = context(args.config, args.run)
    try:
        if args.command == 'check-files':
            check_files(config, manifest, run, db, args.workers)
        elif args.command == 'make-sheets':
            make_sheets(run, db, args.limit_sheets, args.seed)
        elif args.command == 'next-batch':
            if not 1 <= args.batch_sheets <= 16:
                raise ValueError('Use one to sixteen review sheets per request')
            rows = db.execute('''SELECT sheet_id,path,records_json,viewed_at FROM sheets
                              WHERE notes_json IS NULL ORDER BY sheet_id LIMIT ?''', (args.batch_sheets,)).fetchall()
            print(json.dumps({'stage': 'READY_TO_DISPLAY_NOT_REVIEWED', 'sheets': [
                {'sheet_id': sid, 'path': str(run/path), 'record_ids': json.loads(records),
                 'previous_display_at': viewed} for sid,path,records,viewed in rows]}, indent=2))
        else:
            status(run, db)
    finally:
        db.close()


if __name__ == '__main__':
    main()
