"""Published families are optional, but their verification requirements are not."""
import sys

import pytest

from product.nz_election.pipeline import export, verify
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.refresh import config, refresh


@pytest.fixture
def polls_only(tmp_path):
    path = tmp_path / 'data'
    refresh(path, now='2026-10-17T01:00:00Z')
    assert not set(export.NEW_FIELDS) & export.validate_bundle(path).keys()
    return path


@pytest.mark.parametrize('daily', [False, True], ids=['polls-only', 'all-families'])
def test_verify_all_supplied_bundle(polls_only, tmp_path, monkeypatch, capsys, daily):
    if daily:
        daily_refresh(polls_only, now='2026-10-17T02:00:00Z')
        assert set.union(*export.FAMILIES.values()) <= export.validate_bundle(polls_only).keys()
    site = build(polls_only, tmp_path / 'site' / 'nz-election')
    monkeypatch.setattr(sys, 'argv', ['verify.py', 'all', '--data', str(polls_only), '--site', str(site.parent)])
    verify.main()
    assert capsys.readouterr().out.endswith('PASS all\n')


def test_polls_only_build_electorate_empty_states(polls_only, tmp_path):
    site = build(polls_only, tmp_path / 'site' / 'nz-election')
    assert (site / 'electorates/index.html').is_file()
    assert len(list((site / 'electorates').glob('*/index.html'))) == 71
    for row in config('electorates'):
        html = (site / 'electorates' / row['slug'] / 'index.html').read_text()
        assert 'Official candidates not available for this electorate.' in html
        for identity in row['baseline_ids']:
            assert f'No candidate baseline or party baseline available for original electorate {identity}.' in html


@pytest.mark.parametrize('check', ['all', 'candidates', 'electorates'])
@pytest.mark.parametrize('family, reason', [
    ('candidates', 'supplied candidate coverage'),
    ('baseline-2023', 'supplied original baselines'),
])
def test_supplied_family_requirements_retained(polls_only, monkeypatch, check, family, reason):
    daily_refresh(polls_only, now='2026-10-17T02:00:00Z')
    env = export.validate_bundle(polls_only)[family]
    if family == 'candidates':
        # Keep identities and list references valid while removing electorate coverage.
        for row in env['data']:
            row['electorate_id'] = None
    else:
        env['data'].pop()
    export.pair(polls_only, family, env)
    export.inventory(polls_only, 'offline-verification', 'test', '2026-10-17T03:00:00Z')
    export.validate_bundle(polls_only)
    monkeypatch.setattr(sys, 'argv', ['verify.py', check, '--data', str(polls_only)])
    with pytest.raises(ValueError, match='VERIFY_FAILED: ' + reason):
        verify.main()
