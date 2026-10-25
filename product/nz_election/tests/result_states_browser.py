# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Offline populated state screenshots and terminal client checks."""
from datetime import datetime, timezone
from decimal import Decimal
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from playwright.sync_api import sync_playwright
from product.nz_election.pipeline import export, fixtures, night_live, result_states
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.night_page import live_package
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler, CONTRAST, contrast
import json


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('artifacts/result-states')
    out.mkdir(parents=True, exist_ok=True)
    def capture(name):
        return json.loads(fixtures.captures(paths={name})[name])
    initial = capture('result-states/2026-11-07-preliminary-final.json')
    daily_refresh(out / 'live-data', loaders={'night': lambda: night_live.loaded(initial)}, now=initial['retrieved_at'])
    envs = export.validate_bundle(out / 'live-data')
    live_site = out / 'live' / 'site'
    build(out / 'live-data', live_site / 'nz-election', built=initial['retrieved_at'])
    sites = []
    handover_packs = {}
    for state, now in [('settled', '2026-11-08T06:00:00Z'), ('official', '2026-11-27T11:00:00Z')]:
        loaded = result_states.transition(envs, state, now=now, captured=capture('result-states/2026-11-27-official.json') if state == 'official' else None)
        data = out / (state + '-data')
        daily_refresh(data, loaders={'night': lambda: loaded}, now=now)
        envs = export.validate_bundle(data)
        handover_packs[state] = live_package(envs)
        site = out / state / 'site'
        build(data, site / 'nz-election', built=now)
        sites.append((state, now, site))
    with sync_playwright() as pw, launch_chromium(pw) as browser:
        for state, now, site in sites:
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = f'http://127.0.0.1:{server.server_port}'
            try:
                for route in ['night', 'home']:
                    for width, height in [(390, 844), (1280, 800)]:
                        context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce')
                        page = context.new_page()
                        page.clock.install(time=datetime.fromisoformat(now).astimezone(timezone.utc))
                        requests, errors = [], []
                        page.on('pageerror', lambda e: errors.append(str(e)))
                        page.on('request', lambda r: requests.append(r.url))
                        context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin + '/') else r.abort())
                        page.goto(origin + '/unattended/nz-election/' + ('night/' if route == 'night' else ''))
                        page.wait_for_load_state('networkidle')
                        page.clock.run_for(120000)
                        assert not any(u.endswith('night-live.json') for u in requests)
                        assert not errors, errors
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        for pair in page.evaluate(CONTRAST):
                            assert contrast(pair['fg'], pair['bg']) >= Decimal('4.5'), pair
                        page.add_script_tag(path=str(Path(__file__).with_name('axe.min.js')))
                        assert not page.evaluate('async()=> (await axe.run(document)).violations')
                        page.screenshot(path=str(out / f'{state}-{route}-{width}x{height}.png'))
                        if route == 'night':
                            assert page.locator('.night-map').is_visible()
                            search = page.locator('.night-search')
                            if width == 390:
                                assert search.bounding_box()['y'] + search.bounding_box()['height'] <= height * 2
                            search.fill('Auckland Central')
                            assert not page.locator('.night-map').is_visible()
                            row = page.locator('.night-electorates tbody tr:visible')
                            assert row.count() == 1
                            assert 'CHANG, Johan' in row.inner_text()
                            assert '5,000' in row.inner_text() or '5000' in row.inner_text()
                            if width == 390:
                                # Reset auto-scrolling by fill; exactly one viewport scroll from the top.
                                page.evaluate('scrollTo(0, 844)')
                                box = row.bounding_box()
                                assert box['y'] >= 0 and box['y'] + box['height'] <= height, box
                                leader_box = row.locator('td').nth(1).bounding_box()
                                assert leader_box['x'] >= 0 and leader_box['x'] + leader_box['width'] <= width, leader_box
                                page.screenshot(path=str(out / f'{state}-electorate-{width}x{height}.png'))
                            search.fill('')
                            assert page.locator('.night-map').is_visible()
                            assert page.locator('.night-electorates tbody tr:visible').count() == 71
                        context.close()
            finally:
                server.shutdown()
                server.server_close()
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(live_site)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_port}'
        try:
            from datetime import timedelta
            # The per-state builds above cover redeployment after the live loop ends.
            official_site = next(site for state, _, site in sites if state == 'official')
            official_html = (official_site / 'nz-election/night/index.html').read_text()
            assert 'data-mode="Official results"' in official_html
            assert 'Change since preliminary result' in official_html
            assert 'official results due' not in official_html
            for state, pack in handover_packs.items():
                for width, height in [(390, 844), (1280, 800)]:
                    context = browser.new_context(viewport=dict(width=width, height=height))
                    page = context.new_page()
                    # A live poll can hand over only before the shared cutoff.
                    instant = (night_live.CLOSE - timedelta(minutes=5) if state == 'settled'
                               else datetime(2026, 11, 27, 11, tzinfo=timezone.utc))
                    page.clock.install(time=instant)
                    replies = [0]
                    handover = [False]
                    errors = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    def serve(route):
                        if route.request.url.endswith('/night-live.json'):
                            replies[0] += 1
                            route.fulfill(status=200 if handover[0] else 503, content_type='application/json',
                                          body=json.dumps(pack) if handover[0] else '{}')
                        elif route.request.url.startswith(origin + '/'):
                            route.continue_()
                        else:
                            route.abort()
                    context.route('**/*', serve)
                    page.goto(origin + '/unattended/nz-election/night/')
                    page.wait_for_load_state('networkidle')
                    assert page.locator('#night-result-status').is_visible()
                    assert 'official results due 27 November' in page.locator('#night-result-status').inner_text()
                    assert replies[0] == (1 if state == 'settled' else 0)
                    handover[0] = True
                    page.clock.run_for(121000)
                    if state == 'settled':
                        page.wait_for_function("mode => document.querySelector('#night-snapshot').dataset.mode === mode", arg=pack['mode'])
                        assert replies[0] == 2  # One 503 followed by the settled package.
                        assert page.locator('#night-result-status').count() == 0
                        assert 'Live preliminary results' not in page.evaluate('document.body.innerText')
                        nav_link = page.locator('nav[aria-label="Packaged results"] a[href="?sequence=live"]')
                        assert nav_link.is_visible()
                        assert nav_link.get_attribute('href') == '?sequence=live'
                        assert page.locator('#night-live-status').inner_text() == pack['state_sentence']
                        assert 'live updates ended' in page.locator('#night-live-status').inner_text()
                    else:
                        # An old page cannot poll into official results after the cutoff;
                        # the official build checked above supplies that state instead.
                        assert replies[0] == 0
                        assert page.locator('#night-snapshot').get_attribute('data-mode') == night_live.MODE
                        assert 'Live updates ended.' in page.locator('#night-live-status').inner_text()
                    calls = replies[0]
                    page.clock.run_for(120000)
                    assert replies[0] == calls
                    assert not errors, errors
                    page.screenshot(path=str(out / f'handover-{state}-night-{width}x{height}.png'))
                    context.close()
        finally:
            server.shutdown()
            server.server_close()
    print('PASS result states browser: 8 images plus 6 leader/handover images; no terminal polling; DOM handover, named leader within one scroll, contrast, accessibility, overflow')


if __name__ == '__main__':
    main()
