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


def rendered_cell(cell, context):
    measured = cell.evaluate("""e => {
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 1;
        const paint = canvas.getContext('2d');
        const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
        const text = [];
        let node;
        while ((node = walker.nextNode())) {
            if (!node.textContent.trim()) continue;
            const range = document.createRange();
            range.selectNodeContents(node);
            const style = getComputedStyle(node.parentElement);
            let opacity = 1;
            for (let parent = node.parentElement; parent; parent = parent.parentElement) {
                opacity *= Number(getComputedStyle(parent).opacity);
            }
            paint.clearRect(0, 0, 1, 1);
            paint.fillStyle = style.color;
            paint.fillRect(0, 0, 1, 1);
            text.push({rects: [...range.getClientRects()].map(r => ({
                left: r.left, right: r.right, width: r.width, height: r.height
            })), opacity, color: style.color, alpha: paint.getImageData(0, 0, 1, 1).data[3],
            visibility: style.visibility});
        }
        return {viewport: innerWidth, scrollWidth: e.scrollWidth, clientWidth: e.clientWidth,
                scrollHeight: e.scrollHeight, clientHeight: e.clientHeight, text};
    }""")
    message = f'{context}: rendered measurements={measured}'
    assert measured['scrollWidth'] <= measured['clientWidth'], message
    assert measured['scrollHeight'] <= measured['clientHeight'], message
    assert measured['text'], message
    for text in measured['text']:
        assert text['opacity'] > 0 and text['alpha'] > 0 and text['visibility'] == 'visible', message
        assert text['rects'], message
        for rect in text['rects']:
            assert 0 <= rect['left'] <= rect['right'] <= measured['viewport'], message
            assert rect['width'] > 0 and rect['height'] > 0, message


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
    try:
        groups = funding_page.groups(donations.load_donations())
        count = sum(len(records) for _, records in groups)
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            page = browser.new_page(java_script_enabled=False, reduced_motion='reduce', color_scheme='light')
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            for width, height in ((360, 844), (390, 844), (1280, 800), (1280, 900)):
                page.set_viewport_size(dict(width=width, height=height))
                for party, records in groups:
                    page.goto(origin + PREFIX + 'funding/#' + party, wait_until='load')
                    page.evaluate('document.fonts.ready')
                    region = page.get_by_role('region', name=funding_page.name(party, records) + ' declared returns', exact=True)
                    context = f'{width}px party={party} return=all'
                    assert region.is_visible(), f'{context} field=region visible=False'
                    dimensions = page.evaluate('({scrollWidth: document.documentElement.scrollWidth, viewport: innerWidth})')
                    assert dimensions['scrollWidth'] == dimensions['viewport'], f'{context} field=page {dimensions}'
                    dimensions = region.evaluate('e => ({scrollWidth: e.scrollWidth, clientWidth: e.clientWidth})')
                    assert dimensions['scrollWidth'] <= dimensions['clientWidth'], f'{context} field=region {dimensions}'
                    table = region.get_by_role('table')
                    for label in ('Donor', 'Amount', 'Received'):
                        count_headers = table.get_by_role('columnheader', name=label, exact=True).count()
                        assert count_headers == 1, f'{context} field={label} headers={count_headers}, expected=1'
                    rows = table.get_by_role('row').all()[1:]
                    ordered = sorted(records, key=lambda r: (r.get('received', ''), r['id']), reverse=True)
                    assert len(rows) == len(ordered), f'{context} field=rows actual={len(rows)} expected={len(ordered)}'
                    for row, record in zip(rows, ordered, strict=True):
                        context = f'{width}px party={party} return={record["id"]} donor={record["donor"]!r}'
                        if width in (360, 390):
                            row.scroll_into_view_if_needed()
                        link = row.get_by_role('link', name=record['donor'], exact=True)
                        assert link.is_visible(), f'{context} field=Donor visible=False'
                        href = link.get_attribute('href')
                        assert href == record['document_url'], f'{context} field=document actual={href!r} expected={record["document_url"]!r}'
                        fields = [('Donor', record['donor']),
                                  ('Amount', funding_page.money(donations.amount_cents(record['amount_nzd'])))]
                        if record.get('received'):
                            fields.append(('Received', observation_label(record['received'])))
                        for field, value in fields:
                            cell = row.get_by_role('cell', name=value, exact=True)
                            assert cell.is_visible(), f'{context} field={field} name={value!r} visible=False'
                            if width in (360, 390):
                                rendered_cell(cell, f'{context} field={field}')
                            else:
                                dimensions = cell.evaluate('e => ({scrollWidth: e.scrollWidth, clientWidth: e.clientWidth})')
                                assert dimensions['scrollWidth'] <= dimensions['clientWidth'], f'{context} field={field} {dimensions}'
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
