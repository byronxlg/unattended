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
    sites = []
    for state, now in [('settled', '2026-11-08T06:00:00Z'), ('official', '2026-11-27T11:00:00Z')]:
        loaded = result_states.transition(envs, state, now=now, captured=capture('result-states/2026-11-27-official.json') if state == 'official' else None)
        data = out / (state + '-data')
        daily_refresh(data, loaders={'night': lambda: loaded}, now=now)
        envs = export.validate_bundle(data)
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
                            page.locator('.night-search').fill('Auckland Central')
                            assert page.locator('.night-electorates tbody tr:visible').count() == 1
                        context.close()
            finally:
                server.shutdown()
                server.server_close()
    print('PASS result states browser: 8 images; no terminal polling; search, contrast, accessibility, overflow')


if __name__ == '__main__':
    main()
