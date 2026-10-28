"""The home summary and funding ranking consume the same party totals."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from html import unescape
import re

import pytest

from product.nz_election.pipeline import donations, funding_page, home_graphics
from product.nz_election.pipeline.content_checks import Tree


def displayed_values(monkeypatch, records):
    monkeypatch.setattr(donations, 'load_donations', lambda: records)
    sentence = Tree(funding_page.feed()).root.text
    match = re.search(r'Who funds the parties\?(.+?) has declared NZD ([\d,]+) across (\d+) returns?\b', sentence)
    assert match, sentence
    leader = (match[1], Decimal(match[2].replace(',', '')), int(match[3]))
    ranking = []

    def capture_table(caption, headings, rows, **kwargs):
        ranking.extend((unescape(party), Decimal(amount.removeprefix('NZD ').replace(',', '')), int(count))
                       for party, amount, count in rows)
        return ''

    monkeypatch.setattr(home_graphics, 'table', capture_table)
    funding_page.ranking(funding_page.groups(records))
    return leader, ranking


@pytest.mark.parametrize('amounts', [None, ['20000.24', '20000.25'],
                                    ['20000.25', '20000.25'], ['20000.75', '20000.75'], ['20000.50']])
def test_funding_totals_match_home_summary(monkeypatch, amounts):
    records = donations.load_donations()
    if amounts:
        records = [dict(records[0], amount_nzd=amount) for amount in amounts]
    exact, counts = defaultdict(Decimal), defaultdict(int)
    for row in records:
        party = funding_page.name(row['party_id'], [row])
        exact[party] += Decimal(row['amount_nzd'])
        counts[party] += 1
    expected = {party: (amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP), counts[party])
                for party, amount in exact.items()}
    leader, ranking = displayed_values(monkeypatch, records)
    assert {party: (amount, count) for party, amount, count in ranking} == expected
    assert leader == ranking[0]


def test_funding_home_and_ranking_use_shared_totals(monkeypatch):
    records = donations.load_donations()
    # A distinct projection catches callers that independently recompute identical facts.
    shared = [dict(party='lab', name='Shared leader', cents=12345650,
                   amount='NZD 123,457', count=7, returns='7 returns')]
    monkeypatch.setattr(funding_page, 'funding_totals', lambda ranked: shared)
    leader, ranking = displayed_values(monkeypatch, records)
    assert leader == ranking[0] == ('Shared leader', Decimal('123457'), 7)
