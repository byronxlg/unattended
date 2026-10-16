# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Deterministic M1 checks. No network or optional test dependencies."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export
from product.nz_election.pipeline.average import trend, threshold_watch, select_window
from product.nz_election.pipeline.build import build, config
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.seats import project


def require(condition, reason):
    if not condition:
        raise ValueError('VERIFY_FAILED: ' + reason)


def verify_polls(envs, root):
    polls = envs['polls']['data']
    average = envs['averages']['data'][-1]
    require(len(polls) > 30, 'full captured history')
    require(len({p['id'] for p in polls}) == len(polls), 'distinct polls')
    missing = [dict(p, shares=dict(p['shares'], nat=None)) for p in polls]
    incomplete = trend(missing, [average['date']])[0]
    require(not incomplete['coherent'] and not project(incomplete)['available'], 'withhold incomplete seats')
    page = build(root / 'data', root / 'rendered') / 'index.html'
    html = page.read_text()
    require('Poll history' in html and '<script' not in html, 'static poll history')
    coherent = next(a for a in reversed(envs['averages']['data']) if a['coherent'])
    from product.nz_election.pipeline.build import strip
    seats = project(coherent)
    if seats['available']:
        rendered = strip(seats)
        require('class="strip"' in rendered and 'class="majority"' in rendered, 'strip and majority mark')
        require(sum(seats['seats'].values()) == seats['assumed_house'], 'seat sum')


def verify_thresholds(envs, root):
    polls = [dict(id='a', revision='1', fieldwork_end='2026-10-17', shares=dict(opp=200, tpm=700, others=9100), scale=100),
             dict(id='b', revision='1', fieldwork_end='2026-10-16', shares=dict(opp=100, tpm=None, others=9900), scale=100)]
    average = trend(polls, ['2026-10-17'])[0]
    watch = threshold_watch(polls, average, {'electorate_wins': {'tpm': 6}})
    require({w['party_id'] for w in watch} == {'opp', 'tpm'}, 'inclusive any-poll membership')
    tpm = next(w for w in watch if w['party_id'] == 'tpm')
    require(tpm['missing_poll_ids'] == ['b'] and tpm['electorate_qualifies'], 'missing coverage and electorate qualification')
    require(len(select_window(polls, '2026-11-15')) == 1, 'inclusive 30-day boundary')


def verify_provenance(envs, root):
    export.validate_bundle(root / 'data')
    require(all(p['source_ref'] and p['reference_urls'] for p in envs['polls']['data']), 'poll source links')
    require('CC BY-SA 4.0' in (root / 'data/LICENCES.md').read_text(), 'share-alike')
    require('No open licence stated' in (root / 'data/LICENCES.md').read_text(), 'EC licence')
    for stem in ('averages', 'seats'):
        require(envs[stem]['input_hashes'] and envs[stem]['method_version'], 'calculation provenance')


def verify_pipeline(envs, root):
    bundle = root / 'data'
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in {'polls', 'averages', 'seats'}}
    def fail(*args):
        raise ParseDrift('verification failure')
    refresh(bundle, now='2026-10-17T02:00:00Z', parse=fail)
    require(all((bundle / name).read_bytes() == raw for name, raw in before.items()), 'last-good retention')
    status = refresh(root / 'unavailable', now='2026-10-17T02:00:00Z', parse=fail)
    require(status['state'] == 'unavailable' and status['last_success_at'] is None, 'first failure')
    out = build(root / 'absent', root / 'empty-site')
    require('No data yet' in (out / 'index.html').read_text(), 'no data build')
    deployed = (out / 'index.html').read_bytes()
    broken = root / 'broken'
    shutil.copytree(bundle, broken)
    (broken / 'seats.csv').write_text('broken')
    try:
        build(broken, out)
    except ValueError:
        pass
    else:
        raise ValueError('VERIFY_FAILED: accepted corrupted data')
    require((out / 'index.html').read_bytes() == deployed, 'failed deployment retention')
    remote, seed = root / 'remote.git', root / 'seed'
    remote.mkdir()
    seed.mkdir()
    git(remote, 'init', '--bare', '-q')
    git(seed, 'init', '-q', '-b', 'data')
    git(seed, 'config', 'user.name', 'Offline verification')
    git(seed, 'config', 'user.email', 'offline@example.invalid')
    shutil.copytree(bundle, seed / DATA)
    git(seed, 'add', str(DATA))
    git(seed, 'commit', '-qm', 'Seed local verification data')
    git(seed, 'push', str(remote), 'data')
    newer, newest = root / 'newer', root / 'newest'
    refresh(newer, now='2026-10-17T03:00:00Z')
    refresh(newest, now='2026-10-17T04:00:00Z')
    barrier = threading.Barrier(2)
    def race(path):
        return publish(path, remote, before_push=lambda attempt: barrier.wait(timeout=10) if not attempt else None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(race, [newer, newest]))
    require(any(r['attempts'] == 2 for r in results), 'non-fast-forward retry')
    require(publish(newer, remote)['outcome'] == 'older-run-retained', 'older publisher rejected')
    require(publish(newest, remote)['outcome'] == 'unchanged', 'identical publication skipped')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=['all', 'polls', 'thresholds', 'provenance', 'pipeline'])
    parser.add_argument('--data', type=Path)
    parser.add_argument('--site', type=Path)
    args = parser.parse_args()
    checks = {'polls': verify_polls, 'thresholds': verify_thresholds, 'provenance': verify_provenance, 'pipeline': verify_pipeline}
    with tempfile.TemporaryDirectory(prefix='nz-verify-') as tmp:
        root = Path(tmp)
        refresh(root / 'data', now='2026-10-17T01:00:00Z')
        envs = export.validate_bundle(root / 'data')
        if args.data:
            export.validate_bundle(args.data)
        if args.site:
            product = args.site / 'nz-election' if (args.site / 'nz-election').is_dir() else args.site
            for route in config('routes'):
                require((product / route['path'] / 'index.html').is_file(), 'site route ' + route['path'])
            export.validate_envelope(json.loads((product / 'build-manifest.json').read_text()), 'build-manifest')
            if (product / 'data').exists():
                export.validate_bundle(product / 'data')
        for name, check in checks.items():
            if args.check in ('all', name):
                check(envs, root)
                print('PASS ' + name)
        if args.check == 'all':
            print('PASS all')


if __name__ == '__main__':
    main()
