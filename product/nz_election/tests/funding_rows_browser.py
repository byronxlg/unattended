# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Verify every funding return fits a phone and retains its accessible facts."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import donations, funding_page
from product.nz_election.pipeline.build import PREFIX, observation_label
from product.nz_election.tests.night_browser import launch_chromium
from product.nz_election.tests.screenshots import Handler


def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(args.site.resolve())))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    groups = funding_page.groups(donations.load_donations())
    count = sum(len(records) for _, records in groups)
    try:
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            page = browser.new_page(java_script_enabled=False, reduced_motion='reduce', color_scheme='light')
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            for width, height in ((360, 844), (390, 844), (1280, 800), (1280, 900)):
                page.set_viewport_size(dict(width=width, height=height))
                for party, records in groups:
                    page.goto(origin + PREFIX + 'funding/#' + party, wait_until='load')
                    page.evaluate('document.fonts.ready')
                    region = page.get_by_role('region', name=funding_page.name(party, records) + ' declared returns', exact=True)
                    assert region.is_visible()
                    assert page.evaluate('document.documentElement.scrollWidth === innerWidth'), f'{width}: page overflow'
                    assert region.evaluate('e => e.scrollWidth <= e.clientWidth'), f'{width}: {party} returns overflow'
                    table = region.get_by_role('table')
                    for label in ('Donor', 'Amount', 'Received'):
                        assert table.get_by_role('columnheader', name=label, exact=True).count() == 1
                    rows = table.get_by_role('row').all()[1:]
                    ordered = sorted(records, key=lambda r: (r.get('received', ''), r['id']), reverse=True)
                    assert len(rows) == len(ordered)
                    for row, record in zip(rows, ordered, strict=True):
                        link = row.get_by_role('link', name=record['donor'], exact=True)
                        assert link.is_visible() and link.get_attribute('href') == record['document_url']
                        amount = funding_page.money(donations.amount_cents(record['amount_nzd']))
                        assert row.get_by_role('cell', name=amount, exact=True).is_visible()
                        if record.get('received'):
                            assert row.get_by_role('cell', name=observation_label(record['received']), exact=True).is_visible()
                        for cell in row.get_by_role('cell').all():
                            assert cell.evaluate('e => e.scrollWidth <= e.clientWidth'), f'{width}: clipped return'
                    if party == groups[0][0]:
                        page.screenshot(path=str(args.out / f'returns-{width}x{height}.png'))
                        page.screenshot(path=str(args.out / f'funding-{width}x{height}-full.png'), full_page=True)
                        if width == 390:
                            page.emulate_media(color_scheme='dark')
                            page.screenshot(path=str(args.out / 'returns-390-dark.png'))
                            page.emulate_media(color_scheme='light')
                print(f'PASS {width}x{height}: page and all {len(groups)} returns regions fit; {count} returns retain donor, amount, date and document')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
