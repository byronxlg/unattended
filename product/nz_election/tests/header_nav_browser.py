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


def settled(page):
    page.evaluate('document.fonts.ready')
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")


def navigation_state(page):
    settled(page)
    return page.get_by_role('banner').get_by_role('navigation').evaluate("""nav => {
        const clip = nav.getBoundingClientRect();
        return [...nav.querySelectorAll('a')].map(link => {
            const box = link.getBoundingClientRect(), css = getComputedStyle(link);
            return {name:link.textContent, current:link.getAttribute('aria-current')==='page',
                focused:link===document.activeElement, opacity:Number(css.opacity), visibility:css.visibility,
                whole:box.left>=clip.left-.5 && box.right<=clip.right+.5 &&
                    box.top>=clip.top-.5 && box.bottom<=clip.bottom+.5,
                overlaps:box.right>clip.left && box.left<clip.right,
                left:box.left, right:box.right, clipLeft:clip.left, clipRight:clip.right};
        });
    }""")


def painted_whole(row):
    return row['whole'] and row['opacity'] == 1 and row['visibility'] == 'visible'


def check_paint(rows, *, binary=False):
    if binary:
        assert all(r['opacity'] in (0, 1) for r in rows), ('HEADER_INTERMEDIATE_OPACITY', rows)
    assert all(r['whole'] for r in rows if r['opacity'] > 0 and r['visibility'] == 'visible'), ('HEADER_PARTIAL_PAINT', rows)
    assert all(r['opacity'] == 0 or r['visibility'] != 'visible'
               for r in rows if r['overlaps'] and not r['whole']), ('HEADER_EDGE_PAINT', rows)


def resize_checks(browser, origin, out):
    sizes = ((390, 844), (844, 390), (1280, 800), (390, 844))
    url = origin + PREFIX + 'electorates/'
    fresh_heights = {}
    for width, height in sizes:
        fresh = browser.new_page(viewport=dict(width=width, height=height), reduced_motion='reduce')
        fresh.goto(url, wait_until='load')
        settled(fresh)
        fresh_heights[width] = fresh.get_by_role('banner').bounding_box()['height']
        fresh.close()
    for focused in (False, True):
        page = browser.new_page(viewport=dict(width=390, height=844), reduced_motion='reduce')
        page.goto(url, wait_until='load')
        settled(page)
        nav = page.get_by_role('banner').get_by_role('navigation')
        if focused:
            # Keep a different, adjacent route focused so resize cannot merely reveal focus.
            links = nav.get_by_role('link')
            current = next(i for i in range(links.count()) if links.nth(i).get_attribute('aria-current') == 'page')
            links.nth(current - 1).focus()
        for step, (width, height) in enumerate(sizes):
            page.set_viewport_size(dict(width=width, height=height))
            rows = navigation_state(page)
            current = [r for r in rows if r['current']]
            assert len(current) == 1 and painted_whole(current[0]), ('HEADER_RESIZE_CURRENT', focused, width, rows)
            check_paint(rows, binary=True)
            actual = page.get_by_role('banner').bounding_box()['height']
            assert abs(actual - fresh_heights[width]) < .5, ('HEADER_RESIZE_HEIGHT', focused, width, actual, fresh_heights[width])
            if focused:
                assert any(r['focused'] for r in rows), ('HEADER_RESIZE_FOCUS_LOST', width)
            page.screenshot(path=str(out / f'resize-{focused}-{step}-{width}.png'))
        page.close()
    print('PASS header resize: same-page 390/844/1280/390, current painted, fresh-load height, binary opacity; with and without focus')


def interaction_checks(browser, origin):
    for width in (360, 390):
        page = browser.new_page(viewport=dict(width=width, height=844), reduced_motion='reduce')
        page.goto(origin + PREFIX + 'electorates/', wait_until='load')
        nav = page.get_by_role('banner').get_by_role('navigation')
        links = nav.get_by_role('link')
        settled(page)
        # Start before the navigation so every forward focus change is a real Tab.
        page.get_by_role('banner').get_by_role('link').first.focus()
        for key, indexes in (('Tab', range(links.count())), ('Shift+Tab', range(links.count()-2, -1, -1))):
            for index in indexes:
                page.keyboard.press(key)
                rows = navigation_state(page)
                assert rows[index]['focused'] and painted_whole(rows[index]), ('HEADER_KEYBOARD_PAINT', width, key, index, rows)
                check_paint(rows)
        # Shift+Tab into the last nav link from its next tab stop, too.
        links.last.focus()
        page.keyboard.press('Tab')
        page.keyboard.press('Shift+Tab')
        rows = navigation_state(page)
        assert rows[-1]['focused'] and painted_whole(rows[-1]), ('HEADER_REVERSE_ENTRY_PAINT', width, rows)
        check_paint(rows)
        page.locator(':focus').evaluate('e=>e.blur()')
        partial_seen = False
        for fraction in (0, .17, .5, .83, 1):
            nav.evaluate("(nav, fraction)=>{nav.scrollLeft=(nav.scrollWidth-nav.clientWidth)*fraction;nav.dispatchEvent(new Event('scroll'));}", fraction)
            rows = navigation_state(page)
            check_paint(rows)
            partial_seen |= any(r['overlaps'] and not r['whole'] for r in rows)
            assert any(r['whole'] and r['opacity'] > 0 and r['visibility'] == 'visible' for r in rows), ('HEADER_SCROLL_EMPTY', width, fraction, rows)
        assert partial_seen, ('HEADER_SCROLL_EDGE_NOT_EXERCISED', width)
        page.close()
    print('PASS header keyboard paint: Tab and Shift+Tab at 360/390; PASS header manual scroll: whole painted labels, partial labels unpainted')


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
            resize_checks(browser, origin, out)
            interaction_checks(browser, origin)
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
