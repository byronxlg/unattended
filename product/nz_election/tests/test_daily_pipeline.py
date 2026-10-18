"""Daily live transport, capture fallback and independent market retention."""
import io
import json
from datetime import datetime, timezone
from urllib.error import HTTPError
import pytest
from product.nz_election.pipeline import daily_sources, markets, fetch, export
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.fixtures import ROOT
from product.nz_election.pipeline.publish import success_order

NOW = '2026-10-18T01:00:00Z'


class Response(io.BytesIO):
    status = 200
    headers = {}


def acquired(url):
    if url == fetch.CANDIDATE_URL:
        return dict(fetch.decode((ROOT / 'wikipedia/candidates-2026.api.json').read_bytes(), fetch.CANDIDATE_TITLE), fetched_at=NOW)
    slug = url.split('slug=')[1]
    return dict(raw=(ROOT / ('polymarket/' + slug + '.json')).read_bytes(), fetched_at=NOW)


def test_daily_live_sources_and_provenance(tmp_path):
    calls = []
    def acquire(*, url):
        calls.append(url)
        return acquired(url)
    loaders, messages = daily_sources.live_loaders(acquire)
    daily_refresh(tmp_path / 'data', now=NOW, loaders=loaders, messages=messages, run_url='https://example.org/run')
    envs = export.validate_bundle(tmp_path / 'data')
    assert len(calls) == 6 and calls[0] == fetch.CANDIDATE_URL
    assert all(s['fetched_at'] == NOW for s in envs['markets']['source'])
    assert all(r['observed_at'] == NOW for r in envs['markets']['data'])
    wiki = next(s for s in envs['candidates']['source'] if s['id'].startswith('wikipedia/'))
    assert wiki['url'].endswith('oldid=' + wiki['revision']) and wiki['fetched_at'] == NOW
    assert all('live/polymarket/' + e['slug'] + '.json' in envs['markets']['input_hashes'] for e in markets.events())
    assert 'Live Gamma' in next(r['message'] for r in envs['status']['data'] if r['dataset'] == 'markets')
    assert markets.ATTRIBUTION in (tmp_path / 'data/LICENCES.md').read_text()


@pytest.mark.parametrize('first', [False, True])
def test_live_failure_retains_last_good_and_publishes_failure(tmp_path, monkeypatch, first):
    import importlib
    from product.nz_election.pipeline.publish import publish, git, DATA
    module = importlib.import_module('product.nz_election.pipeline.daily_refresh')
    data = tmp_path / 'data'
    if not first:
        loaders, messages = daily_sources.live_loaders(acquired_adapter)
        daily_refresh(data, now=NOW, loaders=loaders, messages=messages, run_url='https://example.org/good')
    before = {p.name: p.read_bytes() for p in data.glob('markets.*')}
    def failed(**kwargs):
        raise fetch.FetchError('HTTP_RETRIES_EXHAUSTED')
    monkeypatch.setattr(fetch, 'acquire', failed)
    monkeypatch.setattr(module, 'utc_now', lambda: '2026-10-19T01:00:00Z')
    output = tmp_path / 'output'
    for key, value in dict(GITHUB_OUTPUT=str(output), GITHUB_SERVER_URL='https://github.com',
                           GITHUB_REPOSITORY='example/repo', GITHUB_RUN_ID='123', GITHUB_SHA='a'*40).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr('sys.argv', ['daily_refresh.py', '--live', '--out', str(data)])
    with pytest.raises(SystemExit, match='HTTP_RETRIES_EXHAUSTED'):
        module.main()
    envs = export.validate_bundle(data)
    assert before == {p.name: p.read_bytes() for p in data.glob('markets.*')}
    for family in ('candidates', 'markets'):
        status = next(r for r in envs['status']['data'] if r['dataset'] == family)
        assert status['state'] == ('unavailable' if first else 'stale')
        assert status['last_success_at'] == (None if first else NOW)
        assert status['last_good_run_url'] == (None if first else 'https://example.org/good')
        assert status['last_attempt_at'] == '2026-10-19T01:00:00Z'
        assert status['error_code'] == 'HTTP_RETRIES_EXHAUSTED'
    assert output.read_text() == 'validated=true\n'
    remote = tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    assert publish(data, remote, family='daily')['outcome'] == 'published'
    assert json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'] == envs['status']['data']
    for name, raw in before.items():
        assert git(remote, 'show', 'data:' + str(DATA / name)).stdout.encode() == raw


def acquired_adapter(*, url):
    return acquired(url)


def test_partial_daily_failure_retains_family(tmp_path):
    data = tmp_path / 'data'
    daily_refresh(data, now=NOW)
    before = [(data / ('markets' + ext)).read_bytes() for ext in ('.json', '.csv')]
    def fail():
        raise ValueError('INVALID_MARKET')
    daily_refresh(data, now='2026-10-19T01:00:00Z', loaders={'markets': fail})
    assert before == [(data / ('markets' + ext)).read_bytes() for ext in ('.json', '.csv')]
    envs = export.validate_bundle(data)
    status = next(r for r in envs['status']['data'] if r['dataset'] == 'markets')
    assert status['state'] == 'stale' and status['last_success_at'] == NOW
    assert envs['electorates']['generated_at'] == '2026-10-19T01:00:00Z'


def test_success_order_missing_acquisition():
    assert success_order({'polls': {}, 'averages': {'generated_at': NOW}}) == ('', NOW)
    assert success_order({'polls': {'fetched_at': None}, 'averages': {'generated_at': NOW}}) == ('', NOW)
    assert success_order({'markets': {'generated_at': NOW}}, 'markets') == ('', NOW)


def test_daily_transport_bounds_and_hosts():
    sleeps, calls = [], []
    url = fetch.gamma_url(markets.events()[0]['slug'])
    raw = acquired(url)['raw']
    def retry(request, *, timeout):
        calls.append(request.full_url)
        assert timeout == 20
        if len(calls) < 3:
            raise HTTPError(url, 429, '', {'Retry-After': '2'}, None)
        return Response(raw)
    result = fetch.acquire(retry, sleep=sleeps.append, url=url, now=lambda: datetime(2026, 10, 18, 1, tzinfo=timezone.utc))
    assert result == dict(raw=raw, fetched_at=NOW) and sleeps == [2, 2] and calls == [url]*3
    for unsafe in ('http://gamma-api.polymarket.com/events?slug=x', 'https://evil.test/', url + '&redirect=x', 'https://en.wikipedia.org/other'):
        with pytest.raises(fetch.FetchError, match='UNAPPROVED_SOURCE'):
            fetch.acquire(lambda *a, **k: pytest.fail('transport called'), url=unsafe)
    with pytest.raises(fetch.FetchError, match='RESPONSE_TOO_LARGE'):
        fetch.acquire(lambda *a, **k: Response(b'x' * (fetch.LIMIT + 1)), url=url)
    with pytest.raises(fetch.FetchError, match='HTTP_REJECTED'):
        def redirect(*a, **k):
            raise HTTPError(url, 302, '', {}, None)
        fetch.acquire(redirect, url=url)
    candidate = fetch.acquire(lambda *a, **k: Response((ROOT / 'wikipedia/candidates-2026.api.json').read_bytes()), url=fetch.CANDIDATE_URL)
    assert candidate['revision'] == '1380178146'


def test_daily_malformed_live_market_fails():
    def bad(*, url):
        return dict(raw=b'null', fetched_at=NOW)
    loaders, messages = daily_sources.live_loaders(bad)
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        loaders['markets']()
    assert 'markets' not in messages


def test_daily_cli_validated_gate_and_unexpected_failure(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module('product.nz_election.pipeline.daily_refresh')
    output = tmp_path / 'output'
    for key, value in dict(GITHUB_OUTPUT=str(output), GITHUB_SERVER_URL='https://github.com',
                           GITHUB_REPOSITORY='example/repo', GITHUB_RUN_ID='123', GITHUB_SHA='a'*40).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr('sys.argv', ['daily_refresh.py', '--live', '--out', str(tmp_path / 'data')])
    def failure():
        raise ValueError('INVALID_MARKET')
    monkeypatch.setattr(daily_sources, 'live_loaders', lambda: ({'markets': failure}, {}))
    with pytest.raises(SystemExit, match='INVALID_MARKET'):
        module.main()
    assert output.read_text() == 'validated=true\n'
    output.unlink()
    def unexpected():
        raise RuntimeError('programmer error')
    monkeypatch.setattr(daily_sources, 'live_loaders', lambda: ({'markets': unexpected}, {}))
    before = (tmp_path / 'data/status.json').read_bytes()
    with pytest.raises(RuntimeError):
        module.main()
    assert not output.exists() and (tmp_path / 'data/status.json').read_bytes() == before


def test_daily_overdue_after_36_hours():
    from product.nz_election.pipeline.presentation import overdue
    assert not overdue(NOW, '2026-10-19T13:00:00Z', 'daily')
    assert overdue(NOW, '2026-10-19T13:00:01Z', 'daily')


def test_market_mixed_source_regression_rejected(tmp_path):
    from product.nz_election.pipeline.publish import publish, git, DATA
    old, incoming, remote = [tmp_path / p for p in ('old', 'incoming', 'remote.git')]
    daily_refresh(old, now=NOW, loaders={'markets': markets.load})
    daily_refresh(incoming, now='2026-10-19T01:00:00Z', loaders={'markets': markets.load})
    env = json.loads((incoming / 'markets.json').read_text())
    env['source'][0]['fetched_at'] = '2026-10-01T00:00:00Z'
    env['source'][1]['fetched_at'] = '2026-10-19T00:00:00Z'
    env['fetched_at'] = max(s['fetched_at'] for s in env['source'])
    export.pair(incoming, 'markets', env)
    export.inventory(incoming, 'offline-verification', 'test', '2026-10-19T01:00:00Z')
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    publish(old, remote, family='daily')
    publish(incoming, remote, family='daily')
    assert git(remote, 'show', 'data:' + str(DATA / 'markets.json')).stdout.encode() == (old / 'markets.json').read_bytes()
    state = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data']
    market = next(r for r in state if r['dataset'] == 'markets')
    assert market['last_success_at'] == NOW and market['last_attempt_at'] == '2026-10-19T01:00:00Z'


def test_candidate_reviewed_claims_not_relabelled(monkeypatch):
    from product.nz_election.pipeline import candidates
    original = candidates.load
    row = original()[0]['candidates'][0]
    config = candidates.config
    mapping = dict(candidate_id=row['id'], electorate_id=row['electorate_id'], party_id=row['party_id'],
                   reviewer='offline test', evidence='synthetic reviewed claim',
                   claims={'name': [dict(value=row['name'], source_id=candidates.WIKI, locator='synthetic locator')]})
    monkeypatch.setattr(candidates, 'config', lambda name: {'mappings': [mapping]} if name == 'candidate-mappings' else config(name))
    def changed(*, url):
        result = acquired(url)
        result['wikitext'] += '\nChanged content'
        return result
    loaders, messages = daily_sources.live_loaders(changed)
    with pytest.raises(ValueError, match='^CANDIDATE_REVISION_REVIEW_REQUIRED$'):
        loaders['candidates']()
    assert 'candidates' not in messages
