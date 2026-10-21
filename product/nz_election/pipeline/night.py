"""Closed-world offline night family, with explicit synthetic derivation."""
from copy import deepcopy
import json
from pathlib import Path
import re
from . import export, fixtures, xml_parser

LABEL = 'Illustrative replay based on 2023 final results'
MODES = {'final': 'Final snapshot', 'illustrative': LABEL, 'demo': 'Recorded demo'}


def allowed(name):
    return isinstance(name, str) and bool(re.fullmatch(r'night/(?:index|references/[a-z0-9-]{1,80}|[a-z0-9-]{1,40}/[a-z0-9-]{1,80})\.(?:json|csv)', name))


def load():
    entries = json.loads((fixtures.ROOT / 'manifest.json').read_text())['entries']
    entries = [e for e in entries if re.fullmatch(r'ec-(2017|2020|2023|mediademo)-xml/.*', e['path'])]
    raw = fixtures.captures(paths={e['path'] for e in entries})
    sources = [dict(id=e['path'], url=e['url'], revision=e['revision'], licence=e['licence'],
                    fetched_at=e['captured_at'], history_url=None) for e in entries]
    hashes = {e['path']: e['sha256'] for e in entries}
    payloads, sequences = {}, []
    for year in ('2017', '2020', '2023', 'mediademo'):
        prefix = 'ec-' + year + '-xml/'
        refs = xml_parser.references(*(raw[prefix + n + '.xml'] for n in ('parties', 'electorates', 'candidates')))
        refpath = 'night/references/' + year
        payloads[refpath] = [dict(id=year, source_ref=[prefix + n + '.xml' for n in ('parties', 'electorates', 'candidates')], **refs)]
        names = ['election-obs1', 'election-obs2'] if year == 'mediademo' else ['election']
        paths = []
        for name in names:
            result = xml_parser.election(raw[prefix + name + '.xml'], refs)
            path = 'night/' + year + '/' + result['source_updated_local'].replace(':', '').lower()
            row = dict(id=path, source_ref=[prefix + name + '.xml'], mode=MODES['demo' if year == 'mediademo' else 'final'], **result)
            payloads[path] = [row]
            paths.append(path + '.json')
        sequences.append(dict(id=year, source_ref=[prefix + n + '.xml' for n in names], sequence_id=year,
                              mode=row['mode'], reference_path=refpath + '.json', reference_version=refs['reference_version'], snapshot_paths=paths))
        if year == '2023':
            replay = []
            for step, numerator in enumerate((1, 5, 10)):
                path = 'night/illustrative-2023/step-' + str(step)
                sample = deepcopy(row)
                sample.update(id=path, mode=LABEL, elapsed_seconds=step * 300,
                              derivation=dict(method='floor(final party votes * numerator / 10)', numerator=numerator, denominator=10,
                                              basis=paths[0]))
                del sample['source_updated_local']
                if numerator != 10:
                    sample.pop('reported_house')
                    sample.pop('statistics')
                    sample['party_results'] = {p: dict(votes=r['votes'] * numerator // 10) for p, r in row['party_results'].items()}
                    sample['valid_party_votes'] = sum(r['votes'] for r in sample['party_results'].values())
                payloads[path] = [sample]
                replay.append(path + '.json')
            sequences.append(dict(id='illustrative-2023', source_ref=row['source_ref'], sequence_id='illustrative-2023', mode=LABEL,
                                  reference_path=refpath + '.json', reference_version=refs['reference_version'], snapshot_paths=replay))
    payloads['night/index'] = sequences
    return payloads, sources, hashes


def prepare(root, loaded, run_url, sha, now):
    payloads, sources, hashes = loaded
    if type(payloads) is not dict or 'night/index' not in payloads or any(not allowed(stem + '.json') for stem in payloads):
        raise ValueError('NIGHT_PATH')
    for stem, data in payloads.items():
        if stem == 'night/index':
            continue
        export.pair(root, stem, export.envelope(data, sources, run_url, sha, inputs=hashes, method='night-v1', generated=now))
    index = deepcopy(payloads['night/index'])
    for sequence in index:
        paths = [sequence['reference_path']] + sequence['snapshot_paths']
        sequence['files'] = {name: export.digest((root / name).read_bytes()) for path in paths for name in (path, path[:-5] + '.csv')}
    export.pair(root, 'night/index', export.envelope(index, sources, run_url, sha, inputs=hashes, method='night-v1', generated=now))
    validate(root)


def validate_mode(row):
    # Capture identity and derivation constrain labels even if both labels are edited.
    refs = row['source_ref']
    if not refs or any(type(ref) is not str for ref in refs):
        raise ValueError('NIGHT_MODE')
    if all(re.fullmatch(r'ec-mediademo-xml/election-obs[1-9][0-9]*\.xml', ref) for ref in refs):
        expected = MODES['demo']
        if 'derivation' in row:
            raise ValueError('NIGHT_MODE')
    elif all(re.fullmatch(r'ec-(2017|2020|2023)-xml/election\.xml', ref) for ref in refs):
        expected = MODES['final']
        if 'derivation' in row:
            if refs != ['ec-2023-xml/election.xml'] or not isinstance(row['derivation'], dict) or not row['derivation']:
                raise ValueError('NIGHT_MODE')
            expected = LABEL
    else:
        raise ValueError('NIGHT_MODE')
    if row.get('mode') != expected:
        raise ValueError('NIGHT_MODE')


def validate_row(row, stem):
    try:
        if not isinstance(row, dict) or not {'id', 'source_ref'} <= row.keys() or not isinstance(row['source_ref'], list):
            raise ValueError('NIGHT_ROW')
        if stem == 'night/index':
            if set(row) != {'id', 'source_ref', 'sequence_id', 'mode', 'reference_path', 'reference_version', 'snapshot_paths', 'files'}:
                raise ValueError('NIGHT_INDEX')
            if row['mode'] not in MODES.values() or type(row['snapshot_paths']) is not list or not row['snapshot_paths'] or not isinstance(row['files'], dict):
                raise ValueError('NIGHT_INDEX')
        elif stem.startswith('night/references/'):
            refs = {k: row[k] for k in ('parties', 'electorates', 'candidates')}
            if export.digest(export.canonical(refs).encode()) != row.get('reference_version'):
                raise ValueError('NIGHT_REFERENCE')
        else:
            validate_mode(row)
            if row.get('mode') not in MODES.values() or not row['party_results']:
                raise ValueError('NIGHT_ROW')
            for result in row['party_results'].values():
                for key, value in result.items():
                    if key == 'percent_votes':
                        xml_parser.percent(value)
                    elif key not in {'votes', 'party_seats', 'candidate_seats', 'total_seats'} or type(value) is not int or not 0 <= value <= 999999999:
                        raise ValueError('NIGHT_ROW')
            if row['valid_party_votes'] != sum(r['votes'] for r in row['party_results'].values()):
                raise ValueError('NIGHT_ROW')
            if 'reported_house' in row and row['reported_house'] != sum(r['total_seats'] for r in row['party_results'].values()):
                raise ValueError('NIGHT_ROW')
            if row['mode'] == LABEL:
                if 'source_updated_local' in row or type(row['elapsed_seconds']) is not int or row['elapsed_seconds'] < 0 or not row['derivation']:
                    raise ValueError('NIGHT_ROW')
            elif 'elapsed_seconds' in row or 'source_updated_local' not in row:
                raise ValueError('NIGHT_ROW')
    except (KeyError, TypeError, AttributeError):
        raise ValueError('NIGHT_ROW') from None


def validate_capture(row, env, cache):
    if row['mode'] != MODES['final']:
        return
    if len(row['source_ref']) != 1:
        raise ValueError('NIGHT_CAPTURE_MISMATCH')
    source = row['source_ref'][0]
    if source not in cache:
        prefix = source.rsplit('/', 1)[0] + '/'
        paths = {source} | {prefix + name + '.xml' for name in ('parties', 'electorates', 'candidates')}
        # The committed captures are the trust anchor, not the package's editable metadata.
        raw = fixtures.captures(root=fixtures.ROOT, paths=paths)
        refs = xml_parser.references(*(raw[prefix + name + '.xml'] for name in ('parties', 'electorates', 'candidates')))
        cache[source] = xml_parser.election(raw[source], refs), {name: export.digest(data) for name, data in raw.items()}
    captured, hashes = cache[source]
    if (any(env.get('input_hashes', {}).get(name) != digest for name, digest in hashes.items())
            or any(row.get(field) != value for field, value in captured.items())):
        raise ValueError('NIGHT_CAPTURE_MISMATCH')


def validate(root):
    root = Path(root)
    folder = root / 'night'
    if folder.is_symlink():
        raise ValueError('NIGHT_PATH')
    paths = list(folder.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('NIGHT_PATH')
    actual = {p.relative_to(root).as_posix() for p in paths if p.is_file()}
    if any(not allowed(p) for p in actual):
        raise ValueError('NIGHT_PATH')
    try:
        index_env = export.validate_envelope(json.loads((folder / 'index.json').read_text()), 'night/index')
        if (folder / 'index.csv').read_bytes() != export.csv_bytes(index_env):
            raise ValueError('NIGHT_CSV')
        index = index_env['data']
        expected = {'night/index.json', 'night/index.csv'}
        snapshots, ids = set(), set()
        capture_cache = {}
        for seq in index:
            validate_row(seq, 'night/index')
            if seq['id'] in ids:
                raise ValueError('NIGHT_INDEX')
            ids.add(seq['id'])
            deps = [seq['reference_path']] + seq['snapshot_paths']
            if len(deps) != len(set(deps)) or snapshots.intersection(seq['snapshot_paths']):
                raise ValueError('NIGHT_INDEX')
            snapshots.update(seq['snapshot_paths'])
            names = {n for p in deps for n in (p, p[:-5] + '.csv')}
            if set(seq['files']) != names or any(not allowed(p) or not p.endswith('.json') for p in deps):
                raise ValueError('NIGHT_INDEX')
            expected.update(names)
            for name, sha in seq['files'].items():
                if export.digest((root / name).read_bytes()) != sha:
                    raise ValueError('NIGHT_HASH')
            reference = json.loads((root / seq['reference_path']).read_text())['data'][0]
            if not seq['reference_path'].startswith('night/references/'):
                raise ValueError('NIGHT_REFERENCE')
            for path in deps:
                env = export.validate_envelope(json.loads((root / path).read_text()), path[:-5])
                if (root / (path[:-5] + '.csv')).read_bytes() != export.csv_bytes(env):
                    raise ValueError('NIGHT_CSV')
                if len(env['data']) != 1 or any(env.get(k) != index_env.get(k) for k in ('source', 'input_hashes', 'generated_at', 'run_url', 'code_sha')):
                    raise ValueError('NIGHT_GENERATION')
                row = env['data'][0]
                if path in seq['snapshot_paths'] and set(row['party_results']) - reference['parties'].keys():
                    raise ValueError('NIGHT_REFERENCE')
                if row['reference_version'] != seq['reference_version']:
                    raise ValueError('NIGHT_REFERENCE')
                if path in seq['snapshot_paths']:
                    if row['mode'] != seq['mode']:
                        raise ValueError('NIGHT_MODE')
                    validate_capture(row, env, capture_cache)
            if seq['mode'] == 'Final snapshot' and len(seq['snapshot_paths']) != 1:
                raise ValueError('NIGHT_INDEX')
        if not index or actual != expected:
            raise ValueError('NIGHT_INDEX')
        return expected
    except (KeyError, TypeError, OSError, json.JSONDecodeError):
        raise ValueError('NIGHT_INDEX') from None
