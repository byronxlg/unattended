"""Reject campaign modules without backing observations and explicit provenance."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from .campaign_page import eligible


class Content(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text, self.nodes, self.headings = [], [], []
        self.heading = None

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))
        if re.fullmatch(r'h[1-6]', tag):
            self.heading = []
            self.headings.append(self.heading)

    def handle_endtag(self, tag):
        if re.fullmatch(r'h[1-6]', tag):
            self.heading = None

    def handle_data(self, data):
        self.text.append(data)
        if self.heading is not None:
            self.heading.append(data)


def check_markup(html, envs, historical=False):
    rows = eligible(envs, historical)
    parser = Content()
    parser.feed(html)
    modules = sum(attrs.get('data-campaign-module') == 'advance-voting' for _, attrs in parser.nodes)
    present = modules == 1
    visible = ' '.join(' '.join(parser.text).lower().split())
    if modules != int(bool(rows)) or any(s in visible for s in ('not available', 'not reported')):
        raise ValueError('M3_PRESENCE')
    if present:
        if any(r['date'] not in html or any(f'{r[k]:,}' not in html for k in ('daily', 'cumulative') if r[k] is not None) for r in rows):
            raise ValueError('M3_BACKING_ROWS')
        if 'aria-describedby="source-advance"' not in html or 'class="source-note"' not in html:
            raise ValueError('M3_PROVENANCE')
        if historical and 'Offline verification: historical 2023' not in html:
            raise ValueError('M3_HISTORICAL_LABEL')
    else:
        tags = {tag for tag, _ in parser.nodes}
        advance_heading = any(re.search(r'advance|voted early|early vot', ' '.join(h), re.I) for h in parser.headings)
        placeholder = re.search(r'\bno (?:campaign|advance(?: voting)?) (?:totals|counts|data|observations|statistics|votes)\b', visible)
        if tags & {'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 'svg', 'table', 'canvas'} or advance_heading or placeholder:
            raise ValueError('M3_EMPTY_MODULE')
    return True


def check_night_markup(html, envs):
    parser = Content()
    parser.feed(html)
    present = bool(envs.get('night/index', {}).get('data'))
    modules = [attrs for _, attrs in parser.nodes if 'data-sequence' in attrs]
    if bool(modules) != present:
        raise ValueError('M3_NIGHT_PRESENCE')
    if not present and any(tag in {'figure', 'svg', 'table', 'progress', 'canvas'} for tag, _ in parser.nodes):
        raise ValueError('M3_EMPTY_NIGHT')
    if present:
        for seq in envs['night/index']['data']:
            if seq['mode'] not in html:
                raise ValueError('M3_NIGHT_MODE')
            for path in seq['snapshot_paths']:
                row = envs[path[:-5]]['data'][0]
                if f'{row["valid_party_votes"]:,}' not in html:
                    raise ValueError('M3_NIGHT_BACKING_ROWS')
    return True


def check_site(site, envs):
    check_night_markup((site / 'night/index.html').read_text(), envs)
    html = (site / 'campaign/index.html').read_text()
    return check_markup(html, envs, 'Offline verification: historical 2023' in html)


def main():
    from . import export
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, action='append', required=True)
    args = parser.parse_args()
    for site in args.site:
        site = site / 'nz-election' if (site / 'nz-election').is_dir() else site
        envs = export.validate_bundle(site / 'data') if (site / 'data').exists() else {}
        check_site(site, envs)
        print('PASS m3 presence: ' + str(site))


if __name__ == '__main__':
    main()
