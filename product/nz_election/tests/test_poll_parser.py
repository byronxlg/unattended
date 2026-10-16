"""Pinned capture and small explicit structural drift cases."""
from copy import deepcopy
from decimal import Decimal
import pytest
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import parse_polls, compare_revisions

REVISION = '1380524613'
HEADER = '''==Party vote==
=== Table of polls ===
{| class="wikitable"
! Date
! Polling organisation
! Sample size
! NAT
! LAB
! GRN
! ACT
! NZF
! TPM
! OPP
! Others
! Lead
'''
ROW = '''|-
| data-sort-value="2026-10-12" | 8–12 Oct 2026
| [https://example.org/poll Roy Morgan]
| 1,000 || 30 || 30 || 10 || 10 || 10 || 3 || 5 || 2 || Tie
'''


def parse(text, mapping, revision=REVISION, identities=None):
    return parse_polls(text, revision, mapping, identities or {})


def test_pinned_wikitext(wikitext, mapping):
    result = parse(wikitext, mapping)
    assert len(result.polls) == 43
    assert result.polls[0]['fieldwork_end'] == '2026-10-12'
    assert result.polls[0]['shares']['nat'] == Decimal('28')
    assert result.polls[1]['shares']['others'] is None
    assert len({p['id'] for p in result.polls}) == 43
    assert result.diagnostics['date_exceptions'][0]['sort'] == '2026-08-12'
    assert any(p['fieldwork_end'] == '2026-08-11' for p in result.polls)
    assert all(p['reference_urls'] for p in result.polls)


def test_event_rows(mapping):
    event = '|-\n| 13 Oct 2026\n| colspan=11 | Leaders debate\n'
    result = parse(HEADER + event + ROW + '|}', mapping)
    assert len(result.polls) == 1
    assert result.excluded_rows[0]['reason'] == 'event'


def test_footnotes_and_named_refs(mapping):
    text = HEADER + ROW.replace('|| 3 ||', '|| 3{{efn|note with [[link|label]] and a | pipe}} ||')
    text = text.replace('Roy Morgan]', 'Roy Morgan]<ref name="citation"/>') + '|}\n<ref name="citation">https://example.org/citation</ref>'
    result = parse(text, mapping)
    assert result.polls[0]['shares']['tpm'] == Decimal(3)
    assert 'https://example.org/citation' in result.polls[0]['reference_urls']
    with pytest.raises(ParseDrift, match='unknown_named_ref'):
        parse(text.replace('<ref name="citation">https://example.org/citation</ref>', ''), mapping)
    with pytest.raises(ParseDrift, match='unknown_template'):
        parse((HEADER + ROW + '|}').replace('|| 3 ||', '|| {{unknown|3}} ||'), mapping)


def test_merged_cells(mapping):
    first = ROW.replace('| 1,000', '| rowspan="2" | 1,000')
    second = ROW.replace('8–12 Oct', '9–12 Oct').replace('| 1,000 ||', '|')
    result = parse(HEADER + first + second + '|}', mapping)
    assert [p['sample'] for p in result.polls] == [1000, 1000]
    with pytest.raises(ParseDrift, match='unexplained_merge'):
        parse((HEADER + ROW + '|}').replace('|| 3 ||', '|| rowspan="2" | 3 ||'), mapping)
    with pytest.raises(ParseDrift, match='unexplained_merge'):
        parse(HEADER + first + '|}', mapping)


def test_changed_headers(mapping):
    with pytest.raises(ParseDrift, match='unknown_headers'):
        parse((HEADER + ROW + '|}').replace('! NAT', '! NEW'), mapping)
    with pytest.raises(ParseDrift, match='national_table_count'):
        parse((HEADER + ROW + '|}').replace('==Party vote==', '==Preferred prime minister=='), mapping)


def test_malformed_rows(mapping):
    text = HEADER + ROW + '|}'
    mutations = [('|| 3 ||', '|| 101 ||', 'invalid_shares'),
                 ('|| 3 ||', '|| NaN ||', 'invalid_shares'),
                 ('|| 3 ||', '|| -1 ||', 'invalid_shares'),
                 ('|| Tie', '', 'unexplained_width'),
                 ('8–12 Oct', '8–32 Oct', 'invalid_dates'),
                 ('2026-10-12', '2026-10-11', 'invalid_dates'),
                 ('| 1,000', '| unknown', 'invalid_sample')]
    for before, after, error in mutations:
        with pytest.raises(ParseDrift, match=error):
            parse(text.replace(before, after), mapping)
    with pytest.raises(ParseDrift, match='size_limit'):
        parse('x' * (2 * 1024 * 1024 + 1), mapping)


def test_non_national_tables_excluded(mapping):
    national = HEADER + ROW + '|}'
    for section in ('Electorate polling', 'Preferred prime minister', 'Approval', 'Forecast', 'Māori-roll'):
        other = national.replace('==Party vote==', f'=={section}==')
        result = parse(other + '\n' + national, mapping)
        assert len(result.polls) == 1
        assert result.excluded_rows[0]['reason'] == 'non_national_table'


def test_stable_ids_and_corrections(mapping):
    text = HEADER + ROW + '|}'
    first = parse(text, mapping)
    changed = parse(text.replace('|| 3 ||', '|| 3.1 ||').replace('example.org/poll', 'example.org/corrected'), mapping, '2')
    assert first.polls[0]['id'] == changed.polls[0]['id']
    report = compare_revisions(first.polls, changed, {})
    assert report.polls[0]['history'][0]['shares']['tpm'] == Decimal(3)
    assert report.polls[0]['shares']['tpm'] == Decimal('3.1')
    assert not changed.polls[0]['history']
    identities = {'roy-morgan|2026-10-09|2026-10-12': {'id': first.polls[0]['id']}}
    corrected = parse(text.replace('8–12 Oct', '9–12 Oct'), mapping, identities=identities)
    assert corrected.polls[0]['id'] == first.polls[0]['id']
    with pytest.raises(ParseDrift, match='ambiguous_duplicates'):
        parse(HEADER + ROW + ROW + '|}', mapping)


def test_unknown_party_mapping(mapping):
    mapping = deepcopy(mapping)
    del mapping['headers']['OPP']
    with pytest.raises(ParseDrift, match='unknown_party_mapping'):
        parse(HEADER + ROW + '|}', mapping)


def test_unexplained_row_count_drift(mapping):
    previous = parse(HEADER + ROW + ROW.replace('8–12 Oct', '9–12 Oct') + '|}', mapping)
    current = parse(HEADER + ROW + '|}', mapping, '2')
    removed = previous.polls[1]['id']
    with pytest.raises(ParseDrift, match='missing_previous_polls'):
        compare_revisions(previous.polls, current, {})
    review = {'removals': {removed: {'revision': '2', 'reason': 'Synthetic duplicate survey correction'}}}
    assert compare_revisions(previous.polls, current, review).diagnostics['removed_ids'] == [removed]
    report = compare_revisions(current.polls, previous, {})
    assert report.diagnostics['new_count'] == 2
    assert report.diagnostics['added_ids'] == [removed]
