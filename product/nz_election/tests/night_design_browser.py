# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Rendered night design behavior, using offline replay and terminal packages."""
from datetime import datetime
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from playwright.sync_api import sync_playwright
from product.nz_election.pipeline import export, fixtures, night, night_live, result_states
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.presentation import election_countdown
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler


def main(out):
    def capture(name):
        path = 'result-states/' + name + '.json'
        return json.loads(fixtures.captures(paths={path})[path])

    initial = capture('2026-11-07-preliminary-final')
    envs = None
    with sync_playwright() as pw, launch_chromium(pw) as browser:
        for state, now in [('replay', '2026-10-26T00:00:00Z'), ('live', initial['retrieved_at']),
                           ('settled', '2026-11-08T06:00:00Z'), ('official', '2026-11-27T11:00:00Z')]:
            if state == 'replay':
                loader = night.load
            else:
                loaded = night_live.loaded(initial) if state == 'live' else result_states.transition(
                    envs, state, now=now, captured=capture('2026-11-27-official') if state == 'official' else None)
                loader = lambda: loaded
            data, site = out / state / 'data', out / state / 'site'
            daily_refresh(data, loaders={'night': loader}, now=now)
            envs = export.validate_bundle(data)
            build(data, site / 'nz-election', built=now)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(site)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = f'http://127.0.0.1:{server.server_port}'
            try:
                for width, height in [(390, 844), (1280, 900)]:
                    context = browser.new_context(viewport=dict(width=width, height=height), reduced_motion='reduce')
                    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
                    page = context.new_page()
                    page.clock.install(time=datetime.fromisoformat(now))
                    page.goto(origin + '/unattended/nz-election/night/')
                    page.wait_for_load_state('networkidle')
                    assert page.get_by_role('heading', name='Who is winning?', exact=True).is_visible()
                    graphic = page.get_by_role('img', name=re.compile('One dot per seat'))
                    assert graphic.is_visible()
                    strokes = graphic.locator('path').evaluate_all('''paths => paths.map(path => {
                        const style = getComputedStyle(path), box = path.getBBox();
                        return {dash: style.strokeDasharray, color: style.stroke, width: parseFloat(style.strokeWidth),
                                bounds: [box.x, box.y, box.width, box.height]};
                    })''')
                    marker = next(stroke for stroke in strokes if stroke['dash'] != 'none')
                    assert any(stroke['dash'] == 'none' and stroke['width'] > marker['width'] and
                               stroke['color'] != marker['color'] and stroke['bounds'] == marker['bounds'] for stroke in strokes)
                    search = page.get_by_role('searchbox', name='Find an electorate')
                    cards = page.locator('.night-combination')
                    assert page.get_by_role('heading', name='Who is winning?', exact=True).bounding_box()['y'] < search.bounding_box()['y']
                    assert search.bounding_box()['y'] < cards.first.bounding_box()['y']
                    assert cards.last.bounding_box()['y'] < page.get_by_text(re.compile(r'^[\d,]+ valid party votes$')).bounding_box()['y']
                    jump = page.get_by_role('link', name='Find your electorate', exact=True)
                    assert jump.bounding_box()['y'] < cards.first.bounding_box()['y']
                    expected_combinations = 3 if state == 'replay' else 1
                    assert page.get_by_text('Majority reached', exact=True).count() == expected_combinations
                    assert all(mark.is_visible() for mark in page.get_by_text('Majority reached', exact=True).all())
                    if state == 'replay':
                        assert page.get_by_text(election_countdown(now), exact=True).is_visible()
                        assert page.get_by_role('link', name='How to vote', exact=True).is_visible()
                        assert page.get_by_text('Replay of 2023', exact=True).is_visible()
                        assert 'Results last updated 10 November 2024 at 00:00.' not in page.locator('#night-snapshot').inner_text()
                        assert '2023 final count' in page.locator('#night-snapshot').inner_text()
                        replay = next(s for s in envs['night/index']['data'] if s['id'] == '2023')
                        archive = envs[replay['snapshot_paths'][0][:-5]]
                        captured = max(s['fetched_at'] for s in archive['source']
                                       if s['id'] in archive['data'][0]['source_ref'])
                        assert page.get_by_text(f'Source XML captured at {captured}.').is_visible()
                        assert 'timezone unverified' not in page.locator('body').inner_text()
                        assert page.get_by_role('heading', name='All 8 majority combinations', exact=True).is_visible()
                        combinations = page.get_by_role('list', name=re.compile(r'All majority combinations$'))
                        groups = combinations.get_by_role('listitem')
                        assert groups.count() == 8
                        assert all(group.is_visible() for group in groups.all())
                        assert all(int(re.search(r': (\d+) seats$', group.inner_text())[1]) >= 62 for group in groups.all())
                    jump.click()
                    search_y = search.bounding_box()['y']
                    assert 0 <= search_y < height, f'JUMP_TARGET: state={state}, width={width}, y={search_y}'
                    search.fill('Auckland Central')
                    table = page.get_by_role('table', name=re.compile('electorate', re.I))
                    matches = table.get_by_role('row').filter(has_text='Auckland Central')
                    assert matches.count() == 1 and matches.is_visible()
                    if state == 'replay':
                        assert page.get_by_text('Provisional leaders, not elected members.', exact=True).is_visible()
                        assert page.get_by_text('2023 electorates, on their original boundaries. Links lead to today’s electorate information; no votes are transferred to new boundaries.', exact=True).is_visible()
                    else:
                        assert 'Johan Chang' in matches.inner_text() and 'CHANG, Johan' in matches.inner_text()
                    page.screenshot(path=str(out / f'{state}-filtered-{width}x{height}.png'), full_page=True)
                    search.fill('')
                    page.screenshot(path=str(out / f'{state}-{width}x{height}.png'), full_page=True)
                    context.close()
            finally:
                server.shutdown()
                server.server_close()
    print('PASS night design behavior: replay, live, settled, official')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
