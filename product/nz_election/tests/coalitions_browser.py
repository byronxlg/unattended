"""Host-run coalition interaction and static fallback checks over loopback."""
import argparse
from decimal import Decimal
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
from urllib.parse import quote, unquote

from screenshots import Handler, PREFIX, CONTRAST, contrast, static_text

PRODUCT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT.parents[1]))
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline import coalitions


def serve(site):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, 'http://127.0.0.1:' + str(server.server_port)


def edit_state(page, state):
    root = page.locator('#coalition-explorer')
    root.locator('fieldset').wait_for(state='visible')
    root.locator('[data-select="nat"]').check()
    if state == 'coalition-edit':
        root.locator('[data-select="act"]').check()
        root.locator('[data-count="nat"]').fill('40')
        root.locator('[data-count="nat"]').press('Tab')
    else:
        # Capacity remains unknown; this state never invents a list or vacancy count.
        root.locator('[data-count="nat"]').fill('0')
        root.locator('[data-count="nat"]').press('Tab')
        root.locator('[data-count="tpm"]').fill('20')
        root.locator('[data-count="tpm"]').press('Tab')
        assert 'Vacancies and the occupied House are unknown' in root.inner_text()
    root.scroll_into_view_if_needed()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def context(browser, origin, width=390, **options):
    ctx = browser.new_context(viewport=dict(width=width, height=844 if width == 390 else 800),
                              reduced_motion='reduce', **options)
    ctx.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
    return ctx


def checks(browser, site):
    server, origin = serve(site)
    url = origin + PREFIX + 'nz-election/'
    try:
        for width in (390, 1280):
            ctx = context(browser, origin, width)
            page = ctx.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url, wait_until='networkidle')
            root = page.locator('#coalition-explorer')
            root.locator('fieldset').wait_for(state='visible')
            plain_ctx = context(browser, origin, width, java_script_enabled=False)
            plain = plain_ctx.new_page(); plain.goto(url, wait_until='networkidle')
            assert static_text(plain) == static_text(page)
            assert plain.locator('#coalition-explorer fieldset').is_hidden()
            assert 'requires JavaScript' in plain.locator('[data-note]').inner_text()
            assert plain.locator('main > .seat-figure .majority').count() == 1
            assert plain.locator('#source-seats').is_visible()
            assert root.locator('input:checked').count() == 0
            assert root.locator('[data-select="others"]').count() == 0
            assert '0 seats' in root.locator('[data-live]').inner_text()
            seats = json.loads((site / 'nz-election/data/seats.json').read_text())['data']
            remaining = 71 - sum(seats['assumptions']['electorate_wins'].values())
            assert f'{remaining} electorate seats unassigned' in root.locator('[data-unassigned]').inner_text()
            assert '2026 has different boundaries' in root.inner_text()
            first = root.locator('[data-select="nat"]')
            first.focus(); page.keyboard.press('Space')
            assert first.is_checked()
            style = first.evaluate('(e)=>({width:getComputedStyle(e).outlineWidth,colour:getComputedStyle(e).outlineColor})')
            assert style == {'width': '3px', 'colour': 'rgb(0, 94, 168)'}
            assert root.locator('[data-live]').get_attribute('aria-live') == 'polite'
            edit_state(page, 'coalition-edit')
            shared = page.url
            total = root.locator('[data-live]').inner_text()
            page.reload(wait_until='networkidle')
            assert root.locator('[data-live]').inner_text() == total
            assert page.url == shared
            bad = root.locator('[data-count="nat"]')
            bad.fill('72'); bad.press('Tab')
            assert 'last valid result' in root.locator('[data-warning]').inner_text()
            assert root.locator('[data-live]').inner_text() == total
            root.locator('[data-reset]').click()
            assert root.locator('input:checked').count() == 0 and '#' not in page.url
            assert '0 seats' in root.locator('[data-live]').inner_text()
            edit_state(page, 'coalition-vacancy')
            assert 'majority requirement is assumed' in root.inner_text()
            for pair in page.evaluate(CONTRAST):
                assert contrast(pair['fg'], pair['bg']) >= Decimal('4.5'), pair
            for control in root.locator('input,button').all():
                assert control.bounding_box()['height'] >= 44
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            assert page.evaluate("[...document.querySelectorAll('*')].every(e=>getComputedStyle(e).animationName==='none')")
            state = json.loads(unquote(page.url.split('#coalition=')[1]))
            state['fingerprint'] = '0' * 64
            page.goto(url + coalitions.encode(state), wait_until='networkidle')
            assert 'different poll inputs' in root.locator('[data-warning]').inner_text()
            assert root.locator('input:checked').count() == 0
            for value in ['null', '{}', '{"__proto__":{}}', '"<img src=x onerror=alert(1)>"']:
                page.goto(url + '#coalition=' + quote(value), wait_until='networkidle')
                assert 'invalid' in root.locator('[data-warning]').inner_text()
                assert root.locator('img').count() == 0
            assert not errors, errors
            plain_ctx.close(); ctx.close()
        for resource in ('coalitions.mjs', 'allocator.mjs', 'data/averages.json', 'data/seats.json'):
            ctx = context(browser, origin)
            ctx.route('**/' + resource, lambda route: route.abort())
            page = ctx.new_page(); page.goto(url, wait_until='networkidle')
            assert page.locator('#coalition-explorer fieldset').is_hidden()
            assert page.locator('main > .seat-figure .majority').count() == 1
            assert page.locator('#source-seats').is_visible()
            ctx.close()
    finally:
        server.shutdown(); server.server_close()


def check_unassigned_after_unavailable_allocation(browser, site):
    from coalition_unassigned_cases import unassigned_inputs
    from product.nz_election.pipeline.build import explorer
    from product.nz_election.pipeline import export

    server, origin = serve(site)
    url = origin + PREFIX + 'nz-election/'
    try:
        for no_eligible in (False, True):
            average, seats = unassigned_inputs(no_eligible)
            averages_raw = export.canonical(dict(data=[average]))
            average_hash = export.digest(averages_raw.encode())
            seats_env = dict(data=seats, input_hashes={'averages.json': average_hash})
            seats_raw = export.canonical(seats_env)
            envs = dict(averages=dict(data=[average]), seats=seats_env,
                        manifest=dict(data=[dict(path='seats.json', sha256=export.digest(seats_raw.encode()))]))
            html = ('<!doctype html><html><head><link rel="stylesheet" href="' + url + 'styles.css">'
                    '</head><body><main><h1>Synthetic allocation regression</h1>' + explorer(envs) +
                    '</main></body></html>')
            ctx = context(browser, origin)
            try:
                ctx.route(url, lambda route: route.fulfill(content_type='text/html', body=html))
                ctx.route(url + 'data/averages.json', lambda route: route.fulfill(content_type='application/json', body=averages_raw))
                ctx.route(url + 'data/seats.json', lambda route: route.fulfill(content_type='application/json', body=seats_raw))
                page = ctx.new_page()
                page.goto(url, wait_until='networkidle')
                root = page.locator('#coalition-explorer')
                root.locator('fieldset').wait_for(state='visible')
                unassigned = root.locator('[data-unassigned]')
                assert unassigned.is_visible()
                assert unassigned.inner_text().startswith('71 electorate seats unassigned.')
                assert root.locator('[data-picture] .strip').count() == (0 if no_eligible else 1)
                count = root.locator('[data-count="b"]')
                count.fill('1'); count.press('Tab')
                assert 'Seats are unavailable' in root.locator('[data-live]').inner_text()
                assert root.locator('[data-picture]').inner_text() == ''
                assert unassigned.inner_text().startswith('70 electorate seats unassigned.')
                count.fill('0'); count.press('Tab')
                assert unassigned.inner_text().startswith('71 electorate seats unassigned.')
                assert root.locator('[data-picture] .strip').count() == (0 if no_eligible else 1)
            finally:
                ctx.close()
    finally:
        server.shutdown(); server.server_close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    assert (args.site / 'nz-election/index.html').is_file()
    with sync_playwright() as pw:
        candidates = sorted((Path.home() / 'Library/Caches/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
        candidates += [Path(pw.chromium.executable_path)]
        candidates += sorted((Path.home() / 'Library/Caches/ms-playwright').glob('chromium-*/chrome-mac-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'))
        executable = next((p for p in candidates if p.is_file()), None)
        if executable is None:
            raise SystemExit('CHROMIUM_REQUIRED')
        try:
            browser = pw.chromium.launch(executable_path=str(executable), headless=True, timeout=15000)
        except Exception as exc:
            raise SystemExit('CHROMIUM_REQUIRED: ' + str(exc))
        # The committed latest window is incomplete; use the captured coherent window for edits.
        with tempfile.TemporaryDirectory(prefix='nz-coalition-browser-') as tmp:
            root = Path(tmp)
            refresh(root / 'data', now='2026-10-17T01:00:00Z', end_date='2026-07-18')
            build(root / 'data', root / 'site/nz-election', built='2026-10-17T01:00:00Z')
            checks(browser, root / 'site')
            check_unassigned_after_unavailable_allocation(browser, root / 'site')
        server, origin = serve(args.site.resolve())
        try:
            ctx = context(browser, origin)
            page = ctx.new_page(); page.goto(origin + PREFIX + 'nz-election/', wait_until='networkidle')
            if not page.locator('#coalition-explorer').get_attribute('data-averages'):
                assert page.locator('#coalition-explorer fieldset').is_hidden()
                assert 'incomplete' in page.locator('[data-note]').inner_text()
            ctx.close()
        finally:
            server.shutdown(); server.server_close()
        browser.close()
    print('PASS coalition browser')


if __name__ == '__main__':
    main()
