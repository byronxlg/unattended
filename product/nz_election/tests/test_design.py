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
    (None, None, 'New Zealand votes on 7 November 2026.'),
])
def test_home_sentence(seats, majority, expected):
    assert home_sentence(dict(seats=seats, assumed_majority=majority)) == expected
    assert 'bloc' not in expected


def rgb(hex_colour):
    return [int(hex_colour[i:i+2], 16) for i in (1, 3, 5)]


@pytest.mark.parametrize('mode', ['light', 'night'])
def test_all_token_and_party_pairings(mode):
    from product.nz_election.pipeline.home_graphics import PARTIES
    css = (PRODUCT / 'web/styles.css').read_text()
    tables = re.findall(r':root\{([^}]+)', css)
    light = dict(re.findall(r'--([\w-]+):(#[0-9A-Fa-f]{6})', tables[0]))
    # Dark mode overrides the light table; a token it leaves out keeps its light value.
    tokens = {**light, **dict(re.findall(r'--([\w-]+):(#[0-9A-Fa-f]{6})', tables[mode == 'night']))}
    assert {'paper', 'wash', 'ink', 'soft', 'grey', 'rule', 'hair', 'surface', 'tick', 'focus', 'left', 'right',
            'notice', 'mast', 'mast-ink', 'accent'} <= set(tokens)
    for fg in ('ink', 'soft', 'grey'):
        for bg in ('paper', 'surface', 'wash', 'notice'):
            assert contrast(rgb(tokens[fg]), rgb(tokens[bg])) >= Decimal('4.5'), (mode, fg, bg)
    for fg in ('left', 'right'):
        for bg in ('paper', 'surface'):
            assert contrast(rgb(tokens[fg]), rgb(tokens[bg])) >= Decimal('4.5'), (mode, fg, bg)
    # Control boundaries (inputs use --grey, buttons and boxes --ink) and the focus ring.
    for fg in ('grey', 'ink', 'focus'):
        for bg in ('paper', 'surface'):
            assert contrast(rgb(tokens[fg]), rgb(tokens[bg])) >= 3, (mode, fg, bg)
    # Masthead tabs: text and the current-tab accent on the dark band.
    assert contrast(rgb(tokens['mast-ink']), rgb(tokens['mast'])) >= Decimal('4.5')
    assert contrast(rgb(tokens['accent']), rgb(tokens['mast'])) >= 3
    # Selection ticks sit on paper in an ink box, never behind text.
    assert 'border:solid var(--tick)' in css
    assert contrast(rgb(tokens['tick']), rgb(tokens['paper'])) >= 3
    for party in PARTIES + ('other',):
        fill = tokens['p-' + party]
        # A fill may merge with its ink border; the complete silhouette against paper
        # still has the required boundary. Party names and counts carry its identity.
        assert max(contrast(rgb(fill), rgb(tokens['paper'])),
                   contrast(rgb(tokens['ink']), rgb(tokens['paper']))) >= 3, (mode, party)
    for party in config('party-colours'):
        assert len(rgb(config('party-colours')[party]['colour'])) == 3
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
    from product.nz_election.pipeline.home import seat_hero
    from product.nz_election.pipeline.build import home_presentation
    hero = seat_hero(envs, '2026-10-17T01:00:00Z', home_presentation(envs, '2026-10-17T01:00:00Z'))
    assert hero in html
    text = ' '.join(re.sub(r'<[^>]+>', ' ', hero).split())
    assert f'{sum(result["seats"].get(p, 0) for p in ("nat", "act", "nzf"))} Government' in text
    assert f'{sum(result["seats"].get(p, 0) for p in ("lab", "grn", "tpm"))} Opposition' in text


def test_built_routes_have_source_targets(built_design):
    _, site = built_design
    pages = list(site.rglob('index.html'))
    expected = [r['path'] for r in config('routes')] + ['electorates/' + r['slug'] + '/' for r in config('electorates')]
    assert len(expected) == len(set(expected)) == 82
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
    explorer_assets = {'allocator.mjs', 'data/averages.json', 'data/seats.json'}
    for page in ('index.html', 'polls/index.html'):
        total, files = transfer_bytes(site, page)
        assert {f'fonts/{name}.woff2' for name in ('libre-franklin-400', 'libre-franklin-700', 'jetbrains-mono-400')} <= files.keys()
        assert {'favicon.svg', 'icon-180.png', 'manifest.webmanifest', page, 'styles.css'} <= files.keys()
        assert not explorer_assets & files.keys()
        modules = {name for name in files if name.endswith('.mjs')}
        assert modules == ({'home-live.mjs'} if page == 'index.html' else set())
        if page == 'index.html':
            assert files['home-live.mjs'] < 2048, f"HOME_CLIENT_GZIP_BYTES: {files['home-live.mjs']}"
        if page == 'polls/index.html':
            assert 'polls.css' in files
        assert not any('2025' in name for name in files), page
    assert not list(site.rglob('axe*'))


def test_source_dates_and_identity(built_design):
    _, site = built_design
    html = (site / 'methods/index.html').read_text()
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
    assert 'class="hemicycle"' not in html
    assert 'data-averages=' not in html


@pytest.mark.parametrize(('cadence', 'seconds'), [('hourly', 10800), ('daily', 129600), ('live', 90)])
def test_staleness_boundaries(cadence, seconds):
    from datetime import datetime, timedelta, timezone
    from product.nz_election.pipeline.presentation import overdue
    start = datetime(2026, 10, 17, tzinfo=timezone.utc)
    assert not overdue(start.isoformat(), (start + timedelta(seconds=seconds)).isoformat(), cadence)
    assert overdue(start.isoformat(), (start + timedelta(seconds=seconds + 1)).isoformat(), cadence)
    assert overdue(None, start.isoformat(), cadence)


def test_live_state_fixtures(tmp_path):
    from product.nz_election.tests.design_states import STATES, COHERENT, CATEGORIES, fixture
    assert len(CATEGORIES) == 10 and set(CATEGORIES.values()) <= set(STATES)
    assert len(STATES) == len(set(STATES))
    for state in STATES:
        site, route = fixture(tmp_path, state)
        path = route.split('#')[0]
        html = (site / 'nz-election' / path / 'index.html').read_text()
        provenance(html)
        if state in COHERENT:
            assert 'class="hemicycle"' in html
        if state == 'unavailable':
            assert 'id="home-seats"' not in html
        if state == 'validation-error':
            assert 'update failed; showing previous data' in html
        if state == 'stale':
            assert 'Update overdue.' in html and 'class="hemicycle"' not in html
        if state == 'missing-baseline':
            assert 'class="local-margin"' not in html and 'candidate votes' not in html
        if state == 'unresolved':
            assert 'Not matched: Kāpiti (local poll)' in html


def test_state_category_copy(tmp_path):
    from product.nz_election.tests.design_states import fixture
    for state, words in [('no-data', 'New Zealand votes on 7 November'),
                         ('allocation-tie', 'Tie for the last seat between National and Labour; shown unassigned.'),
                         ('source-conflict', 'id="candidates-title"'),
                         ('offline', 'fixture run')]:
        site, route = fixture(tmp_path, state)
        assert words in (site / 'nz-election' / route / 'index.html').read_text()


def test_self_hosted_font_contract():
    css = (PRODUCT / 'web/styles.css').read_text()
    for family in ('Libre Franklin', 'JetBrains Mono'):
        assert f'font-family:"{family}"' in css
    assert css.count('font-display:swap') == css.count('@font-face') >= 3
    assert '"Helvetica Neue"' not in css
    for name in ('libre-franklin-400', 'libre-franklin-600', 'libre-franklin-700', 'libre-franklin-800', 'jetbrains-mono-400'):
        raw = (PRODUCT / 'web/fonts' / (name + '.woff2')).read_bytes()
        assert raw[:4] == b'wOF2'
    for name in ('LibreFranklin-OFL.txt', 'JetBrainsMono-OFL.txt'):
        assert 'SIL OPEN FONT LICENSE Version 1.1' in (PRODUCT / 'web/fonts' / name).read_text()


@pytest.mark.parametrize('chart', ['map', 'trend', 'header'])
def test_phone_rendered_type_and_targets(built_design, tmp_path, chart):
    import subprocess
    _, site = built_design
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('type_scale_browser.py')),
                             '--site', str(site.parent), '--chart', chart, '--out', str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS ' + chart in result.stdout


def landmark_links(html):
    from product.nz_election.pipeline.content_checks import Tree, Node

    landmarks = {'banner': [], 'contentinfo': []}
    sectioning = {'article', 'aside', 'main', 'nav', 'section'}

    def visit(node, scoped=False):
        role = node.attrs.get('role')
        implicit = {'header': 'banner', 'footer': 'contentinfo'}.get(node.tag)
        if role in landmarks:
            landmarks[role].append(node)
        elif role is None and implicit and not scoped:
            landmarks[implicit].append(node)
        for child in node.children:
            if isinstance(child, Node):
                visit(child, scoped or node.tag in sectioning)

    visit(Tree(html).root)
    assert len(landmarks['banner']) == 1, 'Expected exactly one banner header'
    assert len(landmarks['contentinfo']) == 1, 'Expected exactly one contentinfo footer'

    def links(node):
        found = {node.attrs['href']} if node.tag == 'a' and 'href' in node.attrs else set()
        for child in node.children:
            if isinstance(child, Node):
                found.update(links(child))
        return found

    return links(landmarks['banner'][0]) | links(landmarks['contentinfo'][0])


@pytest.mark.parametrize('attrs', ['', ' class="masthead" id="top"', ' role="banner"'])
def test_design_landmarks_allow_attributes_and_ignore_section_headers(attrs):
    html = (f'<header{attrs}><nav><a href="/home/">Home</a></nav></header>'
            '<main><header><a href="/local/">Local</a></header>'
            '<article><footer>Article credit</footer></article></main>'
            '<footer class="footer" role="contentinfo"><a href="/methods/">Methods</a></footer>')
    assert landmark_links(html) == {'/home/', '/methods/'}


@pytest.mark.parametrize('html,message', [
    ('<main><header>Local</header></main><footer></footer>', 'banner'),
    ('<header></header><footer></footer><footer class="extra"></footer>', 'contentinfo'),
    ('<header></header><header id="extra"></header><footer></footer>', 'banner'),
    ('<header></header><main><footer>Local</footer></main>', 'contentinfo'),
])
def test_design_landmarks_reject_missing_or_duplicate(html, message):
    with pytest.raises(AssertionError, match=message):
        landmark_links(html)


def test_header_footer_link_every_registered_route(built_design):
    from product.nz_election.pipeline.build import PREFIX
    _, site = built_design
    expected = {PREFIX + route['path'] for route in config('routes')}
    for path in site.rglob('index.html'):
        links = landmark_links(path.read_text())
        assert expected <= links, (path, expected - links)
