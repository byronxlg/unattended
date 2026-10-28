"""Read-only acceptance of the registered current-election capture in a release."""
from datetime import date
from html.parser import HTMLParser
import re

from . import advance, export


class AdvanceAcceptanceError(ValueError):
    """Only fixed codes cross the CLI boundary, never supplied file contents."""


class VisibleText(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # The advance line has no stylesheet hiding rules. Inline hiding and
        # semantic hidden attributes must suppress the entire descendant subtree.
        style = re.sub(r'/\*.*?\*/', '', attrs.get('style') or '', flags=re.S)
        inline_hidden = any(re.fullmatch(
            r'\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))\s*(?:!\s*important\s*)?',
            declaration, flags=re.I) for declaration in style.split(';'))
        hidden = (inline_hidden or tag in {'script', 'style', 'template', 'head'} or 'hidden' in attrs or
                  (attrs.get('aria-hidden') or '').strip().lower() == 'true')
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, hidden))
        self.parts.append(' ')

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        self.parts.append(' ')

    def handle_data(self, text):
        if not any(hidden for _, hidden in self.stack):
            self.parts.append(text)


def check(data=None, site=None):
    """Require release evidence; a gap is a distinct non-passing acceptance state."""
    if site is not None and (site / 'nz-election').is_dir():
        site = site / 'nz-election'
    locations = ([data] if data is not None else []) + ([site / 'data'] if site is not None else [])
    if not locations or any(not (p / 'advance-voting.json').is_file() for p in locations):
        raise AdvanceAcceptanceError('ADVANCE_NOT_PUBLISHED')
    try:
        captured = advance.load(year=2026)
        if captured is None:
            raise ValueError()
        expected = captured[0]['advance-voting']
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        raise AdvanceAcceptanceError('ADVANCE_CAPTURE_INVALID') from None
    latest = max(expected, key=lambda r: r['date'])
    for location in locations:
        try:
            env = export.validate_bundle(location)['advance-voting']
            rows = env['data']
            actual = max(rows, key=lambda r: r['date'])
        except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
            raise AdvanceAcceptanceError('ADVANCE_INVALID_BUNDLE') from None
        # Compare observations even when provenance claims the expected capture hash.
        # Null is not a count, so gap acceptance requires the complete series.
        fields = ('date', 'daily', 'cumulative')
        matches = (actual['date'], actual['cumulative']) == (latest['date'], latest['cumulative'])
        if latest['cumulative'] is None:
            matches = [[r[k] for k in fields] for r in rows] == [[r[k] for k in fields] for r in expected]
        if not matches:
            raise AdvanceAcceptanceError('ADVANCE_STALE')
    if site is not None:
        day = date.fromisoformat(latest['date'])
        expected_sentence = (f"{latest['cumulative']:,} advance votes reported through {day.day} {day:%B}."
                             if latest['cumulative'] is not None else None)
        for route in ('index.html', 'vote/index.html'):
            try:
                visible = ' '.join(''.join(VisibleText((site / route).read_text()).parts).split())
            except (OSError, ValueError):
                raise AdvanceAcceptanceError('ADVANCE_RENDER_MISMATCH') from None
            sentences = re.findall(r'[\d,]+ advance votes reported through \d+ \w+\.', visible)
            if expected_sentence and not sentences:
                raise AdvanceAcceptanceError('ADVANCE_NOT_PUBLISHED')
            if sentences != ([expected_sentence] if expected_sentence else []):
                raise AdvanceAcceptanceError('ADVANCE_RENDER_MISMATCH')
    if latest['cumulative'] is None:
        raise AdvanceAcceptanceError('ADVANCE_GAP')
