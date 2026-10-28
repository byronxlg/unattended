"""Documented sort disagreements waive lag bounds without weakening date validity."""
from pathlib import Path

import pytest

from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import dates, parse_polls

FIXTURE = Path(__file__).resolve().parents[3] / 'evals/polls-exception-sort-before-end/row.wikitext'


def incident(mapping):
    exception = next(e for e in mapping['date_exceptions'] if e['sort'] == '2026-10-01')
    return FIXTURE.read_text(), exception


@pytest.mark.parametrize('revision', ['1382442932', '9999999999'])
@pytest.mark.parametrize('sort', ['2026-10-01', '2026-10-25', '2026-11-03', '9999-12-31'])
def test_documented_sort_disagreement(mapping, revision, sort):
    text, exception = incident(mapping)
    text = text.replace(exception['sort'], sort)
    exception['sort'] = sort
    result = parse_polls(text, revision, mapping, {})
    row, = result.polls
    assert (row['fieldwork_start'], row['fieldwork_end']) == ('2026-10-20', '2026-10-26')
    assert row['pollster'] == 'reid-research'
    assert row['revision'] == revision
    assert result.diagnostics['date_exceptions'] == [
        dict(exception, locator=row['source_ref'], kind='documented-exception')]


@pytest.mark.parametrize('sort', ['2026-10-01', '2026-11-03'])
@pytest.mark.parametrize('field,value', [
    ('visible', '21–26 Oct 2026'), ('sort', '2026-10-02'),
    ('pollster', 'Roy Morgan'), ('source', ''), ('reason', ''),
    ('source', None), ('reason', None), ('missing', None),
])
def test_undocumented_disagreement_fails(mapping, sort, field, value):
    text, exception = incident(mapping)
    text = text.replace(exception['sort'], sort)
    exception['sort'] = sort
    if field == 'missing':
        mapping['date_exceptions'] = []
    else:
        exception[field] = value
    with pytest.raises(ParseDrift) as error:
        parse_polls(text, '1382442932', mapping, {})
    assert error.value.code == 'parse_drift'
    assert error.value.reason == 'invalid_dates'
    assert error.value.public_locator == 'table:3/row:1'


@pytest.mark.parametrize('field', ['visible', 'sort'])
@pytest.mark.parametrize('bad', ['', 'null', '[]', 'False', '12.5', '9' * 1000,
                                 '２０２６-１０-０１', '2026-02-30', '27–26 Oct 2026'])
def test_matching_exception_still_validates_dates(mapping, field, bad):
    text, exception = incident(mapping)
    text = text.replace(exception[field], bad)
    exception[field] = bad
    with pytest.raises(ParseDrift) as error:
        parse_polls(text, '1382442932', mapping, {})
    assert error.value.reason == 'invalid_dates'


@pytest.mark.parametrize('bad', [None, False, [], {}, 12.5, 10**1000])
def test_exception_date_argument_types(bad):
    for value, attrs in [(bad, ''), ('20–26 Oct 2026', bad)]:
        with pytest.raises(ParseDrift) as error:
            dates(value, attrs, documented_exception=True)
        assert error.value.reason == 'invalid_dates'
