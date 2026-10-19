"""Absent facts never become public placeholders; snapshot facts stay attributed."""
import pytest
from product.nz_election.tools.check_visible_text import check_absent_text, check_site
from product.nz_election.pipeline.electorate_pages import source, detail
from product.nz_election.pipeline.snapshot_views import result, load
from product.nz_election.pipeline.build import config
from product.nz_election.tests.test_home import populated  # noqa: F401


@pytest.mark.parametrize('text', ['Not available', 'UNAVAILABLE', 'pending', 'Withheld', 'missing', 'not supplied', 'not\n available'])
def test_absence_gate_rejects_text_and_alternatives(text):
    for html in [f'<p>{text}</p>', f'<details><p>{text}</p></details>', f'<img alt="{text}">']:
        with pytest.raises(ValueError, match='ABSENT_TEXT'):
            check_absent_text(html)


def test_populated_public_routes_and_map(populated):
    envs, site = populated
    assert check_site(site) == 79
    html = (site / 'index.html').read_text()
    assert html.count('<a href="/unattended/nz-election/electorates/') >= 71
    assert '2023 holders on original boundaries' in html
    assert 'stroke-width="3.5"' in html
    assert 'home-leaders' in html and 'people/christopher-luxon.webp' in html
    for c in load('leaders'):
        if c.get('photo'):
            assert c['photo']['source_url'].replace('&', '&amp;') in (site / 'methods/index.html').read_text()
    row = next(r for r in config('electorates') if r['slug'] == 'port-waikato')
    actual = result(row, envs)
    winner = next(r for r in load('port-waikato-2023') if r['winner'])
    assert actual['margin'] == winner['margin']
    assert actual['name'] == winner['name']
    assert 'by-election' in detail(row, envs)


def test_failure_date_and_full_warning_stay_reachable():
    entry = dict(id='E', url='https://elections.nz/', licence='Copyright Electoral Commission',
                 fetched_at='2026-10-17T01:00:00Z', history_url=None)
    envs = {'candidates': dict(source=[entry], run_url='offline-verification'),
            'status': dict(data=[dict(dataset='candidates', state='stale', error_code='parse_drift',
                  last_success_at='2026-10-18T01:00:00Z', last_attempt_at='2026-10-19T01:00:00Z')])}
    compact = source(envs, 'candidates', '2026-10-19T05:00:00Z')
    assert 'Data to 18 Oct' in compact and 'methods/#records-candidates' in compact
    assert compact.count('<a ') == 1
    assert 'update failed' in source(envs, 'candidates', '2026-10-19T05:00:00Z', full=True)


def test_gate_allows_reasons_only_in_methods(tmp_path):
    (tmp_path / 'methods').mkdir()
    (tmp_path / 'methods/index.html').write_text('<p>Missing input.</p>')
    (tmp_path / 'index.html').write_text('<p>Election information.</p>')
    assert check_site(tmp_path) == 2
    (tmp_path / 'og').mkdir()
    (tmp_path / 'og/home.html').write_text('<p>Not available.</p>')
    with pytest.raises(ValueError, match='ABSENT_TEXT'):
        check_site(tmp_path)


def test_map_never_assigns_a_tied_winner(populated):
    from copy import deepcopy
    envs, _ = populated
    envs = deepcopy(envs)
    row = next(r for r in config('electorates') if r['slug'] == 'nelson')
    baseline = next(r for r in envs['baseline-2023']['data'] if r['old_electorate_id'] == row['baseline_ids'][0])
    ranked = sorted(baseline['candidate_votes'], key=lambda r: -r['votes'])
    ranked[1]['votes'] = ranked[0]['votes']
    assert result(row, envs) is None
