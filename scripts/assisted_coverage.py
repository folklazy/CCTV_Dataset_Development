"""Private CPU screening and human coverage recording; no model/GT acceptance.

Only source-bound measurements are automated. Visual assessments are append-only
operator declarations, collected during annotation review rather than invented by
statistics. Source images and historical coverage databases are never modified.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import csv
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import math
from pathlib import Path
import secrets
import sqlite3
import tempfile
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
VERSION = "assisted-coverage-1"
AXES = ('people', 'scale', 'occlusion', 'blur', 'lighting', 'view',
        'garments', 'color', 'source_artifacts', 'task_support')
TARGETS = ('Hair', 'Face', 'Upper', 'Lower')
STATES = {'observed', 'uncertain', 'unobservable', 'not_assessed'}


def now():
    return datetime.now(timezone.utc).isoformat()


def packed(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def regular(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink paths are not accepted')
    return path.resolve(strict=True)


def source_path(config, row):
    root = regular(config['image_root'])
    # The intake ledger paths are relative to the package, including images/.
    rel = Path(row['relative_path'])
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] != root.name:
        raise ValueError('Unsafe ledger path')
    path = regular(root.parent / rel)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Source path escapes image root')
    return path


def connect(run):
    db = sqlite3.connect(Path(run) / 'screening.sqlite3', timeout=15)
    db.row_factory = sqlite3.Row
    return db


@contextmanager
def lock(run, name):
    with (Path(run) / name).open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('Another process owns this run lock') from error
        yield


def atomic_json(path, obj):
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as f:
        temp = Path(f.name)
        f.write(packed(obj) + '\n')
        f.flush()
        import os
        os.fsync(f.fileno())
    temp.replace(path)


def verify_config(run):
    c = read_json(Path(run) / 'CONFIG.json')
    if c['schema'] != VERSION or c['source_sha256'] != sha(Path(__file__).read_bytes()):
        raise ValueError('Implementation binding changed; make an explicit child run')
    if c['ui_sha256'] != sha((REPO / 'scripts/assisted_coverage.html').read_bytes()):
        raise ValueError('UI binding changed; make an explicit child run')
    for key, value in c['pinned_files'].items():
        if sha(regular(key).read_bytes()) != value:
            raise ValueError('Pinned control file changed')
    return c


def initialize(binding_path, output):
    binding_path = regular(binding_path)
    b = read_json(binding_path)
    manifest = regular(b['manifest_path'])
    ledger = regular(b['file_ledger_path'])
    if sha(manifest.read_bytes()) != b['manifest_sha256'] or sha(ledger.read_bytes()) != b['file_ledger_sha256']:
        raise ValueError('Intake binding mismatch')
    with manifest.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    records = read_json(ledger)
    byid = {r['candidate_id']: r for r in records}
    if not rows or len(byid) != len(records) or len({r['candidate_id'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate population')
    if set(byid) != {r['candidate_id'] for r in rows}:
        raise ValueError('Ledger and manifest membership differ')
    if len({r['filename'] for r in rows}) != len(rows):
        raise ValueError('Duplicate filenames')
    root = regular(b['image_root'])
    output = Path(output).absolute()
    # No symlink ancestors, no nesting in source, intake evidence, or Git repo.
    for ancestor in (output, *output.parents):
        if ancestor.is_symlink():
            raise ValueError('Symlink output path')
    output = output.resolve()
    for p in (root.parent, binding_path.parent, REPO):
        if output.is_relative_to(p) or p.is_relative_to(output):
            raise ValueError('Source, evidence, repository and output must be disjoint')
    if output.exists():
        raise ValueError('Use a fresh run directory')
    config = {'schema': VERSION, 'created_at': now(), 'image_root': str(root),
              'source_sha256': sha(Path(__file__).read_bytes()),
              'ui_sha256': sha((REPO / 'scripts/assisted_coverage.html').read_bytes()),
              'pinned_files': {str(p): sha(p.read_bytes()) for p in (binding_path, manifest, ledger)},
              'expected': len(rows), 'inference_calls': 0, 'annotation_acceptance': False,
              'measurement': {'max_side': 256, 'gray': 'Pillow L', 'resample': 'BILINEAR',
                              'dark_pixel_lte': 32, 'bright_pixel_gte': 224,
                              'edge': 'FIND_EDGES mean excluding one-pixel border',
                              'thresholds_are_acceptance_rules': False},
              'review_policy': 'semantic coverage confirmed during human annotation review; no automatic acceptance'}
    prepared = []
    for r in rows:
        a = byid[r['candidate_id']]
        if a['filename'] != r['filename'] or a['md5'] != r['byte_md5'] or not a.get('verification'):
            raise ValueError('Manifest differs from accepted ledger')
        p = source_path(config, a)
        s = p.stat()
        prepared.append((r['candidate_id'], packed(r), packed(a), s.st_size, s.st_mtime_ns))
    output.mkdir(parents=True)
    atomic_json(output / 'CONFIG.json', config)
    with connect(output) as db:
        db.executescript('''
        CREATE TABLE inventory(id TEXT PRIMARY KEY, metadata TEXT, ledger TEXT, bytes INTEGER, mtime_ns INTEGER);
        CREATE TABLE measurements(id TEXT PRIMARY KEY, content TEXT NOT NULL);
        CREATE TABLE failures(id TEXT PRIMARY KEY, content TEXT NOT NULL);
        CREATE TABLE views(token TEXT PRIMARY KEY, id TEXT NOT NULL, byte_sha TEXT NOT NULL, at TEXT NOT NULL);
        CREATE TABLE reviews(seq INTEGER PRIMARY KEY, id TEXT NOT NULL, content TEXT NOT NULL, at TEXT NOT NULL);
        ''')
        db.executemany('INSERT INTO inventory VALUES(?,?,?,?,?)', prepared)
    return summary(output)


def measure(data, expected_size):
    from PIL import Image, ImageFilter, ImageStat
    with Image.open(io.BytesIO(data)) as im:
        if im.size != tuple(expected_size):
            raise ValueError('Geometry changed from intake ledger')
        im.load()
        gray = im.convert('L')
        gray.thumbnail((256, 256), Image.Resampling.BILINEAR)
    hist = gray.histogram()
    pixels = gray.width * gray.height
    edge = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edge.crop((1, 1, gray.width-1, gray.height-1))).mean[0] if min(gray.size) > 2 else None
    return {'luma_mean': ImageStat.Stat(gray).mean[0],
            'luma_std': ImageStat.Stat(gray).stddev[0],
            'dark_fraction': sum(hist[:33]) / pixels,
            'bright_fraction': sum(hist[224:]) / pixels,
            'edge_mean': edge_mean, 'analysis_size': list(gray.size),
            'evidence': 'CPU_MEASUREMENT_NOT_VISUAL_REVIEW',
            'semantic_targets': 'NOT_ASSESSED', 'measured_at': now()}


def analyze(run, limit=None):
    run = Path(run)
    with lock(run, '.analysis.lock'):
        c = verify_config(run)
        with connect(run) as db:
            for done in db.execute('SELECT i.ledger,m.content FROM inventory i JOIN measurements m ON i.id=m.id'):
                stat = source_path(c, json.loads(done['ledger'])).stat()
                if [stat.st_size, stat.st_mtime_ns] != json.loads(done['content'])['source_stat']:
                    raise ValueError('Completed source stat changed; explicit reconciliation required')
            pending = db.execute('SELECT * FROM inventory WHERE id NOT IN (SELECT id FROM measurements) AND id NOT IN (SELECT id FROM failures) ORDER BY id').fetchall()
            for i, row in enumerate(pending[:limit] if limit else pending):
                try:
                    a = json.loads(row['ledger'])
                    p = source_path(c, a)
                    data = p.read_bytes()
                    if sha(data) != a['sha256']:
                        raise ValueError('Source SHA256 changed from accepted intake')
                    result = measure(data, (a['width'], a['height']))
                    result['byte_sha256'] = a['sha256']
                    stat = p.stat()
                    result['source_stat'] = [stat.st_size, stat.st_mtime_ns]
                    with db:
                        db.execute('INSERT INTO measurements VALUES(?,?)', (row['id'], packed(result)))
                except Exception as error:
                    with db:
                        db.execute('INSERT INTO failures VALUES(?,?)', (row['id'], packed({'at': now(), 'type': type(error).__name__, 'message': str(error)})))
                    summary(run)
                    raise  # stop, preserve completed rows, no automatic retry
                if (i + 1) % 100 == 0:
                    summary(run)
                    print(packed({'new_measurements': i+1, 'at': now()}), flush=True)
        return summary(run)


def snapshot(run):
    with connect(run) as db:
        rows = [dict(r) for r in db.execute('SELECT * FROM inventory ORDER BY id')]
        measured = {r['id']: json.loads(r['content']) for r in db.execute('SELECT * FROM measurements')}
        reviews = {r['id']: json.loads(r['content']) for r in db.execute('SELECT * FROM reviews ORDER BY seq')}
    edge = sorted((m['edge_mean'], rid) for rid, m in measured.items() if m['edge_mean'] is not None)
    # Queue order only. Bottom decile is not a blur label or exclusion rule.
    edge_tail = {rid for _, rid in edge[:math.ceil(len(edge)*.1)]}
    items = []
    for row in rows:
        m = measured.get(row['id'])
        metadata = json.loads(row['metadata'])
        flags = []
        if m:
            if row['id'] in edge_tail:
                flags.append('low_edge_signal_queue_only')
            if m['dark_fraction'] >= .5:
                flags.append('mostly_dark_pixels_queue_only')
            if m['bright_fraction'] >= .5:
                flags.append('mostly_bright_pixels_queue_only')
        items.append({'id': row['id'], 'metadata': metadata, 'measurement': m,
                      'queue_hints': flags, 'review': reviews.get(row['id'])})
    return sorted(items, key=lambda x: (x['review'] is not None, -len(x['queue_hints']), x['id']))


def summary(run):
    c = read_json(Path(run) / 'CONFIG.json')
    with connect(run) as db:
        n = db.execute('SELECT COUNT(*) FROM measurements').fetchone()[0]
        failed = db.execute('SELECT COUNT(*) FROM failures').fetchone()[0]
        latest = {r['id']: json.loads(r['content']) for r in db.execute('SELECT * FROM reviews ORDER BY seq')}
        groups = Counter((json.loads(r['metadata']).get('site',''), json.loads(r['metadata']).get('camera_name','')) for r in db.execute('SELECT metadata FROM inventory'))
        metadata = [json.loads(r['metadata']) for r in db.execute('SELECT metadata FROM inventory')]
        measurements = [json.loads(r['content']) for r in db.execute('SELECT content FROM measurements')]
    complete = sum(all(v['state'] != 'not_assessed' for v in r['fields'].values()) for r in latest.values())
    result = {'schema': VERSION, 'updated_at': now(), 'expected': c['expected'],
              'cpu_measured': n, 'measurement_failures': failed, 'remaining_measurements': c['expected']-n-failed,
              'operator_coverage_records': len(latest), 'operator_coverage_complete': complete,
              'annotation_accepted': 0, 'inference_calls': 0,
              'site_camera_groups': len(groups),
              'status': 'MEASUREMENTS_COMPLETE_HUMAN_REVIEW_PENDING' if n == c['expected'] else 'MEASUREMENT_PARTIAL',
              'annotation_readiness': 'NOT_GRANTED_BY_THIS_TOOL'}
    atomic_json(Path(run) / 'STATUS.json', result)
    measured_stats = {}
    for key in ('luma_mean','luma_std','dark_fraction','bright_fraction','edge_mean'):
        values = sorted(x[key] for x in measurements if x[key] is not None)
        measured_stats[key] = {'n':len(values), 'min':values[0] if values else None,
                             'max':values[-1] if values else None,
                             'mean':sum(values)/len(values) if values else None}
    atomic_json(Path(run) / 'MEASUREMENT_SUMMARY_PRIVATE.json', {
        'updated_at': now(), 'counts': result, 'numeric_measurements': measured_stats,
        'site_camera_membership': [{'site':k[0],'camera':k[1],'n':v} for k,v in sorted(groups.items())],
        'metadata_only_time_bins':dict(Counter(r.get('time_bin','UNSPECIFIED') for r in metadata)),
        'observed_target_states':{k:dict(Counter(r['fields'][k]['state'] for r in latest.values())) for k in TARGETS},
        'unassessed_images_not_in_operator_ledger':c['expected']-len(latest),
        'caveat':'Measurements and clock bins are not semantic visual labels or annotation acceptance'})
    return result


def save_review(run, payload):
    config = verify_config(run)
    if not isinstance(payload, dict) or not isinstance(payload.get('actor'), str) or not payload['actor'].strip():
        raise ValueError('Named operator required')
    fields = payload.get('fields', {})
    if set(fields) != set(AXES + TARGETS):
        raise ValueError('All ten axes and four target slots required')
    for value in fields.values():
        if not isinstance(value, dict) or value.get('state') not in STATES or not isinstance(value.get('note'), str):
            raise ValueError('Invalid state/note')
        if value['state'] != 'not_assessed' and not value['note'].strip():
            raise ValueError('Every assessment needs a concrete observation/reason')
    with connect(run) as db:
        view = db.execute('SELECT * FROM views WHERE token=? AND id=?', (payload.get('view_token'), payload.get('id'))).fetchone()
        if view is None or payload.get('confirmed_image_loaded') is not True:
            raise ValueError('Load source image and explicitly confirm review first')
        row = db.execute('SELECT ledger FROM inventory WHERE id=?', (payload['id'],)).fetchone()
        ledger = json.loads(row['ledger'])
        if view['byte_sha'] != ledger['sha256'] or sha(source_path(config,ledger).read_bytes()) != ledger['sha256']:
            raise ValueError('Source changed after display; explicit reconciliation required')
        content = {'actor': payload['actor'].strip(), 'fields': fields,
                   'view_token': view['token'], 'byte_sha256': view['byte_sha'],
                   'evidence': 'OPERATOR_DECLARED_VISUAL_REVIEW', 'native_boundary_acceptance': False,
                   'annotation_accepted': False, 'recorded_at': now()}
        with db:
            db.execute('INSERT INTO reviews(id,content,at) VALUES(?,?,?)', (payload['id'], packed(content), now()))
    summary(run)
    return {'saved': True, 'annotation_accepted': False}


def serve(run, port):
    run = Path(run)
    c = verify_config(run)
    with lock(run, '.server.lock'):
        token = secrets.token_urlsafe(32)

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass  # don't log private filenames, images or access tokens

            def reply(self, data, kind='application/json', code=200):
                if kind == 'application/json':
                    data = packed(data).encode()
                self.send_response(code)
                self.send_header('Content-Type', kind)
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                route = urlsplit(self.path).path
                if route == '/':
                    return self.reply((REPO / 'scripts/assisted_coverage.html').read_bytes(), 'text/html; charset=utf-8')
                if self.headers.get('Authorization') != 'Bearer ' + token:
                    return self.reply({'error': 'Unauthorized'}, code=401)
                try:
                    if route == '/api/items':
                        return self.reply(snapshot(run))
                    if route == '/api/status':
                        return self.reply(summary(run))
                    if route.startswith('/api/image/'):
                        rid = route.removeprefix('/api/image/')
                        with connect(run) as db:
                            row = db.execute('SELECT ledger FROM inventory WHERE id=?', (rid,)).fetchone()
                            if row is None:
                                return self.reply({'error': 'Not found'}, code=404)
                            a = json.loads(row['ledger'])
                            data = source_path(c, a).read_bytes()
                            if sha(data) != a['sha256']:
                                raise ValueError('Source changed; review stopped')
                            view = secrets.token_urlsafe(20)
                            with db:
                                db.execute('INSERT INTO views VALUES(?,?,?,?)', (view,rid,a['sha256'],now()))
                        # Decode on raw original grid, strip EXIF to prevent browser autorotation.
                        from PIL import Image
                        with Image.open(io.BytesIO(data)) as im:
                            if im.size != (a['width'], a['height']):
                                raise ValueError('Source geometry changed')
                            image = im.convert('RGB')
                            buf = io.BytesIO()
                            image.save(buf, format='PNG')
                        return self.reply({'view_token': view, 'data_url': 'data:image/png;base64,' + __import__('base64').b64encode(buf.getvalue()).decode()})
                    return self.reply({'error': 'Not found'}, code=404)
                except Exception as error:
                    return self.reply({'error': str(error)}, code=400)

            def do_POST(self):
                if self.headers.get('Authorization') != 'Bearer ' + token:
                    return self.reply({'error': 'Unauthorized'}, code=401)
                if self.path != '/api/review':
                    return self.reply({'error': 'Not found'}, code=404)
                try:
                    size = int(self.headers.get('Content-Length', '0'))
                    if size <= 0 or size > 65536:
                        raise ValueError('Invalid request size')
                    result = save_review(run, json.loads(self.rfile.read(size)))
                    return self.reply(result)
                except Exception as error:
                    return self.reply({'error': str(error)}, code=400)

        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        url = f'http://127.0.0.1:{server.server_port}/#{token}'
        atomic_json(run / 'SERVER_PRIVATE.json', {'url': url, 'pid': __import__('os').getpid(), 'started_at': now(), 'bind': '127.0.0.1'})
        print('Private URL is in SERVER_PRIVATE.json (contains access token)', flush=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    init = subs.add_parser('init'); init.add_argument('--binding', required=True); init.add_argument('--output', required=True)
    for name in ('analyze', 'status', 'serve'):
        p = subs.add_parser(name); p.add_argument('--run', required=True)
        if name == 'analyze':
            p.add_argument('--limit', type=int)
        if name == 'serve':
            p.add_argument('--port', type=int, default=8041)
    args = parser.parse_args()
    if args.command == 'init':
        result = initialize(args.binding, args.output)
    elif args.command == 'analyze':
        result = analyze(args.run, args.limit)
    elif args.command == 'status':
        result = summary(args.run)
    else:
        return serve(args.run, args.port)
    print(packed(result))


if __name__ == '__main__':
    main()
