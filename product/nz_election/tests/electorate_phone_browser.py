# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Reader-visible electorate answers and link destinations in a real browser."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import re
import sys
import threading
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.build import PREFIX, config
from product.nz_election.pipeline import snapshot_views
from product.nz_election.pipeline.electorate_pages import detail
from product.nz_election.pipeline.export import validate_bundle
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler


def map_targets(page):
    maps = page.get_by_role('group', name=re.compile('map', re.I))
    assert maps.count(), 'An accessible electorate map must remain present'
    for graphic in maps.all():
        for link in graphic.get_by_role('link').all():
            assert link.evaluate('e=>Boolean(e.getAttribute("aria-label") || e.textContent.trim())'), 'Unnamed map link'
            assert link.evaluate('''e=>{
                const url=new URL(e.href.baseVal || e.getAttribute('href'), location.href);
                return url.pathname !== location.pathname || !url.hash ||
                    document.getElementById(decodeURIComponent(url.hash.slice(1))) !== null;
            }'''), 'Map link has no destination on this page'


def fold(page, record):
    candidates = record['matched'] + record['added_by_ec']
    heading = page.get_by_role('heading', name='Who is standing in 2026?', exact=True)
    assert heading.is_visible()
    listing = page.get_by_role('list').filter(has=page.get_by_text(candidates[0]['snapshot_name'], exact=True))
    assert listing.count() == 1
    for candidate in candidates:
        name = listing.get_by_text(candidate['snapshot_name'], exact=True)
        assert name.is_visible()
        assert name.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)>=16'), 'Candidate text below reading floor'
        assert candidate['party'] in listing.inner_text()
        if 'list_rank' in candidate:
            assert f'List {candidate["list_rank"]}' in listing.inner_text()
    assert listing.evaluate('''e=>{
        const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);
        let node;
        while(node=walker.nextNode()) {
            if(node.textContent.trim() && parseFloat(getComputedStyle(node.parentElement).fontSize)<16) return false;
        }
        return true;
    }'''), 'Candidate information below the reading floor'
    action = page.get_by_role('link', name='Check your enrolled electorate at vote.nz', exact=True)
    box = action.bounding_box()
    assert box and box['height'] >= 44, 'Enrolment target below 44px'
    assert box['y'] >= 0 and box['y'] + box['height'] <= 844, f'ENROLMENT_BELOW_FOLD: {record["electorate_slug"]}: {box}'
    bounds = listing.bounding_box()
    assert bounds and 0 <= bounds['y'] and bounds['y'] + bounds['height'] <= box['y'], 'All candidates must precede enrolment in the first screen'
    assert listing.evaluate('e=>e.scrollHeight<=e.clientHeight && e.scrollWidth<=e.clientWidth'), 'Candidate list must not hide records in a scroller'
    boundary = page.get_by_role('link', name=re.compile('boundary map', re.I))
    bounds = boundary.bounding_box()
    assert bounds and bounds['height'] >= 44 and bounds['y'] + bounds['height'] <= 844, 'Boundary map action must fit the first screen'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Horizontal page overflow'


def main():
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--case', choices=('fold', 'empty'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    records = snapshot_views.load('candidate-reconciliation-2026')
    maximum = max(len(r['matched'] + r['added_by_ec']) for r in records)
    cases = [r for r in records if len(r['matched'] + r['added_by_ec']) == maximum
             or r['electorate_slug'] in {'nelson', 'wellington-north', 'te-tai-tonga'}]
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(args.site.resolve())))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            page = browser.new_page(viewport=dict(width=390, height=844), reduced_motion='reduce')
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            for record in cases:
                slug = record['electorate_slug']
                page.goto(origin + PREFIX + 'electorates/' + slug + '/', wait_until='networkidle')
                if args.case == 'empty':
                    original = snapshot_views.load
                    def empty(name):
                        return [dict(r, matched=[], added_by_ec=[]) for r in original(name)] if name == 'candidate-reconciliation-2026' else original(name)
                    row = next(r for r in config('electorates') if r['slug'] == slug)
                    with patch.object(snapshot_views, 'load', empty):
                        html = detail(row, validate_bundle(args.site / 'nz-election/data'), '2026-10-17T01:00:00Z')
                    page.get_by_role('main').evaluate('(el,html)=>el.innerHTML=html', html)
                    assert not page.get_by_role('heading', name='Who is standing in 2026?', exact=True).count()
                page.evaluate('document.fonts.ready')
                page.screenshot(path=str(args.out / f'{slug}-{args.case}-390x844.png'), full_page=True)
                map_targets(page)
                if args.case == 'fold':
                    fold(page, record)
                    page.emulate_media(color_scheme='dark')
                    page.screenshot(path=str(args.out / f'{slug}-390x844-dark.png'), full_page=True)
                    page.emulate_media(color_scheme='light')
                    page.set_viewport_size(dict(width=1280, height=900))
                    page.screenshot(path=str(args.out / f'{slug}-1280x900.png'), full_page=True)
                    page.set_viewport_size(dict(width=390, height=844))
            print(f'PASS electorate {args.case}: {len(cases)} electorates; largest candidate list {maximum}')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
