# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check initial visible HTML text without requiring a browser or evaluating scripts."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
BLOCK = {'address', 'article', 'aside', 'blockquote', 'br', 'caption', 'dd', 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'header', 'hr', 'li', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'summary', 'table', 'td', 'th', 'tr', 'ul'}


class VisibleText(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        visible = parent['visible'] if parent else True
        if parent and parent['closed']:
            # Only the first direct summary is visible in a closed disclosure.
            visible = visible and tag == 'summary' and not parent['summary']
            if tag == 'summary':
                parent['summary'] = True
        style = re.sub(r'\s+', '', attrs.get('style', '').lower())
        visible = visible and tag not in {'head', 'script', 'style', 'template'} and 'hidden' not in attrs
        visible = visible and 'display:none' not in style and 'visibility:hidden' not in style
        if visible and tag in BLOCK:
            self.parts.append(' ')
        if tag not in VOID:
            self.stack.append(dict(tag=tag, visible=visible, closed=tag == 'details' and 'open' not in attrs, summary=False))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                if self.stack[index]['visible'] and tag in BLOCK:
                    self.parts.append(' ')
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1]['visible'] and not self.stack[-1]['closed']:
            self.parts.append(data)

    @property
    def text(self):
        return ''.join(self.parts)


def check_site(site):
    paths = sorted(Path(site).rglob('index.html'))
    if not paths:
        raise ValueError('VISIBLE_TEXT_NO_ROUTES')
    for path in paths:
        runs = re.findall(r'\S+', VisibleText(path.read_text()).text)
        longest = max(map(len, runs), default=0)
        if longest > 200:
            raise ValueError(f'VISIBLE_TEXT_RUN: {path.relative_to(site)}: {longest} > 200 characters')
    return len(paths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    try:
        count = check_site(args.site)
    except ValueError as error:
        raise SystemExit('FAIL ' + str(error)) from error
    print(f'PASS visible text: {count} routes, no whitespace-free run over 200 characters')
