"""Reject campaign modules without backing observations and explicit provenance."""
from html.parser import HTMLParser
from .campaign_page import eligible


class Content(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)


def check_markup(html, envs, historical=False):
    rows = eligible(envs, historical)
    present = 'data-campaign-module="advance-voting"' in html
    parser = Content()
    parser.feed(html)
    visible = ' '.join(parser.text).lower()
    if present != bool(rows) or any(s in visible for s in ('not available', 'not reported')):
        raise ValueError('M3_PRESENCE')
    if present:
        if any(r['date'] not in html or any(f'{r[k]:,}' not in html for k in ('daily', 'cumulative') if r[k] is not None) for r in rows):
            raise ValueError('M3_BACKING_ROWS')
        if 'aria-describedby="source-advance"' not in html or 'class="source-note"' not in html:
            raise ValueError('M3_PROVENANCE')
        if historical and 'Offline verification: historical 2023' not in html:
            raise ValueError('M3_HISTORICAL_LABEL')
    elif '<h2' in html or '<svg' in html or '<table' in html:
        raise ValueError('M3_EMPTY_MODULE')
    return True


def check_site(site, envs):
    html = (site / 'campaign/index.html').read_text()
    return check_markup(html, envs, 'Offline verification: historical 2023' in html)
