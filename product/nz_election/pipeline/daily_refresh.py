# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Daily ingestion with optional bounded live sources and atomic family retention."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, geography, candidates, baseline, enrolment, electorate_polls, markets, advance, night
from product.nz_election.pipeline.refresh import config, code_sha, utc_now
from product.nz_election.pipeline.storage import replace_directory


def daily_refresh(out, *, now=None, sha=None, run_url='offline-verification', load=geography.load, loaders=None, messages=None, historical_advance=False):
    out = Path(out).absolute()
    if out.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    now, sha = export.timestamp(now or utc_now()), sha or code_sha()
    capture_message = ('Offline verification from captured sources. Not live data.' if run_url == 'offline-verification'
                       else 'Ingested committed captures with original acquisition dates. Not live observations.')
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
                          error_code=error, message='Retained last-good geography.' if error else capture_message)
            statuses = [r for r in statuses if r['dataset'] != 'geography'] + [status]
            producers = loaders if loaders is not None else {'candidates': candidates.load, 'baseline-2023': baseline.load,
                                                            'enrolment': enrolment.load, 'electorate-polls': electorate_polls.load, 'markets': markets.load,
                                                            'night': night.load, 'advance': lambda: advance.load(historical=historical_advance)}
            for family, producer in producers.items():
                previous = next((r for r in statuses if r['dataset'] == family), {})
                failure = None
                try:
                    loaded = producer()
                    if loaded is None and family == 'advance':
                        statuses = [r for r in statuses if r['dataset'] != family] + [dict(
                            id='status-advance', source_ref=[], observed_at=now, dataset=family,
                            state='stale' if previous.get('last_success_at') else 'unavailable',
                            last_attempt_at=now, last_success_at=previous.get('last_success_at'),
                            last_good_run_url=previous.get('last_good_run_url'), error_code=None,
                            message='Awaiting a verified 2026 capture; any last-good capture is retained.')]
                        continue
                    payloads, sources, hashes = loaded
                    if family != 'night' and set(payloads) != export.FAMILIES[family]:
                        raise ValueError('PARTIAL_DAILY_FAMILY')
                    if family not in {'advance', 'night'} and (stage / 'electorates.json').exists():
                        registry = json.loads((stage / 'electorates.json').read_text())['data']
                        if hashes['electorates.data'] != export.digest(export.canonical(registry).encode()):
                            raise ValueError('DAILY_REGISTRY_MISMATCH')
                    with tempfile.TemporaryDirectory(prefix='.family-', dir=out.parent) as family_tmp:
                        prepared = Path(family_tmp)
                        if family == 'night':
                            night.prepare(prepared, loaded, run_url, sha, now)
                        for stem, data in ({} if family == 'night' else payloads).items():
                            export.pair(prepared, stem, export.envelope(data, sources, run_url, sha, inputs=hashes,
                                                                       method=family + '-v1', generated=now))
                        if family == 'night':
                            if (stage / 'night').exists():
                                shutil.rmtree(stage / 'night')
                            shutil.copytree(prepared / 'night', stage / 'night')
                        else:
                            for path in prepared.iterdir():
                                shutil.copyfile(path, stage / path.name)
                    success, good_run = now, run_url
                except ValueError as exc:
                    failure = str(exc)
                    success, good_run = previous.get('last_success_at'), previous.get('last_good_run_url')
                family_status = dict(id='status-' + family, source_ref=[], observed_at=now, dataset=family,
                                     state=('stale' if success else 'unavailable') if failure else 'fresh',
                                     last_attempt_at=now, last_success_at=success, last_good_run_url=good_run,
                                     error_code=failure, message=((('Retained last-good family' if success else 'No validated family available') +
                                                               ' (' + failure + ').') if failure else
                                     (messages or {}).get(family, capture_message)))
                statuses = [r for r in statuses if r['dataset'] != family] + [family_status]
            export.pair(stage, 'status', export.envelope(statuses, [], run_url, sha))
            export.merged_licences(stage)
            export.inventory(stage, run_url, sha, now)
            export.validate_bundle(stage)
            replace_directory(stage, out)
    return status


def main(*, now=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--historical-advance', action='store_true', help='2023 offline verification only')
    args = parser.parse_args()
    from product.nz_election.pipeline.sunsets import skip
    if args.live and skip('daily', now() if now else None):
        return
    if args.live and args.historical_advance:
        parser.error('historical advance is offline only')
    options = dict(historical_advance=args.historical_advance)
    if args.live:
        from product.nz_election.pipeline.deployment_guard import require_publication_allowed
        require_publication_allowed()
        from product.nz_election.pipeline.daily_sources import live_loaders
        loaders, messages = live_loaders(**({"now": now} if now else {}))
        options = dict(loaders=loaders, messages=messages, sha=os.environ['GITHUB_SHA'],
                       run_url=os.environ['GITHUB_SERVER_URL'] + '/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID'])
    daily_refresh(args.out, **options)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('validated=true\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write('## Daily refresh\n\n```json\n' + json.dumps(export.validate_bundle(args.out)['status']['data'], indent=2) + '\n```\n')
    failures = [r['error_code'] for r in export.validate_bundle(args.out)['status']['data'] if r['dataset'] in export.FAMILIES.keys() - {'polls', 'social'} and r['error_code']]
    if failures:
        raise SystemExit('FAIL refresh: ' + '; '.join(failures))
    print('PASS refresh: daily bundles')


if __name__ == '__main__':
    main()
