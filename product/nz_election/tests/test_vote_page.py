"""Voting actions follow NZ midnight and omit absent snapshot facts."""
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest

from product.nz_election.pipeline.vote_page import page
from product.nz_election.pipeline.snapshots import load_voting


@pytest.mark.parametrize(('clock', 'first', 'second'), [
    ('2026-10-25T10:59:59Z', 'enrol', 'places'),
    ('2026-10-25T11:00:00Z', 'places', 'enrol'),
])
def test_order_at_nz_midnight(clock, first, second):
    html = page(clock)
    assert html.index(f'id="{first}"') < html.index(f'id="{second}"') < html.index('id="two-votes"')
    assert html.index('id="two-votes"') < html.index('id="help"') < html.index('id="compare"')
    assert '<strong>13</strong>' in html if first == 'enrol' else '<strong>12</strong>' in html


@pytest.mark.parametrize('identity', ['enrolment-closes', 'advance-opens', 'election-day'])
def test_missing_date_drops_line(identity):
    rows = load_voting()
    removed = next(r for r in rows if r['id'] == identity)
    html = page('2026-10-25T11:00:00Z', [r for r in rows if r['id'] != identity])
    assert removed['summary'] not in html
    assert f'datetime="{removed["date"]}"' not in html
    if identity == 'election-day':
        assert 'days until election day' not in html


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.append(dict(attrs)['href'])


@pytest.mark.parametrize('clock', ['2026-10-25T10:59:59Z', '2026-10-25T11:00:00Z'])
def test_first_screen_links_are_snapshot_ec_actions(clock):
    parser = Links()
    parser.feed(page(clock).split('<section id="help">')[0])
    official = {r['url'] for r in load_voting() if r.get('url')}
    assert parser.hrefs
    assert set(parser.hrefs) <= official
    assert all(urlsplit(url).hostname in {'vote.nz', 'elections.nz'} for url in parser.hrefs)


def test_missing_action_drops_link_and_no_accessible_deadline():
    rows = [r for r in load_voting() if r['id'] != 'find-where-to-vote']
    html = page('2026-10-25T11:00:00Z', rows)
    assert 'Use the official finder' not in html
    accessible = html.split('Accessible formats</a>')[1].split('</div>')[0]
    assert 'Deadline' not in accessible
    assert '12:00 pm, Saturday 7 November 2026 NZDT' in html
    assert '7:00 pm, Saturday 7 November 2026 NZDT' in html
