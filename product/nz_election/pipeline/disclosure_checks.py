"""Principle 4: non-home disclosures are reserved for data tables."""
from html.parser import HTMLParser


class Disclosures(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.prose = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            self.stack.append(dict(table=False, line=self.getpos()[0]))
        elif tag == 'table':
            for disclosure in self.stack:
                disclosure['table'] = True

    def handle_endtag(self, tag):
        if tag == 'details' and self.stack:
            disclosure = self.stack.pop()
            if not disclosure['table']:
                self.prose.append(disclosure['line'])


def check_site(site):
    pages = sorted(p for p in site.rglob('index.html') if p != site / 'index.html')
    if not pages:
        raise ValueError('PROSE_DISCLOSURE: no non-home routes found')
    for page in pages:
        lines = Disclosures(page.read_text()).prose
        if lines:
            raise ValueError(f'PROSE_DISCLOSURE: {page.relative_to(site)}:{lines[0]}: details requires a table')
    return len(pages)


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS disclosures: {check_site(args.site)} non-home routes')
