# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Measure enhanced navigation on every built route, before keyboard interaction."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.build import PREFIX
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler, header_check, header_nav_check


def main():
    from playwright.sync_api import sync_playwright
    site, out = map(Path, sys.argv[1:])
    out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site.parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    routes = sorted(p.parent.relative_to(site).as_posix() for p in site.rglob('index.html'))
    try:
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            for width, height in ((360, 844), (390, 844), (1280, 800)):
                page = browser.new_page(viewport=dict(width=width, height=height), reduced_motion='reduce')
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                for route in routes:
                    route = '' if route == '.' else route + '/'
                    page.goto(origin + PREFIX + route, wait_until='load')
                    page.evaluate('document.fonts.ready')
                    header_nav_check(page)
                    if route in ('', 'electorates/', 'night/'):
                        name = route.strip('/') or 'home'
                        page.screenshot(path=str(out / f'{name}-{width}x{height}.png'))
                    header_check(page)
                page.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f'PASS header navigation: {len(routes)} routes at 360, 390 and 1280; current links visible, no partial labels')


if __name__ == '__main__':
    main()
