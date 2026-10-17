"""Canonical envelopes, lossless CSV siblings and a validated file inventory."""
import csv
import hashlib
import io
import json
import re
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
GEO = {'general-2025', 'maori-2025'}
FAMILIES = {'polls': {'polls', 'averages', 'seats'}, 'geography': GEO | {'electorates'}}
FIELDS['electorates'] = ROW | set('name kind slug stats_id search_key baseline_ids boundary_note mapping_status'.split())
for stem in GEO:
    FIELDS[stem] = ROW | {'name', 'kind'}
NEW_FIELDS = {
    'candidates': 'person_id name party_id electorate_id list_rank wikidata_id wikipedia_url join_status conflict_ids field_sources',
    'party-lists': 'party_id candidate_ids complete review_ref field_sources',
    'candidate-review': 'person_id electorate_id field claims resolution review_ref',
    'baseline-2023': 'old_electorate_id old_name election_date result_as_of party_votes candidate_votes field_sources',
    'enrolment': 'electorate_id as_of enrolled eligible roll_basis field_sources',
    'electorate-polls': 'electorate_id poll_id pollster fieldwork_start fieldwork_end sample measure shares scale reference_urls boundary_basis',
}
for stem, fields in NEW_FIELDS.items():
    FIELDS[stem] = ROW | set(fields.split())
FAMILIES.update({'candidates': {'candidates', 'party-lists', 'candidate-review'},
                 **{s: {s} for s in ('baseline-2023', 'enrolment', 'electorate-polls')}})
FAMILIES['social'] = {'social/daily', 'social/credits'}
FIELDS['social/daily'] = ROW | set('day sample party_counts attitude topic_counts model_versions question_version provenance probability_sums'.split())
FIELDS['social/credits'] = ROW | set('day reserved spent cap requests allocation closed'.split())
DATE_OBSERVATIONS = {'polls', 'averages', 'seats', 'baseline-2023', 'enrolment'}
STEMS = {'social/daily', 'social/credits'} | set(NEW_FIELDS) | GEO | {'electorates', 'polls', 'averages', 'seats', 'status', 'manifest'}
ALLOWED = {s + ext for s in STEMS for ext in ('.json', '.csv')} | {'LICENCES.md'}
META = ['schema_version', 'source_json', 'fetched_at', 'run_url', 'code_sha',
        'input_hashes_json', 'method_version', 'generated_at']
INSTANT_FIELDS = {'fetched_at', 'generated_at', 'last_attempt_at', 'last_success_at', 'built_at', 'captured_at'}
DATE_FIELDS = {'fieldwork_start', 'fieldwork_end', 'date', 'window_start', 'window_end', 'election_date', 'result_as_of', 'as_of'}
DATE_PATTERN = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'


def timestamp(value, field='timestamp', *, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not re.fullmatch(DATE_PATTERN + r'T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', value):
        raise ValueError('INVALID_TIMESTAMP: ' + field)
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('INVALID_TIMESTAMP: ' + field) from None
    return value


def calendar_date(value, field):
    if not isinstance(value, str) or not re.fullmatch(DATE_PATTERN, value):
        raise ValueError('INVALID_DATE: ' + field)
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError('INVALID_DATE: ' + field) from None


def validate_times(value, path='envelope', *, nullable_dates=False):
    # Source references and retained history can also contain acquisition metadata.
    if isinstance(value, dict):
        for key, item in value.items():
            field = path + '.' + key
            if key in INSTANT_FIELDS:
                timestamp(item, field, nullable=key in {'fetched_at', 'last_success_at'})
            elif key in DATE_FIELDS:
                if item is not None or not nullable_dates:
                    calendar_date(item, field)
            elif key in {'observed_at', 'observation_start', 'observation_end'}:
                if isinstance(item, str) and re.fullmatch(DATE_PATTERN, item):
                    calendar_date(item, field)
                else:
                    timestamp(item, field, nullable=key != 'observed_at' or nullable_dates)
            validate_times(item, field, nullable_dates=nullable_dates)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_times(item, f'{path}[{index}]', nullable_dates=nullable_dates)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def envelope(data, sources, run_url, code_sha, *, inputs=None, method=None, generated=None):
    for source in sources:
        timestamp(source['fetched_at'], 'source.fetched_at')
    result = dict(schema_version=1, source=sources, fetched_at=max((s['fetched_at'] for s in sources), default=None),
                  run_url=run_url, code_sha=code_sha, data=data)
    if inputs is not None:
        result.update(input_hashes=inputs, method_version=method, generated_at=generated)
    validate_times(result, nullable_dates=method in {"enrolment-v1", "electorate-polls-v1"})
    return result


def rows(env):
    return env['data'] if isinstance(env['data'], list) else [env['data']]


def validate_envelope(env, stem):
    extra = {'type', 'features'} if stem in GEO else set()
    if set(env) not in (BASE | extra, BASE | DERIVED | extra) or type(env['schema_version']) is not int or env['schema_version'] != 1:
        raise ValueError('INVALID_ENVELOPE')
    validate_times(env, nullable_dates=env.get("method_version") in {"enrolment-v1", "electorate-polls-v1"})
    for source in env['source']:
        if set(source) != SOURCE:
            raise ValueError('INVALID_SOURCE')
        timestamp(source['fetched_at'], 'source.fetched_at')
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
    exact({k: v for k, v in env.items() if k != 'features'} if stem in GEO else env)
    if stem in GEO:
        from .geography import validate
        validate(env, stem.split('-')[0])
        prop = 'GED2025_V1_00' if stem.startswith('general') else 'MED2025_V1_00'
        if {r['id'] for r in env['data']} != {f.get('id') for f in env['features']}:
            raise ValueError('BOUNDARY_ID_MISMATCH')
        for feature in env['features']:
            exact({k: v for k, v in feature.items() if k != 'geometry'})
            exact({k: v for k, v in feature['geometry'].items() if k != 'coordinates'})
            row = next(r for r in env['data'] if r['id'] == feature['id'])
            if row['name'] != feature['properties'][prop + '_NAME'] or row['kind'] != stem.split('-')[0]:
                raise ValueError('BOUNDARY_METADATA_MISMATCH')
            if feature['id'] != 'stats-nz-2025-' + feature['properties'][prop]:
                raise ValueError('BOUNDARY_ID_MISMATCH')
    seen = set()
    for row in rows(env):
        if set(row) != FIELDS[stem] or row['id'] in seen or not isinstance(row['source_ref'], list):
            raise ValueError('INVALID_ROW: ' + stem)
        seen.add(row['id'])
        if stem in DATE_OBSERVATIONS:
            if stem == 'enrolment' and row['observed_at'] is None:
                pass
            else:
                calendar_date(row['observed_at'], stem + '.observed_at')
        elif stem == 'electorate-polls' and isinstance(row['observed_at'], str) and re.fullmatch(DATE_PATTERN, row['observed_at']):
            calendar_date(row['observed_at'], stem + '.observed_at')
        else:
            timestamp(row['observed_at'], stem + '.observed_at')
        if stem == 'manifest':
            for key in ('observation_start', 'observation_end'):
                value = row[key]
                if value is not None:
                    if Path(row['path']).stem in DATE_OBSERVATIONS or (Path(row['path']).stem == 'electorate-polls' and re.fullmatch(DATE_PATTERN, value)):
                        calendar_date(value, 'manifest.' + key)
                    else:
                        timestamp(value, 'manifest.' + key)
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
        if stem.startswith('social/'):
            from .social import validate_row
            validate_row(row, stem)
        if stem in NEW_FIELDS:
            validate_daily_row(row, stem, env['source'])
        if stem == 'status':
            if row['state'] not in {'fresh', 'stale', 'unavailable'}:
                raise ValueError('INVALID_STATUS')
            if (row['state'] == 'unavailable') != (row['last_success_at'] is None):
                raise ValueError('INVALID_STATUS_SUCCESS')
    return env


def validate_daily_row(row, stem, sources):
    def natural(value, nullable=False):
        if value is None and nullable:
            return
        if type(value) is not int or value < 0:
            raise ValueError('INVALID_DAILY_NUMBER: ' + stem)
    if stem == 'candidates':
        if not isinstance(row['name'], str) or not row['name'] or not isinstance(row['party_id'], str) or not row['party_id']:
            raise ValueError('INVALID_CANDIDATE')
        natural(row['list_rank'], True)
        if row['list_rank'] == 0:
            raise ValueError('INVALID_LIST_RANK')
        if not isinstance(row['conflict_ids'], list) or not row['join_status']:
            raise ValueError('INVALID_CANDIDATE')
    elif stem == 'party-lists':
        if row['complete'] is not False or not isinstance(row['candidate_ids'], list) or len(set(row['candidate_ids'])) != len(row['candidate_ids']):
            raise ValueError('UNCHECKED_LIST_IDENTITY')
    elif stem == 'candidate-review':
        if not row['claims'] or any(not {'value', 'source_id', 'locator'} <= c.keys() for c in row['claims']):
            raise ValueError('INVALID_CANDIDATE_CLAIM')
    elif stem == 'baseline-2023':
        natural(row['old_electorate_id'])
        for field in ('party_votes', 'candidate_votes'):
            votes = row[field]
            if votes is None and field == 'candidate_votes':
                continue
            if not isinstance(votes, list) or not votes:
                raise ValueError('INVALID_BASELINE_TOTAL')
            for vote in votes:
                natural(vote['votes'])
                if not vote['name'] or not vote['source_ref']:
                    raise ValueError('INVALID_BASELINE_TOTAL')
    elif stem == 'enrolment':
        natural(row['enrolled'], True)
        natural(row['eligible'], True)
        if row['observed_at'] != row['as_of'] or (row['enrolled'] is not None and (row['as_of'] is None or row['roll_basis'] is None)):
            raise ValueError('INVALID_ENROLMENT_OBSERVATION')
    elif stem == 'electorate-polls':
        if row['measure'] not in {'candidate_vote', 'party_vote', 'other'} or row['scale'] != 100:
            raise ValueError('INVALID_LOCAL_POLL')
        natural(row['sample'], True)
        if (row['fieldwork_start'] is None) != (row['fieldwork_end'] is None):
            raise ValueError('INVALID_LOCAL_FIELDWORK')
        if row['fieldwork_end'] is not None and (row['fieldwork_start'] > row['fieldwork_end'] or row['observed_at'] != row['fieldwork_end']):
            raise ValueError('INVALID_LOCAL_FIELDWORK')
        for share in row['shares'].values():
            natural(share['value'], True)
            if (share['value'] is not None and share['value'] > 10000) or type(share['approximate']) is not bool:
                raise ValueError('INVALID_LOCAL_SHARE')
    source_ids = {s['id'] for s in sources}
    for ref in row['source_ref']:
        if not isinstance(ref, dict) or ref.get('source_id') not in source_ids or not ref.get('locator'):
            raise ValueError('INVALID_FIELD_SOURCE')


def csv_bytes(env):
    validate_times(env, nullable_dates=env.get("method_version") in {"enrolment-v1", "electorate-polls-v1"})
    payload = rows(env)
    if env.get('type') == 'FeatureCollection':
        geometries = {f['id']: f['geometry'] for f in env['features']}
        payload = [dict(r, geometry=geometries[r['id']]) for r in payload]
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
    (root / stem).parent.mkdir(parents=True, exist_ok=True)
    (root / (stem + '.json')).write_text(canonical(env) + '\n')
    (root / (stem + '.csv')).write_bytes(csv_bytes(env))


def inventory(root, run_url, code_sha, now):
    timestamp(now, 'inventory.now')
    entries = []
    for path in sorted(data_files(root)):
        name = path.relative_to(root).as_posix()
        if name.startswith('manifest.'):
            continue
        if name not in ALLOWED or path.is_symlink() or not path.is_file():
            raise ValueError('UNSAFE_DATA_PATH')
        stem = path.relative_to(root).with_suffix('').as_posix()
        env = json.loads((root / (stem + '.json')).read_text()) if path.suffix in {'.json', '.csv'} else None
        if env:
            validate_envelope(env, stem)
        data = rows(env) if env else []
        observations = [r['observed_at'] for r in data if r['observed_at'] is not None]
        entries.append(dict(id=name, source_ref=env['source'] if env else [], observed_at=now,
                            path=name, format=path.suffix[1:], sha256=digest(path.read_bytes()),
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
    paths = data_files(root)
    files = {p.relative_to(root).as_posix() for p in paths}
    if files - ALLOWED or not {'manifest.json', 'manifest.csv', 'status.json', 'status.csv', 'LICENCES.md'} <= files:
        raise ValueError('INVALID_INVENTORY')
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError('UNSAFE_DATA_PATH')
    envs = {}
    for path in [p for p in paths if p.suffix == '.json']:
        stem = path.relative_to(root).with_suffix('').as_posix()
        env = validate_envelope(json.loads(path.read_text()), stem)
        if path.with_suffix('.csv').read_bytes() != csv_bytes(env):
            raise ValueError('CSV_MISMATCH')
        envs[stem] = env
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
                env = envs[str(Path(name).with_suffix(''))]
                payload = rows(env)
                observations = [r['observed_at'] for r in payload if r['observed_at'] is not None]
                if (entry['row_count'] != len(payload)
                        or entry['licences'] != sorted({s['licence'] for s in env['source']})
                        or entry['fetched_at'] != env['fetched_at']
                        or entry['producing_run_url'] != env['run_url']
                        or entry['input_hashes'] != env.get('input_hashes', {})
                        or entry['observation_start'] != min(observations, default=None)
                        or entry['observation_end'] != max(observations, default=None)):
                    raise ValueError('INVENTORY_METADATA_MISMATCH')
    if 'social/daily' in envs and 'social/credits' not in envs:
        raise ValueError('MISSING_SOCIAL_LEDGER')
    if 'social/credits' in envs:
        from .social import validate_ledger
        validate_ledger(envs['social/credits']['data'])
    geo = FAMILIES['geography'] & envs.keys()
    if geo and geo != FAMILIES['geography']:
        raise ValueError('PARTIAL_GEOGRAPHY_BUNDLE')
    if geo:
        from .geography import validate
        # A retained snapshot is validated against its own inventory and registry.
        # Current configuration is checked only by the geography producer.
        registry = envs['electorates']['data']
        common = {canonical({k: envs[stem].get(k) for k in ('source', 'input_hashes', 'generated_at', 'run_url', 'code_sha')}) for stem in geo}
        if len(common) != 1:
            raise ValueError('MIXED_GEOGRAPHY_GENERATION')
        registry_hash = digest(canonical(registry).encode('utf-8'))
        if any(envs[stem]['input_hashes'].get('electorates.data') != registry_hash for stem in geo):
            raise ValueError('GEOGRAPHY_REGISTRY_HASH_MISMATCH')
        for kind in ('general', 'maori'):
            validate(envs[kind + '-2025'], kind, registry)
    for family in ('candidates', 'baseline-2023', 'enrolment', 'electorate-polls'):
        present_new = FAMILIES[family] & envs.keys()
        if present_new and present_new != FAMILIES[family]:
            raise ValueError('PARTIAL_DAILY_FAMILY')
        if present_new:
            common = {canonical({k: envs[stem].get(k) for k in ('source', 'input_hashes', 'generated_at', 'run_url', 'code_sha')}) for stem in present_new}
            if len(common) != 1 or any(not envs[stem].get('input_hashes', {}).get('config/electorates.json') for stem in present_new):
                raise ValueError('MIXED_DAILY_GENERATION')
            if 'electorates' in envs and any(envs[stem]['input_hashes'].get('electorates.data') != digest(canonical(envs['electorates']['data']).encode()) for stem in present_new):
                raise ValueError('DAILY_REGISTRY_MISMATCH')
    if 'candidates' in envs:
        candidate_ids = {r['id'] for r in envs['candidates']['data']}
        conflicts = {r['id'] for r in envs['candidate-review']['data']}
        if any(set(r['conflict_ids']) - conflicts for r in envs['candidates']['data']):
            raise ValueError('MISSING_CANDIDATE_CONFLICT')
        if any(set(r['candidate_ids']) - candidate_ids or r['complete'] is not False for r in envs['party-lists']['data']):
            raise ValueError('UNCHECKED_LIST_IDENTITY')
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


def merged_licences(root):
    from .refresh import licences
    root = Path(root)
    text = licences(json.loads((root / 'polls.json').read_text())['source'][0]) if (root / 'polls.json').exists() else licences()
    if (root / 'electorates.json').exists():
        sources = json.loads((root / 'electorates.json').read_text())['source']
        text += '\nGeography: Stats NZ 2025 electorate boundaries and derived registry.\n'
        text += ''.join(s['url'] + '\n' + s['licence'] + '\n' for s in sources)
    for family in ('candidates', 'baseline-2023', 'enrolment', 'electorate-polls'):
        path = root / (family + '.json')
        if path.exists():
            text += '\n' + family + ':\n'
            text += ''.join(s['url'] + '\n' + s['licence'] + '\n' for s in json.loads(path.read_text())['source'])
    (root / 'LICENCES.md').write_text(text)


def data_files(root):
    paths = []
    for path in root.iterdir():
        if path.is_symlink():
            raise ValueError('UNSAFE_DATA_PATH')
        if path.is_dir():
            if path.name != 'social':
                raise ValueError('UNSAFE_DATA_PATH')
            children = list(path.iterdir())
            if any(p.is_symlink() or not p.is_file() for p in children):
                raise ValueError('UNSAFE_DATA_PATH')
            paths.extend(children)
        else:
            paths.append(path)
    return paths
