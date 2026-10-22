# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Measure the real picker cascade at phone widths, with no external requests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from product.nz_election.pipeline.build import PRODUCT
from product.nz_election.pipeline.parties_page import page
from product.nz_election.tests.night_browser import launch_chromium


def main():
    from playwright.sync_api import sync_playwright
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    css = '\n'.join((PRODUCT / 'web' / name).read_text() for name in ('styles.css', 'parties.css'))
    markup = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width, initial-scale=1">'
              f'<style>{css}</style></head><body><main>' + page({}, '2026-10-22T07:00:00Z') + '</main></body></html>')
    with sync_playwright() as pw:
        browser = launch_chromium(pw)
        try:
            for width, height in [(360, 780), (390, 844), (1280, 800)]:
                tab = browser.new_page(viewport=dict(width=width, height=height), reduced_motion='reduce')
                tab.route('**/*', lambda route: route.abort())
                tab.set_content(markup, wait_until='networkidle')
                boxes = tab.locator('.party-picker a').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return {top:r.top,width:r.width,height:r.height}})')
                tab.screenshot(path=str(out / f'parties-picker-{width}x{height}.png'))
                assert len(boxes) == 7, boxes
                assert max(b['top'] for b in boxes) - min(b['top'] for b in boxes) < 0.5, f'PARTY_PICKER_WRAPS at {width}: {boxes}'
                assert all(b['width'] >= 24 and b['height'] >= 24 for b in boxes), boxes
                picker = tab.locator('.party-picker')
                assert picker.evaluate('e=>getComputedStyle(e).overflowX') == 'auto'
                assert tab.evaluate('document.documentElement.scrollWidth <= innerWidth')
                tab.locator('.party-picker a').last.focus()
                assert tab.locator('.party-picker a').last.evaluate('e=>{const a=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();return a.left>=p.left && a.right<=p.right+1}')
                tab.close()
        finally:
            browser.close()
    print('PASS party picker: same top offsets and minimum 24 px targets at 360, 390, 1280')


if __name__ == '__main__':
    main()
