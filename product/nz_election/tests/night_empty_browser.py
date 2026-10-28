# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Offline first-capture recovery and the shared polling deadline."""
from datetime import timedelta
import json
import mimetypes
from pathlib import Path
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.sunsets import NIGHT_CLOSE
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.night_live_browser import transition_packages
from playwright.sync_api import sync_playwright, expect


def proof(browser, root, *, ended=False, width=390):
    built = '2026-11-08T06:01:00Z' if ended else '2026-11-07T06:01:00Z'
    site = build(root / 'absent', root / ('ended' if ended else 'waiting') / 'nz-election', built=built)
    context = browser.new_context(viewport=dict(width=width, height=844 if width == 390 else 800), reduced_motion='reduce')
    page = context.new_page()
    errors, requests, navigations = [], [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('framenavigated', lambda frame: navigations.append(frame.url))
    page.clock.install(time=NIGHT_CLOSE + timedelta(minutes=1) if ended else NIGHT_CLOSE - timedelta(minutes=5))
    current = [None]
    pack = transition_packages()['initial']
    pack.update(loop_ends_at=NIGHT_CLOSE.isoformat(), loop_ended=False)

    def route(request):
        path = urlparse(request.request.url).path.removeprefix('/unattended/nz-election/')
        if path == 'night-live.json':
            requests.append(page.evaluate('Date.now()'))
            request.fulfill(status=503 if current[0] is None else 200, content_type='application/json',
                            body=json.dumps(current[0] or {}))
        else:
            file = site / (path + 'index.html' if path.endswith('/') else path)
            request.fulfill(path=file, content_type='text/javascript' if file.suffix == '.mjs' else
                            mimetypes.guess_type(file)[0] or 'application/octet-stream')

    context.route('**/*', route)
    try:
        page.goto('https://night.test/unattended/nz-election/night/')
        page.wait_for_load_state('networkidle')
        main = page.locator('main')
        expect(main.get_by_role('link', name='Official Electoral Commission results')).to_have_attribute('href', 'https://www.electionresults.govt.nz/')
        if ended:
            expect(main).to_contain_text('Live updates ended.')
            page.clock.run_for(180000)
            assert requests == []
        else:
            expect(main).to_contain_text('Waiting for the first complete results.')
            assert len(requests) == 1
            page.screenshot(path=str(root / f'waiting-{width}.png'))
            # Exercise both a failed acquisition and a valid but still empty publication.
            current[0] = dict(available=False, loop_ended=False, loop_ends_at=NIGHT_CLOSE.isoformat())
            with page.expect_response('**/night-live.json'):
                page.clock.run_for(120000)
            expect(main).to_contain_text('Waiting for the first complete results.')
            current[0] = pack
            with page.expect_response('**/night-live.json'):
                page.clock.run_for(60000)
            expect(main).to_contain_text('House 122')
            expect(main).to_contain_text('2,851,211')
            expect(main.get_by_role('heading', name='Who is winning?', exact=True)).to_have_count(1)
            assert len(navigations) == 1
            page.get_by_role('textbox').fill('Auckland Central')
            expect(main).to_contain_text('Auckland Central')
            page.get_by_role('textbox').fill('')
            page.screenshot(path=str(root / f'populated-{width}.png'))
            page.clock.set_system_time(NIGHT_CLOSE)
            count = len(requests)
            page.clock.run_for(181000)
            expect(main).to_contain_text('Live updates ended.')
            expect(main).to_contain_text('House 122')
            assert len(requests) == count
            assert all(at < NIGHT_CLOSE.timestamp() * 1000 for at in requests)
        assert not errors, errors
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(root / f'{"ended" if ended else "retained"}-{width}.png'))
    finally:
        context.close()


def main():
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw, launch_chromium(pw) as browser:
        for width in (390, 1280):
            proof(browser, root, width=width)
            proof(browser, root, ended=True, width=width)
    print('PASS empty night browser: waiting, first complete counts without navigation, cutoff; ended build makes zero requests; 390x844 and 1280x800')


if __name__ == '__main__':
    main()
