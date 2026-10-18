"""Market-specific reader and viewport gates shared with the screenshot harness."""
from html.parser import HTMLParser
import re
from product.nz_election.pipeline.market_panel import eligible

MAX_HOME_HEIGHT = 844


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.text = []
        self.feed(html)

    def handle_data(self, data):
        self.text.append(data)


def check_markup(html, rows):
    text = ' '.join(Text(html).text)
    for row in rows:
        if not eligible(row):
            assert row['question'] not in text, 'UNPRICED_OR_PLACEHOLDER_CONTRACT: ' + row['id']
            assert 'data-market-id="' + row['id'] + '"' not in html, 'UNPRICED_OR_PLACEHOLDER_CONTRACT: ' + row['id']
    if '<section id="markets"' in html:
        module = html.split('<section id="markets"', 1)[1].split('</section>', 1)[0]
        count = len(re.findall(r'<tr(?:\s|>)', module))
        assert count <= 4, 'HOME_MARKET_ROW_BUDGET: ' + str(count)
        assert 'inactive contract without prices' not in module


def check_browser(page):
    module = page.locator('#markets')
    if module.count() and page.viewport_size['width'] == 390:
        height = module.bounding_box()['height']
        assert height <= MAX_HOME_HEIGHT, f'HOME_MARKET_HEIGHT: {height} > {MAX_HOME_HEIGHT}'
