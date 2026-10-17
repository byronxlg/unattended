# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Real Chromium checks over loopback only; no external resources are fetched."""
import argparse
from decimal import Decimal
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
from urllib.parse import unquote, urlsplit

PRODUCT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT.parents[1]))
PREFIX = '/unattended/'


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith(PREFIX):
            self.send_error(404)
            return
        self.path = '/' + self.path[len(PREFIX):]
        super().do_GET()

    def log_message(self, *args):
        pass


def luminance(rgb):
    values = [Decimal(n) / 255 for n in rgb[:3]]
    channels = [v / Decimal('12.92') if v <= Decimal('0.04045') else ((v + Decimal('0.055')) / Decimal('1.055')) ** Decimal('2.4') for v in values]
    return sum(v * w for v, w in zip(channels, map(Decimal, ['0.2126', '0.7152', '0.0722'])))


def contrast(a, b):
    x, y = sorted([luminance(a), luminance(b)])
    return (y + Decimal('0.05')) / (x + Decimal('0.05'))


CONTRAST = '''() => [...document.querySelectorAll('body *')].filter(el =>
  [...el.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim()) &&
  el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden').map(el => {
    const parse = color => (color.match(/[\\d.]+/g)||[]).map(Number);
    let p=el, bg;
    while(p) {bg=parse(getComputedStyle(p).backgroundColor); if(bg.length===3 || bg[3]===1) break; p=p.parentElement;}
    return {text:el.textContent.slice(0,80),fg:parse(getComputedStyle(el).color),bg:p?bg:[255,255,255]};
  })'''


def check_page(page, url, site, origin):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
    response = page.goto(url, wait_until='networkidle')
    assert response and response.status == 200, 'ROUTE_FAILED: ' + url
    assert page.locator('main h1').count() == 1
    from product.nz_election.pipeline.scripts import validate_scripts
    assert validate_scripts(page.content())
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'PAGE_OVERFLOW: ' + url
    for href in page.locator('a[href],link[href]').evaluate_all('(els)=>els.map(e=>new URL(e.getAttribute("href"), document.baseURI).href)'):
        parsed = urlsplit(href)
        if not href.startswith(origin):
            continue
        assert parsed.path.startswith(PREFIX), 'BAD_PREFIX: ' + href
        path = site / unquote(parsed.path[len(PREFIX):])
        if path.is_dir():
            path = path / 'index.html'
        assert path.resolve().is_relative_to(site.resolve()) and path.is_file(), 'BROKEN_LINK: ' + href
        if parsed.fragment and path.suffix == '.html':
            from html.parser import HTMLParser
            class Ids(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.ids = set()
                def handle_starttag(self, tag, attrs):
                    self.ids.update(v for k, v in attrs if k == 'id')
            parser = Ids()
            parser.feed(path.read_text())
            assert unquote(parsed.fragment) in parser.ids, 'BROKEN_FRAGMENT: ' + href
    for pair in page.evaluate(CONTRAST):
        assert contrast(pair['fg'], pair['bg']) >= Decimal('4.5'), 'TEXT_CONTRAST: ' + str(pair)
    boundaries = page.locator('.segment,.threshold-rule,td,th').evaluate_all('''els=>els.map(el=>{
      const s=getComputedStyle(el); const c=s.borderLeftWidth!=='0px'?s.borderLeftColor:s.borderBottomColor;
      return (c.match(/[\\d.]+/g)||[]).map(Number);
    })''')
    paper = page.locator('body').evaluate("e=>getComputedStyle(e).backgroundColor.match(/[\\d.]+/g).map(Number)")
    assert all(contrast(c, paper) >= 3 for c in boundaries), 'BOUNDARY_CONTRAST'
    targets = page.locator('a:not(svg a),summary,button,input').evaluate_all('els=>els.filter(e=>e.getClientRects().length).map(e=>e.getBoundingClientRect().height)')
    assert all(height >= 44 for height in targets), 'SMALL_TARGET'
    page.keyboard.press('Tab')
    focused = page.evaluate('''()=>{const e=document.activeElement,s=getComputedStyle(e);return {text:e.textContent,width:s.outlineWidth,color:s.outlineColor,top:e.getBoundingClientRect().top}}''')
    assert focused['text'] == 'Skip to content' and focused['width'] == '3px' and focused['top'] >= 0, 'FOCUS_NOT_VISIBLE'
    page.keyboard.press('Enter')
    assert page.evaluate('document.activeElement.id') == 'main', 'SKIP_LINK_FAILED'
    page.evaluate('document.activeElement.blur()')
    page.evaluate('scrollTo(0,0)')
    from product.nz_election.tests.design_checks import provenance
    provenance(page.content())
    levels = page.locator('main h1,main h2,main h3,main h4').evaluate_all('els=>els.map(e=>Number(e.tagName[1]))')
    assert all(b <= a + 1 for a, b in zip(levels, levels[1:])), 'HEADING_OUTLINE'
    for strip in page.locator('.strip').all():
        assert strip.evaluate('e=>e.getBoundingClientRect().height') == (72 if page.viewport_size['width'] < 800 else 120), 'STRIP_HEIGHT'
        assert strip.locator('.segment').evaluate_all('els=>els.every(e=>!e.textContent.trim() && getComputedStyle(e).borderTopWidth==="1px")'), 'FILL_LABEL_OR_OUTLINE'
    for lanes in page.locator('.lanes').all():
        assert lanes.evaluate('e=>e.getBoundingClientRect().height') <= (42 if page.viewport_size['width'] < 800 else 21), 'LABEL_HEIGHT'
        tops = lanes.locator('.lane').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().top)')
        assert len(set(tops)) <= (2 if page.viewport_size['width'] < 800 else 1), 'LABEL_ROWS'
    page.add_script_tag(path=str(PRODUCT / 'tests/axe.min.js'))
    violations = page.evaluate('async () => (await axe.run(document)).violations')
    assert not violations, 'AXE_VIOLATIONS: ' + json.dumps(violations)
    assert not errors, 'CONSOLE_ERRORS: ' + str(errors)
    return static_text(page)


def static_text(page):
    return page.locator('main').evaluate("""el=>{
      const copy=el.cloneNode(true); copy.querySelector('#coalition-explorer')?.remove(); copy.querySelector('.electorate-search')?.remove();
      return copy.textContent;
    }""")


def state_images(browser, out):
    from playwright.sync_api import expect

    sys.path.insert(0, str(PRODUCT.parents[1]))
    results = []
    with tempfile.TemporaryDirectory(prefix='nz-screenshot-states-') as tmp:
        root = Path(tmp)
        from product.nz_election.tests.design_states import STATES, COHERENT, fixture
        for state in STATES:
            site, route_path = fixture(root, state)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for width, height in ([(360, 780)] if state == 'earlier-coherent-window' else []) + [(390, 844), (1280, 800)]:
                    context = browser.new_context(viewport=dict(width=width, height=height), color_scheme='light', reduced_motion='reduce')
                    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    page = context.new_page()
                    check_page(page, origin + PREFIX + 'nz-election/' + route_path, site, origin)
                    if state in ('invalid-link', 'changed-inputs'):
                        # The skip-link check replaces the scenario hash with #main.
                        page.goto(origin + PREFIX + 'nz-election/' + route_path, wait_until='networkidle')
                    if state == 'invalid-count':
                        root_control = page.locator('[data-count="nat"]')
                        root_control.fill('72')
                        root_control.press('Tab')
                        expect(page.locator('[data-warning]')).to_contain_text('last valid result is shown')
                    if state == 'invalid-link':
                        expect(page.locator('[data-warning]')).to_contain_text('This coalition link is invalid.')
                    if state == 'changed-inputs':
                        expect(page.locator('[data-warning]')).to_contain_text('This link uses different poll inputs.')
                    if state == 'missing-baseline':
                        assert 'No 2023 candidate results for this electorate' in page.locator('main').inner_text()
                    if state == 'unresolved':
                        assert 'Not matched: Kāpiti (local poll)' in page.locator('main').inner_text()
                    if state == 'allocation-tie':
                        assert 'Tie for the last seat between National and Labour; shown unassigned.' in page.locator('main').inner_text()
                    if state == 'source-conflict':
                        assert 'Comparison unresolved' in page.locator('main').inner_text()
                    if state == 'offline':
                        assert 'fixture run' in page.locator('main').inner_text()
                    if state == 'validation-error':
                        assert 'update failed; showing previous data' in page.locator('main').inner_text()
                    if state.startswith('coalition-'):
                        from coalitions_browser import edit_state
                        edit_state(page, state)
                    if state in COHERENT:
                        assert page.locator('main > .seat-figure .strip').count() == 1, 'COHERENT_STRIP_REQUIRED'
                        for box in page.locator('.lane').all():
                            if box.is_visible():
                                assert box.evaluate('(e)=>e.scrollWidth<=e.clientWidth'), 'STRIP_LABEL_OVERFLOW'
                    else:
                        assert page.locator('main > .seat-figure .strip').count() == 0, 'INVALID_CURRENT_STRIP'
                    if state == 'earlier-coherent-window' and width in (360, 390):
                        fold_check(page)
                    name = f'{state}-{width}x{height}.png'
                    page.screenshot(path=str(out / name), full_page=True)
                    results.append(dict(state=state, viewport=dict(width=width, height=height), path=name,
                                        sha256=hashlib.sha256((out / name).read_bytes()).hexdigest(),
                                        code_sha=json.loads((site / 'nz-election/build-manifest.json').read_text())['code_sha'],
                                        data_sha=None, browser_version=browser.version))
                    context.close()
            finally:
                server.shutdown()
                server.server_close()
    return results


def fold_check(page):
    bottom = page.locator('#source-seats').evaluate('e=>e.getBoundingClientRect().bottom + scrollY')
    height = min(780, page.viewport_size['height'])
    assert bottom <= height, f'SOURCE_NOTE_BELOW_FOLD: {page.viewport_size["width"]}px bottom={bottom:.2f}px viewport={height}px'
    return bottom


def extra_images(browser, site, origin, out, og_only=False):
    from html import escape
    from product.nz_election.pipeline import export, geography
    from product.nz_election.pipeline.build import render, strip, config
    results = []
    for width, height, mode in ([] if og_only else [(390, 844, 'dark')]):
        context = browser.new_context(viewport=dict(width=width, height=height), color_scheme=mode, reduced_motion='reduce')
        context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
        page = context.new_page()
        check_page(page, origin + PREFIX + 'nz-election/', site, origin)
        bottom = fold_check(page)
        name = f'home-{width}-{mode}.png'
        page.screenshot(path=str(out / name))
        results.append(dict(state='home-' + mode, path=name, source_note_bottom=bottom))
        context.close()
    if not og_only:
        focus_context = browser.new_context(viewport=dict(width=390, height=844))
        focus_context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
        focus_page = focus_context.new_page()
        focus_page.goto(origin + PREFIX + 'nz-election/', wait_until='networkidle')
        focus_page.keyboard.press('Tab')
        focus_page.screenshot(path=str(out / 'home-keyboard-focus.png'))
        results.append(dict(state='keyboard-focus', path='home-keyboard-focus.png'))
        focus_page.keyboard.press('Enter')
        focus_page.screenshot(path=str(out / 'home-main-focus.png'))
        results.append(dict(state='main-focus', path='home-main-focus.png'))
        focus_context.close()
    envs = export.validate_bundle(site / 'nz-election/data') if (site / 'nz-election/data').exists() else {}
    context = browser.new_context(viewport=dict(width=1200, height=630), color_scheme='light', reduced_motion='reduce')
    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
    for slug in ('home', 'wellington-north'):
        page = context.new_page()
        page.goto(origin + PREFIX + 'nz-election/', wait_until='networkidle')
        if slug == 'home':
            home = json.loads((site / 'nz-election/home-presentation.json').read_text())
            result = home['result']
            title = home['title']
            picture = strip(result).split('<details class="seat-data">')[0] if result else ''
            source = home['source']
        else:
            row = next(r for r in config('electorates') if r['slug'] == slug)
            title = row['name'] + ': your electorate on the 2025 boundaries'
            collections = {k: envs[k + '-2025'] for k in geography.KINDS if k + '-2025' in envs} or geography.load()
            picture = geography.svg(collections, [row], row['id']).replace('<svg ', '<svg aria-describedby="source-og-geography" ')
            from product.nz_election.pipeline.build import link, compact_time
            entry = next(e for e in json.loads((geography.ROOT / 'manifest.json').read_text())['entries'] if e['path'] == 'stats-nz/general-2025.geojson')
            source = '<p class="source-note" id="source-og-geography">From ' + link(entry['url'], 'Stats NZ, 2025 boundaries') + f'. Retrieved <time datetime="{entry["captured_at"]}">{compact_time(entry["captured_at"])}</time>. ' + escape(entry['licence']) + '.</p>'
        page.set_content(render('og', title=escape(title), prefix=origin + PREFIX + 'nz-election/', picture=picture, source=source), wait_until='networkidle')
        page.add_script_tag(path=str(PRODUCT / 'tests/axe.min.js'))
        violations = page.evaluate('async () => (await axe.run(document)).violations')
        assert not violations, 'AXE_VIOLATIONS: ' + json.dumps(violations)
        name = 'og-' + slug + '.png'
        page.screenshot(path=str(out / name))
        results.append(dict(state='og-' + slug, path=name, viewport=dict(width=1200, height=630)))
        page.close()
    context.close()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--og-only', action='store_true', help='Render the two 1200 by 630 identity cards only')
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit('PLAYWRIGHT_REQUIRED: ' + str(exc))
    site = args.site.resolve()
    routes = json.loads((PRODUCT / 'config/routes.json').read_text())
    registry = json.loads((PRODUCT / 'config/electorates.json').read_text())
    expected_count = len(routes) + len(registry)
    routes += [dict(path='electorates/' + r['slug'] + '/') for r in registry]
    assert len(routes) == expected_count and len({r['path'] for r in routes}) == expected_count
    args.out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    build = json.loads((site / 'nz-election/build-manifest.json').read_text())['data']
    manifest = []
    map_images = []
    has_geography = (site / 'nz-election/data/general-2025.json').is_file()
    has_baseline = (site / 'nz-election/data/baseline-2023.json').is_file()
    try:
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
            for width, height in ([] if args.og_only else [(360, 780), (390, 844), (1280, 800)]):
                context = browser.new_context(viewport={'width': width, 'height': height}, color_scheme='light', reduced_motion='reduce')
                context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                nojs = browser.new_context(viewport={'width': width, 'height': height}, java_script_enabled=False)
                nojs.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                for route in routes:
                    path = route['path']
                    if width == 360 and path not in {'', 'electorates/', 'night/', 'campaign/', 'downloads/', 'methods/', 'electorates/wellington-north/', 'electorates/te-tai-tonga/'}:
                        continue
                    page = context.new_page()
                    url = origin + PREFIX + 'nz-election/' + path
                    text = check_page(page, url, site, origin)
                    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                    assert page.evaluate("[...document.querySelectorAll('*')].every(e=>getComputedStyle(e).animationName==='none')")
                    bottom = fold_check(page) if path == '' and width in (360, 390) else None
                    name = (path.strip('/').replace('/', '--') or 'polls') + f'-{width}x{height}.png'
                    target = args.out / name
                    page.screenshot(path=str(target))
                    plain = nojs.new_page()
                    plain.goto(url, wait_until='networkidle')
                    assert static_text(plain) == text, 'NO_JS_CONTENT_MISMATCH'
                    if width <= 390:
                        plain.locator('.phone-menu summary').click()
                        assert plain.locator('.phone-menu nav').is_visible(), 'NO_JS_MENU_FAILED'
                        plain.locator('.phone-menu summary').click()
                    manifest.append(dict(route=PREFIX + 'nz-election/' + path, viewport=dict(width=width, height=height),
                                         path=name, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                                         code_sha=build['code_sha'], data_sha=build['data_sha'], browser_version=browser.version, source_note_bottom=bottom))
                    if path == 'electorates/' and width == 390:
                        name_all = 'all-electorate-names-390.png'
                        page.locator('.electorate-directory').screenshot(path=str(args.out / name_all))
                        map_images.append(dict(state='all-electorate-names', path=name_all))
                    if path == 'electorates/':
                        assert plain.locator('.electorate-directory li').count() == 71
                        assert page.locator('.electorate-map').count() == int(has_geography), 'MAP_PRESENCE'
                        if not has_geography:
                            assert 'Map not available' in text
                        page.locator('#electorate-search').fill('TAMAKI')
                        assert page.locator('[data-search-key]:visible').count() >= 1
                        page.locator('#electorate-search').fill('')
                        for kind in (('general', 'maori') if has_geography else ()):
                            page.locator('#map-' + kind).check()
                            page.locator('#map-' + kind).focus()
                            assert page.locator('.layer-' + kind).is_visible()
                            state_name = f'map-{kind}-{width}x{height}.png'
                            page.screenshot(path=str(args.out / state_name))
                            map_images.append(dict(state='map-' + kind, path=state_name,
                                                   viewport=dict(width=width, height=height),
                                                   sha256=hashlib.sha256((args.out / state_name).read_bytes()).hexdigest()))
                    if path == 'electorates/' and has_geography:
                        page.locator('#map-general').check()
                        page.locator('a[href$="/electorates/wellington-north/"]').last.focus()
                        state_name = f'map-selected-focus-{width}x{height}.png'
                        page.screenshot(path=str(args.out / state_name))
                        map_images.append(dict(state='map-selected-focus', path=state_name,
                                               viewport=dict(width=width, height=height),
                                               sha256=hashlib.sha256((args.out / state_name).read_bytes()).hexdigest()))
                    if path == 'electorates/wellington-north/':
                        if has_baseline:
                            assert 'Wellington Central (2023)' in text
                        else:
                            assert 'No candidate baseline or party baseline available' in text
                    if path == 'electorates/te-tai-tonga/':
                        from product.nz_election.pipeline.electorate_pages import detail
                        row = next(r for r in registry if r['slug'] == 'te-tai-tonga')
                        page.locator('main').evaluate('(el,html)=>el.innerHTML=html', '<h1>Te Tai Tonga</h1><p>Controlled missing-data verification.</p>' + detail(row, {}))
                        assert 'Official candidates not available' in page.locator('main').inner_text()
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        state_name = f'electorate-missing-data-{width}x{height}.png'
                        page.screenshot(path=str(args.out / state_name), full_page=True)
                        map_images.append(dict(state='electorate-missing-data', path=state_name,
                                               viewport=dict(width=width, height=height),
                                               sha256=hashlib.sha256((args.out / state_name).read_bytes()).hexdigest()))
                    plain.close()
                    page.close()
                nojs.close()
                context.close()
            additional = ([] if args.og_only else state_images(browser, args.out) + map_images) + extra_images(browser, site, origin, args.out, args.og_only)
            browser.close()
        if not args.og_only:
            for width in (390, 1280):
                captured = [r['route'] for r in manifest if r['viewport']['width'] == width]
                assert len(captured) == len(set(captured)) == expected_count
                assert set(captured) == {PREFIX + 'nz-election/' + r['path'] for r in routes}
        (args.out / 'manifest.json').write_text(json.dumps({'baseline': manifest, 'additional': additional}, indent=2) + '\n')
    finally:
        server.shutdown()
        server.server_close()
    print(f'PASS screenshots: {0 if args.og_only else expected_count} routes, {len(manifest) + len(additional)} images')
    print('Source-note bottom edges: ' + json.dumps([r for r in manifest + additional if r.get('source_note_bottom') is not None]))


if __name__ == '__main__':
    main()
