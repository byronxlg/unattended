"""Count original UTF-8 SVG bytes required by rendered HTML, without reserialization."""
from html.parser import HTMLParser
import re
from urllib.parse import unquote, urljoin, urlsplit


def svg_page_bytes(html, site, page_url='/unattended/nz-election/electorates/'):
    offsets = [0]
    for line in html.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))

    stylesheets = set()

    def local_path(url):
        resolved = urlsplit(url)
        assert not resolved.netloc and not resolved.scheme, 'External SVG must be locally budgeted'
        assert resolved.path.startswith('/unattended/'), 'SVG outside site prefix'
        relative = unquote(resolved.path[len('/unattended/'):])
        path = (site / relative).resolve()
        assert path.is_relative_to(site.resolve()) and path.is_file(), 'Missing or unsafe linked SVG'
        return relative, path

    def css_urls(css, base, links):
        # Strip comments so examples cannot add phantom assets to the budget.
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        for match in re.finditer(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*?))\s*\)", css, re.I):
            value = next(v for v in match.groups() if v is not None).strip()
            url = urljoin(base, value)
            suffix = urlsplit(url).path.lower()
            if suffix.endswith('.svg'):
                relative, _ = local_path(url)
                links.add(relative)
            elif suffix.endswith('.css'):
                stylesheet(url, links)

    def stylesheet(url, links):
        relative, path = local_path(url)
        if relative not in stylesheets:
            stylesheets.add(relative)
            css_urls(path.read_text(), url, links)

    class SVGs(HTMLParser):
        depth = 0
        start = 0
        total = 0
        links = set()
        in_style = False

        def position(self):
            line, column = self.getpos()
            return offsets[line - 1] + column

        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            if tag == 'style':
                self.in_style = True
            if attributes.get('style'):
                css_urls(attributes['style'], page_url, self.links)
            if tag == 'link' and 'stylesheet' in attributes.get('rel', '').lower().split():
                stylesheet(urljoin(page_url, attributes['href']), self.links)
            if tag == 'svg':
                if self.depth == 0:
                    self.start = self.position()
                self.depth += 1
            for key, value in attrs:
                if key in {'href', 'xlink:href', 'src', 'data', 'poster'} and value:
                    resolved = urlsplit(urljoin(page_url, value))
                    if resolved.path.lower().endswith('.svg'):
                        assert not resolved.netloc and not resolved.scheme, 'External SVG must be locally budgeted'
                        assert resolved.path.startswith('/unattended/'), 'SVG outside site prefix'
                        self.links.add(unquote(resolved.path[len('/unattended/'):]))

        def handle_data(self, data):
            if self.in_style:
                css_urls(data, page_url, self.links)

        def handle_endtag(self, tag):
            if tag == 'style':
                self.in_style = False
            if tag == 'svg':
                self.depth -= 1
                assert self.depth >= 0, 'Unbalanced SVG'
                if self.depth == 0:
                    end = html.index('>', self.position()) + 1
                    self.total += len(html[self.start:end].encode('utf-8'))

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag == 'svg':
                self.handle_endtag(tag)

    parser = SVGs()
    parser.feed(html)
    parser.close()
    assert parser.depth == 0, 'Unclosed SVG'
    for link in parser.links:
        path = (site / link).resolve()
        assert path.is_relative_to(site.resolve()) and path.is_file(), 'Missing or unsafe linked SVG'
        parser.total += len(path.read_bytes())
    return parser.total
