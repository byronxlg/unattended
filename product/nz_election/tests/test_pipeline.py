"""Publication transports use only temporary local bare repositories."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import threading
import pytest
from product.nz_election.pipeline import export
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.pipeline.storage import replace_directory


def fail(*args):
    raise ParseDrift('synthetic drift')


def make_bundle(root, hour=1):
    out = root / ('bundle-' + str(hour))
    refresh(out, now=f'2026-10-17T{hour:02d}:00:00Z')
    return out


def repository(tmp_path, bundle):
    remote = tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    seed = tmp_path / 'seed'
    seed.mkdir()
    git(seed, 'init', '-q', '-b', 'data')
    git(seed, 'config', 'user.name', 'Offline test')
    git(seed, 'config', 'user.email', 'test@example.invalid')
    shutil.copytree(bundle, seed / DATA)
    git(seed, 'add', str(DATA))
    git(seed, 'commit', '-qm', 'Seed local test repository')
    git(seed, 'push', str(remote), 'data')
    return remote


def test_atomic_poll_bundle(tmp_path):
    bundle = make_bundle(tmp_path)
    old = export.validate_bundle(bundle)
    refresh(bundle, now='2026-10-18T01:00:00Z')
    new = export.validate_bundle(bundle)
    assert old['averages']['data'][-1]['date'] == '2026-10-17'
    assert new['averages']['data'][-1]['date'] == '2026-10-18'
    assert new['seats']['data']['average_id'] == new['averages']['data'][-1]['id']
    stage = tmp_path / 'bad-stage'
    stage.mkdir()
    link = tmp_path / 'link'
    link.symlink_to(bundle, target_is_directory=True)
    with pytest.raises(ValueError, match='UNSAFE'):
        replace_directory(stage, link)
    assert export.validate_bundle(bundle) == new


def test_last_good_retained(tmp_path):
    bundle = make_bundle(tmp_path)
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in {'polls', 'averages', 'seats'}}
    status = refresh(bundle, now='2026-10-17T02:00:00Z', parse=fail)
    assert status['state'] == 'stale' and status['error_code'] == 'parse_drift'
    assert all((bundle / name).read_bytes() == raw for name, raw in before.items())
    export.validate_bundle(bundle)


def test_first_failure_unavailable(tmp_path):
    bundle = tmp_path / 'unavailable'
    status = refresh(bundle, now='2026-10-17T01:00:00Z', parse=fail)
    assert status['state'] == 'unavailable' and status['last_success_at'] is None
    assert not (bundle / 'polls.json').exists()
    export.validate_bundle(bundle)


def test_partial_failure_preserves_unowned_files(tmp_path):
    bundle = make_bundle(tmp_path)
    env = json.loads((bundle / 'status.json').read_text())
    other = dict(env['data'][0], id='status-other', dataset='other', message='Unowned state')
    env['data'].append(other)
    export.pair(bundle, 'status', env)
    export.inventory(bundle, env['run_url'], env['code_sha'], '2026-10-17T01:00:00Z')
    remote = repository(tmp_path, bundle)
    newer = make_bundle(tmp_path, 2)
    refresh(newer, now='2026-10-17T03:00:00Z', parse=fail)
    publish(newer, remote)
    result = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)
    assert other in result['data']


def test_invalid_bundle_never_published(tmp_path):
    bundle = make_bundle(tmp_path)
    remote = repository(tmp_path, bundle)
    before = git(remote, 'rev-parse', 'data').stdout
    (bundle / 'rogue.json').write_text('{}')
    with pytest.raises(ValueError, match='INVENTORY'):
        publish(bundle, remote)
    assert git(remote, 'rev-parse', 'data').stdout == before
    (bundle / 'rogue.json').unlink()
    (bundle / 'polls.json').unlink()
    (bundle / 'polls.json').symlink_to(tmp_path / 'secret')
    with pytest.raises(ValueError, match='UNSAFE'):
        publish(bundle, remote)


def test_concurrent_publishers(tmp_path):
    base = make_bundle(tmp_path)
    remote = repository(tmp_path, base)
    second, third = make_bundle(tmp_path, 2), make_bundle(tmp_path, 3)
    barrier = threading.Barrier(2)
    def race(bundle):
        return publish(bundle, remote, before_push=lambda attempt: barrier.wait(timeout=10) if attempt == 0 else None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(race, [second, third]))
    assert all(r['outcome'] in {'published', 'older-run-retained'} for r in results)
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status['last_attempt_at'] == '2026-10-17T03:00:00Z'


def test_non_fast_forward_retry(tmp_path):
    remote = repository(tmp_path, make_bundle(tmp_path))
    second, third = make_bundle(tmp_path, 2), make_bundle(tmp_path, 3)
    def intervene(attempt):
        if attempt == 0:
            publish(second, remote)
    result = publish(third, remote, before_push=intervene)
    assert result['attempts'] == 2 and result['outcome'] == 'published'
    assert publish(third, remote)['outcome'] == 'unchanged'


def test_older_run_cannot_replace_newer_data(tmp_path):
    old = make_bundle(tmp_path)
    remote = repository(tmp_path, old)
    publish(make_bundle(tmp_path, 3), remote)
    before = git(remote, 'rev-parse', 'data').stdout
    assert publish(make_bundle(tmp_path, 2), remote)['outcome'] == 'older-run-retained'
    assert before == git(remote, 'rev-parse', 'data').stdout


def test_correction_history_keeps_exact_previous_shares(tmp_path):
    from decimal import Decimal
    from product.nz_election.pipeline.poll_parser import parse_polls
    bundle = make_bundle(tmp_path)
    before = export.validate_bundle(bundle)['polls']['data'][0]
    def corrected(*args):
        parsed = parse_polls(*args)
        parsed.polls[0]['shares']['nat'] += Decimal('0.1')
        return parsed
    refresh(bundle, now='2026-10-17T02:00:00Z', parse=corrected)
    after = export.validate_bundle(bundle)['polls']['data'][0]
    previous = after['history'][-1]
    assert previous['shares'] == before['shares'] and previous['scale'] == before['scale']
    refresh(bundle, now='2026-10-17T03:00:00Z', parse=corrected)
    assert export.validate_bundle(bundle)['polls']['data'][0]['history'] == after['history']


def test_fetch_bounds_retries_and_validation(monkeypatch):
    import io
    import socket
    from datetime import datetime, timezone
    from urllib.error import HTTPError
    from product.nz_election.pipeline import fetch
    from product.nz_election.pipeline.fixtures import ROOT

    def no_network(*args, **kwargs):
        raise AssertionError('Tests must never open a socket')
    monkeypatch.setattr(socket, 'socket', no_network)
    body = (ROOT / 'wikipedia/polls-2026.api.json').read_bytes()
    requests, sleeps = [], []
    class Response(io.BytesIO):
        status = 200
        headers = {}
        def read(self, size=-1):
            assert size == fetch.LIMIT + 1
            return super().read(size)
    def transport(request, *, timeout):
        requests.append(request)
        assert timeout == 20
        assert request.get_header('User-agent') == fetch.USER_AGENT
        assert request.full_url.startswith('https://en.wikipedia.org/w/api.php?')
        assert 'maxlag=5' in request.full_url
        return Response(body)
    clock = lambda: datetime(2026, 10, 17, 1, tzinfo=timezone.utc)
    acquired = fetch.acquire(transport, now=clock)
    assert acquired['revision'] == '1380524613'
    assert acquired['timestamp'] == '2026-10-16T07:01:22Z'
    assert acquired['fetched_at'] == '2026-10-17T01:00:00Z'
    assert len(requests) == 1
    for header in ('7', 'Sat, 17 Oct 2026 01:00:07 GMT'):
        calls = []
        sleeps.clear()
        def retry(request, *, timeout):
            calls.append(1)
            if len(calls) < 3:
                raise HTTPError(fetch.URL, 503, 'Unavailable', {'Retry-After': header}, None)
            return transport(request, timeout=timeout)
        fetch.acquire(retry, sleep=sleeps.append, now=clock)
        assert sleeps == [7, 7] and len(calls) == 3
    calls = []
    def exhausted(*args, **kwargs):
        calls.append(1)
        raise TimeoutError
    with pytest.raises(fetch.FetchError, match='HTTP_RETRIES_EXHAUSTED'):
        fetch.acquire(exhausted, sleep=lambda _: None)
    assert len(calls) == 3
    for header, code in [('61', 'RETRY_AFTER_EXCESSIVE'), ('9' * 5000, 'RETRY_AFTER_EXCESSIVE'), ('bad', 'INVALID_RETRY_AFTER')]:
        def excessive(*args, **kwargs):
            raise HTTPError(fetch.URL, 429, 'Limited', {'Retry-After': header}, None)
        with pytest.raises(fetch.FetchError, match=code):
            fetch.acquire(excessive, sleep=no_network)
    for status in (301, 302, 401, 403, 404):
        def rejected(*args, **kwargs):
            raise HTTPError(fetch.URL, status, 'Rejected', {}, None)
        with pytest.raises(fetch.FetchError, match='HTTP_REJECTED'):
            fetch.acquire(rejected, sleep=no_network)
    for length in (None, str(fetch.LIMIT + 1)):
        response = Response(b'x' * (fetch.LIMIT + 50))
        response.headers = {'Content-Length': length} if length else {}
        if length:
            response.read = no_network
        with pytest.raises(fetch.FetchError, match='RESPONSE_TOO_LARGE'):
            fetch.acquire(lambda *a, **k: response)
    for raw in (b'', b'null', b'[]', b'1', b'1.5', b'"strange"', b'<html>challenge</html>', b'\xff'):
        with pytest.raises(fetch.FetchError, match='INVALID_RESPONSE'):
            fetch.decode(raw)
    for field, values, code in (
        ('revid', ['', None, True, [], {}, 1.5, 0, -1, 2 ** 100, '123', '1e9', '\u0661'], 'INVALID_REVISION'),
        ('timestamp', ['', None, True, [], {}, 1.5, 2 ** 100, '2026-01-01', '2026-01-01T00:00:00+00:00', '2026-02-30T00:00:00Z'], 'INVALID_TIMESTAMP'),
    ):
        for value in values:
            mutated = json.loads(body)
            mutated['query']['pages'][0]['revisions'][0][field] = value
            with pytest.raises(fetch.FetchError) as error:
                fetch.decode(json.dumps(mutated).encode())
            assert error.value.code == code
    with pytest.raises(fetch.FetchError, match='INVALID_REVISION'):
        fetch.decode(body.replace(b'1380524613', b'9' * 5000))
    mutated = json.loads(body)
    mutated['query']['pages'][0]['title'] = 'Some other page'
    with pytest.raises(fetch.FetchError, match='WRONG_PAGE'):
        fetch.decode(json.dumps(mutated).encode())
    sleeps.clear()
    with pytest.raises(fetch.FetchError, match='MAXLAG_RETRIES_EXHAUSTED'):
        fetch.acquire(lambda *a, **k: Response(b'{"error":{"code":"maxlag"}}'), sleep=sleeps.append)
    assert sleeps == [1, 2]
    assert fetch.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.invalid/') is None


def test_live_refresh_provenance_and_failure_retention(tmp_path):
    from product.nz_election.pipeline.fetch import decode, FetchError
    from product.nz_election.pipeline.fixtures import ROOT
    acquired = decode((ROOT / 'wikipedia/polls-2026.api.json').read_bytes())
    acquired['fetched_at'] = '2026-10-17T01:00:00Z'
    bundle = tmp_path / 'live'
    run = 'https://github.com/byronxlg/unattended/actions/runs/123'
    status = refresh(bundle, acquire=lambda: acquired, now='2026-10-17T01:00:00Z', run_url=run, sha='a' * 40)
    assert status['state'] == 'fresh' and 'Offline' not in status['message']
    envs = export.validate_bundle(bundle)
    assert envs['polls']['run_url'] == run and envs['polls']['code_sha'] == 'a' * 40
    assert envs['polls']['fetched_at'] == acquired['fetched_at']
    assert envs['polls']['source'][0]['url'].endswith('oldid=' + acquired['revision'])
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in {'polls', 'averages', 'seats'}}
    def fail_fetch():
        raise FetchError('HTTP_RETRIES_EXHAUSTED')
    status = refresh(bundle, acquire=fail_fetch, now='2026-10-17T02:00:00Z', run_url=run, sha='b' * 40)
    assert status['state'] == 'stale' and status['error_code'] == 'HTTP_RETRIES_EXHAUSTED'
    assert all((bundle / n).read_bytes() == raw for n, raw in before.items())
    before = {p.name: p.read_bytes() for p in bundle.iterdir()}
    def unexpected():
        raise RuntimeError('unexpected')
    with pytest.raises(RuntimeError, match='unexpected'):
        refresh(bundle, acquire=unexpected, now='2026-10-17T03:00:00Z')
    assert {p.name: p.read_bytes() for p in bundle.iterdir()} == before


def test_live_cli_signals_only_validated_results(tmp_path, monkeypatch):
    import importlib
    from product.nz_election.pipeline import fetch
    module = importlib.import_module('product.nz_election.pipeline.refresh')
    output, summary = tmp_path / 'output', tmp_path / 'summary'
    for key, value in {'GITHUB_OUTPUT': str(output), 'GITHUB_STEP_SUMMARY': str(summary),
                       'GITHUB_SERVER_URL': 'https://github.com', 'GITHUB_REPOSITORY': 'byronxlg/unattended',
                       'GITHUB_RUN_ID': '123', 'GITHUB_SHA': 'a' * 40}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr('sys.argv', ['refresh.py', '--out', str(tmp_path / 'data')])
    def handled():
        raise fetch.FetchError('HTTP_RETRIES_EXHAUSTED')
    monkeypatch.setattr(fetch, 'acquire', handled)
    with pytest.raises(SystemExit, match='HTTP_RETRIES_EXHAUSTED'):
        module.main()
    assert output.read_text() == 'validated=true\n'
    envs = export.validate_bundle(tmp_path / 'data')
    assert envs['status']['run_url'].endswith('/actions/runs/123')
    assert envs['status']['code_sha'] == 'a' * 40
    assert 'attempted_revision' in summary.read_text()
    output.unlink()
    def unexpected():
        raise RuntimeError('unexpected')
    monkeypatch.setattr(fetch, 'acquire', unexpected)
    with pytest.raises(RuntimeError):
        module.main()
    assert not output.exists()
