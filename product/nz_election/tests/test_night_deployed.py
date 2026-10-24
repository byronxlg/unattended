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
    build(root / 'data', root / 'served/unattended/nz-election', built='2026-11-05T00:00:00Z')
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
