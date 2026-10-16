# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Offline daily geography ingestion, retaining last-good family bytes atomically."""
import argparse
import fcntl
import json
from pathlib import Path
import shutil
import sys
import tempfile
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, geography
from product.nz_election.pipeline.refresh import config, code_sha, utc_now
from product.nz_election.pipeline.storage import replace_directory


def daily_refresh(out, *, now=None, sha=None, run_url='offline-verification', load=geography.load):
    out = Path(out).absolute()
    if out.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    now, sha = export.timestamp(now or utc_now()), sha or code_sha()
    with (out.parent / ('.' + out.name + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = export.validate_bundle(out) if out.exists() else {}
        statuses = old.get('status', {}).get('data', [])
        prior = next((r for r in statuses if r['dataset'] == 'geography'), {})
        with tempfile.TemporaryDirectory(prefix='.daily-', dir=out.parent) as tmp:
            stage = Path(tmp) / 'data'
            shutil.copytree(out, stage) if out.exists() else stage.mkdir()
            error = None
            try:
                collections = load()
                rows = config('electorates')
                if rows != geography.registry(collections):
                    raise ValueError('REGISTRY_MISMATCH')
                entries = json.loads((geography.ROOT / 'manifest.json').read_text())['entries']
                entries = [e for e in entries if e['path'] in {'stats-nz/' + k + '-2025.geojson' for k in geography.KINDS}]
                sources = [dict(id='G:' + e['path'], url=e['url'], revision=e['revision'], licence=e['licence'],
                                fetched_at=e['captured_at'], history_url=None) for e in entries]
                report = next(e for e in json.loads((geography.ROOT / 'manifest.json').read_text())['entries']
                              if e['path'] == 'representation-commission/report-2025.pdf')
                sources.append(dict(id='config/electorate-correspondence.json', url=report['url'],
                                    revision=export.digest((geography.PRODUCT / 'config/electorate-correspondence.json').read_bytes()),
                                    licence=report['licence'], fetched_at=report['captured_at'], history_url=None))
                inputs = {name: export.digest((geography.PRODUCT / name).read_bytes()) for name in
                          ('config/electorates.json', 'config/electorate-correspondence.json')}
                # Hash the published payload, avoiding a self-reference through envelope metadata.
                inputs['electorates.data'] = export.digest(export.canonical(rows).encode('utf-8'))
                inputs.update({'fixtures/' + e['path']: e['sha256'] for e in entries})
                def envelope(data):
                    return export.envelope(data, sources, run_url, sha, inputs=inputs, method='geography-v1', generated=now)
                export.pair(stage, 'electorates', envelope(rows))
                for kind, collection in collections.items():
                    prop = geography.KINDS[kind][0]
                    metadata = [dict(id=r['id'], name=r['name'], kind=kind, observed_at=r['observed_at'],
                                     source_ref=[ref for ref in r['source_ref'] if ref['field'] in {'id', 'name', 'kind', 'observed_at'}] +
                                     [dict(field=field, source_id='G:stats-nz/' + kind + '-2025.geojson', locator=prop + '=' + r['stats_id'])
                                      for field in ('geometry', 'properties')]) for r in rows if r['kind'] == kind]
                    features = [dict(f, id='stats-nz-2025-' + f['properties'][prop],
                                     properties={k: str(v) if isinstance(v, float) else v for k, v in f['properties'].items()})
                                for f in collection['features']]
                    export.pair(stage, kind + '-2025', dict(envelope(metadata), type='FeatureCollection', features=features))
                export.merged_licences(stage)
                success, good_run = now, run_url
            except ValueError as exc:
                error = str(exc)
                shutil.rmtree(stage)
                shutil.copytree(out, stage) if out.exists() else stage.mkdir()
                success, good_run = prior.get('last_success_at'), prior.get('last_good_run_url')
            status = dict(id='status-geography', source_ref=[], observed_at=now, dataset='geography',
                          state=('stale' if success else 'unavailable') if error else 'fresh',
                          last_attempt_at=now, last_success_at=success, last_good_run_url=good_run,
                          error_code=error, message='Retained last-good geography.' if error else 'Offline verification from captured sources. Not live data.')
            export.pair(stage, 'status', export.envelope([r for r in statuses if r['dataset'] != 'geography'] + [status], [], run_url, sha))
            export.merged_licences(stage)
            export.inventory(stage, run_url, sha, now)
            export.validate_bundle(stage)
            replace_directory(stage, out)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    status = daily_refresh(args.out)
    if status['error_code']:
        raise SystemExit('FAIL refresh: ' + status['error_code'])
    print('PASS refresh: daily bundles')


if __name__ == '__main__':
    main()
