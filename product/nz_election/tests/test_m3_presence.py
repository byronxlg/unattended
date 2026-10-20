"""Absent campaign modules and historical verification cannot leak into production."""
import pytest
from product.nz_election.pipeline import advance, export
from product.nz_election.pipeline.campaign_page import page
from product.nz_election.pipeline.m3_checks import check_markup
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh


def test_absent_campaign_modules_not_rendered(tmp_path):
    html = page({})
    assert check_markup(html, {})
    assert '<h2' not in html and '<svg' not in html and '<table' not in html
    assert 'vote.nz' in html
    site = build(tmp_path / 'absent', tmp_path / 'rendered')
    actual = (site / 'campaign/index.html').read_text()
    assert 'data-campaign-module' not in actual and 'no campaign totals' not in actual
    with pytest.raises(ValueError, match='M3_EMPTY_MODULE'):
        check_markup(html + '<h2>Advance votes</h2>', {})


def test_historical_requires_labelled_verification(tmp_path):
    daily_refresh(tmp_path / 'data', historical_advance=True)
    with pytest.raises(ValueError, match='HISTORICAL_ADVANCE_REQUIRES_VERIFICATION'):
        build(tmp_path / 'data', tmp_path / 'production')
    site = build(tmp_path / 'data', tmp_path / 'verification', historical_advance=True)
    html = (site / 'campaign/index.html').read_text()
    envs = export.validate_bundle(tmp_path / 'data')
    assert check_markup(html, envs, historical=True)
    assert '1,640,204' in html and 'Offline verification: historical 2023' in html
    assert 'data-campaign-module' not in page(envs)


def test_advance_export_validates_derivation():
    data, sources, hashes = advance.load(historical=True)
    env = export.envelope(data['advance-voting'], sources, 'offline-verification', 'test', inputs=hashes, method='advance-v1', generated='2026-10-20T01:00:00Z')
    env['data'][-1]['cumulative'] += 1
    with pytest.raises(ValueError, match='INVALID_ADVANCE'):
        export.validate_envelope(env, 'advance-voting')


@pytest.mark.parametrize('fragment', [
    '<h3>Advance voting</h3>',
    '<figure></figure>',
    '<p>No campaign totals are available here yet.</p>',
    '<H3 class="quiet"><span>Advance</span> voting</H3>',
    '<h1>Advance voting</h1>',
    '<FIGURE aria-label="Advance votes" />',
    '<p>No <strong>campaign totals</strong> are available here yet.</p>',
    '<h6>Advance votes</h6>',
])
def test_absent_campaign_structure_rejects_empty_content(fragment):
    with pytest.raises(ValueError, match='^M3_EMPTY_MODULE$'):
        check_markup(page({}) + fragment, {})


def test_preopening_zeros_do_not_hide_voting_window():
    from copy import deepcopy
    from datetime import date
    from product.nz_election.pipeline.campaign_page import eligible, source
    payload, sources, hashes = advance.load(historical=True)
    rows = deepcopy(payload['advance-voting'])
    shift = date(2026, 10, 26) - date(2023, 10, 2)
    for row in rows:
        for key in ('date', 'observed_at', 'span_start'):
            row[key] = (date.fromisoformat(row[key]) + shift).isoformat()
        row['id'] = 'advance-' + row['date']
    env = export.envelope(rows, sources, 'offline-verification', 'test', inputs=hashes,
                          method='advance-v1', generated='2026-11-07T01:00:00Z')
    export.validate_envelope(env, 'advance-voting')
    envs = {'advance-voting': env}
    assert [(r['date'], r['daily']) for r in rows[:3]] == [('2026-10-24', 0), ('2026-10-25', 0), ('2026-10-26', 65845)]
    assert eligible(envs) == rows[2:]
    html = page(envs)
    assert check_markup(html, envs)
    assert '2026-10-26' in html and '65,845' in html and '1,640,204' in html
    assert '2026-10-24' not in html and '2026-10-25' not in html
    disclosure = 'Observations outside 26 October to 6 November 2026 are omitted from this view.'
    assert disclosure in html and disclosure in source(envs)
    assert 'Cumulative totals retain the full source series' in html
    assert env['data'] == rows
    assert eligible(envs, historical=True) == rows
    assert disclosure not in page(envs, historical=True)


def test_outside_rows_alone_do_not_render_a_disclosure_module():
    envs = {'advance-voting': {'data': [{'date': '2026-10-25'}]}}
    assert page(envs) == page({})
    assert check_markup(page(envs), envs)
