"""Canonical envelopes, lossless CSV siblings and a validated file inventory."""
import csv
import hashlib
import io
import json
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = {'schema_version', 'source', 'fetched_at', 'run_url', 'code_sha', 'data'}
DERIVED = {'input_hashes', 'method_version', 'generated_at'}
SOURCE = {'id', 'url', 'revision', 'licence', 'fetched_at', 'history_url'}
ROW = {'id', 'source_ref', 'observed_at'}
FIELDS = {
    'polls': ROW | set('fieldwork_start fieldwork_end pollster sample shares scale reference_urls revision history'.split()),
    'averages': ROW | set('date window_start window_end coherent shares scale denominator descriptive poll_ids excluded_ids exclusions missing rounding_policy'.split()),
    'seats': ROW | set('average_id available reason assumptions entitlements list_members seats overhang vacancies occupied_house majority assumed_house assumed_majority capacity_checked quotients unresolved_ties'.split()),
    'status': ROW | set('dataset state last_attempt_at last_success_at last_good_run_url error_code message'.split()),
    'manifest': ROW | set('path format sha256 bytes row_count licences observation_start observation_end fetched_at producing_run_url input_hashes'.split()),
    'build-manifest': ROW | set('code_sha data_sha build_run_url built_at data_available'.split()),
}
STEMS = {'polls', 'averages', 'seats', 'status', 'manifest'}
ALLOWED = {s + ext for s in STEMS for ext in ('.json', '.csv')} | {'LICENCES.md'}
META = ['schema_version', 'source_json', 'fetched_at', 'run_url', 'code_sha',
        'input_hashes_json', 'method_version', 'generated_at']


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def envelope(data, sources, run_url, code_sha, *, inputs=None, method=None, generated=None):
    result = dict(schema_version=1, source=sources, fetched_at=max((s['fetched_at'] for s in sources), default=None),
                  run_url=run_url, code_sha=code_sha, data=data)
    if inputs is not None:
        result.update(input_hashes=inputs, method_version=method, generated_at=generated)
    return result


def rows(env):
    return env['data'] if isinstance(env['data'], list) else [env['data']]


def validate_envelope(env, stem):
    if set(env) not in (BASE, BASE | DERIVED) or type(env['schema_version']) is not int or env['schema_version'] != 1:
        raise ValueError('INVALID_ENVELOPE')
    for source in env['source']:
        if set(source) != SOURCE:
            raise ValueError('INVALID_SOURCE')
    if env['fetched_at'] != max((s['fetched_at'] for s in env['source']), default=None):
        raise ValueError('INVALID_ACQUISITION')
    if stem in {'averages', 'seats'} and not DERIVED <= env.keys():
        raise ValueError('MISSING_DERIVATION')
    def exact(value):
        if isinstance(value, float):
            raise ValueError('INEXACT_NUMBER')
        if isinstance(value, dict):
            for v in value.values():
                exact(v)
        if isinstance(value, list):
            for v in value:
                exact(v)
    exact(env)
    seen = set()
    for row in rows(env):
        if set(row) != FIELDS[stem] or row['id'] in seen or not isinstance(row['source_ref'], list):
            raise ValueError('INVALID_ROW: ' + stem)
        seen.add(row['id'])
        if stem == 'polls':
            if type(row['scale']) is not int or row['scale'] < 1 or str(row['scale']).strip('0') != '1':
                raise ValueError('INVALID_POLL_SCALE')
            start, end = date.fromisoformat(row['fieldwork_start']), date.fromisoformat(row['fieldwork_end'])
            if start > end or row['observed_at'] != row['fieldwork_end']:
                raise ValueError('INVALID_FIELDWORK')
            if row['sample'] is not None and (type(row['sample']) is not int or row['sample'] < 1):
                raise ValueError('INVALID_SAMPLE')
            for value in row['shares'].values():
                if value is not None and (type(value) is not int or not 0 <= value <= 100 * row['scale']):
                    raise ValueError('INVALID_SHARE')
        if stem == 'status':
            if row['state'] not in {'fresh', 'stale', 'unavailable'}:
                raise ValueError('INVALID_STATUS')
            datetime.fromisoformat(row['last_attempt_at'].replace('Z', '+00:00'))
            if (row['state'] == 'unavailable') != (row['last_success_at'] is None):
                raise ValueError('INVALID_STATUS_SUCCESS')
    return env


def csv_bytes(env):
    payload = rows(env)
    keys = sorted({key for row in payload for key in row})
    nested = {key for key in keys if any(isinstance(r.get(key), (list, dict)) for r in payload)}
    columns = [key + '_json' if key in nested else key for key in keys]
    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(META + columns)
    meta = [canonical(env.get(k[:-5])) if k.endswith('_json') else scalar(env.get(k)) for k in META]
    for row in payload:
        writer.writerow(meta + [canonical(row.get(k)) if k in nested else scalar(row.get(k)) for k in keys])
    return out.getvalue().encode()


def scalar(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def pair(root, stem, env):
    validate_envelope(env, stem)
    (root / (stem + '.json')).write_text(canonical(env) + '\n')
    (root / (stem + '.csv')).write_bytes(csv_bytes(env))


def inventory(root, run_url, code_sha, now):
    entries = []
    for path in sorted(root.iterdir()):
        if path.name.startswith('manifest.'):
            continue
        if path.name not in ALLOWED or path.is_symlink() or not path.is_file():
            raise ValueError('UNSAFE_DATA_PATH')
        stem = path.stem
        env = json.loads((root / (stem + '.json')).read_text()) if path.suffix in {'.json', '.csv'} else None
        data = rows(env) if env else []
        observations = [r['observed_at'] for r in data]
        entries.append(dict(id=path.name, source_ref=env['source'] if env else [], observed_at=now,
                            path=path.name, format=path.suffix[1:], sha256=digest(path.read_bytes()),
                            bytes=path.stat().st_size, row_count=len(data),
                            licences=sorted({s['licence'] for s in env['source']}) if env else ['See LICENCES.md'],
                            observation_start=min(observations, default=None), observation_end=max(observations, default=None),
                            fetched_at=env['fetched_at'] if env else None,
                            producing_run_url=env['run_url'] if env else run_url, input_hashes=env.get('input_hashes', {}) if env else {}))
    for name in ('manifest.json', 'manifest.csv'):
        entries.append(dict(id=name, source_ref=[{'reason': 'self-reference excluded'}], observed_at=now,
                            path=name, format=name.split('.')[1], sha256=None, bytes=None,
                            row_count=len(entries) + (2 if name.endswith('json') else 1), licences=[],
                            observation_start=None, observation_end=None, fetched_at=None,
                            producing_run_url=run_url, input_hashes={}))
    pair(root, 'manifest', envelope(entries, [], run_url, code_sha))


def validate_bundle(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('UNSAFE_DATA_PATH')
    files = {p.name for p in root.iterdir()}
    if files - ALLOWED or not {'manifest.json', 'manifest.csv', 'status.json', 'status.csv', 'LICENCES.md'} <= files:
        raise ValueError('INVALID_INVENTORY')
    for path in root.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ValueError('UNSAFE_DATA_PATH')
    envs = {}
    for path in root.glob('*.json'):
        env = validate_envelope(json.loads(path.read_text()), path.stem)
        if (root / (path.stem + '.csv')).read_bytes() != csv_bytes(env):
            raise ValueError('CSV_MISMATCH')
        envs[path.stem] = env
    entries = envs['manifest']['data']
    if {e['path'] for e in entries} != files or len(entries) != len(files):
        raise ValueError('INVALID_INVENTORY')
    for entry in entries:
        name = entry['path']
        if name not in ALLOWED:
            raise ValueError('UNSAFE_DATA_PATH')
        if name.startswith('manifest.'):
            if entry['sha256'] is not None or entry['bytes'] is not None:
                raise ValueError('RECURSIVE_MANIFEST')
        else:
            raw = (root / name).read_bytes()
            if digest(raw) != entry['sha256'] or len(raw) != entry['bytes']:
                raise ValueError('DATA_HASH_MISMATCH')
            if Path(name).suffix in {'.json', '.csv'}:
                env = envs[Path(name).stem]
                payload = rows(env)
                observations = [r['observed_at'] for r in payload]
                if (entry['row_count'] != len(payload)
                        or entry['licences'] != sorted({s['licence'] for s in env['source']})
                        or entry['fetched_at'] != env['fetched_at']
                        or entry['producing_run_url'] != env['run_url']
                        or entry['input_hashes'] != env.get('input_hashes', {})
                        or entry['observation_start'] != min(observations, default=None)
                        or entry['observation_end'] != max(observations, default=None)):
                    raise ValueError('INVENTORY_METADATA_MISMATCH')
    present = {'polls', 'averages', 'seats'} & envs.keys()
    if present and present != {'polls', 'averages', 'seats'}:
        raise ValueError('PARTIAL_POLL_BUNDLE')
    if present:
        from .average import trend
        from .seats import project
        polls = envs['polls']['data']
        averages = envs['averages']['data']
        if not polls or not averages:
            raise ValueError('EMPTY_SUCCESS')
        dates = [date.fromisoformat(a['date']) for a in averages]
        if dates[0] != min(date.fromisoformat(p['fieldwork_end']) for p in polls) or any(
                right - left != timedelta(days=1) for left, right in zip(dates, dates[1:])):
            raise ValueError('INCOMPLETE_DAILY_SERIES')
        # Recompute from the exported rows, not rounded display strings.
        from .refresh import config
        expected = trend(polls, [a['date'] for a in averages], config('party-map'), config('poll-review'))
        if expected != averages or project(averages[-1]) != envs['seats']['data']:
            raise ValueError('DERIVATION_MISMATCH')
        for stem, deps in [('averages', ['polls.json']), ('seats', ['averages.json'])]:
            hashes = envs[stem]['input_hashes']
            if any(hashes.get(dep) != digest((root / dep).read_bytes()) for dep in deps):
                raise ValueError('INPUT_HASH_MISMATCH')
    return envs
