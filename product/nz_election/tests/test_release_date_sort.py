"""Release metadata is bounded and every accepted substitution is traceable."""
from datetime import date, timedelta

import pytest

from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import MAX_RELEASE_LAG_DAYS, dates, parse_polls


def row_text(sort):
    return f'''==Party vote==
=== Table of polls ===
{{| class="wikitable"
! Date !! Polling organisation !! Sample size !! NAT !! LAB !! GRN !! ACT !! NZF !! TPM !! OPP !! Others !! Lead
|-
| data-sort-value="{sort}" | 9–19 Oct 2026
| [https://www.thepost.co.nz/politics/361101225/ The Post/Freshwater Strategy]
| 1,458 || 27.6 || 28.7 || 14.3 || 9 || 11.8 || 2.0 || 5.4 || – || –
|}}
'''


@pytest.mark.parametrize('lag', [0, 1, MAX_RELEASE_LAG_DAYS])
def test_release_date_boundaries(mapping, lag):
    sort = (date(2026, 10, 19) + timedelta(days=lag)).isoformat()
    assert dates('9–19 Oct 2026', f'data-sort-value="{sort}"') == ('2026-10-09', '2026-10-19')
    result = parse_polls(row_text(sort), '1381086195', mapping, {})
    poll = result.polls[0]
    assert (poll['fieldwork_start'], poll['fieldwork_end']) == ('2026-10-09', '2026-10-19')
    if lag:
        diagnostic, = result.diagnostics['date_exceptions']
        assert diagnostic['kind'] == 'release-date'
        assert diagnostic['locator'] == poll['source_ref']
        assert diagnostic['visible'] == '9–19 Oct 2026'
        assert diagnostic['sort'] == sort
        assert diagnostic['pollster'] == 'The Post/Freshwater Strategy'
        assert diagnostic['source'] == 'https://en.wikipedia.org/w/index.php?oldid=1381086195'
        assert 'visible fieldwork dates retained' in diagnostic['reason']
    else:
        assert not result.diagnostics.get('date_exceptions')


@pytest.mark.parametrize('sort', [
    (date(2026, 10, 19) + timedelta(days=MAX_RELEASE_LAG_DAYS + 1)).isoformat(),
    '2026-10-08', '2026-10-18', '', 'null', 'False', '[]', '1.5', '9' * 1000,
    '２０２６-１０-２０', '20261020', '2026-10-20T00:00:00', '2026-02-30',
])
def test_invalid_sort_dates(mapping, sort):
    with pytest.raises(ParseDrift) as direct:
        dates('9–19 Oct 2026', f'data-sort-value="{sort}"')
    assert direct.value.reason == 'invalid_dates'
    with pytest.raises(ParseDrift) as parsed:
        parse_polls(row_text(sort), '1381086195', mapping, {})
    assert parsed.value.reason == direct.value.reason
    assert parsed.value.public_locator == 'table:3/row:1'


@pytest.mark.parametrize('bad', [None, False, [], {}, 1.5, 10**1000])
def test_wrong_date_argument_types(bad):
    for value, attrs in [(bad, ''), ('9–19 Oct 2026', bad)]:
        with pytest.raises(ParseDrift) as caught:
            dates(value, attrs)
        assert caught.value.reason == 'invalid_dates'
