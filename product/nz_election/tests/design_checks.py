"""Checks shared by Python tests and the real-browser harness."""
import gzip
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

PREFIX = '/unattended/nz-election/'


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def provenance(html):
    nodes = Document(html).nodes
    ids = [a['id'] for _, a in nodes if 'id' in a]
    assert len(ids) == len(set(ids)), 'DUPLICATE_ID'
    for tag, attrs in nodes:
        if tag in {'table', 'figure', 'svg'}:
            assert attrs.get('aria-describedby'), f'MISSING_SOURCE: {tag} {attrs}'
        for identity in attrs.get('aria-describedby', '').split():
            assert identity in ids, 'MISSING_DESCRIPTION: ' + identity


def transfer_bytes(root):
    """Follow built first-view dependencies, including module imports and startup fetches."""
    root = Path(root)
    pending, seen = ['index.html'], set()
    sizes = {}
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        raw = (root / name).read_bytes()
        text_asset = Path(name).suffix in {'.html', '.css', '.svg', '.mjs', '.js', '.json', '.webmanifest'}
        sizes[name] = len(gzip.compress(raw, mtime=0)) if text_asset else len(raw)
        if not text_asset:
            continue
        text = raw.decode()
        urls = []
        if name.endswith('.html'):
            for tag, attrs in Document(text).nodes:
                if tag == 'script' or tag == 'img' and attrs.get('loading') != 'lazy':
                    urls.append(attrs.get('src', ''))
                if tag == 'link' and attrs.get('rel') in {'stylesheet', 'preload', 'icon', 'apple-touch-icon', 'manifest'}:
                    urls.append(attrs.get('href', ''))
                if attrs.get('data-averages'):
                    urls += ['data/averages.json', 'data/seats.json']
        elif name.endswith('.mjs'):
            urls += re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]", text)
        elif name.endswith('.css'):
            urls += re.findall(r'url\([\'\"]?([^\'\")]+)', text)
        for url in urls:
            resolved = urlsplit(urljoin(PREFIX + name, url)).path
            assert resolved.startswith(PREFIX), 'EXTERNAL_FIRST_VIEW_ASSET: ' + url
            pending.append(resolved.removeprefix(PREFIX))
    return sum(sizes.values()), sizes
