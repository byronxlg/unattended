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
