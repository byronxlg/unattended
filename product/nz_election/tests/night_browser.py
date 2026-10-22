# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Deterministic replay, browser XML parity and exact screenshot states."""
import base64
from decimal import Decimal
from functools import partial
from http.server import ThreadingHTTPServer
import json
import re
from pathlib import Path
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.tests.screenshots import Handler, check_page, CONTRAST, contrast
from product.nz_election.pipeline import night, xml_parser, fixtures
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh

STATES = ('illustrative-start', 'illustrative-middle', 'illustrative-end', 'recorded-demo',
          'final-2017', 'final-2020', 'final-2023', 'reset-focus', 'no-js', 'absent',
          'waterfall-early', 'waterfall-middle', 'waterfall-final', 'overhang', 'unresolved-tie',
          'unchecked-capacity', 'selected-leader', 'electorate-map', 'electorate-table',
          'official-comparison', 'no-specials', 'unavailable-live')
SIZES = ((390, 844), (1280, 800))


def images(browser, out):
    results = []
    with tempfile.TemporaryDirectory(prefix='night-browser-') as tmp:
        root = Path(tmp)
        daily_refresh(root / 'data', loaders={'night': night.load})
        build(root / 'data', root / 'site/nz-election', built='2026-11-05T00:00:00Z')
        build(root / 'missing', root / 'empty/nz-election', built='2026-11-05T00:00:00Z')
        for absent in (False, True):
            site = root / ('empty' if absent else 'site')
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for state in STATES:
                    if (state == 'absent') != absent:
                        continue
                    for width, height in SIZES:
                        context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce', java_script_enabled=state != 'no-js')
                        requests = []
                        context.on('request', lambda req: requests.append(req.url))
                        context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                        page.clock.install()
                        sequence = 'illustrative-2023' if state.startswith('illustrative') or state == 'reset-focus' else 'mediademo' if state == 'recorded-demo' else state.removeprefix('final-') if state.startswith('final-') else '2023'
                        url = origin + '/unattended/nz-election/night/?sequence=' + sequence
                        if state == 'no-js':
                            page.goto(url)
                            assert page.locator('table').count() == 3
                            assert not page.locator('#night-controls').is_visible()
                        else:
                            check_page(page, url, site, origin)
                        page.evaluate('scrollTo(0, 0)')
                        if width == 390:
                            for locator in (page.locator('.countdown'), page.locator('main a[href="/unattended/nz-election/vote/"]')):
                                box = locator.bounding_box()
                                assert box and 0 <= box['y'] and box['y'] + box['height'] <= height, 'NIGHT_PRE_CLOSE_FOLD'
                            if not absent:
                                assert page.locator('.countdown').bounding_box()['y'] < page.locator('#night-snapshot').bounding_box()['y']
                        if sequence == 'illustrative-2023':
                            label = page.locator('#night-snapshot .night-mode')
                            assert 'Illustrative replay based on 2023 final results' in label.inner_text()
                            assert page.locator('#night-play').inner_text() == 'Play'
                            assert page.locator('#night-clock').get_attribute('aria-live') == 'off'
                            assert page.locator('#night-announcement').get_attribute('aria-live') == 'polite'
                            assert 'Replay frame 1 of 3, 0:00 elapsed' in page.locator('#night-snapshot').inner_text()
                            page.locator('#night-speed').select_option('60')
                            if state != 'illustrative-start':
                                page.locator('#night-play').click()
                                page.clock.run_for(5000 if state == 'illustrative-middle' else 10000)
                                if state == 'illustrative-middle':
                                    page.locator('#night-play').click()
                                    assert page.locator('[data-frame="1"]:visible').count() == 1
                                    assert 'Replay frame 2 of 3, 5:00 elapsed' in page.locator('#night-snapshot').inner_text()
                                    assert 'published only in the final archive' in page.locator('#night-snapshot').inner_text()
                                    page.clock.run_for(30000)
                                    assert page.locator('[data-frame="1"]:visible').count() == 1
                                else:
                                    assert '2,851,211' in page.locator('#night-snapshot').inner_text()
                                    assert 'House 122' in page.locator('#night-snapshot').inner_text()
                                    assert 'Final archive updated' in page.locator('#night-snapshot .night-frame-context').inner_text()
                                    assert page.locator('#night-announcement').inner_text() == 'Replay ended.'
                                if state == 'reset-focus':
                                    page.locator('#night-play').focus()
                                    page.keyboard.press('Tab')
                                    page.keyboard.press('Enter')
                                    assert page.locator('#night-reset:focus-visible').count() == 1
                                    assert page.locator('[data-frame="0"]:visible').count() == 1
                            assert label.is_visible()
                        if state.startswith('final-'):
                            assert 'Final snapshot' in page.locator('#night-snapshot').inner_text()
                            assert not page.locator('#night-controls').is_visible()
                        if state == 'recorded-demo':
                            assert 'Recorded demo' in page.locator('#night-snapshot').inner_text()
                        if absent:
                            assert page.locator('figure,table,progress').count() == 0
                            assert page.locator('a[href="https://www.electionresults.govt.nz/"]').count() == 1
                        if state in {'waterfall-early', 'waterfall-middle', 'waterfall-final', 'overhang', 'unresolved-tie', 'unchecked-capacity', 'selected-leader', 'electorate-map', 'electorate-table', 'official-comparison', 'no-specials', 'unavailable-live'}:
                            from copy import deepcopy
                            from product.nz_election.pipeline.night_page import snapshot
                            payloads, _, _ = night.load()
                            row = deepcopy(payloads['night/illustrative-2023/step-' + ('0' if state == 'waterfall-early' else '1' if state == 'waterfall-middle' else '2')][0])
                            refs = payloads['night/references/2023'][0]
                            if state == 'unavailable-live':
                                seq = next(s for s in payloads['night/index'] if s['id'] == '2026-media')
                                row = payloads[seq['snapshot_paths'][0][:-5]][0]
                                refs = payloads[seq['reference_path'][:-5]][0]
                            if state == 'unchecked-capacity':
                                row['capacity_verified'] = False
                            if state == 'unresolved-tie':
                                row['allocation_input'] = dict(partyVotes={'a':50,'b':50}, electorateWins={'a':0,'b':0}, lists={'a':['a1'],'b':['b1']}, electorateWinners={'a':[],'b':[]}, nonListWinners=[], baseSeats=1)
                            if state in {'official-comparison', 'no-specials'}:
                                row['preliminary_baseline'] = dict(status='preliminary', election='synthetic-2026', reference_version='synthetic', date='2026-11-08', seats={'a':60,'b':60})
                                row['official_result'] = dict(status='official', election='synthetic-2026', reference_version='synthetic', date='2026-11-27', seats={'a':61,'b':59})
                            html = '<p class="night-mode">Offline verification: labelled synthetic proof; ' + row['mode'] + '</p>' + snapshot(row, refs, 'proof', 'night/illustrative-2023/step-2.json')
                            page.locator('#night-snapshot').evaluate('(node,html)=>node.innerHTML=html', html)
                            if state == 'selected-leader':
                                page.locator('.night-search').fill('Auckland Central')
                                assert page.locator('.night-electorates tbody tr:visible').count() == 1
                            target = '.night-search' if state in {'selected-leader','electorate-table'} else '.night-electorates h2' if state in {'electorate-map','unavailable-live'} else '.night-waterfall' if state in {'waterfall-final','overhang','unchecked-capacity'} else '.night-calculation' if state in {'waterfall-early','waterfall-middle','unresolved-tie'} else 'h2:has-text("Change since preliminary result")'
                            page.locator(target).evaluate('(node)=>node.scrollIntoView()')
                        assert not errors, errors
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), state
                        for pair in page.evaluate(CONTRAST):
                            assert contrast(pair['fg'], pair['bg']) >= Decimal('4.5'), pair
                        if state != 'no-js':
                            assert not page.evaluate('async () => (await axe.run(document)).violations'), state
                        assert all(u.startswith(origin + '/') for u in requests), 'REPLAY_OFFICIAL_FEED_REQUEST'
                        assert not any('/data/' in u for u in requests), 'REPLAY_FETCH'
                        name = f'night-{state}-{width}x{height}.png'
                        if state in STATES[:10]:
                            page.evaluate('scrollTo(0, 0)')
                        page.screenshot(path=str(out / name))
                        results.append(dict(state='night-' + state, path=name, viewport=dict(width=width, height=height)))
                        context.close()
            finally:
                server.shutdown()
                server.server_close()
    assert {(r['state'], r['viewport']['width']) for r in results} == {('night-' + s, w) for s in STATES for w, _ in SIZES}
    return results


def parity(browser):
    page = browser.new_page()
    # Loopback gives Web Crypto a secure origin without accessing any external host.
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / 'parser.mjs').write_bytes((fixtures.ROOT.parent / 'web/night-parser.mjs').read_bytes())
        (site / 'index.html').write_text('<title>Parser checks</title>')
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            page.goto(f'http://127.0.0.1:{server.server_port}/unattended/index.html')
            page.evaluate("async()=>{window.parser=await import('./parser.mjs')}")
            for year in ('2017', '2020', '2023', 'mediademo'):
                prefix = 'ec-' + year + '-xml/'
                filename = 'election-obs1' if year == 'mediademo' else 'election'
                paths = [prefix+n+'.xml' for n in ('parties','electorates','candidates',filename)]
                raw = fixtures.captures(paths=set(paths))
                refs = xml_parser.references(*(raw[p] for p in paths[:3]))
                result = page.evaluate('''async files=>{
                    const bytes=files.map(s=>new TextEncoder().encode(s));
                    const refs=await parser.references(...bytes.slice(0,3));
                    return {refs,result:parser.election(bytes[3],refs)};
                }''', [raw[p].decode('utf-8-sig') for p in paths])
                assert result['refs'] == refs
                assert result['result'] == xml_parser.election(raw[paths[3]], refs)
                valid = raw[paths[3]].decode('utf-8-sig')
                cases = []
                for token in ('', ' ', 'null', 'true', '1.5', '1000000000', '１', '-1', '1e3',
                              '<x>1</x>', '1<x>2</x>', '<![CDATA[1.5]]>'):
                    malformed = re.sub(r'<votes>.*?</votes>', lambda _: '<votes>' + token + '</votes>', valid, count=1)
                    cases.append(malformed)
                cases += ['', '<broken>', '<parties/>', '<election/>',
                          '<election updated="2026-10-20T14:22:32"/>', valid[:-20],
                          '<!DOCTYPE election><election/>',
                          '<!DOCTYPE election [<!ENTITY x "1">]><election>&x;</election>']
                for malformed in cases:
                    try:
                        xml_parser.election(malformed.encode(), refs)
                    except ValueError as exc:
                        expected = str(exc)
                    else:
                        raise AssertionError('malformed election accepted')
                    if '<votes><x>1</x></votes>' in malformed:
                        assert expected == 'XML_COUNT'
                    actual = page.evaluate('''({text, refs})=>{
                        try {parser.election(new TextEncoder().encode(text), refs); return 'accepted';}
                        catch(e) {return e.message;}
                    }''', dict(text=malformed, refs=refs))
                    assert actual == expected, (year, malformed[:120], expected, actual)

            prefix = 'ec-2026-media-xml/'
            raw = fixtures.captures(paths={e['path'] for e in json.loads((fixtures.ROOT / 'manifest.json').read_text())['entries'] if e['path'].startswith(prefix)})
            refs = xml_parser.references(*(raw[prefix+n+'.xml'] for n in ('parties','electorates','candidates')))
            for path, captured in raw.items():
                if not re.fullmatch(prefix + r'e[0-9]{2}/e[0-9]{2}\.xml', path):
                    continue
                cases = [captured.decode()]
                for field in ('votes', 'total_voting_places', 'total_candidates'):
                    for token in ('', 'null', 'true', '1.5', '1000000000', '異', '<x>1</x>'):
                        cases.append(re.sub('<' + field + '>.*?</' + field + '>', '<' + field + '>' + token + '</' + field + '>', captured.decode(), count=1))
                for text in cases:
                    try:
                        expected = xml_parser.detail(text.encode(), refs)
                    except ValueError as exc:
                        expected = str(exc)
                    actual = page.evaluate('({text,refs})=>{try{return parser.detail(new TextEncoder().encode(text),refs)}catch(e){return e.message}}', dict(text=text, refs=refs))
                    assert actual == expected, (path, expected, actual)

            for value in ['', None, [], {}, True, 1.5, 10**100, '１', ' 1', '01', '1e3', '-1', '1000000000', '1\n', '1\r', '1\u2028', '1\u2029']:
                try:
                    xml_parser.count(value)
                except ValueError as exc:
                    expected = str(exc)
                else:
                    raise AssertionError(value)
                assert page.evaluate('v=>{try{parser.count(v)}catch(e){return e.message}}', value) == expected
            for value in [None, [], {}, True, 1.5, 10**100, '異']:
                try:
                    xml_parser.document(value, 'election')
                except ValueError as exc:
                    expected = str(exc)
                else:
                    raise AssertionError('malformed document accepted')
                assert page.evaluate('v=>{try{parser.documentXML(v,"election")}catch(e){return e.message}}', value) == expected == 'XML_DOCUMENT'
            for raw_bytes in [b'', b'\xff', b'<election>' + b' ' * 2_000_000]:
                try:
                    xml_parser.document(raw_bytes, 'election')
                except ValueError as exc:
                    expected = str(exc)
                else:
                    raise AssertionError('malformed document accepted')
                assert page.evaluate('v=>{try{parser.documentXML(Uint8Array.from(atob(v), c=>c.charCodeAt(0)),"election")}catch(e){return e.message}}', base64.b64encode(raw_bytes).decode()) == expected == 'XML_DOCUMENT'

        finally:
            server.shutdown()
            server.server_close()
            page.close()


def launch_chromium(pw):
    candidates = sorted((Path.home() / 'Library/Caches/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
    executable = next((p for p in candidates if p.is_file()), None)
    # On CI, Playwright resolves its own platform-specific installed browser.
    return pw.chromium.launch(**({'executable_path': str(executable)} if executable else {}))


def main():
    from playwright.sync_api import sync_playwright
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('artifacts/nz-election/night')
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        with launch_chromium(pw) as browser:
            parity(browser)
            images(browser, out)
    print('PASS night browser: clock, labels, archives, no-JS, absent, no official-feed requests, XML parity; ' + str(len(STATES) * len(SIZES)) + ' images')


if __name__ == '__main__':
    main()
