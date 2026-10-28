"""Injected-clock Chromium proof; all result transport stays on loopback."""
from datetime import datetime
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright
from product.nz_election.pipeline import night, night_live
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.night_page import live_package
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.tests.night_live_cases import Clock, captures
from product.nz_election.tests.screenshots import Handler


def run(case):
    with tempfile.TemporaryDirectory(dir='artifacts') as tmp:
        root = Path(tmp)
        refresh(root / 'data', now='2026-11-05T00:00:00Z', end_date='2026-07-18')
        late = case.endswith('after-stop')
        built_at = '2026-11-07T06:01:00Z' if case == 'waiting-after-stop' else '2026-11-05T00:00:00Z'
        build(root / 'data', root / 'site/nz-election', built=built_at)
        from product.nz_election.pipeline.home import night_summary
        settled = night_summary({}, '2026-11-08T06:01:00Z')
        clock = Clock()
        captured = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
        night.prepare(root / 'live', night_live.loaded(captured), 'offline-verification', 'a'*40, captured['retrieved_at'])
        envs = {p.relative_to(root / 'live').as_posix()[:-5]: json.loads(p.read_text()) for p in (root / 'live').rglob('*.json')}
        if case == 'complete':
            # Synthetic seat totals exercise the populated home answer, not real results.
            row = envs['night/live/current']['data'][0]
            row['reported_house'] = 120
            next(iter(row['party_results'].values()))['total_seats'] = 120
        pack = live_package(envs, now=clock.now())
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root / 'site')))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                from product.nz_election.tests.night_browser import launch_chromium
                browser = launch_chromium(pw)
                for width, height in [(390, 844), (1280, 800)]:
                    context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce')
                    page = context.new_page()
                    requests, errors = [], []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    def route(r):
                        if r.request.url.endswith('/night-live.json'):
                            requests.append(page.evaluate('Date.now()'))
                            body = dict(available=False, loop_ended=False, loop_ends_at='2026-11-08T06:00:00Z') if case == 'absent' else pack
                            r.fulfill(status=503 if (case == 'recovery' and len(requests) == 1) or (case == 'complete' and requests[-1] >= datetime.fromisoformat('2026-11-07T10:00:00Z').timestamp()*1000) else 200,
                                      content_type='application/json', body=json.dumps(body))
                        elif r.request.url.startswith(origin + '/'):
                            r.continue_()
                        else:
                            r.abort()
                    context.route('**/*', route)
                    page.clock.install(time=datetime.fromisoformat('2026-11-08T06:01:00+00:00' if late else '2026-11-07T05:59:30+00:00'))
                    page.goto(origin + '/unattended/nz-election/')
                    page.wait_for_load_state('networkidle')
                    if late:
                        assert page.locator('#seats').count() == 0
                        assert 'counting is under way' not in page.locator('#main').inner_text()
                        assert page.locator('#home-live').inner_html() == settled
                        assert settled and 'Live updates ended.' in settled
                        page.clock.run_for(120000)
                        assert requests == [] and not errors
                        context.close()
                        continue
                    assert page.locator('#seats').count() == 1
                    assert requests == []
                    if case == 'absent':
                        page.screenshot(path=f'artifacts/home-0559-{width}.png')
                    page.clock.run_for(35000)
                    page.wait_for_function("document.querySelector('#night-summary') !== null")
                    assert page.locator('#seats').count() == 0
                    assert page.locator('#dates').inner_text() == 'Voting closed on 7 November at 7pm.'
                    assert page.locator('#night-summary a[href$="night/"]').count() == 1
                    if case in {'absent', 'recovery'}:
                        assert 'Polls have closed and counting is under way.' in page.locator('#night-summary').inner_text()
                    if case == 'recovery':
                        page.clock.run_for(125000)
                    if case != 'absent':
                        expected = 'House: 120 seats' if case == 'complete' else '0 national seats reported'
                        page.wait_for_function('(text) => document.querySelector("#night-summary").textContent.includes(text)', arg=expected)
                    if case == 'absent':
                        page.clock.run_for(55000)
                        assert page.locator('#dates').inner_text() == 'Voting closed on 7 November at 7pm.'
                        page.screenshot(path=f'artifacts/home-0601-{width}.png')
                    if case == 'complete':
                        page.clock.pause_at(datetime.fromisoformat('2026-11-07T10:00:00Z'))
                        page.clock.run_for(1000)
                        text = page.locator('#night-summary').inner_text()
                        assert 'Stale: last complete cycle retrieved' in text
                        assert 'Live preliminary results' not in text and 'House: 120 seats' in text
                        page.screenshot(path=f'artifacts/home-stale-{width}.png')
                    page.clock.pause_at(datetime.fromisoformat('2026-11-08T06:00:00+00:00'))
                    count = len(requests)
                    page.clock.run_for(120000)
                    assert len(requests) == count
                    if case == 'complete':
                        text = page.locator('#night-summary').inner_text()
                        assert 'Live updates ended.' in text
                        assert 'Live preliminary results' not in text and 'House: 120 seats' in text
                        page.screenshot(path=f'artifacts/home-ended-{width}.png')
                    if case == 'absent':
                        assert page.locator('#home-live').inner_html() == settled
                    assert all(datetime.fromisoformat('2026-11-07T06:00:00+00:00').timestamp()*1000 <= t < datetime.fromisoformat('2026-11-08T06:00:00+00:00').timestamp()*1000 for t in requests)
                    assert requests and not errors
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    context.close()
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
    print('PASS home browser: ' + case + '; 390 and 1280; pre-close and stop request guards')


if __name__ == '__main__':
    Path('artifacts').mkdir(exist_ok=True)
    run(sys.argv[1])
