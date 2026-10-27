# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Measure phone targets and SVG lettering using the rendered coordinate transform."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler, header_check
from product.nz_election.pipeline.build import config, PREFIX


def measure(page, selector):
    return page.locator(selector).evaluate_all('''els=>els.map(e=>{
        const r=e.getBoundingClientRect(), m=e.getScreenCTM();
        return {text:e.textContent, size:parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.c,m.d),
                left:r.left,right:r.right,top:r.top,bottom:r.bottom};
    })''')


def check_labels(page, chart):
    selector = 'svg.hex-map' if chart == 'map' else 'svg.trend.narrow'
    assert page.locator(selector).is_visible(), 'SVG_CHART_ABSENT: ' + chart
    labels = measure(page, selector + ' text')
    assert len(labels) >= (2 if chart == 'map' else 7), 'SVG_LABELS_ABSENT: ' + chart
    for label in labels:
        assert label['size'] >= 12, ('SVG_TEXT_TOO_SMALL', chart, label)
        assert 0 <= label['left'] < label['right'] <= 360, ('SVG_TEXT_BOUNDS', chart, label)
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            overlap = (min(first['right'], second['right']) - max(first['left'], second['left']) > .5
                       and min(first['bottom'], second['bottom']) - max(first['top'], second['top']) > .5)
            assert not overlap, ('SVG_TEXT_OVERLAP', chart, first, second)
    print(f'PASS {chart}: {len(labels)} labels, minimum rendered size {min(r["size"] for r in labels):.2f}px at 360; no overlaps')


def main():
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True, help='Built directory containing nz-election/')
    parser.add_argument('--chart', choices=('map', 'trend', 'header'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(args.site.resolve())))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            page = browser.new_page(viewport=dict(width=360, height=844), reduced_motion='reduce',
                                    java_script_enabled=args.chart != 'header')
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            route = 'polls/' if args.chart == 'trend' else ''
            page.goto(origin + '/unattended/nz-election/' + route, wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            if args.chart == 'header':
                expected = {PREFIX + r['path'] for r in config('routes')}
                for width, height in ((360, 844), (390, 844), (1280, 800)):
                    page.set_viewport_size(dict(width=width, height=height))
                    for path in sorted(args.site.joinpath('nz-election').rglob('index.html')):
                        route = path.parent.relative_to(args.site / 'nz-election').as_posix()
                        route = '' if route == '.' else route + '/'
                        page.goto(origin + PREFIX + route, wait_until='load')
                        page.evaluate('document.fonts.ready')
                        header_check(page)
                        linked = set(page.locator('header a, footer a').evaluate_all('els=>els.map(e=>e.getAttribute("href"))'))
                        assert expected <= linked, ('HEADER_ROUTES', route, expected - linked)
                        assert page.locator('footer a').evaluate_all('''els=>els.every(e=>{
                            const r=e.getBoundingClientRect();
                            return r.height>=44 && r.width>=44 && parseFloat(getComputedStyle(e).fontSize)>=16;
                        })'''), 'FOOTER_ROUTE_TARGETS'
                        current = page.locator('header nav a[aria-current="page"], footer a[aria-current="page"]')
                        assert current.count() == int(route in {r['path'] for r in config('routes')})
                        if current.count():
                            assert current.get_attribute('href') == PREFIX + route
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'PAGE_OVERFLOW'
                        name = route.strip('/').replace('/', '--') or 'home'
                        page.screenshot(path=str(args.out / f'{name}-{width}x{height}.png'))
                print('PASS header: one row below 100px at 360 and 390; all routes linked; keyboard-accessible 44px targets and 16px type')
            else:
                check_labels(page, args.chart)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'PAGE_OVERFLOW'
            page.screenshot(path=str(args.out / (args.chart + '-360.png')), full_page=True)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
