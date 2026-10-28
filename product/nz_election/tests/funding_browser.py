# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Check funding navigation without scripting and capture both reader layouts."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from product.nz_election.pipeline import donations, funding_page
from product.nz_election.pipeline.build import PREFIX
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
    url = f'http://127.0.0.1:{server.server_port}{PREFIX}funding/'
    try:
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            page = browser.new_page(java_script_enabled=False, reduced_motion='reduce')
            for width, height in ((390, 844), (1280, 800)):
                page.set_viewport_size(dict(width=width, height=height))
                page.goto(url, wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                for party, rows in funding_page.groups(donations.load_donations()):
                    group = page.locator('[id="' + party + '"]')
                    assert not group.get_by_role('link', name=rows[0]['donor'], exact=True).first.is_visible()
                page.screenshot(path=str(args.out / f'funding-{width}.png'))
                page.screenshot(path=str(args.out / f'funding-{width}-full.png'), full_page=True)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                print(f'{width}: page height={page.evaluate("document.documentElement.scrollHeight")}; '
                      f'pace heading y={page.locator("#funding-time h2").bounding_box()["y"]}')
                if width == 1280:
                    assert page.get_by_role('heading', name='Who gave the most?').bounding_box()['y'] < height
                for party, rows in funding_page.groups(donations.load_donations()):
                    page.goto(url + '#' + party, wait_until='load')
                    group = page.locator('[id="' + party + '"]')
                    for row in rows:
                        assert group.get_by_role('link', name=row['donor'], exact=True).first.is_visible()
                    group.get_by_role('link', name='Close returns and choose a party').click()
                    assert not group.get_by_role('link', name=rows[0]['donor'], exact=True).first.is_visible()
            print('PASS funding: all party fragments reveal their documents without JavaScript')
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
