# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Measure and enforce the design-principles home budgets on built HTML."""
from html.parser import HTMLParser
from pathlib import Path
import argparse


class Home(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.details = self.links = self.h2 = 0
        self.text = []
        self.hidden = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.details += tag == 'details'
        self.links += tag == 'a'
        self.h2 += tag == 'h2'
        if tag in {'head', 'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {'head', 'script', 'style'}:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


def measure(path):
    raw = Path(path).read_bytes()
    home = Home(raw.decode())
    counts = dict(details=home.details, links=home.links,
                  source=' '.join(home.text).lower().count('source'),
                  html_bytes=len(raw), h2=home.h2)
    assert counts['details'] == 0, counts
    assert counts['links'] < 60, counts
    assert counts['source'] < 12, counts
    assert counts['html_bytes'] < 35_000, counts
    assert counts['h2'] <= 7, counts
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('home', type=Path)
    args = parser.parse_args()
    print('PASS home: ' + ', '.join(f'{key} {value}' for key, value in measure(args.home).items()))
