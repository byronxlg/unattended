"""Row-scoped exceptions retain validation and operational failure details."""
from copy import deepcopy
from datetime import date, timedelta
import json

import pytest

from product.nz_election.pipeline import export, refresh
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import MAX_RELEASE_LAG_DAYS, dates, parse_polls


def assert_release_date_fallback(wikitext, mapping):
    result = parse_polls(wikitext, '9999999999', mapping, {})
    row, = [p for p in result.polls if p['pollster'] == 'verian'
            and p['fieldwork_end'] == '2026-08-11']
    assert row['fieldwork_start'] == '2026-08-08'
    diagnostic, = [d for d in result.diagnostics['date_exceptions']
                   if d['locator'] == row['source_ref']]
    assert diagnostic['kind'] == 'release-date'
    assert diagnostic['visible'] == '8\u201311 Aug 2026'
    assert diagnostic['sort'] == '2026-08-12'
    assert diagnostic['pollster'] == '1 News\u2013Verian'
    assert diagnostic['source'] == 'https://en.wikipedia.org/w/index.php?oldid=9999999999'
    assert 'visible fieldwork dates retained' in diagnostic['reason']


@pytest.mark.parametrize('revision', ['1380524613', '1380694545', '9999999999'])
def test_exception_survives_revision(wikitext, mapping, revision):
    result = parse_polls(wikitext, revision, mapping, {})
    row = next(p for p in result.polls if p['fieldwork_end'] == '2026-08-11')
    assert row['fieldwork_start'] == '2026-08-08'
    assert row['revision'] == revision
    exception = result.diagnostics['date_exceptions'][0]
    assert exception['sort'] == '2026-08-12'
    assert exception['source'] and exception['reason']


@pytest.mark.parametrize('field,value', [
    ('visible', '9\u201311 Aug 2026'), ('sort', '2026-08-13'),
    ('pollster', 'Roy Morgan'), ('source', ''), ('reason', ''),
])
def test_exception_requires_documented_exact_row(wikitext, mapping, field, value):
    original = parse_polls(wikitext, '9999999999', mapping, {})
    assert original.diagnostics['date_exceptions'][0]['kind'] == 'documented-exception'
    mapping = deepcopy(mapping)
    mapping['date_exceptions'][0][field] = value
    assert_release_date_fallback(wikitext, mapping)
    outside_bound = (date(2026, 8, 11) + timedelta(days=MAX_RELEASE_LAG_DAYS + 1)).isoformat()
    for invalid_sort in (outside_bound, '2026-08-07'):
        changed = wikitext.replace('data-sort-value="2026-08-12"', f'data-sort-value="{invalid_sort}"')
        assert changed != wikitext
        with pytest.raises(ParseDrift) as error:
            parse_polls(changed, '9999999999', mapping, {})
        assert error.value.code == 'parse_drift'
        assert error.value.reason == 'invalid_dates'
        assert error.value.locator == '8\u201311 Aug 2026 / ' + invalid_sort
        assert error.value.public_locator == 'table:15/row:19'


@pytest.mark.parametrize('bad', ['', 'null', '[]', '12.5', '9' * 100, 'not-a-date', '2026-02-30'])
@pytest.mark.parametrize('field', ['sort', 'visible'])
def test_matching_exception_cannot_bypass_invalid_date(wikitext, mapping, bad, field):
    mapping = deepcopy(mapping)
    exception = mapping['date_exceptions'][0]
    wikitext = wikitext.replace(exception[field], bad)
    exception[field] = bad
    with pytest.raises(ParseDrift) as error:
        parse_polls(wikitext, '9999999999', mapping, {})
    assert error.value.code == 'parse_drift'
    assert error.value.reason == 'invalid_dates'


@pytest.mark.parametrize('bad', [None, [], {}, 12.5, 10**100])
def test_date_wrong_types_are_drift(bad):
    with pytest.raises(ParseDrift, match='invalid_dates'):
        dates(bad, '')
    with pytest.raises(ParseDrift, match='invalid_dates'):
        dates('8 Aug 2026', bad)


@pytest.mark.parametrize('last_good', [False, True])
def test_main_reports_drift_and_publishes_status(tmp_path, monkeypatch, last_good):
    out = tmp_path / 'bundle'
    if last_good:
        refresh.refresh(out, now='2026-10-17T01:00:00Z')
    previous = (out / 'polls.json').read_bytes() if last_good else None
    summary = tmp_path / 'summary'
    output = tmp_path / 'output'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))
    monkeypatch.setattr('sys.argv', ['refresh', '--fixtures', '--out', str(out)])
    real_refresh = refresh.refresh
    locator = '8\u201311 Aug 2026 / 2026-08-12'

    def fail(*args):
        error = ParseDrift('invalid_dates', locator)
        error.args = ('private response body must not be exposed',)
        raise error

    monkeypatch.setattr(refresh, 'refresh', lambda path: real_refresh(
        path, parse=fail, now='2026-10-17T02:00:00Z'))
    with pytest.raises(SystemExit) as error:
        refresh.main()
    log = str(error.value)
    assert log.startswith('FAIL refresh: parse_drift ')
    details = json.dumps(dict(reason='invalid_dates', locator=''))
    assert details in log
    summary_status = json.loads(summary.read_text().split('```json\n')[1].split('\n```')[0])
    assert details in summary_status['message']
    assert 'private response body' not in log + summary.read_text()
    status = export.validate_bundle(out)['status']['data'][0]
    assert status['state'] == ('stale' if last_good else 'unavailable')
    assert status['message'] == summary_status['message']
    assert output.read_text() == 'validated=true\n'
    if last_good:
        assert (out / 'polls.json').read_bytes() == previous


@pytest.mark.parametrize('case,reason,locator', [
    ('attributes', 'invalid_attributes', 'table:15/row:2'),
    ('template', 'unknown_template', 'table:15/row:4'),
    ('merge', 'unexplained_merge', 'table:15/row:2'),
    ('pollster', 'unknown_pollster', 'table:15/row:4'),
    ('date', 'invalid_dates', 'table:15/row:4'),
    ('reference', 'invalid_attributes', ''),
    ('incident', 'invalid_dates', 'table:15/row:19'),
])
def test_public_drift_has_only_structural_locator(
        tmp_path, monkeypatch, wikitext, mapping, case, reason, locator):
    marker = 'BROKEN_WIKITEXT'
    if case == 'attributes':
        wikitext = wikitext.replace('data-sort-value=', 'data-sort-value ' + marker + '=', 1)
    elif case == 'merge':
        wikitext = wikitext.replace('colspan=11', 'colspan=' + marker, 1)
    elif case == 'template':
        wikitext = wikitext.replace('8–12 Oct 2026', '{{' + marker + '}}', 1)
    elif case == 'pollster':
        wikitext = wikitext.replace(' 1 News–Verian]', ' ' + marker + ']', 1)
    elif case == 'date':
        wikitext = wikitext.replace('8–12 Oct 2026', marker, 1)
    elif case == 'reference':
        wikitext += '<ref name ' + marker + '="bad"/>'
    else:
        mapping['date_exceptions'] = []
        assert_release_date_fallback(wikitext, mapping)
        outside_bound = (date(2026, 8, 11) + timedelta(days=MAX_RELEASE_LAG_DAYS + 1)).isoformat()
        wikitext = wikitext.replace('data-sort-value="2026-08-12"', f'data-sort-value="{outside_bound}"')

    def parse(*args):
        return parse_polls(wikitext, '9999999999', mapping, {})

    with pytest.raises(ParseDrift, match=reason) as failure:
        parse()
    assert failure.value.public_locator == locator
    if case == 'incident':
        assert failure.value.code == 'parse_drift'
        assert failure.value.reason == 'invalid_dates'
        assert failure.value.locator == '8\u201311 Aug 2026 / ' + outside_bound
    if case != 'incident':
        assert marker in str(failure.value)

    out = tmp_path / 'bundle'
    real_refresh = refresh.refresh
    status = real_refresh(out, parse=parse, now='2026-10-17T01:00:00Z')
    detail = json.dumps(dict(reason=reason, locator=locator))
    assert detail in status['message']
    summary = tmp_path / 'summary'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    monkeypatch.setattr('sys.argv', ['refresh', '--fixtures', '--out', str(out)])
    monkeypatch.setattr(refresh, 'refresh', lambda path: real_refresh(
        path, parse=parse, now='2026-10-17T02:00:00Z'))
    with pytest.raises(SystemExit) as failure:
        refresh.main()
    assert detail in str(failure.value)
    summary_status = json.loads(summary.read_text().split('```json\n')[1].split('\n```')[0])
    assert detail in summary_status['message']
    published = export.validate_bundle(out)['status']['data'][0]
    for public in (status['message'], published['message'], str(failure.value), summary.read_text()):
        assert marker not in public
        assert '8–11 Aug 2026' not in public
