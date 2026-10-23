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


def assert_chart_text_sizes(samples, body_size):
    assert samples, 'HOME_CHART_TEXT_SIZE: no chart labels measured'
    bad = [s for s in samples if not 12 <= s['pixels'] <= body_size]
    assert not bad, 'HOME_CHART_TEXT_SIZE: ' + str(bad)


def chart_type_check(page):
    samples = page.locator('.home-module svg text,.home-module .chart-label,.margin-row a,.market-summary .numeric').evaluate_all("""els=>els.map(e=>{
      const font=parseFloat(getComputedStyle(e).fontSize);
      const matrix=e instanceof SVGTextElement ? e.getScreenCTM() : null;
      return {text:e.textContent,pixels:font*(matrix ? Math.hypot(matrix.c,matrix.d) : 1)};
    })""")
    body_size = page.locator('body').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
    assert_chart_text_sizes(samples, body_size)
    return samples


def home_mark_geometry(page):
    markers = page.locator('.poll-marker > *').evaluate_all("""els=>els.map(e=>{
      const r=e.getBoundingClientRect();return {width:r.width,height:r.height,ratio:r.width/r.height};
    })""")
    if page.locator('#latest-polls .home-chart').count():
        assert markers and all(0.9 <= m['ratio'] <= 1.1 for m in markers), 'HOME_POLL_MARKER_SHAPE: ' + str(markers)
    if page.locator('#trend .home-chart').count():
        offsets = page.locator('#trend').evaluate("""e=>{
          const plot=e.querySelector('.home-chart').getBoundingClientRect();
          const dates=e.querySelectorAll('.chart-dates .chart-label');
          return [dates[0].getBoundingClientRect().left-plot.left,
                  dates[1].getBoundingClientRect().right-(plot.left+plot.width*330/350)];
        }""")
        assert all(abs(offset) <= 0.5 for offset in offsets), 'HOME_TREND_DATE_POSITION: ' + str(offsets)
    return markers


def assert_picker_targets(targets):
    assert targets, 'HOME_PICKER_TARGET: no electorate links measured'
    bad = [t for t in targets if t['width'] < 24 or t['height'] < 24]
    assert not bad, 'HOME_PICKER_TARGET: ' + str(bad)


def picker_target_check(page):
    if not page.locator('.home-picker').count():
        return []
    links = page.locator('.home-picker svg a')
    targets = links.evaluate_all("""els=>els.map(e=>{
      const r=e.getBoundingClientRect();
      return {name:e.getAttribute('aria-label'),width:r.width,height:r.height};
    })""")
    assert_picker_targets(targets)
    return targets


def home_question_check(page):
    if page.viewport_size != {'width': 390, 'height': 844} or not page.locator('#seats.home-hero').count():
        return
    for selector in ('#dates', '#seats .seat-answer', '#seats .strip', '#seats .poll-change'):
        box = page.locator(selector).bounding_box()
        assert box and box['y'] >= 0 and box['y'] + box['height'] <= 844, 'HOME_QUESTION_FOLD: ' + selector + ' ' + str(box)


def night_target_check(page):
    """Every visible night electorate has an adequately sized table selection route."""
    sections = page.locator('.night-electorates')
    if not sections.count():
        return
    assert page.locator('.night-leader-map a,.night-leader-map [tabindex]').count() == 0, 'NIGHT_SMALL_MAP_TARGET'
    targets = page.locator('.night-electorates tbody tr').evaluate_all('''rows=>rows.filter(row=>row.getClientRects().length).map(row=>({
        electorate:row.cells[0].textContent,
        links:[...row.cells[0].querySelectorAll('a[href]')].map(link=>{
            const box=link.getBoundingClientRect();
            return {width:box.width,height:box.height,href:link.getAttribute('href'),name:link.textContent.trim()};
        })
    }))''')
    assert targets, 'NIGHT_SELECTION_ROWS'
    for row in targets:
        assert row['links'], ('NIGHT_SELECTION_LINK', row['electorate'])
        for link in row['links']:
            assert link['width'] >= 24 and link['height'] >= 24, ('NIGHT_SELECTION_TARGET', row)
            assert link['name'] and '/electorates/' in link['href'], ('NIGHT_SELECTION_DESTINATION', row)


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
    if page.locator('.home-hero .strip').count() and page.viewport_size['width'] in (360, 390, 1280):
        assert page.locator('.home-hero .strip').evaluate("""e=>{
          const bar=e.getBoundingClientRect(), main=document.querySelector('main');
          const column=main.getBoundingClientRect(), css=getComputedStyle(main);
          return bar.left>=column.left+parseFloat(css.paddingLeft)-0.5 &&
                 bar.right<=column.right-parseFloat(css.paddingRight)+0.5;
        }"""), 'HOME_SEAT_BAR_BOUNDS'
        if page.locator('.home-chart').count():
            chart_type_check(page)
            home_mark_geometry(page)

    assert max(map(len, page.locator('body').inner_text().split()), default=0) <= 200, 'VISIBLE_TEXT_RUN: ' + url
    if page.viewport_size['width'] in (360, 390):
        assert page.locator('header').evaluate('e=>e.scrollWidth<=e.clientWidth'), 'HEADER_OVERFLOW'
        assert page.locator('header a').evaluate_all('els=>els.every(e=>{const r=e.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.height>=44})'), 'HEADER_TARGET_BOUNDS'
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
    picker_target_check(page)
    home_question_check(page)
    night_target_check(page)
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
        hero = strip.evaluate('e=>Boolean(e.closest(".home-hero"))')
        expected = (120 if page.viewport_size['width'] < 800 else 144) if hero else (72 if page.viewport_size['width'] < 800 else 120)
        assert strip.evaluate('e=>e.getBoundingClientRect().height') == expected, 'STRIP_HEIGHT'
        assert strip.locator('.segment').evaluate_all('els=>els.every(e=>!e.textContent.trim() && getComputedStyle(e).borderTopWidth==="1px")'), 'FILL_LABEL_OR_OUTLINE'
    for lanes in page.locator('.lanes').all():
        assert lanes.evaluate('e=>e.getBoundingClientRect().height') <= (42 if page.viewport_size['width'] < 800 else 21), 'LABEL_HEIGHT'
        tops = lanes.locator('.lane').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().top)')
        assert len(set(tops)) <= (2 if page.viewport_size['width'] < 800 else 1), 'LABEL_ROWS'
    page.add_script_tag(path=str(PRODUCT / 'tests/axe.min.js'))
    violations = page.evaluate('async () => (await axe.run(document)).violations')
    assert not violations, 'AXE_VIOLATIONS: ' + json.dumps(violations)
    from product.nz_election.tests.market_checks import check_markup, check_browser
    market_file = site / 'nz-election/data/markets.json'
    market_rows = json.loads(market_file.read_text())['data'] if market_file.exists() else []
    check_markup(page.content(), market_rows)
    check_browser(page)
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
                        assert page.locator('.local-margin').count() == 0
                    if state == 'unresolved':
                        assert 'Not matched: Kāpiti (local poll)' in page.locator('main').inner_text()
                    if state == 'allocation-tie':
                        assert 'Tie for the last seat between National and Labour; shown unassigned.' in page.locator('main').inner_text()
                    if state == 'source-conflict':
                        assert page.locator('.local-margin').count() == 0
                    if state == 'offline':
                        assert 'fixture run' in page.locator('main').inner_text()
                    if state == 'validation-error':
                        assert 'update failed; showing previous data' in page.locator('main').inner_text()
                    if state.startswith('coalition-'):
                        from coalitions_browser import edit_state
                        edit_state(page, state)
                    if state in COHERENT:
                        assert page.locator('main .seat-module .seat-figure .strip').count() == 1, 'COHERENT_STRIP_REQUIRED'
                        for box in page.locator('.lane').all():
                            if box.is_visible():
                                assert box.evaluate('(e)=>e.scrollWidth<=e.clientWidth'), 'STRIP_LABEL_OVERFLOW'
                    else:
                        assert page.locator('main .seat-module .seat-figure .strip').count() == 0, 'INVALID_CURRENT_STRIP'
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


def legend_check(page):
    overlaps = page.locator('.seat-figure').evaluate_all("""figures=>figures.flatMap(figure=>{
      const visible=e=>e.getClientRects().length;
      const labels=[...figure.querySelectorAll('.lane')].filter(visible);
      const rules=[...figure.querySelectorAll('.segment,.majority,.label-connector')].filter(visible);
      return labels.flatMap(label=>rules.filter(rule=>{
        const a=label.getBoundingClientRect(),b=rule.getBoundingClientRect();
        return a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom;
      }).map(rule=>({label:label.textContent,rule:rule.className})));
    })""")
    assert not overlaps, f'LEGEND_RULE_OVERLAP: {page.viewport_size["width"]}: {overlaps}'


def fold_check(page):
    if not page.locator('.home-hero .strip,.seat-figure').count():
        return None
    assert page.locator('#source-seats.source-note').count() == 1, 'SOURCE_NOTE_REQUIRED'
    bottom = page.locator('#source-seats').evaluate('e=>e.getBoundingClientRect().bottom + scrollY')
    height = min(780, page.viewport_size['height'])
    assert bottom <= height, f'SOURCE_NOTE_BELOW_FOLD: {page.viewport_size["width"]}px bottom={bottom:.2f}px viewport={height}px'
    return bottom


def extra_images(browser, site, origin, out, og_only=False):
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
        row_selector = '.watch-rows a:focus' if focus_page.locator('.watch-rows a').count() else '.home-directory a:focus'
        for _ in range(300):
            focus_page.keyboard.press('Tab')
            if focus_page.locator(row_selector).count():
                break
        assert focus_page.locator(row_selector).count() == 1, 'HOME_ROW_KEYBOARD_FOCUS'
        focus_page.screenshot(path=str(out / 'home-row-focus.png'))
        results.append(dict(state='home-row-focus', path='home-row-focus.png'))
        focus_context.close()
    cards = json.loads((site / 'nz-election/og-manifest.json').read_text())
    from product.nz_election.pipeline.route_cards import route_key
    from product.nz_election.pipeline.build import config
    paths = [r['path'] for r in config('routes')] + ['electorates/' + r['slug'] + '/' for r in config('electorates')]
    assert len(cards) == len({c['key'] for c in cards}) == 81, 'OG_INVENTORY'
    assert {c['route'] for c in cards} == set(paths), 'OG_ROUTES'
    context = browser.new_context(viewport=dict(width=1200, height=630), color_scheme='light', reduced_motion='reduce')
    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
    for card in cards:
        key = route_key(card['route'])
        assert card['key'] == key and card['html'] == 'og/' + key + '.html' and card['png'] == 'og/' + key + '.png', 'OG_PATH'
        page = context.new_page()
        page.goto(origin + PREFIX + 'nz-election/' + card['html'], wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= 1200 && document.documentElement.scrollHeight <= 630'), 'OG_OVERFLOW: ' + key
        assert page.locator('main').evaluate("e=>[...e.querySelectorAll('*')].filter(n=>n.getClientRects().length).every(n=>{const r=n.getBoundingClientRect();return r.left>=0 && r.top>=0 && r.right<=1200 && r.bottom<=630 && n.scrollWidth<=n.clientWidth+1})"), 'OG_CLIPPING: ' + key
        page.add_script_tag(path=str(PRODUCT / 'tests/axe.min.js'))
        violations = page.evaluate('async () => (await axe.run(document)).violations')
        assert not violations, 'AXE_VIOLATIONS: ' + json.dumps(violations)
        name = 'og-' + key + '.png'
        target = site / 'nz-election' / card['png']
        page.screenshot(path=str(target))
        (out / name).write_bytes(target.read_bytes())
        results.append(dict(state='og-' + key, route=card['route'], path=name, site_path=card['png'],
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest(), viewport=dict(width=1200, height=630)))
        page.close()
    context.close()
    return results


ADVANCE_STATES = ('populated', 'missing-day', 'retained', 'absent')
ADVANCE_SIZES = ((360, 780), (390, 844), (1280, 800))


def advance_images(browser, out):
    from copy import deepcopy
    from product.nz_election.pipeline import advance, export
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.m3_checks import check_site
    results = []
    with tempfile.TemporaryDirectory(prefix='nz-advance-states-') as tmp:
        root = Path(tmp)
        original = advance.load(historical=True)
        for state in ADVANCE_STATES:
            payload = deepcopy(original)
            if state == 'missing-day':
                rows = payload[0]['advance-voting']
                del rows[4]
                derived = advance.normalize([(r['date'], r['daily']) for r in rows], kind='daily', start=rows[0]['span_start'])
                for row, values in zip(rows, derived):
                    row.update(values)
            data = root / (state + '-data')
            daily_refresh(data, loaders={'advance': lambda: None if state == 'absent' else payload})
            if state == 'retained':
                def fail():
                    raise ValueError('CONTROLLED_CAPTURE_FAILURE')
                daily_refresh(data, loaders={'advance': fail})
            site = root / state
            build(data, site / 'nz-election', historical_advance=True)
            check_site(site / 'nz-election', export.validate_bundle(data))
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for width, height in ADVANCE_SIZES:
                    context = browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
                    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    page = context.new_page()
                    url = origin + PREFIX + 'nz-election/campaign/'
                    text = check_page(page, url, site, origin)
                    plain = browser.new_context(viewport={'width': width, 'height': height}, java_script_enabled=False)
                    plain.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    nojs = plain.new_page()
                    nojs.goto(url, wait_until='networkidle')
                    assert static_text(nojs) == text, 'ADVANCE_NO_JS'
                    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                    filename = f'advance-{state}-{width}x{height}.png'
                    page.screenshot(path=str(out / filename), full_page=True)
                    results.append(dict(state='advance-' + state, viewport=dict(width=width, height=height), path=filename,
                                        sha256=hashlib.sha256((out / filename).read_bytes()).hexdigest()))
                    plain.close()
                    context.close()
            finally:
                server.shutdown()
                server.server_close()
    assert {(r['state'], r['viewport']['width']) for r in results} == {
        ('advance-' + state, width) for state in ADVANCE_STATES for width, _ in ADVANCE_SIZES}
    return results


def vote_answer_check(answer, viewport):
    assert answer.is_visible(), 'VOTE_ANSWER_NOT_VISIBLE'
    box = answer.bounding_box()
    assert (box and box['width'] > 0 and box['height'] > 0
            and box['x'] >= 0 and box['y'] >= 0
            and box['x'] + box['width'] <= viewport['width']
            and box['y'] + box['height'] <= viewport['height']), 'VOTE_ANSWER_BOX'
    assert answer.inner_text().strip(), 'VOTE_ANSWER_EMPTY'


def vote_images(browser, out, data):
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.snapshots import load_voting
    official = {r['url'] for r in load_voting() if r.get('url')}
    results = []
    with tempfile.TemporaryDirectory(prefix='nz-vote-states-') as tmp:
        for state, clock in [('before', '2026-10-25T10:59:59Z'), ('open', '2026-10-25T11:00:00Z')]:
            site = Path(tmp) / state
            build(data, site / 'nz-election', built=clock)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for width, height in ADVANCE_SIZES:
                    context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce')
                    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    page = context.new_page()
                    check_page(page, origin + PREFIX + 'nz-election/vote/', site, origin)
                    assert page.locator('.vote-first section').first.get_attribute('id') == ('enrol' if state == 'before' else 'places')
                    if width == 390:
                        vote_answer_check(page.locator('#two-votes'), dict(width=width, height=height))
                        assert page.locator('#help').evaluate('e=>e.getBoundingClientRect().top') >= height, 'VOTE_HELP_ABOVE_FOLD'
                    hrefs = page.locator('a').evaluate_all('els=>els.filter(e=>e.getBoundingClientRect().top<innerHeight && e.getBoundingClientRect().bottom>0 && e.getBoundingClientRect().right>0).map(e=>e.getAttribute("href"))')
                    assert hrefs and set(hrefs) <= official, 'VOTE_FIRST_SCREEN_EC_LINKS'
                    name = f'vote-{state}-{width}x{height}.png'
                    page.screenshot(path=str(out / name))
                    results.append(dict(state='vote-' + state, path=name, viewport=dict(width=width, height=height)))
                    context.close()
            finally:
                server.shutdown()
                server.server_close()
    assert len(results) == 6
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=Path('site'))
    parser.add_argument('--out', type=Path, default=Path('artifacts/nz-election/screenshots'))
    parser.add_argument('--og-only', action='store_true', help='Render all registered 1200 by 630 route cards only')
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
    assert len(routes) == expected_count == 81 and len({r['path'] for r in routes}) == expected_count
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
                    if width == 360 and path not in {'', 'polls/', 'electorates/', 'night/', 'vote/', 'parties/', 'campaign/', 'downloads/', 'methods/', 'electorates/wellington-north/', 'electorates/te-tai-tonga/', 'electorates/port-waikato/'}:
                        continue
                    page = context.new_page()
                    url = origin + PREFIX + 'nz-election/' + path
                    text = check_page(page, url, site, origin)
                    if path == "":
                        legend_check(page)
                    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                    assert page.evaluate("[...document.querySelectorAll('*')].every(e=>getComputedStyle(e).animationName==='none')")
                    bottom = fold_check(page) if path == '' and width in (360, 390) else None
                    name = (path.strip('/').replace('/', '--') or 'home') + f'-{width}x{height}.png'
                    target = args.out / name
                    page_height = page.evaluate('document.documentElement.scrollHeight')
                    if path == 'electorates/nelson/' and width == 1280:
                        assert page_height < 2500, f'NELSON_PAGE_HEIGHT: {page_height}'
                    page.screenshot(path=str(target), full_page=path == 'electorates/nelson/')
                    if path == 'parties/':
                        chips = page.locator('.party-picker a')
                        for href in chips.evaluate_all('els=>els.map(e=>e.getAttribute("href"))'):
                            assert page.locator(href).count() == 1, 'PARTY_PICKER_ANCHOR'
                        if width == 390 and page.locator('.party-number').count():
                            viewport = dict(width=width, height=height)
                            vote_answer_check(page.locator('.party-picker'), viewport)
                            vote_answer_check(page.locator('.party-number').first, viewport)
                            chips.first.click()
                            section = page.locator('.party-section').first
                            for selector in ('.party-portrait', '.party-position', '.party-policy', '.party-candidates'):
                                vote_answer_check(section.locator(selector).first, viewport)
                            anchor_name = 'parties-first-anchor-390x844.png'
                            page.screenshot(path=str(args.out / anchor_name))
                            map_images.append(dict(state='parties-first-anchor', path=anchor_name,
                                                   viewport=viewport))
                    if path == 'methods/' and width in (390, 1280) and page.locator('#markets').count():
                        page.locator('#markets').screenshot(path=str(args.out / f'markets-module-{width}.png'))
                        (args.out / f'markets-module-{width}.json').write_text(json.dumps(page.locator('#markets').bounding_box()))
                    plain = nojs.new_page()
                    plain.goto(url, wait_until='networkidle')
                    assert static_text(plain) == text, 'NO_JS_CONTENT_MISMATCH'
                    assert plain.locator('.desktop-nav').is_visible(), 'NO_JS_NAVIGATION_FAILED'
                    manifest.append(dict(route=PREFIX + 'nz-election/' + path, viewport=dict(width=width, height=height),
                                         path=name, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                                         code_sha=build['code_sha'], data_sha=build['data_sha'], page_height=page_height, browser_version=browser.version, source_note_bottom=bottom,
                                         poll_markers_360=home_mark_geometry(page) if path == '' and width == 360 else None))
                    if path == 'electorates/' and width == 390:
                        name_all = 'all-electorate-names-390.png'
                        page.locator('.electorate-directory').screenshot(path=str(args.out / name_all))
                        map_images.append(dict(state='all-electorate-names', path=name_all))
                    if path == 'electorates/':
                        assert plain.locator('.electorate-directory li[id^="electorate-"]').count() == 71
                        assert page.locator('.electorate-map').count() == int(has_geography), 'MAP_PRESENCE'
                        if not has_geography:
                            assert page.locator('.electorate-map').count() == 0
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
                    if path.startswith('electorates/') and path != 'electorates/':
                        assert page.locator('.electorate-locator').count() == 1
                        if width == 390 and not page.locator('.electorate-night').count():
                            vote_answer_check(page.locator('.race-cards'), dict(width=width, height=height))
                            vote_answer_check(page.locator('.enrolled-electorate'), dict(width=width, height=height))
                            if page.locator('.electorate-policy').count():
                                assert page.locator('.electorate-policy').bounding_box()['y'] < 2 * height
                    if path == 'electorates/wellington-north/':
                        if has_baseline:
                            assert 'Wellington Central (2023)' in page.locator('.original-results').inner_text()
                            assert page.locator('.result-bars').is_visible()
                            assert page.locator('.original-results details').count() == 0
                        else:
                            assert page.locator('.original-results').count() == 0
                    if path == 'electorates/te-tai-tonga/':
                        from product.nz_election.pipeline.electorate_pages import detail
                        row = next(r for r in registry if r['slug'] == 'te-tai-tonga')
                        page.locator('main').evaluate('(el,html)=>el.innerHTML=html', '<h1>Te Tai Tonga</h1><p>Controlled missing-data verification.</p>' + detail(row, {}))
                        assert 'Standing in 2026' in page.locator('main').inner_text()
                        assert page.locator('.local-margin').count() == 0
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
            from product.nz_election.tests.night_browser import images as night_images, STATES as NIGHT_STATES, SIZES as NIGHT_SIZES
            additional = ([] if args.og_only else night_images(browser, args.out) + state_images(browser, args.out) + map_images + advance_images(browser, args.out) + vote_images(browser, args.out, site / 'nz-election/data')) + extra_images(browser, site, origin, args.out, args.og_only)
            browser.close()
        if not args.og_only:
            for width in (390, 1280):
                captured = [r['route'] for r in manifest if r['viewport']['width'] == width]
                assert len(captured) == len(set(captured)) == expected_count
                assert set(captured) == {PREFIX + 'nz-election/' + r['path'] for r in routes}
        if not args.og_only and has_geography and has_baseline:
            assert len(manifest) + len(additional) == 306 + len(ADVANCE_STATES) * len(ADVANCE_SIZES) + 6 + len(NIGHT_STATES) * len(NIGHT_SIZES), 'IMAGE_INVENTORY'
        (args.out / 'manifest.json').write_text(json.dumps({'baseline': manifest, 'additional': additional}, indent=2) + '\n')
    finally:
        server.shutdown()
        server.server_close()
    print(f'PASS screenshots: {0 if args.og_only else expected_count} routes, {len(manifest) + len(additional)} images')
    print('Source-note bottom edges: ' + json.dumps([r for r in manifest + additional if r.get('source_note_bottom') is not None]))


if __name__ == '__main__':
    main()
