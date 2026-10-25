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
    (sunsets.NIGHT_CLOSE.isoformat().replace('+00:00', 'Z'), (False, False, True, True)),
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
        with pytest.raises(sunsets.SunsetReached, match='DAILY_CLOSED'):
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
                                 clock_now=lambda: current[0], send=lambda *a: pytest.fail('paid call')) == 'ended'


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
    with pytest.raises(sunsets.SunsetReached, match=kind.upper() + '_CLOSED'):
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


def live_crossing(monkeypatch):
    current = ['2026-11-14T10:00:00Z']
    calls = []
    monkeypatch.setattr(social, 'utc_now', lambda: current[0])
    def collect(*args, **kwargs):
        current[0] = '2026-11-14T11:00:00Z'
        return [], [], False
    def classify(*args, send, **kwargs):
        send('POST', 'classification', {}, b'')
        return [], dict.fromkeys(social.EXCLUSIONS, 0)
    monkeypatch.setattr(social, 'collect', collect)
    monkeypatch.setattr(social, 'classify', classify)
    return current, calls


def test_live_default_clock_crossing_is_clean(tmp_path, monkeypatch):
    from product.nz_election.pipeline import export
    current, calls = live_crossing(monkeypatch)
    result = social.refresh_social(tmp_path / 'data', '2026-11-13', now=current[0],
        run_url='https://example.test/live', send=lambda *a: calls.append(a))
    assert calls == []
    assert result == 'ended'
    envs = export.validate_bundle(tmp_path / 'data')
    assert envs['status']['data'] == []
    row = envs['social/credits']['data'][0]
    assert (row['requests'], row['spent'], row['closed']) == (0, 0, True)


def test_live_cli_crossing_exits_zero(tmp_path, monkeypatch, capsys):
    from product.nz_election.pipeline import export
    _, calls = live_crossing(monkeypatch)
    monkeypatch.setattr(social, 'transport', lambda *a: calls.append(a))
    monkeypatch.setattr(sys, 'argv', ['social', '--out', str(tmp_path / 'data'), '--day', '2026-11-13'])
    assert social.main() is None
    assert calls == []
    assert export.validate_bundle(tmp_path / 'data')['status']['data'] == []
    assert capsys.readouterr().out == 'Social scheduled collection has ended.\n'


@pytest.mark.parametrize('entry', ['classify', 'transport'])
def test_direct_paid_entry_refuses_after_sunset(monkeypatch, entry):
    from product.nz_election.tests.test_social import post, classifier
    calls = []
    monkeypatch.setattr(social, 'utc_now', lambda: '2026-11-14T11:00:00Z')
    class Response:
        status = 200
        def __enter__(self):
            calls.append('network')
            return self
        def __exit__(self, *args):
            pass
        def read(self, *args):
            return b'{}'
    class Opener:
        def open(self, *args, **kwargs):
            return Response()
    monkeypatch.setattr(social, 'build_opener', lambda *args: Opener())
    with pytest.raises(Exception, match='SOCIAL_CLOSED'):
        if entry == 'classify':
            social.classify([post()], key='fiction', send=classifier(calls=calls))
        else:
            social.transport('POST', 'https://example.test/', {}, b'{}')
    assert calls == []


def test_built_home_vote_after_official_date(tmp_path):
    site = tmp_path / 'site/nz-election'
    build.build(tmp_path / 'missing', site, built='2026-11-28T00:00:00Z')
    for path in ('index.html', 'vote/index.html', 'og/vote.html'):
        html = (site / path).read_text()
        assert 'due 27 November' not in html
        assert 'Official results' in html or 'official results' in html


@pytest.mark.parametrize('crossing', ['sleep', 'checkpoint'])
def test_sunset_keeps_actual_credits_and_previous_status(tmp_path, monkeypatch, crossing):
    from product.nz_election.pipeline import export
    from product.nz_election.tests.test_social import fixture
    data = tmp_path / 'data'
    fixture(data)
    old_status = (data / 'status.json').read_bytes()
    old_sample = (data / 'social/daily.json').read_bytes()
    current = ['2026-11-14T10:00:00Z']
    calls = []
    def send(*args):
        calls.append(args)
        return 200, b'{"tweets":[],"has_next_page":false}'
    def sleep(_):
        current[0] = '2026-11-14T11:00:00Z'
    if crossing == 'checkpoint':
        replace = social.replace_directory
        def replace_at_boundary(*args):
            replace(*args)
            current[0] = '2026-11-14T11:00:00Z'
        monkeypatch.setattr(social, 'replace_directory', replace_at_boundary)
    result = social.refresh_social(data, '2026-11-13', now=current[0], clock_now=lambda: current[0], send=send, sleep=sleep)
    assert result == 'ended'
    assert (data / 'status.json').read_bytes() == old_status
    assert (data / 'social/daily.json').read_bytes() == old_sample
    row = export.validate_bundle(data)['social/credits']['data'][-1]
    count = 1 if crossing == 'sleep' else 0
    assert len(calls) == count
    assert (row['requests'], row['spent'], row['reserved'], row['closed']) == (count, count * 15, count * social.RESERVATION, True)


@pytest.mark.parametrize('kind', ['hourly', 'daily'])
def test_cutoff_does_not_publish_failure_status(tmp_path, monkeypatch, capsys, kind):
    from product.nz_election.pipeline import refresh, daily_refresh, fetch
    data = tmp_path / 'data'
    refresh.refresh(data, now='2026-10-17T01:00:00Z')
    before = {p.name: p.read_bytes() for p in data.iterdir()}
    def stopped(*args, **kwargs):
        raise sunsets.SunsetReached(kind)
    monkeypatch.setattr(fetch, 'acquire', stopped)
    monkeypatch.setattr(daily_sources, 'live_loaders', lambda **kw: ({'markets': stopped}, {}))
    for key, value in dict(GITHUB_SERVER_URL='https://example.test', GITHUB_REPOSITORY='repo/test', GITHUB_RUN_ID='1', GITHUB_SHA='a'*40, GITHUB_EVENT_NAME='schedule').items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, 'argv', ['loader', '--out', str(data)] + (['--live'] if kind == 'daily' else []))
    module = refresh if kind == 'hourly' else daily_refresh
    assert module.main(now=lambda: '2026-10-17T01:00:00Z') is None
    assert capsys.readouterr().out == kind.capitalize() + ' scheduled collection has ended.\n'
    assert {p.name: p.read_bytes() for p in data.iterdir()} == before


def test_direct_collect_after_sunset(monkeypatch):
    from product.nz_election.tests.test_social import run_row
    monkeypatch.setattr(social, 'utc_now', lambda: '2026-11-14T11:00:00Z')
    with pytest.raises(sunsets.SunsetReached, match='SOCIAL_CLOSED'):
        social.collect('2026-11-13', [], run_row(), key='fiction', send=lambda *a: pytest.fail('paid call'), sleep=lambda _: pytest.fail('sleep'))


def test_one_night_deadline_definition():
    from product.nz_election.pipeline import night_live, night_page
    assert night_live.CLOSE is sunsets.NIGHT_CLOSE
    package = night_page.live_package({}, now=sunsets.NIGHT_CLOSE)
    assert datetime.fromisoformat(package['loop_ends_at']) == sunsets.NIGHT_CLOSE
    assert package['loop_ended'] is True


@pytest.mark.parametrize('built,published', [('2026-11-26T10:59:59Z', False), ('2026-11-26T11:00:00Z', True)])
def test_official_copy_at_nz_midnight_and_provenance(built, published):
    from product.nz_election.pipeline.result_sources import official_results_notice
    notice = official_results_notice(built)
    assert ('due 27 November' not in notice) is published
    envs = {'night/live/current': {'data': [{'result_state': 'official'}]}}
    assert 'due 27 November' not in vote_page.page(built, envs=envs)
    assert 'due 27 November' not in home.voting_dates(built, envs=envs)
    _, description = route_cards.summary({'path': 'vote/', 'label': 'Vote'}, envs, {'title': 'Election'}, built)
    assert 'due 27 November' not in description


def test_default_production_transport_uses_live_clock(tmp_path, monkeypatch):
    current, _ = live_crossing(monkeypatch)
    monkeypatch.setattr(social, 'build_opener', lambda *a: pytest.fail('paid network'))
    assert social.refresh_social(tmp_path / 'data', '2026-11-13', now=current[0]) == 'ended'


def test_populated_settled_home_after_official_date(tmp_path):
    from product.nz_election.tests.test_result_states import prepare, capture
    from product.nz_election.pipeline import night_live, result_states
    preliminary = capture('preliminary')
    live = prepare(tmp_path / 'live', night_live.loaded(preliminary), preliminary['retrieved_at'])
    settled = result_states.transition(live, 'settled', now=night_live.stamp(lambda: sunsets.NIGHT_CLOSE))
    data = tmp_path / 'data'
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(data, loaders={'night': lambda: settled}, now=night_live.stamp(lambda: sunsets.NIGHT_CLOSE))
    site = tmp_path / 'site/nz-election'
    build.build(data, site, built='2026-11-28T00:00:00Z')
    for path in ('index.html', 'vote/index.html'):
        html = (site / path).read_text()
        assert 'due 27 November' not in html
        assert 'results are published' in html
