"""Offline deployed acceptance contracts, using a real fixture-built site."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import threading

import pytest

from product.nz_election.pipeline import night
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.night_deployed import Record, golden


@pytest.mark.parametrize('votes,house,expected', [
    (2851211, 122, True), (2851210, 122, False), (2851211, 120, False),
    ('2851211', 122, False), (2851211, 122.0, False), (None, None, False),
    (True, 122, False), (10**100, 122, False), ('異', [], False),
])
def test_golden(votes, house, expected):
    assert golden(votes, house) is expected


def test_record(tmp_path):
    record = Record('probe', 'http://localhost:8000/product/', tmp_path)
    record.check('one', True, 'valid')
    line, failed = record.write()
    assert line == 'PASS deployed-probe' and not failed
    record.check('two', False, 'bad body')
    line, failed = record.write()
    assert line == 'FAIL deployed-probe: two' and failed
    data = json.loads((record.out / 'record.json').read_text())
    assert data['origin'] == 'http://localhost:8000'
    assert data['start_utc'] <= data['end_utc']
    assert data['checks'][1] == dict(check='two', status='FAIL', reason='bad body')
    assert data['status'] == 'FAIL'
    assert Record('probe', 'http://localhost/', tmp_path).out != record.out


@pytest.fixture(scope='module')
def local_site(tmp_path_factory):
    root = tmp_path_factory.mktemp('deployed')
    daily_refresh(root / 'data', loaders={'night': night.load})
    build(root / 'data', root / 'served/unattended/nz-election', built='2026-11-05T00:00:00Z',
          sha='a' * 40, data_sha='b' * 40)
    feed = root / 'served/unattended/nz-election/offline-feed'
    feed.mkdir()
    for name, raw in national_captures().items():
        (feed / name).parent.mkdir(parents=True, exist_ok=True)
        (feed / name).write_bytes(raw)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(root / 'served')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}/unattended/nz-election/'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize('mode', ['probe', 'rehearse', 'faults'])
def test_browser_checks(local_site, tmp_path, mode):
    # Match the existing harness's uv environment, without adding a project dependency.
    script = '''
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from product.nz_election.tests.night_deployed import (
    Record, launch_chromium, observe, probe, rehearse, faults, provenance)
mode, base, out = sys.argv[1:]
record = Record(mode, base, Path(out))
with sync_playwright() as pw:
    try:
        browser = launch_chromium(pw)
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            print('Chromium is not installed')
            sys.exit(77)
        raise
    with browser, browser.new_context() as context:
        responses = observe(context, record)
        page = context.new_page()
        if mode == 'probe':
            probe(page, base, record, responses, feed_root=base + 'offline-feed/')
        elif mode == 'rehearse':
            rehearse(page, base, record)
        else:
            faults(page, base, record)
        provenance(page, base, record)
line, failed = record.write()
print(line)
sys.exit(int(failed))
'''
    result = subprocess.run(['uv', 'run', '--with', 'playwright', 'python', '-c', script,
                             mode, local_site, str(tmp_path)], capture_output=True, text=True, timeout=120)
    if result.returncode == 77:
        pytest.skip(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f'PASS deployed-{mode}' in result.stdout
    record = json.loads(next(tmp_path.glob('*/record.json')).read_text())
    assert all(check['status'] == 'PASS' for check in record['checks'])
    assert record['screenshots']
    assert all(Path(next(tmp_path.iterdir()), shot['path']).is_file() for shot in record['screenshots'])
    assert all(url.startswith(local_site.split('/unattended')[0]) for url in record['urls'])



def national_captures():
    from product.nz_election.pipeline import fixtures
    prefix = 'ec-2026-media-xml/'
    names = ('electorates.xml', 'parties.xml', 'candidates.xml', 'election.xml', 'e01/e01.xml')
    return {path.removeprefix(prefix): raw for path, raw in
            fixtures.captures(paths={prefix + name for name in names}).items()}


@pytest.mark.parametrize('failure', ['dns', 'tls', 'timeout', 'http', 'empty', 'no-cors-diagnostic', 'browser-timeout'])
def test_cors_inconclusive(monkeypatch, tmp_path, failure):
    checks, record = probe_evidence(monkeypatch, tmp_path, failure)
    assert {c['status'] for c in checks} == {'INCONCLUSIVE'}
    line, failed = record.write()
    assert failed and line.startswith('FAIL deployed-probe:')
    assert all(c['reason'] for c in checks)


@pytest.mark.parametrize('failure', ['readable-http', 'readable-empty', 'readable-malformed', 'readable-count'])
def test_cors_readable_requires_validation(monkeypatch, tmp_path, failure):
    checks, record = probe_evidence(monkeypatch, tmp_path, failure)
    assert any(c['status'] == 'FAIL' for c in checks)
    assert record.write()[1]


@pytest.mark.parametrize('mode', ['blocked', 'readable'])
def test_cors_valid_evidence(monkeypatch, tmp_path, mode):
    checks, record = probe_evidence(monkeypatch, tmp_path, mode)
    assert len(checks) == 5 and all(c['status'] == 'PASS' for c in checks)
    assert not record.write()[1]


def probe_evidence(monkeypatch, tmp_path, mode):
    from product.nz_election.tests import night_deployed as deployed
    from types import SimpleNamespace
    record = deployed.Record('probe', 'https://site.example/product/', tmp_path)
    captured = national_captures()
    def acquire(url):
        if mode in {'dns', 'tls', 'timeout'}:
            raise OSError(mode + ' failure')
        return dict(status=503 if mode == 'http' else 200,
                    raw=b'' if mode == 'empty' else captured['e01/e01.xml' if url.endswith('/e01/e01.xml') else url.rsplit('/', 1)[-1]])
    def evaluate(script, url):
        if url.endswith('night-live.mjs'):
            return schedule_result(False)
        if mode.startswith('readable'):
            raw = captured['e01/e01.xml' if url.endswith('/e01/e01.xml') else url.rsplit('/', 1)[-1]]
            if mode == 'readable-count' and url.endswith('election.xml'):
                raw = raw.replace(b'<votes>0</votes>', b'<votes>-1</votes>', 1)
            text = '' if mode == 'readable-empty' else '<invalid>' if mode == 'readable-malformed' else raw.decode('utf-8-sig')
            return dict(outcome='readable', status=503 if mode == 'readable-http' else 200, text=text)
        if mode != 'no-cors-diagnostic':
            record.data['console_errors'].append(dict(kind='console', text=url + ' blocked by CORS policy'))
        return dict(outcome='blocked-or-network-error', name='TimeoutError' if mode == 'browser-timeout' else 'TypeError', error=mode)
    # Exercise probe itself so these regressions also run against the pre-fix implementation.
    page = SimpleNamespace(goto=lambda url: None, wait_for_load_state=lambda state: None,
                           evaluate=evaluate, locator=lambda selector: SimpleNamespace(
                               inner_text=lambda: 'Final snapshot 2023-11-03 Official results',
                               get_attribute=lambda name: None, is_visible=lambda: True))
    monkeypatch.setattr(deployed, 'host_fetch', acquire, raising=False)
    monkeypatch.setattr(deployed, 'pictures', lambda *args: None)
    deployed.probe(page, record.data['base_url'], record, [], now=lambda: host_instant(False))
    return [c for c in record.data['checks'] if c['check'].startswith('cors-evidence-')], record


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100, '異', 'a'*39, 'a'*41, 'g'*40, 'a'*40+'\n'])
@pytest.mark.parametrize('key', ['code_sha', 'data_sha'])
def test_provenance_requires_sha(tmp_path, value, key):
    body = dict(code_sha='a'*40, data_sha='b'*40)
    body[key] = value
    assert_provenance(tmp_path, dict(status=200, body=dict(data=body)), False)


@pytest.mark.parametrize('response', [
    dict(error='DNS failure'), dict(error='TLS failure'), dict(error='invalid JSON'),
    dict(status=404, body=dict(data=dict(code_sha='a'*40, data_sha='b'*40))),
    dict(status=200, body=None), dict(status=200, body=[]), dict(status=200, body={}),
    dict(status=200, body=dict(data=[])), dict(status=200, body=dict(data=[{}, {}])),
])
def test_provenance_requires_response(tmp_path, response):
    assert_provenance(tmp_path, response, False)


@pytest.mark.parametrize('as_list', [False, True])
def test_provenance_valid(tmp_path, as_list):
    body = dict(code_sha='a'*40, data_sha='B'*40)
    record = assert_provenance(tmp_path, dict(status=200, body=dict(data=[body] if as_list else body)), True)
    assert record.data['code_sha'] == body['code_sha']
    assert record.data['data_sha'] == body['data_sha']


def assert_provenance(tmp_path, response, valid):
    from product.nz_election.tests import night_deployed as deployed
    from types import SimpleNamespace
    record = deployed.Record('probe', 'https://site.example/', tmp_path)
    page = SimpleNamespace(evaluate=lambda script, url: response)
    deployed.provenance(page, record.data['base_url'], record)
    checks = [c for c in record.data['checks'] if c['check'] == 'provenance']
    assert len(checks) == 1 and checks[0]['status'] == ('PASS' if valid else 'FAIL')
    assert record.write()[1] is not valid
    return record


def test_fault_fixture_stays_under_record(tmp_path):
    from product.nz_election.tests.night_deployed import fault_package
    record = Record('faults', 'https://site.example/', tmp_path)
    pack = fault_package(record.out)
    assert pack['available']
    night.validate(record.out / 'fault-fixture')
    assert (record.out / 'fault-fixture/night/index.json').is_file()



def schedule_result(after):
    from datetime import datetime
    opening = datetime.fromisoformat('2026-11-07T06:00:00+00:00').timestamp() * 1000
    return dict(status=200, source=(Path(__file__).parents[1] / 'web/night-live.mjs').read_text(),
                now_ms=opening if after else opening - 1)


@pytest.mark.parametrize('case,after,expected', [
    ('zero', True, False), ('valid', True, True), ('pageerror', False, False), ('clean', False, True),
    ('console', False, False), ('pageerror', True, False), ('console', True, False),
    ('no-countdown', False, False), ('no-vote-link', False, False),
    ('pending', True, False), ('pending-with-valid', True, False),
    ('pre-close-response', True, False), ('http-error', True, False), ('invalid-json', True, False),
    ('late-pageerror', False, False),
])
def test_probe_phase_acceptance(monkeypatch, tmp_path, case, after, expected):
    from types import SimpleNamespace
    from product.nz_election.tests import night_deployed as deployed
    base = 'https://site.example/product/'
    record = deployed.Record('probe', base, tmp_path)
    schedule = schedule_result(after)
    def evaluate(script, url):
        assert url == base + 'night-live.mjs'
        assert 'import(' not in script, 'Schedule inspection must not initialize the page'
        return schedule
    def locator(selector):
        visible = not (case == 'no-countdown' and 'countdown' in selector or
                       case == 'no-vote-link' and 'vote/' in selector)
        return SimpleNamespace(inner_text=lambda: 'Final snapshot 2023-11-03 Official results',
                               get_attribute=lambda key: None, is_visible=lambda: visible)
    page = SimpleNamespace(goto=lambda url: None, wait_for_load_state=lambda state: None,
                           locator=locator, evaluate=evaluate)
    def add_error(kind):
        record.data['console_errors'].append(dict(kind=kind, text='Night initialization failed',
                                                  location=dict(url=base + 'night-live.mjs')))
    if case in {'pageerror', 'console'}:
        add_error(case)
    def cors(*args, **kwargs):
        if case == 'late-pageerror':
            add_error('pageerror')
    monkeypatch.setattr(deployed, 'pictures', lambda *args: None)
    monkeypatch.setattr(deployed, 'cors_probe', cors)
    responses = []
    if case in {'valid', 'pending-with-valid', 'pre-close-response', 'http-error', 'invalid-json'}:
        def body():
            if case == 'invalid-json':
                raise ValueError('Invalid JSON')
            return dict(available=False)
        response = SimpleNamespace(url=base + 'night-live.json', status=503 if case == 'http-error' else 200,
                                   ok=case != 'http-error', json=body,
                                   request=SimpleNamespace(timing=dict(startTime=schedule_result(True)['now_ms'] -
                                                                      (1 if case == 'pre-close-response' else 0))))
        responses.append(response)
        record.data['requests'].append(dict(url=response.url, status=response.status, state='finished'))
    if case in {'pending', 'pending-with-valid'}:
        record.data['requests'].append(dict(url=base + 'night-live.json', status=None, state='pending'))
    deployed.probe(page, base, record, responses, now=lambda: host_instant(after))
    checks = {c['check']: c for c in record.data['checks']}
    assert (checks['night-data-transport']['status'] == 'PASS') is expected
    assert record.write()[1] is not expected
    assert record.data['probe_phase']['name'] == ('after-close' if after else 'before-close')
    assert record.data['probe_phase']['schedule_url'] == base + 'night-live.mjs'
    if 'pageerror' in case or case == 'console':
        assert checks['page-errors']['status'] == 'FAIL'
        assert record.data['unexpected_page_errors'][0]['text'] == 'Night initialization failed'


@pytest.mark.parametrize('mode', ['probe', 'rehearse', 'faults'])
@pytest.mark.parametrize('kind', ['pageerror', 'console'])
def test_unexpected_errors_fail_each_mode(tmp_path, mode, kind):
    from product.nz_election.tests.night_deployed import page_errors
    record = Record(mode, 'https://site.example/', tmp_path)
    record.data['console_errors'].append(dict(kind=kind, text='script failure',
                                              location=dict(url='https://site.example/night-live.mjs')))
    assert page_errors(record)
    assert record.write()[1]



def host_instant(after):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(schedule_result(after)['now_ms'] / 1000, timezone.utc)


def test_overridden_page_clock_cannot_hide_post_close_transport(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from datetime import datetime, timezone
    from product.nz_election.tests import night_deployed as deployed
    base = 'https://site.example/product/'
    record = deployed.Record('probe', base, tmp_path)
    real_now = datetime(2026, 11, 7, 6, 1, tzinfo=timezone.utc)
    # Override the default host clock, so this same test exercises the old implementation.
    monkeypatch.setattr(deployed, 'host_now', lambda: real_now, raising=False)
    monkeypatch.setattr(deployed, 'pictures', lambda *args: None)
    monkeypatch.setattr(deployed, 'cors_probe', lambda *args, **kwargs: None)
    page = SimpleNamespace(goto=lambda url: None, wait_for_load_state=lambda state: None,
                           evaluate=lambda script, url: schedule_result(False),
                           locator=lambda selector: SimpleNamespace(
                               inner_text=lambda: 'Final snapshot 2023-11-03 Official results',
                               get_attribute=lambda key: None, is_visible=lambda: True))
    deployed.probe(page, base, record, [])
    check = next(c for c in record.data['checks'] if c['check'] == 'night-data-transport')
    assert check['status'] == 'FAIL'
    assert record.write()[1]
    phase = record.data['probe_phase']
    assert phase['name'] == 'after-close'
    assert phase['clock_source'] == 'host-utc'
    assert phase['observed_utc'] == real_now.isoformat()
    assert phase['page_now_ms'] < phase['opening_ms']


@pytest.mark.parametrize('after', [False, True])
@pytest.mark.parametrize('page_time', [None, -1, 0, 10**20, 'invalid', {}])
def test_phase_uses_injected_host_clock(after, page_time):
    from types import SimpleNamespace
    from product.nz_election.tests.night_deployed import probe_phase
    result = schedule_result(not after)
    result['now_ms'] = page_time
    phase = probe_phase(SimpleNamespace(evaluate=lambda *args: result), 'https://site.example/',
                        now=lambda: host_instant(after))
    assert phase['name'] == ('after-close' if after else 'before-close')
    assert phase['observed_utc'] == host_instant(after).isoformat()
    assert phase['page_now_ms'] == page_time
