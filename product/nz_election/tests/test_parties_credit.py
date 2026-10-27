"""Portrait attribution follows the answer and retains each image's provenance."""
from html.parser import HTMLParser

from product.nz_election.pipeline.average import display
from product.nz_election.pipeline.parties_page import page
from product.nz_election.pipeline.snapshots import load


class TextOrder(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.text = ''
        self.descriptions = {}
        self.starts = {}
        self.ends = {}
        self.stack = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.descriptions[attrs['src']] = next(
                (a['aria-describedby'] for _, a in reversed(self.stack)
                 if 'aria-describedby' in a), None)
        if 'id' in attrs:
            self.starts[attrs['id']] = len(self.text)
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link'}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            _, attrs = self.stack.pop()
            if 'id' in attrs:
                self.ends[attrs['id']] = len(self.text)

    def handle_data(self, data):
        self.text += data


def test_parties_every_portrait_credit_follows_poll_share():
    leaders = [row for row in load('leaders') if row.get('party_id')]
    values = {row['party_id']: {'value': 285 + i, 'scale': 10}
              for i, row in enumerate(leaders)}
    html = page({'averages': {'data': [{'date': '2026-10-20', 'descriptive': values}]}},
                '2026-10-20T00:00:00Z')
    doc = TextOrder(html)
    for row in leaders:
        photo = row.get('photo')
        if not photo:
            continue
        src = '/unattended/nz-election/' + photo['path'].removeprefix('web/')
        description = doc.descriptions[src]
        credit_start = doc.starts[description]
        credit = doc.text[credit_start:doc.ends[description]]
        value = values[row['party_id']]
        share = display(value['value'], value['scale'])
        assert doc.text.index(share, doc.starts[row['party_id']]) < credit_start
        assert photo['author'] in credit
        assert photo['licence'] in credit
        assert photo['changes'] not in doc.text


def test_home_and_parties_poll_values_have_no_breakable_unit_spaces():
    import re
    from product.nz_election.pipeline.home_graphics import party_cards

    averages = [{'date': f'2026-10-{day:02}', 'descriptive': {
        'lab': {'value': 289 if day == 1 else 285, 'scale': 10},
        'nat': {'value': 321 if day == 1 else 325, 'scale': 10}}}
        for day in range(1, 32)]
    for html in (party_cards(averages, None, load('leaders')),
                 page({'averages': {'data': averages}}, '2026-10-31T00:00:00Z')):
        text = TextOrder(html).text
        assert '28.5%' in text and '32.5%' in text
        assert not re.search(r'\d[ \t\r\n]+%|[+\-][ \t\r\n]+\d', text)
    text = TextOrder(party_cards(averages, None, [])).text
    assert '-0.4' in text and '+0.4' in text
