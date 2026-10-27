"""Funding facts, complete provenance, absent data and accessible equivalents."""
from collections import defaultdict
from decimal import Decimal
from html import unescape
from html.parser import HTMLParser

from product.nz_election.pipeline import donations, funding_page as funding
from product.nz_election.pipeline.build import PREFIX
from product.nz_election.tests.design_checks import Document, provenance
from product.nz_election.tests.test_home import populated


class Tables(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tables, self.rows, self.cells, self.text = [], [], [], None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.rows = []
        elif tag == 'tr':
            self.cells = []
        elif tag in {'td', 'th'}:
            self.text = ''

    def handle_data(self, data):
        if self.text is not None:
            self.text += data

    def handle_endtag(self, tag):
        if tag in {'td', 'th'}:
            self.cells.append(self.text)
            self.text = None
        elif tag == 'tr':
            self.rows.append(self.cells)
        elif tag == 'table':
            self.tables.append(self.rows)


def value(text):
    return Decimal(text.removeprefix('NZD ').replace(',', ''))


def test_totals_match_every_record_and_chart_equivalents():
    records = donations.load_donations()
    html = funding.page(records)
    tables = Tables(html).tables
    totals = defaultdict(Decimal)
    counts = defaultdict(int)
    for r in records:
        key = funding.name(r['party_id'], [r])
        totals[key] += Decimal(r['amount_nzd'])
        counts[key] += 1
    assert {r[0]: value(r[1]) for r in tables[0][1:]} == dict(totals)
    assert {r[0]: int(r[2]) for r in tables[0][1:]} == dict(counts)
    assert [value(r[1]) for r in tables[0][1:]] == sorted(totals.values(), reverse=True)
    assert len(tables[1][1:]) == 10
    assert [value(r[2]) for r in tables[1][1:]] == sorted((Decimal(r['amount_nzd']) for r in records), reverse=True)[:10]
    cumulative = {}
    for row in tables[2][1:]:
        cumulative[row[0]] = value(row[2])
    assert cumulative == {p: v for p, v in totals.items() if counts[p] >= 3}
    nodes = Document(html).nodes
    assert all(a.get('aria-label') for t, a in nodes if t == 'svg')
    assert all(a.get('aria-describedby') for t, a in nodes if t == 'figure')
    provenance(html)


def test_every_document_including_unchecked_and_party_anchors():
    records = donations.load_donations()
    html = funding.page(records)
    nodes = Document(html).nodes
    links = [a['href'] for t, a in nodes if t == 'a']
    assert all(r['document_url'] in links for r in records)
    assert any(not r['document_checked'] for r in records)
    ids = {a['id'] for _, a in nodes if 'id' in a}
    assert {r['party_id'] for r in records} <= ids
    assert donations.LICENCE in unescape(html)
    assert '20 Oct 2026' in html
    tables = Tables(html).tables[3:]
    for (_, rows), table in zip(funding.groups(records), tables, strict=True):
        ordered = sorted(rows, key=lambda r: (r['received'], r['id']), reverse=True)
        assert [r[0] for r in table[1:]] == [r['donor'] for r in ordered]


def test_absent_and_small_data():
    html = funding.page([])
    assert 'not available' not in html.lower()
    assert not any(t in {'svg', 'table'} for t, _ in Document(html).nodes)
    single = funding.page(donations.load_donations()[:1])
    assert 'Cumulative declared' not in single
    assert Tables(single).tables[0][1][2] == '1'
    undated = dict(donations.load_donations()[0])
    undated.pop('received')
    html = funding.page([undated])
    assert 'not available' not in html.lower()
    assert undated['document_url'] in unescape(html)


def test_routes_link_to_resolving_funding_anchors(populated):
    _, site = populated
    funding_html = (site / 'funding/index.html').read_text()
    ids = {a['id'] for _, a in Document(funding_html).nodes if 'id' in a}
    parties = (site / 'parties/index.html').read_text()
    targets = [a['href'] for t, a in Document(parties).nodes if t == 'a' and a.get('href', '').startswith(PREFIX + 'funding/#')]
    assert targets
    assert all(t.split('#')[1] in ids for t in targets)
    assert PREFIX + 'funding/' in (site / 'index.html').read_text()


def test_home_funding_credit_tracks_snapshot(monkeypatch):
    from datetime import datetime, timedelta
    from product.nz_election.pipeline.build import observation_label
    from product.nz_election.pipeline.content_checks import Tree

    original = donations.load_donations()
    for days in (0, 7):
        records = [dict(row) for row in original]
        for row in records:
            retrieved = datetime.fromisoformat(row['retrieved_at'].replace('Z', '+00:00'))
            row['retrieved_at'] = (retrieved + timedelta(days=days)).isoformat().replace('+00:00', 'Z')
            if days:
                row['source_url'] += '#updated-returns'
        monkeypatch.setattr(donations, 'load_donations', lambda: records)
        html = funding.feed()
        links = {attrs['href'] for tag, attrs in Document(html).nodes if tag == 'a'}
        latest = max(records, key=lambda row: row['retrieved_at'])
        assert latest['source_url'] in links
        assert 'Retrieved ' + observation_label(latest['retrieved_at'][:10]) in Tree(html).root.text
        assert donations.LICENCE in Tree(html).root.text
