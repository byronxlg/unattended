"""Home and funding rankings expose the same whole-NZD data to their tables."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from html import unescape

from product.nz_election.pipeline import donations, funding_page, home_graphics


def test_funding_totals_match_between_callers(monkeypatch):
    original = donations.load_donations()
    boundary_rows = [dict(original[0], party_id=party, party=party, amount_nzd=amount)
                     for party, amounts in [('below', ['20000.24', '20000.25']),
                                            ('half', ['20000.25', '20000.25']),
                                            ('above', ['20000.75', '20000.75'])]
                     for amount in amounts]
    for records in (original, boundary_rows):
        exact = defaultdict(Decimal)
        for row in records:
            exact[funding_page.name(row['party_id'], [row])] += Decimal(row['amount_nzd'])
        expected = {party: amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                    for party, amount in exact.items()}
        captured = []

        def capture_table(caption, headings, rows, **kwargs):
            captured.append({unescape(party): Decimal(amount.removeprefix('NZD ').replace(',', ''))
                             for party, amount, count in rows})
            return ''

        monkeypatch.setattr(home_graphics, 'table', capture_table)
        monkeypatch.setattr(funding_page, 'table', capture_table)
        ranked = funding_page.groups(records)
        home_graphics.funding_bars(ranked)
        funding_page.ranking(ranked)
        assert len(captured) == 2
        assert captured[0] == captured[1] == expected
