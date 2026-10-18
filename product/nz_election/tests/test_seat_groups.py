"""Historical groups describe allocator seats, never future coalition commitments."""
from html.parser import HTMLParser
import re

import pytest

from product.nz_election.pipeline.build import config, seat_topline, ungrouped_seats
from product.nz_election.tests.design_checks import provenance
from product.nz_election.tests.design_states import fixture


def test_reviewed_group_membership_and_source():
    groups = config('seat-groups')
    assert groups['arrangement_date'] == '2023-11-24'
    assert groups['government']['parties'] == ['nat', 'act', 'nzf']
    assert groups['opposition']['parties'] == ['lab', 'grn', 'tpm']
    assert groups['source_url'] == 'https://en.wikipedia.org/wiki/Sixth_National_Government_of_New_Zealand#Coalition_agreements'
    assert groups['caption'] == 'Grouped by the 2023 coalition agreements, not by any 2026 commitment.'


@pytest.mark.parametrize('seats,majority', [
    ({'nat': 43, 'act': 8, 'nzf': 10, 'lab': 34, 'grn': 14, 'tpm': 6, 'opp': 5}, 61),
    ({'nat': 50, 'act': 9, 'nzf': 9, 'lab': 31, 'grn': 15, 'tpm': 13, 'opp': 0}, 64),
    ({'lab': 61, 'new-party': 59}, 61),
])
def test_totals_exclude_every_unlisted_party(seats, majority):
    result = dict(seats=seats, assumed_majority=majority)
    html = seat_topline(result)
    government = sum(seats.get(p, 0) for p in ('nat', 'act', 'nzf'))
    opposition = sum(seats.get(p, 0) for p in ('lab', 'grn', 'tpm'))
    assert f'<p class="bloc-left">Government parties: {government} seats</p>' in html
    assert f'<p class="bloc-right">Opposition parties: {opposition} seats</p>' in html
    assert f'on the current poll average, {majority} needed' in html
    hero = html.split('</div>', 1)[0]
    assert hero.count('<p') == 3
    assert 'Outside these groups' not in hero
    assert config('seat-groups')['source_url'] in html
    assert 'class="source-actions"' in html
    other = ungrouped_seats(result)
    assert 'class="bloc-neutral"' in other
    assert 'Government' not in other and 'Opposition' not in other
    if 'new-party' in seats:
        assert 'new-party: 59 seats' in other
    else:
        assert f'Opportunity: {seats["opp"]} seats' in other


class ReaderText(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.text = []
        self.hidden = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden = True

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = False

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


@pytest.mark.parametrize('state', ['earlier-coherent-window', 'incomplete', 'stale', 'no-data'])
def test_reader_copy_and_withheld_topline(tmp_path, state):
    site, _ = fixture(tmp_path, state)
    for route in ('', 'polls/'):
        path = site / 'nz-election' / route / 'index.html'
        html = path.read_text()
        visible = ' '.join(ReaderText(html).text).lower()
        assert not re.search(r'\bconfig\w*\b|\bsupplied\b', visible), path
        provenance(html)
        if state == 'earlier-coherent-window':
            assert 'Government parties:' in html and 'Opposition parties:' in html
            assert html.index('Government parties:') < html.index('id="source-seats"') < html.index('class="strip"')
        else:
            assert 'Seat totals are withheld until a complete, up-to-date poll average is available.' in html
            assert 'Government parties:' not in html and 'Opposition parties:' not in html
