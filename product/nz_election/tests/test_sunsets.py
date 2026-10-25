"""Offline boundary contracts for acquisition and phase copy."""
from datetime import datetime
import subprocess
import sys

import pytest
from product.nz_election.pipeline import sunsets, social, daily_sources, home, vote_page, route_cards, build
from product.nz_election.tests.test_workflows import workflow

CLOCKS = [
    ('2026-11-07T05:59:59Z', (True, True, True, True)),
    ('2026-11-07T06:00:00Z', (False, True, True, True)),
    ('2026-11-08T06:00:00Z', (False, False, True, True)),
    ('2026-11-14T10:59:59Z', (False, False, True, True)),
    ('2026-11-14T11:00:00Z', (False, False, False, False)),
    ('2026-11-27T00:00:00Z', (False, False, False, False)),
]


@pytest.mark.parametrize('now,expected', CLOCKS)
def test_workflow_deadlines(now, expected, tmp_path):
    for kind, active in zip(('hourly', 'night', 'social', 'daily'), expected):
        assert sunsets.allowed(kind, now, 'schedule') is active
        if kind == 'night':
            from product.nz_election.pipeline import night_live
            assert sunsets.allowed(kind, now) == (datetime.fromisoformat(now) < night_live.CLOSE)
            continue
        doc = workflow('nz-election-' + ('social-daily' if kind == 'social' else kind) + '.yml')
        gate = doc['jobs']['window']
        assert gate['steps'][-1]['run'].endswith('sunsets.py ' + kind)
        job = doc['jobs']['reserve' if kind == 'social' else 'refresh']
        assert job['needs'] == 'window'
        assert "needs.window.outputs.allowed == 'true'" in job['if']
        output = tmp_path / 'output'
        import os
        result = subprocess.run([sys.executable, 'product/nz_election/pipeline/sunsets.py', kind, '--now', now],
                                env=dict(os.environ, GITHUB_OUTPUT=str(output), GITHUB_EVENT_NAME='schedule'), capture_output=True, text=True)
        assert result.returncode == 0
        assert output.read_text().splitlines()[-1] == 'allowed=' + str(active).lower()
        assert len(result.stdout.splitlines()) == (0 if active else 1)
    assert sunsets.allowed('daily', now, 'workflow_dispatch')


@pytest.mark.parametrize('now', [c[0] for c in CLOCKS[-2:]])
def test_no_paid_calls_after_sunset(now, tmp_path):
    assert social.refresh_social(tmp_path / 'data', '2026-11-13', now=now,
                                 send=lambda *a: pytest.fail('paid call')) == 'ended'
    assert not (tmp_path / 'data').exists()
    loaders, _ = daily_sources.live_loaders(now=now, event='schedule', acquire=lambda **k: pytest.fail('network'))
    for family in ('markets', 'candidates'):
        with pytest.raises(ValueError, match='DAILY_CLOSED'):
            loaders[family]()


def test_social_deploy_after_publication():
    doc = workflow('nz-election-social-daily.yml')
    job = doc['jobs']['publish']
    assert job['needs'] == 'collect' and "validated == 'true'" in job['if']
    assert job['permissions']['actions'] == 'write'
    publish, deploy = job['steps'][-2:]
    assert 'publish.py --family social' in publish['run']
    assert deploy['run'] == 'gh workflow run pages.yml --ref main'
    assert deploy['if'] == publish['if']
    pages = workflow('pages.yml')
    assert 'workflow_dispatch' in pages[True]
    assert pages['jobs']['deploy']['needs'] == 'build'


@pytest.mark.parametrize('now,expected', CLOCKS)
def test_phase_copy(now, expected):
    after = not expected[0]
    presentation = build.home_presentation({}, now)
    html = home.page({}, now, presentation)
    vote = vote_page.page(now)
    assert ('Who stood where I live?' in html) is after
    assert ('How to vote' in html) is not after
    assert ('Use the official finder' in vote) is not after
    assert ('Vote overseas' in vote) is not after
    assert ('Election results</a>' in vote) is after
    for path in ('', 'vote/', 'night/'):
        title, description = route_cards.summary(dict(path=path, label='How to vote' if path == 'vote/' else path), {}, presentation, now)
        if after:
            assert 'How to vote' not in title
            assert 'votes on' not in title + description
            assert 'find a voting place' not in description
            if path == 'night/':
                assert 'Current preliminary' in description
    assert 'not available' not in (html + vote).lower()


def test_social_sample_caption():
    from product.nz_election.pipeline.social_page import notice
    rows = [dict(day=d, sample={'eligible': 10}, provenance={'windows': []}) for d in ('2026-11-07', '2026-11-08')]
    caption = notice(rows)
    assert '2026-11-07 to 2026-11-08 (New Zealand dates)' in caption
    assert 'Includes post-election days' in caption


def test_collection_crossing_sunset_blocks_classifier(tmp_path, monkeypatch):
    current = ['2026-11-14T10:00:00Z']
    def collect(*args, **kwargs):
        current[0] = '2026-11-14T11:00:00Z'
        return [], [], False
    def classify(*args, send, **kwargs):
        send('POST', 'classification', {}, b'')
        pytest.fail('classification admitted after sunset')
    monkeypatch.setattr(social, 'collect', collect)
    monkeypatch.setattr(social, 'classify', classify)
    assert social.refresh_social(tmp_path / 'data', '2026-11-13', now=current[0],
                                 clock_now=lambda: current[0], send=lambda *a: pytest.fail('paid call')) == 'SOCIAL_UPSTREAM_FAILED'


@pytest.mark.parametrize('kind', ['hourly', 'daily'])
def test_cli_after_sunset_does_not_read_environment_or_fetch(kind, monkeypatch, capsys, tmp_path):
    from product.nz_election.pipeline import refresh, daily_refresh
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'schedule')
    monkeypatch.setattr(sys, 'argv', ['loader', '--out', str(tmp_path / 'data')] + (['--live'] if kind == 'daily' else []))
    module = refresh if kind == 'hourly' else daily_refresh
    module.main(now=lambda: '2026-11-27T00:00:00Z')
    assert capsys.readouterr().out == kind.capitalize() + ' scheduled collection has ended.\n'
    assert not (tmp_path / 'data').exists()


@pytest.mark.parametrize('kind', ['hourly', 'daily'])
def test_source_retry_crossing_deadline(kind, monkeypatch):
    from datetime import timedelta
    from urllib.error import HTTPError
    from product.nz_election.pipeline import fetch
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'schedule')
    deadline = sunsets.HOURLY_CLOSE if kind == 'hourly' else sunsets.DAILY_CLOSE
    clock, calls = [deadline - timedelta(seconds=1)], []
    def transport(request, **kwargs):
        calls.append(request)
        raise HTTPError(request.full_url, 429, 'retry', {'Retry-After': '3'}, None)
    def sleep(seconds):
        clock[0] += timedelta(seconds=seconds)
    with pytest.raises(fetch.FetchError, match=kind.upper() + '_CLOSED'):
        fetch.acquire(transport, sleep=sleep, now=lambda: clock[0], url=fetch.URL if kind == 'hourly' else fetch.CANDIDATE_URL)
    assert len(calls) == 1


@pytest.mark.parametrize('now,expected', CLOCKS)
def test_pages_ignores_expired_crons_but_keeps_manual_deploy(now, expected, monkeypatch):
    for name, active in [('NZ election hourly', expected[0]), ('NZ election daily', expected[3])]:
        monkeypatch.setenv('UPSTREAM_WORKFLOW', name)
        assert sunsets.allowed('pages', now, 'workflow_run') is active
    assert sunsets.allowed('pages', now, 'workflow_dispatch')
    doc = workflow('pages.yml')
    assert doc['jobs']['build']['needs'] == 'window'
    assert "needs.window.outputs.allowed == 'true'" in doc['jobs']['build']['if']
    assert doc['jobs']['window']['steps'][-1]['run'].endswith('sunsets.py pages')
