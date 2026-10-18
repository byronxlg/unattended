"""Feed contracts, using the same validated captures as production rendering."""
from copy import deepcopy
from fractions import Fraction
import re

import pytest

from product.nz_election.pipeline import export
from product.nz_election.pipeline.build import build, config, home_presentation, PREFIX
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.home import page, watch_rows, electorate_summary, social
from product.nz_election.pipeline.presentation import election_countdown
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.tests.design_checks import Document, provenance

NOW = '2026-10-17T01:00:00Z'
MODULES = ('seats', 'polls', 'electorates', 'directory', 'social', 'method')


@pytest.fixture(scope='module')
def populated(tmp_path_factory):
    root = tmp_path_factory.mktemp('home')
    data = root / 'data'
    refresh(data, now=NOW, end_date='2026-07-18')
    daily_refresh(data, now=NOW)
    site = build(data, root / 'site/nz-election', built=NOW)
    return export.validate_bundle(data), site


def test_countdown_before_nz_midnight():
    assert election_countdown('2026-11-06T10:59:59Z') == '1 day until election day'


def test_countdown_on_election_day():
    assert election_countdown('2026-11-06T11:00:00Z') == 'Election day'


def test_countdown_after_election_day():
    assert election_countdown('2026-11-07T11:00:00Z') == 'Results'


def test_home_module_order(populated):
    _, site = populated
    html = (site / 'index.html').read_text()
    positions = [html.index(f'<section id="{name}"') for name in MODULES]
    assert positions == sorted(positions)
    assert html.count('<h1') == 1 and 'New Zealand votes on 7 November 2026' in html
    assert 'coalitions.mjs' not in html and 'Poll history' not in html
    provenance(html)


def test_poll_fragments_preserved(populated):
    envs, site = populated
    html = (site / 'polls/index.html').read_text()
    ids = {attrs['id'] for _, attrs in Document(html).nodes if 'id' in attrs}
    fixed = {'main', 'source-seats', 'coalition-explorer', 'coalition-title', 'source-average', 'source-thresholds', 'source-history', 'seats', 'polls', 'explorer'}
    assert fixed <= ids
    for poll in envs['polls']['data']:
        assert {poll['id'], 'source-' + poll['id']} <= ids
    for _, attrs in Document(html).nodes:
        if attrs.get('href', '').startswith('#'):
            assert attrs['href'][1:] in ids
    provenance(html)


def test_shared_seat_module_identical(populated):
    _, site = populated
    def module(route):
        html = (site / route / 'index.html').read_text()
        return html.split('<div class="seat-module">', 1)[1].split('</section>\n', 1)[0]
    assert module('') == module('polls')


def test_poll_figures_and_coverage(populated):
    from product.nz_election.pipeline.average import display
    from product.nz_election.pipeline.home import poll_figures
    envs, _ = populated
    average = envs['averages']['data'][-1]
    html = poll_figures(envs, home_presentation(envs, NOW))
    ranked = sorted(((p, d) for p, d in average['descriptive'].items() if p != 'others'), key=lambda item: (-Fraction(item[1]['value'], item[1]['scale']), item[0]))
    assert re.findall(r'class="leading">([^<]+)', html) == [display(d['value'], d['scale']) for _, d in ranked[:2]]
    selected = [p for p in envs['polls']['data'] if p['id'] in average['poll_ids']]
    assert f'{len({p["pollster"] for p in selected})} pollsters' in html
    assert 'coverage differs by party' in html and 'Missing observations are not zero' in html
    assert 'CC BY-SA 4.0' in html


def test_watch_selection_and_boundary_exclusion(populated):
    envs, _ = populated
    expected = []
    correspondence = {e['new_id']: e for e in config('electorate-correspondence')['entries']}
    baseline = {r['old_electorate_id']: r for r in envs['baseline-2023']['data']}
    for row in config('electorates'):
        e = correspondence[row['stats_id']]
        if e['relationship'] != 'unchanged' and row['stats_id'] != '008':
            continue
        votes = sorted((baseline[e['old_ids'][0]]['candidate_votes'] or []), key=lambda v: -v['votes'])
        if len(votes) >= 2 and votes[0]['votes'] > votes[1]['votes']:
            expected.append((votes[0]['votes'] - votes[1]['votes'], row['id']))
    assert [(m, i) for m, i, _, _ in watch_rows(envs)] == sorted(expected)[:6]
    east = next(r for r in config('electorates') if r['stats_id'] == '008')
    assert electorate_summary(east, envs)[0] is not None
    changed = deepcopy(envs)
    for row in changed['baseline-2023']['data']:
        if row['old_electorate_id'] == 1:
            row['candidate_votes'] = [dict(party='A', votes=2), dict(party='B', votes=1)]
        if row['old_electorate_id'] == 9:
            row['candidate_votes'] = [dict(party='A', votes=2), dict(party='B', votes=1)]
    assert watch_rows(changed)[0][2]['stats_id'] == '008'
    assert all(r['stats_id'] != '001' for _, _, r, _ in watch_rows(changed))


def test_watch_missing_and_tied_baselines(populated):
    from product.nz_election.pipeline.home import watch
    envs, _ = populated
    changed = deepcopy(envs)
    for row in changed['baseline-2023']['data']:
        row['candidate_votes'] = [dict(party='A', votes=2), dict(party='B', votes=2)]
    assert watch_rows(changed) == []
    assert 'Fewer than six' in watch(changed)
    for row in changed['baseline-2023']['data']:
        row['candidate_votes'] = None
    assert watch_rows(changed) == []
    del changed['candidates']
    assert 'Not available' in watch(changed) and '<article>' not in watch(changed)


def test_no_inferred_incumbents(populated):
    envs, site = populated
    html = (site / 'index.html').read_text()
    assert 'incumbent' not in html.lower()
    assert 'on the original boundaries' in html and 'Changed boundaries' in html
    for _, _, row, _ in watch_rows(envs):
        for candidate in envs['candidates']['data']:
            if candidate['electorate_id'] == row['id']:
                from html import escape
                assert escape(candidate['name'] + ' (' + candidate['party_id'] + ')') in html


def test_directory_all_71(populated):
    _, site = populated
    html = (site / 'index.html').read_text().split('<section id="directory"')[1].split('</section>')[0]
    assert len(re.findall(r'<li>', html)) == 71
    assert all(PREFIX + 'electorates/' + r['slug'] + '/' in html for r in config('electorates'))
    assert 'Boundary changed; 2023 holder not comparable' in html


def test_home_missing_families(populated):
    envs, _ = populated
    for absent in ('polls', 'candidates', 'baseline-2023', 'social/daily'):
        missing = deepcopy(envs)
        missing.pop(absent, None)
        if absent == 'polls':
            missing.pop('averages', None)
            missing.pop('seats', None)
        html = page(missing, NOW, home_presentation(missing, NOW))
        provenance(html)
        assert 'Not available' in html
    html = page({}, NOW, home_presentation({}, NOW))
    provenance(html)
    assert 'No data yet' in html and 'No seat estimate available yet' in html
    assert len(re.findall(r'<li>', html)) == 71


def test_home_navigation(populated):
    _, site = populated
    for path in site.rglob('index.html'):
        html = path.read_text()
        nav = html.split('<header>')[1].split('</header>')[0]
        assert nav.count(f'<a href="{PREFIX}"') == 2
        assert nav.count(f'<a href="{PREFIX}polls/"') == 2
        assert html.count('aria-current="page"') == (0 if path.parent.parent.name == 'electorates' else 2)
        assert ('aria-label="Home sections"' in html) == (path == site / 'index.html')


def test_home_html_css_budget(populated, tmp_path):
    _, site = populated
    empty = build(tmp_path / 'missing', tmp_path / 'out', built=NOW)
    for root in (site, empty):
        assert (root / 'index.html').stat().st_size + (root / 'styles.css').stat().st_size < 200_000


def test_home_social_retains_dated_aggregate(tmp_path):
    from product.nz_election.pipeline.social import refresh_social, fixture_send
    from product.nz_election.pipeline.social_page import page as poc
    refresh_social(tmp_path / 'data', '2026-10-16', now=NOW, fixture=True, send=fixture_send(), sleep=lambda _: None)
    envs = export.validate_bundle(tmp_path / 'data')
    html = social(envs, '2026-10-20T01:00:00Z')
    assert '<svg' in html and '16 October 2026' in html and '240 posts' in html
    assert 'Update overdue' in html and 'synthetic examples' in html
    assert PREFIX + 'social/poc/#social-method' in html
    assert 'under 5' in html and 'Share withheld: fewer than 20 posts' in html
    assert '<svg' not in poc(envs, '2026-10-20T01:00:00Z')
    provenance(html)


def test_screenshot_count_inventory():
    from product.nz_election.tests.design_states import STATES
    routes = len(config('routes')) + len(config('electorates'))
    assert routes == 79
    assert len(STATES) * 2 + 1 == 33
    assert 2 * routes + 9 + 33 + 13 + 4 + 2 == 219


def test_supplied_home_verifier_rejects_missing_fragments(populated, tmp_path):
    from product.nz_election.pipeline.home_checks import check_site
    import shutil
    envs, site = populated
    damaged = tmp_path / 'damaged'
    shutil.copytree(site, damaged)
    target = damaged / 'polls/index.html'
    target.write_text(target.read_text().replace('id="coalition-explorer"', 'id="removed-explorer"'))
    with pytest.raises(ValueError, match='legacy fragment inventory'):
        check_site(damaged, envs)
