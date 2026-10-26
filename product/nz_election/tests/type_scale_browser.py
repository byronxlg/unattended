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
from product.nz_election.tests.screenshots import Handler


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
            page = browser.new_page(viewport=dict(width=360, height=844), reduced_motion='reduce')
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            route = 'polls/' if args.chart == 'trend' else ''
            page.goto(origin + '/unattended/nz-election/' + route, wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            if args.chart == 'header':
                links = page.locator('body>header a')
                assert links.count() >= 2
                assert links.evaluate_all('''els=>els.every(e=>{
                    const r=e.getBoundingClientRect();
                    return r.left>=0 && r.right<=innerWidth && r.height>=44;
                })'''), 'HEADER_TARGET_BOUNDS'
                print('PASS header: all links in viewport with 44px targets at 360')
            else:
                check_labels(page, args.chart)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'PAGE_OVERFLOW'
            page.screenshot(path=str(args.out / (args.chart + '-360.png')), full_page=True)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
