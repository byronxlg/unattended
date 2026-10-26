"""Fault-injected packaged transport proof, separate from a real workflow rehearsal."""
from copy import deepcopy
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
from product.nz_election.pipeline import export, night, night_live
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.night_page import live_package
from product.nz_election.tests.night_live_cases import Clock, captures
from product.nz_election.tests.screenshots import Handler, CONTRAST, contrast
from decimal import Decimal

STATES = ('live-fresh', 'live-selected-detail', 'live-hidden-resumed', 'live-stale-last-good',
          'live-packaged-fallback', 'live-reference-retention', 'live-leader-change', 'live-pre-close', 'live-post-close')
SIZES = ((390, 844), (1280, 800))


def transition_packages():
    """Synthetic transitions only: never add these frames to the historical data family."""
    from product.nz_election.pipeline.night_page import snapshot
    payloads, _, _ = night.load()
    sequence = next(s for s in payloads['night/index'] if s['id'] == '2023')
    row = deepcopy(payloads[sequence['snapshot_paths'][0][:-5]][0])
    refs = deepcopy(payloads[sequence['reference_path'][:-5]][0])
    electorate = next(e for e, leader in row['leaders'].items() if leader['leader'] and
                      sum(c['electorate'] == e for c in refs['candidates'].values()) > 1)
    old = row['leaders'][electorate]['leader']
    new = next(c for c, candidate in refs['candidates'].items() if candidate['electorate'] == electorate and c != old)
    new_name = refs['candidates'][new]['candidate_name']
    row['mode'] = 'Synthetic transition: offline verification, not election results'
    def package():
        return dict(available=True, mode=night_live.MODE, retrieved_at='2026-11-07T06:00:00Z',
                    reference_version=refs['reference_version'],
                    html='<p>Synthetic transition: offline verification, not election results.</p>' +
                    snapshot(row, refs, 'synthetic-transition', sequence['snapshot_paths'][0]))
    initial = package()
    row['leaders'][electorate].update(leader=new, margin=123)
    leader = package()
    renamed = 'Synthetic reference candidate'
    refs['candidates'][new]['candidate_name'] = renamed
    refs['reference_version'] = export.digest(export.canonical({k: refs[k] for k in ('parties', 'electorates', 'candidates')}).encode())
    complete = package()
    incomplete = dict(available=False, reference_version=refs['reference_version'])
    return dict(initial=initial, leader=leader, incomplete=incomplete, complete=complete,
                selector='#night-row-synthetic-transition-' + electorate,
                old=refs['candidates'][old]['candidate_name'], new=new_name, renamed=renamed)


def transition_proof(page, base, scenario, capture=lambda state: None):
    """Exercise a real page across HTTP 200 packages, including an incomplete new set."""
    cases = transition_packages()
    url = base + 'night-live.json'
    current = [cases['initial'] if scenario == 'leader-change' else cases['leader']]
    delivered = []
    def route(request):
        delivered.append(deepcopy(current[0]))
        request.fulfill(status=200, content_type='application/json', body=json.dumps(current[0]))
    page.route(url, route)
    try:
        page.clock.set_system_time(datetime(2026, 11, 7, 6, 1, tzinfo=timezone.utc))
        page.goto(base + 'night/')
        page.wait_for_function("document.querySelector('#night-snapshot').textContent.includes('Synthetic transition:')")
        cell = page.locator(cases['selector'] + ' td:nth-child(2)')
        before_name = cases['old'] if scenario == 'leader-change' else cases['new']
        assert before_name in cell.inner_text()
        capture('synthetic-' + scenario + '-before')
        # Screenshot caret cleanup can leave style="" on the search input. Include
        # that instrumentation in the baseline, not in the transport comparison.
        before = page.locator('#night-snapshot').inner_html()
        page.evaluate('''() => {
          window.nightParsed = 0;
          const original = window.fetch;
          window.fetch = async (...args) => {
            const response = await original(...args);
            if (String(args[0]).endsWith('/night-live.json')) {
              const parse = response.json.bind(response);
              response.json = async () => { const pack = await parse(); window.nightParsed++; return pack; };
            }
            return response;
          };
        }''')
        def advance(pack):
            parsed = page.evaluate('window.nightParsed')
            current[0] = pack
            with page.expect_response(lambda r: r.url == url) as response:
                page.clock.run_for(125000)
            assert response.value.status == 200
            response.value.finished()
            # Await completion of response.json(), not just delivery of HTTP headers.
            page.wait_for_function('previous => window.nightParsed > previous', arg=parsed)
        if scenario == 'reference-retention':
            assert cases['leader']['reference_version'] != cases['incomplete']['reference_version']
            advance(cases['incomplete'])
            assert delivered[-1] == cases['incomplete']
            assert page.locator('#night-snapshot').inner_html() == before
            assert cases['renamed'] not in page.locator('#night-snapshot').inner_text()
            capture('synthetic-reference-retained')
            advance(cases['complete'])
            expected = cases['renamed']
        else:
            advance(cases['leader'])
            expected = cases['new']
        page.wait_for_function("""({selector, expected}) => document.querySelector(selector).textContent.includes(expected)""",
                               arg=dict(selector=cases['selector'], expected=expected))
        assert expected in cell.inner_text() and before_name not in cell.inner_text()
        assert page.locator('#night-snapshot .night-waterfall').is_visible()
        return dict(scenario='synthetic-' + scenario, before=before_name, after=expected,
                    reference_versions=[pack['reference_version'] for pack in delivered],
                    available=[pack['available'] for pack in delivered], statuses=[200] * len(delivered))
    finally:
        page.unroute(url, route)


def images(browser, out):
    results = []
    with tempfile.TemporaryDirectory(prefix='night-live-browser-') as tmp:
        root = Path(tmp)
        daily_refresh(root / 'data', loaders={'night': night.load})
        build(root / 'data', root / 'site/nz-election', built='2026-11-05T00:00:00Z')
        clock = Clock()
        captured = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
        loaded = night_live.loaded(captured)
        night.prepare(root / 'live', loaded, 'offline-verification', 'a'*40, captured['retrieved_at'])
        envs = {p.relative_to(root / 'live').as_posix()[:-5]: json.loads(p.read_text()) for p in (root / 'live').rglob('*.json')}
        pack = live_package(envs)
        # Populated source-reported seat answers are a labelled synthetic rendering proof.
        payloads, _, _ = night.load()
        historical = next(s for s in payloads['night/index'] if s['id'] == '2023')
        from product.nz_election.pipeline.night_page import snapshot
        row = payloads[historical['snapshot_paths'][0][:-5]][0]
        refs = payloads[historical['reference_path'][:-5]][0]
        pack['html'] = '<p>Offline verification: synthetic live transport with 2023 final counts.</p>' + snapshot(row, refs, 'live-proof', historical['snapshot_paths'][0])
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root / 'site')))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_port}'
        try:
            for state in STATES:
                for width, height in SIZES:
                    context = browser.new_context(viewport=dict(width=width,height=height), reduced_motion='reduce')
                    page = context.new_page()
                    errors, requests = [], []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    context.on('request', lambda r: requests.append(r.url))
                    instant = datetime(2026,11,7,5,59,59,tzinfo=timezone.utc) if state in {'live-pre-close','live-post-close'} else datetime(2026,11,7,6,1,tzinfo=timezone.utc)
                    page.clock.install(time=instant)
                    fail = [state == 'live-packaged-fallback']
                    def route(r):
                        if r.request.url.endswith('/night-live.json'):
                            r.fulfill(status=503 if fail[0] else 200, content_type='application/json', body='{}' if fail[0] else json.dumps(pack))
                        elif r.request.url.startswith(origin + '/'):
                            r.continue_()
                        else:
                            r.abort()
                    context.route('**/*', route)
                    page.goto(origin + '/unattended/nz-election/night/')
                    page.wait_for_load_state('networkidle')
                    if state == 'live-pre-close':
                        assert not any(u.endswith('night-live.json') for u in requests)
                        assert page.locator('.countdown').count() == 1
                    elif state == 'live-post-close':
                        page.clock.run_for(1000)
                        page.wait_for_function("document.querySelector('#night-live-status').textContent.includes('Packaged by the site')")
                        assert page.locator('.countdown').count() == 0
                    elif state == 'live-packaged-fallback':
                        assert 'dated packaged snapshot' in page.locator('#night-live-status').inner_text()
                        assert 'Final snapshot' in page.locator('#night-snapshot').inner_text()
                    else:
                        page.wait_for_function("document.querySelector('#night-live-status').textContent.includes('Packaged by the site')")
                        assert 'House 122' in page.locator('#night-snapshot').inner_text()
                        if state == 'live-selected-detail':
                            page.locator('.night-search').fill('Auckland Central')
                            page.locator('.night-search').focus()
                            page.locator('.night-search').scroll_into_view_if_needed()
                            assert page.locator('.night-electorates tbody tr:visible').count() == 1
                        if state == 'live-stale-last-good':
                            before = page.locator('#night-snapshot').inner_html()
                            fail[0] = True
                            page.clock.run_for(15*60000)
                            assert 'Stale' in page.locator('#night-live-status').inner_text()
                            assert page.locator('#night-snapshot').inner_html() == before
                        if state in {'live-reference-retention', 'live-leader-change'}:
                            transition_proof(page, origin + '/unattended/nz-election/', state.removeprefix('live-'))
                        if state == 'live-hidden-resumed':
                            page.evaluate("""() => {
                                window.resumeFetches = [];
                                const original = window.fetch;
                                window.fetch = (...args) => {
                                    if (String(args[0]).endsWith('/night-live.json')) {
                                        window.resumeFetches.push({at: Date.now(), hidden: document.hidden});
                                    }
                                    return original(...args);
                                };
                                Object.defineProperty(document, 'hidden', {configurable:true, value:true});
                                document.dispatchEvent(new Event('visibilitychange'));
                            }""")
                            count = len([u for u in requests if u.endswith('night-live.json')])
                            # install() leaves time running. Freeze it while hidden so the
                            # synchronous fetch and dispatch return share exactly one instant.
                            page.clock.pause_at(page.evaluate('Date.now() / 1000') + 60)
                            page.clock.run_for(120000)
                            assert len([u for u in requests if u.endswith('night-live.json')]) == count
                            assert page.evaluate('window.resumeFetches') == []
                            # networkidle may already be satisfied by initial load. Await this request instead.
                            with page.expect_response(lambda r: r.url.endswith('/night-live.json')) as resumed:
                                with page.expect_request(lambda r: r.url.endswith('/night-live.json')):
                                    resume = page.evaluate("""() => {
                                        Object.defineProperty(document, 'hidden', {configurable:true, value:false});
                                        document.dispatchEvent(new Event('visibilitychange'));
                                        return {at: Date.now(), calls: window.resumeFetches};
                                    }""")
                                    assert resume['calls'] == [dict(at=resume['at'], hidden=False)], resume
                                    # Flush browser delivery under Playwright's clock, not an application delay.
                                    page.clock.run_for(50)
                            assert resumed.value.status == 200
                            resumed.value.finished()
                            page.clock.run_for(1000)
                            assert len([u for u in requests if u.endswith('night-live.json')]) == count+1
                            assert page.evaluate('window.resumeFetches') == resume['calls']
                            page.clock.resume()
                    page.add_script_tag(path=str(Path(__file__).with_name('axe.min.js')))
                    assert not errors, errors
                    assert all(u.startswith(origin+'/') for u in requests)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    for pair in page.evaluate(CONTRAST):
                        assert contrast(pair['fg'],pair['bg']) >= Decimal('4.5'), pair
                    assert not page.evaluate('async()=> (await axe.run(document)).violations'), state
                    name = f'night-{state}-{width}x{height}.png'
                    page.screenshot(path=str(out/name))
                    results.append(dict(state='night-'+state,path=name,viewport=dict(width=width,height=height)))
                    context.close()
        finally:
            server.shutdown()
            server.server_close()
    assert {(r['state'],r['viewport']['width']) for r in results} == {('night-'+s,w) for s in STATES for w,_ in SIZES}
    return results


if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    from product.nz_election.tests.night_browser import launch_chromium
    out = Path('artifacts/nz-election/night-live')
    out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        with launch_chromium(pw) as browser:
            images(browser,out)
    print('PASS live browser: 18 images; fresh, stale, fallback, selection, visibility, references, boundaries')
