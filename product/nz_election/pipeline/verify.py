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
from product.nz_election.pipeline import export, campaign_checks as campaign
from product.nz_election.pipeline.average import trend, threshold_watch, select_window
from product.nz_election.pipeline.build import build, config
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.seats import project

OPTIONAL_CHECKS = frozenset({'night', 'waterfall'})


class MissingNightFamily(ValueError):
    def __init__(self):
        super().__init__('MISSING_NIGHT_FAMILY')


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
    require('<section id="trend"' in html and '<section id="recent-polls"' in html and validate_scripts(html), 'static poll history')
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
    require('id="home-seats"' not in (out / 'index.html').read_text(), 'no data build omits seat module')
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
    from product.nz_election.tests.design_checks import Document
    ids = {a['id'] for _, a in Document(html).nodes if 'id' in a}
    require({'coalition-explorer', 'coalition-title', 'source-seats', 'source-average', 'source-history'} <= ids,
            'retired explorer and source fragments remain resolvable')
    require('<fieldset' not in html and '<script' not in html, 'polls are server-rendered without interactive controls')
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
    require('class="local-margin"' not in detail(central, missing), 'absent baseline omitted')
    row = next(r for r in config('electorates') if r['slug'] == 'te-tai-tonga')
    require('id="candidates-title"' in detail(row, {}) and 'Not available' not in detail(row, {}), 'snapshot candidates without pipeline data')



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
    credits = {suffix: (data / ('social/credits.' + suffix)).read_bytes() for suffix in ('json', 'csv')}
    require(refresh_social(data, '2026-10-16', now=now, fixture=True,
                           send=fixture_send(), sleep=lambda _: None) == 'budget-spent', 'social rerun cap')
    require((data / 'social/daily.json').read_bytes() == original, 'social last-good retention')
    require(all((data / ('social/credits.' + suffix)).read_bytes() == content for suffix, content in credits.items()),
            'social spent-day ledger unchanged')
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
    from product.nz_election.pipeline.landmark_checks import check_site as check_landmarks
    check_landmarks(site)
    html = (site / 'social/poc/index.html').read_text()
    require('Proof of concept' in html and '@' not in html and '<svg' in html, 'social page present')
    require('under 5' in html and 'Withheld:' not in html, 'social small-cell suppression without placeholders')
    require('<svg' not in page(current, '2026-10-19T03:00:00Z'), 'social stale page withheld')
    absent = build(root / 'social-absent', root / 'social-empty-site', built=now)
    html = (absent / 'social/poc/index.html').read_text()
    require('unavailable' not in html and '<svg' not in html, 'social absent page')


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
        from product.nz_election.tools.check_visible_text import check_site as visible_check
        visible_check(site)
        from product.nz_election.pipeline.disclosure_checks import check_site as check_disclosures
        check_disclosures(site)
        from product.nz_election.pipeline.landmark_checks import check_site as check_landmarks
        check_landmarks(site)
        from product.nz_election.pipeline.market_budget_checks import check_site as check_market_budgets
        check_market_budgets(site)
        from product.nz_election.pipeline.source_budget_checks import check_site as check_source_budgets
        check_source_budgets(site)


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
    from product.nz_election.pipeline.market_budget_checks import check_markup
    check_markup(html)
    provenance(html)
    require(html.count('<table') == 3 and ATTRIBUTION in html and ' USD' in html, 'market contracts and terms')
    require('Update overdue' in html and 'Source observations are more than 36 hours old' in html, 'market stale states')
    require('Not available' in panel({}, '2026-10-20T01:00:00Z'), 'market unavailable')
    require(all(r['observed_at'] in html and 'https://polymarket.com/event/' + e['slug'] in html for e, r in leaders(payloads['markets']) if r), 'market observation and rules')


def verify_advance(envs, root, *, data=None):
    from product.nz_election.pipeline import advance
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.m3_checks import check_site
    if data is not None:
        supplied = export.validate_bundle(data)
        if 'advance-voting' in supplied:
            advance.validate(supplied['advance-voting']['data'])
    daily = advance.normalize([('2023-10-02', 10), ('2023-10-03', 20)], kind='daily', start='2023-10-02')
    require(daily[-1]['cumulative'] == 30, 'daily is not cumulative')
    gap = advance.normalize([('2023-10-02', 10), ('2023-10-04', 20)], kind='daily', start='2023-10-02')
    require(gap[-1]['cumulative'] is None and len(gap) == 2, 'missing day is not zero')
    gap = advance.normalize([('2023-10-02', 10), ('2023-10-04', 20)], kind='cumulative', start='2023-10-02')
    require(gap[-1]['daily'] is None and gap[-1]['cumulative'] == 20, 'retain supplied cumulative across gap')
    data = root / 'advance-data'
    daily_refresh(data, historical_advance=True)
    current = export.validate_bundle(data)
    require(current['advance-voting']['data'][-1]['cumulative'] == 1640204, 'captured 2023 total')
    site = build(data, root / 'advance-site', historical_advance=True)
    check_site(site, current)
    empty = build(root / 'advance-absent', root / 'advance-empty')
    check_site(empty, {})
    before = {ext: (data / ('advance-voting' + ext)).read_bytes() for ext in ('.json', '.csv')}
    def fail():
        raise ValueError('CAPTURE_HASH_MISMATCH')
    daily_refresh(data, loaders={'advance': fail})
    require(all((data / ('advance-voting' + ext)).read_bytes() == raw for ext, raw in before.items()), 'advance last-good bytes')


@campaign.report_failure
def verify_campaign(envs, root, *, data=None, site=None):
    from product.nz_election.pipeline.parties_page import page
    rows, _ = campaign.check_snapshots()
    if data is not None:
        campaign.require(data.is_dir(), campaign.DATA)
        envs = campaign.validate_bundle(data)
    campaign.no_total_funding(envs)
    try:
        verify_advance(envs, root, data=data)
    except ValueError:
        raise campaign.CampaignError(campaign.ADVANCE) from None
    # These facts are code-owned snapshots, not daily exports. Use exactly the
    # supplied daily bundle for rendering, without replacing it with fixtures.
    built = '2026-10-25T00:00:00Z'
    try:
        if site is None:
            html = page(envs, built)
        else:
            html = (site / 'parties/index.html').read_text()
            built = json.loads((site / 'build-manifest.json').read_text())['data']['built_at']
    except (KeyError, TypeError, ValueError, OSError):
        raise campaign.CampaignError(campaign.ABSENT) from None
    campaign.check_markup(html, rows, built[:4])
    from product.nz_election.pipeline.parties_page import load, supplemental
    absent = {**{n: load(n) for n in ('leaders', 'positions')},
              **{n: supplemental(n) for n in ('policy-links', 'party-list-tops')},
              'donations': []}
    campaign.check_markup(page({}, built, facts=absent), [], built[:4])


def verify_night(envs, root, *, data=None):
    from product.nz_election.pipeline.night_live import verify_contract
    verify_contract()
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.tests.night_smoke import check
    if data is None:
        data = root / 'night-data'
        daily_refresh(data)
    elif not (data / 'night/index.json').is_file():
        raise MissingNightFamily()
    validated = export.validate_bundle(data)
    check(data)
    from product.nz_election.pipeline.night_page import page
    from product.nz_election.pipeline.m3_checks import check_night_markup
    from product.nz_election.pipeline.landmark_checks import check_page
    html = page(validated, '2026-10-21T00:00:00Z')
    check_night_markup(html, validated)
    check_page(html)


def verify_waterfall(envs, root, *, data=None):
    from product.nz_election.pipeline import night, night_seats, fixtures
    if data is None:
        data = root / 'waterfall-data'
        from product.nz_election.pipeline.daily_refresh import daily_refresh
        daily_refresh(data, loaders={'night': night.load}, now='2026-10-22T00:00:00Z')
    if not (data / 'night/index.json').is_file():
        raise MissingNightFamily()
    validated = export.validate_bundle(data)
    night.validate(data)
    for seq in validated['night/index']['data']:
        refs = validated[seq['reference_path'][:-5]]['data'][0]
        for path in seq['snapshot_paths']:
            row = validated[path[:-5]]['data'][0]
            for e, result in row.get('leaders', {}).items():
                require(e in refs['electorates'], 'electorate reference')
                require(not result['leader'] or result['leader'] in refs['candidates'], 'leader reference')
                require(result['status'] != 'elected', 'provisional leaders')
            if 'allocation_input' in row:
                calc = night_seats.waterfall(row['allocation_input'], complete=True, capacity_verified=True)['calculation']
                require(calc['seats'] == fixtures.golden()['expectedSeats'], 'golden seat calculation')
            else:
                require(night_seats.waterfall(None)['calculation'] is None, 'incomplete suppression')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=['all', 'polls', 'thresholds', 'provenance', 'pipeline', 'coalitions', 'geography', 'candidates', 'electorates', 'social', 'home', 'home-routes', 'markets', 'advance', 'night', 'waterfall', 'campaign'])
    parser.add_argument('--require-year', type=int, metavar='YEAR',
                        help='require a valid registered advance capture for this year')
    parser.add_argument('--data', type=Path)
    parser.add_argument('--site', type=Path)
    parser.add_argument('--require', default=None, metavar='NAME[,NAME]',
                        help='require these checks, failing if their family is absent')
    return parser.parse_args(argv)


def main(args=None):
    args = parse_args() if args is None else args
    if getattr(args, 'require_year', None) is not None:
        from product.nz_election.pipeline import advance
        if args.check not in {'advance', 'all'}:
            raise ValueError('INVALID_REQUIRED_CHECK')
        if advance.load(year=args.require_year) is None:
            raise ValueError('MISSING_ADVANCE_CAPTURE')
    site_data = None
    if args.site:
        product = args.site / 'nz-election' if (args.site / 'nz-election').is_dir() else args.site
        site_data = product / 'data'
    night_data = args.data if args.data is not None else site_data
    checks = {'polls': verify_polls, 'thresholds': verify_thresholds, 'provenance': verify_provenance, 'pipeline': verify_pipeline, 'coalitions': verify_coalitions, 'geography': verify_geography, 'candidates': verify_candidates, 'electorates': verify_electorates, 'social': verify_social, 'home': verify_home, 'home-routes': verify_home_routes, 'markets': verify_markets, 'advance': verify_advance, 'night': verify_night, 'waterfall': verify_waterfall, 'campaign': verify_campaign}
    required = set(args.require.split(',')) if args.require is not None else set()
    if not required <= checks.keys():
        raise ValueError('INVALID_REQUIRED_CHECK')
    # Missing required data must win over stale inventory or site validation errors.
    if {'night', 'waterfall'} & (required | {args.check}):
        for location in (args.data, site_data):
            if location is not None and not (location / 'night/index.json').is_file():
                raise MissingNightFamily()
    with tempfile.TemporaryDirectory(prefix='nz-verify-') as tmp:
        root = Path(tmp)
        refresh(root / 'data', now='2026-10-17T01:00:00Z')
        envs = export.validate_bundle(root / 'data')
        if args.data:
            supplied = (campaign.validate_bundle(args.data) if args.check in {'campaign', 'all'}
                        else export.validate_bundle(args.data))
            if args.check in {'candidates', 'electorates', 'all'}:
                # Unpublished families render empty states; published families retain their checks.
                if 'candidates' in supplied:
                    require({r['electorate_id'] for r in supplied['candidates']['data'] if r['electorate_id']} ==
                            {r['id'] for r in config('electorates')}, 'supplied candidate coverage')
                if 'baseline-2023' in supplied:
                    require(len(supplied['baseline-2023']['data']) == 72, 'supplied original baselines')
        if args.site:
            for route in config('routes') + [dict(path='electorates/' + r['slug'] + '/') for r in config('electorates')]:
                require((product / route['path'] / 'index.html').is_file(), 'site route ' + route['path'])
            export.validate_envelope(json.loads((product / 'build-manifest.json').read_text()), 'build-manifest')
            from product.nz_election.tools.check_visible_text import check_site as check_visible_text
            print(f'PASS visible text: {check_visible_text(product)} routes, no whitespace-free run over 200 characters')
            if (product / 'data').exists():
                export.validate_bundle(product / 'data')
        if args.site and args.check in {'advance', 'all'}:
            from product.nz_election.pipeline.m3_checks import check_site as check_m3
            check_m3(product, export.validate_bundle(product / 'data') if (product / 'data').exists() else {})
        if args.site and args.check in {'home', 'all'}:
            from product.nz_election.pipeline.home_checks import check_site
            check_site(product, export.validate_bundle(product / 'data') if (product / 'data').exists() else {})
        if args.site:
            from product.nz_election.pipeline.disclosure_checks import check_site as check_disclosures
            print(f'PASS disclosures: {check_disclosures(product)} non-home routes')
            from product.nz_election.pipeline.landmark_checks import check_site as check_landmarks
            print(f'PASS landmarks: {check_landmarks(product)} routes including server-rendered tables')
            from product.nz_election.pipeline.market_budget_checks import check_site as check_market_budgets
            print(f'PASS market budgets: {check_market_budgets(product)} routes')
            from product.nz_election.pipeline.source_budget_checks import check_site as check_source_budgets
            print(f'PASS source-note budgets: {check_source_budgets(product)}')
        if args.site and args.check in {'home-routes', 'all'}:
            from product.nz_election.pipeline.route_checks import check_site
            check_site(product, export.validate_bundle(product / 'data') if (product / 'data').exists() else {})
        if args.site and args.check in {'markets', 'all'}:
            from product.nz_election.pipeline.market_panel import panel
            actual = export.validate_bundle(product / 'data') if (product / 'data').exists() else {}
            built = json.loads((product / 'build-manifest.json').read_text())['data']['built_at']
            require(panel(actual, built) in (product / 'methods/index.html').read_text(), 'supplied market provenance')
        for name, check in checks.items():
            if args.check in ('all', name) or name in required:
                if name in OPTIONAL_CHECKS and args.check == 'all' and night_data and not (night_data / 'night/index.json').is_file():
                    if name in required:
                        raise MissingNightFamily()
                    print(f'SKIP {name}: family absent (night/index.json)')
                    continue
                if name == 'campaign':
                    check(envs, root, data=args.data or (night_data if night_data and night_data.exists() else None),
                          site=product if args.site else None)
                elif name == 'advance':
                    check(envs, root, data=args.data or (night_data if night_data and night_data.exists() else None))
                elif name in {'night', 'waterfall'}:
                    check(envs, root, data=night_data)
                else:
                    check(envs, root)
                print('PASS ' + name + {'geography': ': 64 general, 7 Māori', 'candidates': ': 71 electorates', 'electorates': ': 71 pages'}.get(name, ''))
        if args.check == 'all':
            print('PASS all')


def cli(argv=None):
    args = parse_args(argv)
    check = args.check
    try:
        main(args)
    except Exception as exc:
        if isinstance(exc, MissingNightFamily):
            reason = 'MISSING_NIGHT_FAMILY'
        elif check in {'campaign', 'all'}:
            reason = exc.code if isinstance(exc, campaign.CampaignError) else campaign.DATA
        elif isinstance(exc, ValueError):
            reason = str(exc)
        else:
            raise
        raise SystemExit('FAIL ' + check + ': ' + reason) from None


if __name__ == '__main__':
    cli()
