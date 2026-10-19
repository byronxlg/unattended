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
    page = build(root / 'data', root / 'rendered') / 'polls/index.html'
    html = page.read_text()
    from product.nz_election.pipeline.scripts import validate_scripts
    require('How have the polls moved?' in html and validate_scripts(html), 'static poll history')
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


def verify_coalitions(envs, root):
    from product.nz_election.pipeline import coalitions
    from product.nz_election.pipeline.allocator import allocate
    from product.nz_election.pipeline.fixtures import golden
    from product.nz_election.pipeline.build import strip
    average = next(a for a in reversed(envs['averages']['data']) if a['coherent'])
    seats = project(average)
    data = coalitions.inputs(average, seats, 'a' * 64)
    state = data['initial']
    require(state['selected'] == [], 'empty default coalition')
    result = coalitions.scenario(data, state)
    require(result['majority'] is None and result['occupied_house'] is None and result['vacancies'] is None,
            'unknown capacity stays conditional')
    require(result['assumed_majority'] == result['assumed_house'] // 2 + 1, 'conditional majority')
    require(coalitions.decode(coalitions.encode(state), data['parties']) == state, 'share round trip')
    edited = dict(state, counts={p: '71' if p == 'tpm' else '0' for p in data['parties']})
    require(coalitions.scenario(data, edited)['overhang'] > 0, 'overhang scenario')
    official = golden()['input']
    official['lists'] = {p: [] for p in official['lists']}
    # Real captured winners supply candidate identities, never invented capacity.
    official['lists'] = {p: list(v) for p, v in official['electorateWinners'].items() if v}
    vacancy = allocate(official)
    require(vacancy['vacancies'] > 0 and vacancy['occupiedHouse'] == 120 + vacancy['overhang'] - vacancy['vacancies'], 'list vacancies')
    page = build(root / 'data', root / 'coalition-site') / 'polls/index.html'
    html = page.read_text()
    require('<fieldset hidden disabled>' in html and 'data-note' in html and 'source-seats' in html,
            'static fallback and provenance')
    require('Seats needed for a majority' in strip(seats), 'static majority retained')


def verify_geography(envs, root):
    from product.nz_election.pipeline import geography
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.scripts import validate_scripts
    collections = geography.load()
    registry = config('electorates')
    for kind, collection in collections.items():
        geography.validate(collection, kind, registry)
    require(registry == geography.registry(collections), 'reviewed registry')
    require(len(geography.svg(collections, registry).encode()) <= 300000, 'index SVG budget')
    for row in registry:
        require(len(geography.svg(collections, registry, row['id']).encode()) <= 30000, 'outline budget')
    daily_refresh(root / 'data')
    page = build(root / 'data', root / 'geography-site') / 'electorates/index.html'
    html = page.read_text()
    require(validate_scripts(html) and html.count('data-search-key=') == 71, 'static directory')
    require('fill-rule="evenodd"' in html and 'map-general' in html and 'map-maori' in html, 'map layers and holes')


def verify_candidates(envs, root):
    from product.nz_election.pipeline import candidates
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(root / 'data')
    current = export.validate_bundle(root / 'data')
    rows = current['candidates']['data']
    require({r['electorate_id'] for r in rows if r['electorate_id']} == {r['id'] for r in config('electorates')}, 'candidate electorate coverage')
    require(all(r['complete'] is False for r in current['party-lists']['data']), 'unchecked list identities')
    from product.nz_election.pipeline.fixtures import captures
    official = candidates.spreadsheet(captures(paths={candidates.SHEET})[candidates.SHEET])
    require([(r['name'], r['party_id']) for r in rows if r['id'].startswith('ec-row-')] ==
            [(r['Name'], r['Party']) for r in official], 'official spine')


def verify_electorates(envs, root):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.electorate_pages import detail
    daily_refresh(root / 'data')
    site = build(root / 'data', root / 'details-site')
    require(len(list((site / 'electorates').glob('*/index.html'))) == 71, '71 detail pages')
    require('Wellington Central (2023)' in (site / 'electorates/wellington-north/index.html').read_text(), 'original name comparison')
    from copy import deepcopy
    current = export.validate_bundle(root / 'data')
    central = next(r for r in config('electorates') if r['slug'] == 'auckland-central')
    require('No candidate baseline' not in detail(central, current), 'present candidate baseline')
    missing = deepcopy(current)
    old = next(r for r in missing['baseline-2023']['data'] if r['old_electorate_id'] == 1)
    old['candidate_votes'] = None
    old['field_sources']['candidate_status'] = 'Missing candidate capture.'
    require('No candidate baseline. Missing candidate capture.' in detail(central, missing), 'controlled missing baseline')
    row = next(r for r in config('electorates') if r['slug'] == 'te-tai-tonga')
    require('Official candidates not available' in detail(row, {}), 'controlled missing data')



def verify_social(envs, root):
    from copy import deepcopy
    from product.nz_election.pipeline.social import refresh_social, fixture_send, frozen
    from product.nz_election.pipeline.social_page import page
    now = '2026-10-17T03:00:00Z'
    data = root / 'social-verification'
    require(refresh_social(data, '2026-10-16', now=now, fixture=True,
                           send=fixture_send(), sleep=lambda _: None) == 'ok', 'social fixture collection')
    current = export.validate_bundle(data)
    row = current['social/daily']['data'][0]
    require(row['sample']['returned'] == row['sample']['eligible'] == 240, 'social sample counts')
    require(sum(row['party_counts'].values()) == 240, 'social primary-party total')
    require(any(v['withheld'] for v in row['attitude'].values()), 'social attitude withholding')
    ledger = current['social/credits']['data']
    require(sum(r['reserved'] for r in ledger) == 7560 and sum(r['spent'] for r in ledger) == 3600,
            'social credit accounting')
    original = (data / 'social/daily.json').read_bytes()
    require(refresh_social(data, '2026-10-16', now=now, fixture=True,
                           send=fixture_send(), sleep=lambda _: None) == 'SOCIAL_CREDIT_CAP', 'social rerun cap')
    require((data / 'social/daily.json').read_bytes() == original, 'social last-good retention')
    for field in ('post_id', 'handle'):
        malformed = deepcopy(current['social/daily'])
        malformed['data'][0]['sample'][field] = 'fictional-private-value'
        try:
            export.validate_envelope(malformed, 'social/daily')
        except ValueError:
            pass
        else:
            raise ValueError('VERIFY_FAILED: social identifier accepted')
    require(frozen('2026-11-06T11:00:00Z') and not frozen('2026-11-07T06:00:00Z'), 'social freeze boundary')
    site = build(data, root / 'social-site', built=now)
    from product.nz_election.pipeline.disclosure_checks import check_site as check_disclosures
    check_disclosures(site)
    html = (site / 'social/poc/index.html').read_text()
    require('Proof of concept' in html and '@' not in html and '<svg' in html, 'social page present')
    require('under 5' in html and 'Withheld:' in html, 'social small-cell labels')
    require('<svg' not in page(current, '2026-10-19T03:00:00Z'), 'social stale page withheld')
    absent = build(root / 'social-absent', root / 'social-empty-site', built=now)
    html = (absent / 'social/poc/index.html').read_text()
    require('unavailable' in html and '<svg' not in html, 'social absent page')


def verify_home(envs, root):
    from product.nz_election.pipeline.home_checks import check_site
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.presentation import election_countdown
    refresh(root / 'home-data', now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    daily_refresh(root / 'home-data', now='2026-10-17T01:00:00Z')
    current = export.validate_bundle(root / 'home-data')
    site = build(root / 'home-data', root / 'home-site', built='2026-10-17T01:00:00Z')
    check_site(site, current)
    empty = build(root / 'home-absent', root / 'home-empty', built='2026-10-17T01:00:00Z')
    check_site(empty, {})
    for instant, expected in [('2026-11-06T10:59:59Z', '1 day until election day'),
                              ('2026-11-06T11:00:00Z', 'Election day'),
                              ('2026-11-07T11:00:00Z', 'Results')]:
        require(election_countdown(instant) == expected, 'NZ countdown')


def verify_home_routes(envs, root):
    from product.nz_election.pipeline.route_checks import check_site
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    data = root / 'route-data'
    refresh(data, now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    daily_refresh(data, now='2026-10-17T01:00:00Z')
    for source, name in ((data, 'populated'), (root / 'absent-routes', 'empty')):
        site = build(source, root / ('routes-' + name), built='2026-10-17T01:00:00Z')
        check_site(site, export.validate_bundle(source) if source.exists() else {})
        from product.nz_election.pipeline.disclosure_checks import check_site as check_disclosures
        check_disclosures(site)


def verify_markets(envs, root):
    from product.nz_election.pipeline.markets import load, FAMILIES, ATTRIBUTION
    from product.nz_election.pipeline.market_panel import panel, leaders
    from product.nz_election.tests.design_checks import provenance
    payloads, sources, hashes = load()
    current = {'markets': export.envelope(payloads['markets'], sources, 'offline-verification', 'verify',
               inputs=hashes, method='markets-v1', generated='2026-10-18T01:00:00Z')}
    export.validate_envelope(current['markets'], 'markets')
    require({r['family'] for r in payloads['markets']} == FAMILIES, 'three market families')
    html = panel(current, '2026-10-20T01:00:00Z')
    provenance(html)
    require(html.count('<table') == 3 and ATTRIBUTION in html and ' USD' in html, 'market contracts and terms')
    require('Update overdue' in html and 'Source observations are more than 36 hours old' in html, 'market stale states')
    require('Not available' in panel({}, '2026-10-20T01:00:00Z'), 'market unavailable')
    require(all(r['observed_at'] in html and 'https://polymarket.com/event/' + e['slug'] in html for e, r in leaders(payloads['markets']) if r), 'market observation and rules')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=['all', 'polls', 'thresholds', 'provenance', 'pipeline', 'coalitions', 'geography', 'candidates', 'electorates', 'social', 'home', 'home-routes', 'markets'])
    parser.add_argument('--data', type=Path)
    parser.add_argument('--site', type=Path)
    args = parser.parse_args()
    checks = {'polls': verify_polls, 'thresholds': verify_thresholds, 'provenance': verify_provenance, 'pipeline': verify_pipeline, 'coalitions': verify_coalitions, 'geography': verify_geography, 'candidates': verify_candidates, 'electorates': verify_electorates, 'social': verify_social, 'home': verify_home, 'home-routes': verify_home_routes, 'markets': verify_markets}
    with tempfile.TemporaryDirectory(prefix='nz-verify-') as tmp:
        root = Path(tmp)
        refresh(root / 'data', now='2026-10-17T01:00:00Z')
        envs = export.validate_bundle(root / 'data')
        if args.data:
            supplied = export.validate_bundle(args.data)
            if args.check in {'candidates', 'electorates', 'all'}:
                # Unpublished families render empty states; published families retain their checks.
                if 'candidates' in supplied:
                    require({r['electorate_id'] for r in supplied['candidates']['data'] if r['electorate_id']} ==
                            {r['id'] for r in config('electorates')}, 'supplied candidate coverage')
                if 'baseline-2023' in supplied:
                    require(len(supplied['baseline-2023']['data']) == 72, 'supplied original baselines')
        if args.site:
            product = args.site / 'nz-election' if (args.site / 'nz-election').is_dir() else args.site
            for route in config('routes') + [dict(path='electorates/' + r['slug'] + '/') for r in config('electorates')]:
                require((product / route['path'] / 'index.html').is_file(), 'site route ' + route['path'])
            export.validate_envelope(json.loads((product / 'build-manifest.json').read_text()), 'build-manifest')
            from product.nz_election.tools.check_visible_text import check_site as check_visible_text
            print(f'PASS visible text: {check_visible_text(product)} routes, no whitespace-free run over 200 characters')
            if (product / 'data').exists():
                export.validate_bundle(product / 'data')
        if args.site and args.check in {'home', 'all'}:
            from product.nz_election.pipeline.home_checks import check_site
            check_site(product, export.validate_bundle(product / 'data') if (product / 'data').exists() else {})
        if args.site:
            from product.nz_election.pipeline.disclosure_checks import check_site as check_disclosures
            print(f'PASS disclosures: {check_disclosures(product)} non-home routes')
        if args.site and args.check in {'home-routes', 'all'}:
            from product.nz_election.pipeline.route_checks import check_site
            check_site(product, export.validate_bundle(product / 'data') if (product / 'data').exists() else {})
        if args.site and args.check in {'markets', 'all'}:
            from product.nz_election.pipeline.market_panel import panel
            actual = export.validate_bundle(product / 'data') if (product / 'data').exists() else {}
            built = json.loads((product / 'build-manifest.json').read_text())['data']['built_at']
            require(panel(actual, built) in (product / 'methods/index.html').read_text(), 'supplied market provenance')
        for name, check in checks.items():
            if args.check in ('all', name):
                check(envs, root)
                print('PASS ' + name + {'geography': ': 64 general, 7 Māori', 'candidates': ': 71 electorates', 'electorates': ': 71 pages'}.get(name, ''))
        if args.check == 'all':
            print('PASS all')


if __name__ == '__main__':
    main()
