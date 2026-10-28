# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Extract a draft settlement capture from a pinned, complete preliminary bundle."""
import argparse
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, fixtures, night_live

LABEL = re.compile(r'synthetic|demo|replay|rehearsal|offline fixture', re.I)


def labelled(value):
    if isinstance(value, str):
        return bool(LABEL.search(value))
    if isinstance(value, dict):
        return any((LABEL.search(k) and bool(v)) or labelled(v) for k, v in value.items())
    if isinstance(value, list):
        return any(labelled(v) for v in value)
    return False


def reject_labelled(env, row):
    # Shared archive sources are expected; only the live capture's provenance applies.
    provenance = {k: v for k, v in env.items() if k not in {'data', 'source', 'input_hashes'}}
    provenance['source'] = [s for s in env['source'] if s['id'].startswith('actions-xml/')]
    if labelled([row, provenance]):
        raise ValueError('NIGHT_CAPTURE_NOT_REAL')
    entries = json.loads((fixtures.ROOT / 'manifest.json').read_text())['entries']
    paths = {e['path'] for e in entries if e['path'].endswith('.json') and LABEL.search(json.dumps(e))}
    for raw in fixtures.captures(paths=paths).values():
        known = json.loads(raw)
        if isinstance(known, dict) and known.get('raw') == row.get('raw_xml'):
            raise ValueError('NIGHT_CAPTURE_NOT_REAL')


def prepare(data, out):
    envs = export.validate_bundle(data)
    env = envs.get('night/live/current', {})
    rows = env.get('data', [])
    if len(rows) != 1:
        raise ValueError('NIGHT_BASELINE')
    row = rows[0]
    reject_labelled(env, row)
    if (row.get('mode') != night_live.MODE or 'result_state' in row
            or row.get('acquisition_source', {}).get('kind') != 'preliminary'):
        raise ValueError('NIGHT_BASELINE')
    captured = dict(raw=row['raw_xml'], retrieved_at=row['retrieved_at'],
                    acquisition_source=row['acquisition_source'])
    # Use the import's exact comparison before emitting any bytes.
    if night_live.loaded(captured)[0]['night/live/current'][0] != row:
        raise ValueError('NIGHT_BASELINE')
    raw = (json.dumps(captured, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    out = Path(out)
    if out.resolve().is_relative_to(Path(data).resolve()):
        raise ValueError('UNSAFE_CAPTURE_PATH')
    # Exclusive creation preserves existing captures and refuses destination symlinks.
    with out.open('xb') as target:
        target.write(raw)
    return dict(path=out.as_posix(), sha256=export.digest(raw), bytes=len(raw),
                retrieved_at=captured['retrieved_at'], source=captured['acquisition_source'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Complete bundle checked out at the pinned data SHA')
    parser.add_argument('--out', type=Path, required=True, help='New capture file in an existing directory')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.data, args.out), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from None


if __name__ == '__main__':
    main()
