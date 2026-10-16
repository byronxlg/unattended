"""Count original UTF-8 SVG bytes required by rendered HTML, without reserialization."""
from html.parser import HTMLParser
import re
from urllib.parse import unquote, urljoin, urlsplit
from urllib.parse import quote


def reject_svg_data_uri(value):
    if urlsplit(value).scheme.lower() == 'data':
        media = unquote(value.split(':', 1)[1].split(',', 1)[0]).split(';', 1)[0].strip().lower()
        assert media != 'image/svg+xml', 'SVG_DATA_URI_NOT_BUDGETED: use a local SVG file'
        return True
    return False


def css_url_tokens(css):
    """Scan CSS URLs without interpreting comment delimiters inside strings or URL tokens."""
    i, size = 0, len(css)
    whitespace = ' \t\n\r\f'

    def escape():
        nonlocal i
        i += 1
        assert i < size, 'Incomplete CSS escape'
        if css[i] in '\n\r\f':
            if css[i] == '\r' and i + 1 < size and css[i + 1] == '\n':
                i += 1
            i += 1
            return ''
        start = i
        while i < size and i - start < 6 and css[i] in '0123456789abcdefABCDEF':
            i += 1
        if i != start:
            number = int(css[start:i], 16)
            if i < size and css[i] in whitespace:
                if css[i] == '\r' and i + 1 < size and css[i + 1] == '\n':
                    i += 1
                i += 1
            return chr(number) if 0 < number <= 0x10ffff and not 0xd800 <= number <= 0xdfff else '\ufffd'
        value = css[i]
        i += 1
        return value

    def string():
        nonlocal i
        delimiter = css[i]
        i += 1
        value = []
        while i < size and css[i] != delimiter:
            assert css[i] not in '\n\r\f', 'Unescaped newline in CSS string'
            if css[i] == '\\':
                value.append(escape())
            else:
                value.append(css[i])
                i += 1
        assert i < size, 'Unclosed CSS string'
        i += 1
        return ''.join(value)

    def skip_space_comments():
        nonlocal i
        while i < size:
            if css[i] in whitespace:
                i += 1
            elif css.startswith('/*', i):
                end = css.find('*/', i + 2)
                i = size if end < 0 else end + 2
            else:
                break

    while i < size:
        skip_space_comments()
        if i == size:
            break
        if css[i] in "\"'":
            string()
            continue
        if css[i].isalnum() or css[i] in '_-\\' or ord(css[i]) >= 128:
            name = []
            while i < size and (css[i].isalnum() or css[i] in '_-\\' or ord(css[i]) >= 128):
                if css[i] == '\\':
                    name.append(escape())
                else:
                    name.append(css[i])
                    i += 1
            if ''.join(name).lower() != 'url' or i == size or css[i] != '(':
                continue
            i += 1
            while i < size and css[i] in whitespace:
                i += 1
            if i < size and css[i] in "\"'":
                value = string()
                skip_space_comments()
            else:
                parts = []
                while i < size and css[i] != ')':
                    if css[i] in whitespace:
                        while i < size and css[i] in whitespace:
                            i += 1
                        break
                    assert css[i] not in "\"'(", 'Invalid unquoted CSS URL'
                    if css[i] == '\\':
                        parts.append(escape())
                    else:
                        parts.append(css[i])
                        i += 1
                value = ''.join(parts)
            assert i < size and css[i] == ')', 'Unclosed CSS URL'
            i += 1
            yield value
        else:
            i += 1


def normalized_css_urls(css):
    # The existing resolver consumes a canonical URL list, never raw CSS strings.
    # Encode quotes and comment delimiters so its simple carrier syntax is unambiguous.
    return ''.join('url("' + quote(value, safe='/:%#?&=+;,@') + '")'
                   for value in css_url_tokens(css) if not reject_svg_data_uri(value))


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
        css = normalized_css_urls(css)
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
                    if reject_svg_data_uri(value):
                        continue
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
