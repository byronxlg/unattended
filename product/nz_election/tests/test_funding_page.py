"""Funding facts, complete provenance, absent data and accessible equivalents."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
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
    rounded = {p: v.quantize(Decimal('1'), rounding=ROUND_HALF_UP) for p, v in totals.items()}
    assert {r[0]: value(r[1]) for r in tables[0][1:]} == rounded
    assert {r[0]: int(r[2]) for r in tables[0][1:]} == dict(counts)
    assert [value(r[1]) for r in tables[0][1:]] == sorted(rounded.values(), reverse=True)
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


def test_funding_ranking_names_parties_not_electorates():
    records = donations.load_donations()
    assert len(records) == 146
    # EC's register lists Te Tai Tokerau Party from 5 August 2026.
    # Its full name distinguishes this return from the electorate.
    row = next(r for r in records if r['id'] == 'ec-2026-021')
    assert row['party'] == 'Te Tai Tokerau Party'
    assert row['donor'] == 'Stanley Howard Fund via Richard Allen'
    html = funding.page(records)
    ranked = {r[0]: r[1:] for r in Tables(html).tables[0][1:]}
    assert 'Te Tai Tokerau' not in ranked
    assert ranked['Te Tai Tokerau Party'] == ['NZD 50,000', '1']
    assert row['document_url'] in unescape(html)


def test_funding_headline_and_ranking_round_only_after_summing():
    records = donations.load_donations()
    assert 'NZD 2,394,410 across 49 returns' in funding.headline(records)
    for amounts, expected in [(('20000.24', '20000.25'), 'NZD 40,000'),
                              (('20000.25', '20000.25'), 'NZD 40,001'),
                              (('20000.75', '20000.75'), 'NZD 40,002')]:
        rows = [dict(records[0], amount_nzd=amount, id=str(i)) for i, amount in enumerate(amounts)]
        html = funding.page(rows)
        assert expected in funding.headline(rows)
        assert Tables(html).tables[0][1][1] == expected
        assert sorted(value(r[2]) for r in Tables(html).tables[1][1:]) == sorted(map(Decimal, amounts))


def test_party_return_groups_preserve_all_documents_and_navigation():
    from collections import Counter
    from product.nz_election.pipeline.content_checks import Tree, Node

    def descendants(node):
        yield node
        for child in node.children:
            if isinstance(child, Node):
                yield from descendants(child)

    records = donations.load_donations()
    tree = Tree(funding.page(records))
    ids = {n.attrs['id']: n for n in tree.nodes if 'id' in n.attrs}
    complete = ids['all-returns']
    assert f'{len(records)} returns' in complete.text
    document_urls = {r['document_url'] for r in records}
    links = [n.attrs.get('href') for n in descendants(complete) if n.tag == 'a']
    assert Counter(url for url in links if url in document_urls) == Counter(r['document_url'] for r in records)
    for party, rows in funding.groups(records):
        group = ids[party]
        urls = [n.attrs.get('href') for n in descendants(group) if n.tag == 'a']
        assert Counter(url for url in urls if url in document_urls) == Counter(r['document_url'] for r in rows)
        assert funding.return_count(rows) in group.text
        assert '#' + party in links
        assert any(n.tag == 'a' and n.attrs.get('href') == '#' + party
                   for n in tree.nodes[:tree.nodes.index(group)])


def test_funding_party_fragments_without_javascript(populated, tmp_path):
    import subprocess
    from pathlib import Path

    _, site = populated
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('funding_browser.py')),
                             '--site', str(site.parent), '--out', str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
