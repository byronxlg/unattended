"""Keep per-contract provenance outside every height-budgeted markets module."""
from html.parser import HTMLParser
from pathlib import Path
import re


class MarketModule(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = 0
        self.text = []
        self.rows = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            if self.depth or dict(attrs).get('id') == 'markets':
                self.depth += 1
        if self.depth and tag == 'tr':
            self.rows += 1

    def handle_endtag(self, tag):
        if tag == 'section' and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)


def check_markup(html):
    module = MarketModule(html)
    if re.search(r'\b(volume|liquidity)\b', ' '.join(module.text), re.I):
        raise ValueError('MARKET_INLINE_PROVENANCE: amounts belong outside #markets')
    if module.rows > 4:
        raise ValueError(f'HOME_MARKET_ROW_BUDGET: {module.rows} > 4')


def check_site(site):
    pages = sorted(site.rglob('index.html'))
    if not pages:
        raise ValueError('MARKET_BUDGET: no pages found')
    for page in pages:
        try:
            check_markup(page.read_text())
        except ValueError as exc:
            raise ValueError(f'{page.relative_to(site)}: {exc}') from exc
    return len(pages)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS market budgets: {check_site(args.site)} routes, no inline amounts, at most four rows')
