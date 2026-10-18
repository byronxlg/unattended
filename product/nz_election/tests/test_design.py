"""Design numbers are checked against generated fixture pages, not templates."""
from decimal import Decimal
import json
from pathlib import Path
import re
import struct

import pytest

from product.nz_election.pipeline.build import build, config, default_scenario, home_sentence
from product.nz_election.pipeline.refresh import refresh, PRODUCT
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline import export, coalitions
from product.nz_election.tests.design_checks import provenance, transfer_bytes
from product.nz_election.tests.screenshots import contrast


@pytest.mark.parametrize(('seats', 'majority', 'expected'), [
    ({'nat': 65, 'lab': 55}, 61, 'National: 65 calculated seats, reaching the assumed majority of 61.'),
    ({'nat': 43, 'lab': 42, 'grn': 42}, 64, 'National leads with 43 calculated seats; no party reaches the assumed majority of 64.'),
    ({'nat': 60, 'lab': 60}, 61, 'Labour and National are level on 60 calculated seats; no party reaches the assumed majority of 61.'),
    ({'nat': 40, 'lab': 40, 'grn': 40}, 61, 'Green, Labour and National are level on 40 calculated seats; no party reaches the assumed majority of 61.'),
    (None, None, 'No seat estimate available yet.'),
])
def test_home_sentence(seats, majority, expected):
    assert home_sentence(dict(seats=seats, assumed_majority=majority)) == expected
    assert 'bloc' not in expected


def rgb(hex_colour):
    return [int(hex_colour[i:i+2], 16) for i in (1, 3, 5)]


@pytest.mark.parametrize('mode', ['light', 'night'])
def test_all_token_and_party_pairings(mode):
    css = (PRODUCT / 'web/styles.css').read_text()
    tables = re.findall(r':root\{([^}]+)', css)
    tokens = dict(re.findall(r'--(\w+):(#[0-9A-Fa-f]{6})', tables[mode == 'night']))
    assert set(tokens) == {'paper', 'ink', 'grey', 'rule', 'surface', 'tick', 'focus', 'left', 'right', 'notice'} | ({'live'} if mode == 'night' else set())
    if mode == 'light':
        assert {k: tokens[k] for k in ('paper', 'ink', 'grey', 'rule', 'left', 'right', 'notice', 'focus')} == dict(paper='#FFFFFF', ink='#222222', grey='#6B6B6B', rule='#949494', left='#2F6DB5', right='#C94D49', notice='#FFF6CC', focus='#005EA8')
    for fg in ('ink', 'grey'):
        assert contrast(rgb(tokens[fg]), rgb(tokens['notice'])) >= Decimal('4.5')
    for fg in ('ink', 'grey', 'left', 'right'):
        for bg in ('paper', 'surface'):
            assert contrast(rgb(tokens[fg]), rgb(tokens[bg])) >= Decimal('4.5'), (mode, fg, bg)
    for fg in ('rule', 'ink', 'focus'):
        for bg in (('paper',) if fg == 'rule' else ('paper', 'surface')):
            assert contrast(rgb(tokens[fg]), rgb(tokens[bg])) >= 3, (mode, fg, bg)
    # Selection ticks sit on paper in an ink box, never behind text.
    assert 'border:solid var(--tick)' in css
    assert contrast(rgb(tokens['tick']), rgb(tokens['paper'])) >= 3
    if mode == 'night':
        assert contrast(rgb(tokens['live']), rgb(tokens['paper'])) >= Decimal('4.5')
    for party, row in config('party-colours').items():
        fill = row['colour']
        assert len(rgb(fill)) == 3
        # A fill may merge with its ink border; the complete silhouette against paper
        # still has the required boundary. Party names and counts carry its identity.
        assert max(contrast(rgb(fill), rgb(tokens['paper'])),
                   contrast(rgb(tokens['ink']), rgb(tokens['paper']))) >= 3, (mode, party)
    assert '.segment{position:relative;border:1px solid var(--ink)' in css
    assert re.search(r'\.lane\{[^}]*color:var\(--ink\)', css)


@pytest.fixture(scope='module')
def built_design(tmp_path_factory):
    root = tmp_path_factory.mktemp('design')
    data = root / 'data'
    refresh(data, now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    daily_refresh(data, now='2026-10-17T01:00:00Z')
    site = build(data, root / 'site/nz-election', built='2026-10-17T01:00:00Z')
    return data, site


def test_default_scenario_is_unselected(built_design):
    data, site = built_design
    envs = export.validate_bundle(data)
    inputs = coalitions.inputs(envs['averages']['data'][-1], envs['seats']['data'], '0' * 64)
    assert inputs['initial']['selected'] == []
    result = default_scenario(envs)
    assert result == coalitions.scenario(inputs, inputs['initial'])
    html = (site / 'index.html').read_text()
    from product.nz_election.pipeline.build import seat_topline, label
    assert seat_topline(result) in html
    for party, seats in result['seats'].items():
        assert f'{label(party)}: {seats} seats' in html


def test_built_routes_have_source_targets(built_design):
    _, site = built_design
    pages = list(site.rglob('index.html'))
    expected = [r['path'] for r in config('routes')] + ['electorates/' + r['slug'] + '/' for r in config('electorates')]
    assert len(expected) == len(set(expected)) == 79
    assert {p.relative_to(site).as_posix() for p in site.rglob('index.html')} == {p + 'index.html' for p in expected}
    for page in pages:
        try:
            provenance(page.read_text())
        except AssertionError as exc:
            raise AssertionError(f'{page}: {exc}') from exc


def test_absent_routes_have_source_targets(tmp_path):
    site = build(tmp_path / 'absent', tmp_path / 'site/nz-election')
    for page in site.rglob('index.html'):
        provenance(page.read_text())


def test_real_first_view_budget(built_design):
    _, site = built_design
    explorer_assets = {'coalitions.mjs', 'allocator.mjs', 'data/averages.json', 'data/seats.json'}
    for page in ('index.html', 'polls/index.html'):
        css = (site / 'styles.css').stat().st_size
        total, files = transfer_bytes(site, page)
        assert css < 16_000, f'CSS_BYTES: {page}: {css}'
        assert total < 100_000, f'FIRST_VIEW_GZIP_BYTES: {page}: {total}: {files}'
        assert {f'fonts/{name}.woff2' for name in ('libre-franklin-400', 'libre-franklin-700', 'jetbrains-mono-400')} <= files.keys()
        assert {'favicon.svg', 'icon-180.png', 'manifest.webmanifest', page, 'styles.css'} <= files.keys()
        if page == 'index.html':
            assert not explorer_assets & files.keys()
        else:
            assert explorer_assets <= files.keys()
        assert not any('2025' in name for name in files), page
    assert not list(site.rglob('axe*'))


def test_source_dates_and_identity(built_design):
    _, site = built_design
    html = (site / 'index.html').read_text()
    assert 'Fieldwork ended <time datetime=' in html
    assert 'Retrieved <time datetime=' in html and 'NZDT' in html
    assert 'Final results <time datetime="2023-11-03">' in (site / 'methods/index.html').read_text()
    assert html.index('id="source-seats"') < html.index('Theoretical seats and overhang')
    manifest = json.loads((site / 'manifest.webmanifest').read_text())
    assert manifest['display'] == 'standalone'
    for size in (180, 512):
        raw = (site / f'icon-{size}.png').read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', raw[16:24]) == (size, size)
    assert 'viewBox="0 0 32 32"' in (site / 'favicon.svg').read_text()


def test_stale_allocation_not_current(built_design, tmp_path):
    data, _ = built_design
    envs = export.validate_bundle(data)
    envs['polls']['run_url'] = 'https://github.com/example/repo/actions/runs/1'
    from product.nz_election.pipeline.build import polls_page
    html = polls_page(envs, '2026-10-17T04:00:01Z')
    assert 'Update overdue.' in html
    assert 'class="strip"' not in html
    assert 'data-averages=' not in html


@pytest.mark.parametrize(('cadence', 'seconds'), [('hourly', 10800), ('daily', 129600), ('live', 90)])
def test_staleness_boundaries(cadence, seconds):
    from datetime import datetime, timedelta, timezone
    from product.nz_election.pipeline.presentation import overdue
    start = datetime(2026, 10, 17, tzinfo=timezone.utc)
    assert not overdue(start.isoformat(), (start + timedelta(seconds=seconds)).isoformat(), cadence)
    assert overdue(start.isoformat(), (start + timedelta(seconds=seconds + 1)).isoformat(), cadence)
    assert overdue(None, start.isoformat(), cadence)


def test_twelve_state_fixtures(tmp_path):
    from product.nz_election.tests.design_states import STATES, COHERENT, CATEGORIES, fixture
    assert len(CATEGORIES) == 12 and set(CATEGORIES.values()) <= set(STATES)
    assert len(STATES) == len(set(STATES))
    for state in STATES:
        site, route = fixture(tmp_path, state)
        path = route.split('#')[0]
        html = (site / 'nz-election' / path / 'index.html').read_text()
        provenance(html)
        if state in COHERENT:
            assert 'class="strip"' in html
        if state == 'unavailable':
            assert 'No data yet.' in html
        if state == 'validation-error':
            assert 'update failed; showing previous data' in html
        if state == 'stale':
            assert 'Update overdue.' in html and 'class="strip"' not in html
        if state == 'missing-baseline':
            assert 'No 2023 candidate results for this electorate' in html
        if state == 'unresolved':
            assert 'Not matched: Kāpiti (local poll)' in html


def test_state_category_copy(tmp_path):
    from product.nz_election.tests.design_states import fixture
    for state, words in [('no-data', 'No data yet. Polls are checked hourly.'),
                         ('allocation-tie', 'Tie for the last seat between National and Labour; shown unassigned.'),
                         ('source-conflict', 'Comparison unresolved: no reviewed boundary correspondence.'),
                         ('offline', 'fixture run')]:
        site, route = fixture(tmp_path, state)
        assert words in (site / 'nz-election' / route / 'index.html').read_text()


def test_self_hosted_font_contract():
    css = (PRODUCT / 'web/styles.css').read_text()
    for family in ('Libre Franklin', 'JetBrains Mono'):
        assert f'font-family:"{family}"' in css
    assert css.count('font-display:swap') == 3
    assert '"Helvetica Neue"' not in css
    for name in ('libre-franklin-400', 'libre-franklin-700', 'jetbrains-mono-400'):
        raw = (PRODUCT / 'web/fonts' / (name + '.woff2')).read_bytes()
        assert raw[:4] == b'wOF2'
    for name in ('LibreFranklin-OFL.txt', 'JetBrainsMono-OFL.txt'):
        assert 'SIL OPEN FONT LICENSE Version 1.1' in (PRODUCT / 'web/fonts' / name).read_text()
