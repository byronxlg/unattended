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
    for href in page.locator('a[href],link[href]').evaluate_all('(els)=>els.map(e=>e.href)'):
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
    assert all(contrast(c, [255,255,255]) >= 3 for c in boundaries), 'BOUNDARY_CONTRAST'
    targets = page.locator('a').evaluate_all('els=>els.filter(e=>e.getClientRects().length).map(e=>e.getBoundingClientRect().height)')
    assert all(height >= 44 for height in targets), 'SMALL_TARGET'
    page.keyboard.press('Tab')
    focused = page.evaluate('''()=>{const e=document.activeElement,s=getComputedStyle(e);return {text:e.textContent,width:s.outlineWidth,color:s.outlineColor,top:e.getBoundingClientRect().top}}''')
    assert focused['text'] == 'Skip to content' and focused['width'] == '3px' and focused['top'] >= 0, 'FOCUS_NOT_VISIBLE'
    page.keyboard.press('Enter')
    assert page.evaluate('document.activeElement.id') == 'main', 'SKIP_LINK_FAILED'
    page.locator('h1').click()
    page.evaluate('scrollTo(0,0)')
    assert not errors, 'CONSOLE_ERRORS: ' + str(errors)
    return static_text(page)


def static_text(page):
    return page.locator('main').evaluate("""el=>{
      const copy=el.cloneNode(true); copy.querySelector('#coalition-explorer')?.remove();
      return copy.textContent;
    }""")


def state_images(browser, out):
    sys.path.insert(0, str(PRODUCT.parents[1]))
    from product.nz_election.pipeline.refresh import refresh
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.models import ParseDrift
    results = []
    with tempfile.TemporaryDirectory(prefix='nz-screenshot-states-') as tmp:
        root = Path(tmp)
        for state in ('unavailable', 'stale', 'incomplete', 'earlier-coherent-window', 'coalition-edit', 'coalition-vacancy'):
            data = root / (state + '-data')
            site = root / state
            site.mkdir()
            def fail(*args):
                raise ParseDrift('Screenshot unavailable-state verification')
            refresh(data, now='2026-10-17T01:00:00Z',
                    end_date='2026-07-18' if state in {'earlier-coherent-window', 'coalition-edit', 'coalition-vacancy'} else None,
                    **({'parse': fail} if state == 'unavailable' else {}),
                    run_url='local-stale-verification' if state == 'stale' else 'offline-verification')
            build(data, site / 'nz-election', built='2026-10-17T12:00:00Z')
            target = site / 'nz-election/index.html'
            content = target.read_text()
            content = content.replace('<h1>Polls and seats</h1>', '<h1>Polls and seats</h1><p>Layout verification: ' +
                                      state.replace('-', ' ') + '. Not a current projection.</p>')
            target.write_text(content)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for width, height in [(390, 844), (1280, 800)]:
                    context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce')
                    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    page = context.new_page()
                    check_page(page, origin + PREFIX + 'nz-election/', site, origin)
                    if state.startswith('coalition-'):
                        from coalitions_browser import edit_state
                        edit_state(page, state)
                    if state in {'earlier-coherent-window', 'coalition-edit', 'coalition-vacancy'}:
                        assert page.locator('main > .seat-figure .strip').count() == 1, 'COHERENT_STRIP_REQUIRED'
                        for box in page.locator('.seat-label,.lane').all():
                            if box.is_visible():
                                assert box.evaluate('(e)=>e.scrollWidth<=e.clientWidth'), 'STRIP_LABEL_OVERFLOW'
                    else:
                        assert page.locator('main > .seat-figure .strip').count() == 0, 'INVALID_CURRENT_STRIP'
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit('PLAYWRIGHT_REQUIRED: ' + str(exc))
    site = args.site.resolve()
    routes = json.loads((PRODUCT / 'config/routes.json').read_text())
    assert len(routes) == 6 and len({r['path'] for r in routes}) == 6
    args.out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    build = json.loads((site / 'nz-election/build-manifest.json').read_text())['data']
    manifest = []
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
            for width, height in [(390, 844), (1280, 800)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
                context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                nojs = browser.new_context(viewport={'width': width, 'height': height}, java_script_enabled=False)
                nojs.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                for route in routes:
                    path = route['path']
                    page = context.new_page()
                    url = origin + PREFIX + 'nz-election/' + path
                    text = check_page(page, url, site, origin)
                    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                    assert page.evaluate("[...document.querySelectorAll('*')].every(e=>getComputedStyle(e).animationName==='none')")
                    name = (path.strip('/') or 'polls') + f'-{width}x{height}.png'
                    target = args.out / name
                    page.screenshot(path=str(target))
                    plain = nojs.new_page()
                    plain.goto(url, wait_until='networkidle')
                    assert static_text(plain) == text, 'NO_JS_CONTENT_MISMATCH'
                    manifest.append(dict(route=PREFIX + 'nz-election/' + path, viewport=dict(width=width, height=height),
                                         path=name, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                                         code_sha=build['code_sha'], data_sha=build['data_sha'], browser_version=browser.version))
                    plain.close()
                    page.close()
                nojs.close()
                context.close()
            additional = state_images(browser, args.out)
            browser.close()
        (args.out / 'manifest.json').write_text(json.dumps({'baseline': manifest, 'additional': additional}, indent=2) + '\n')
    finally:
        server.shutdown()
        server.server_close()
    print('PASS screenshots: 6 routes, 12 baseline images')


if __name__ == '__main__':
    main()
