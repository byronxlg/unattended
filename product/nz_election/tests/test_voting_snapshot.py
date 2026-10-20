"""Voting facts are verified offline, with named failures for broken provenance."""
import json

import pytest

from product.nz_election.pipeline import snapshots as s


def edit(monkeypatch, tmp_path, mutate):
    data = json.loads((s.SNAPSHOTS / 'voting.json').read_text())
    mutate(data)
    (tmp_path / 'voting.json').write_text(json.dumps(data))
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)


def test_valid_voting_snapshot():
    rows = s.load_voting()
    assert s.load('voting') == rows
    by_id = {row['id']: row for row in rows}
    assert by_id['overseas-opens']['date'] == '2026-10-21'
    assert by_id['enrolment-closes']['at'] == '2026-10-26T00:00:00+13:00'
    assert by_id['advance-opens']['date'] == '2026-10-26'
    assert by_id['advance-closes']['date'] == '2026-11-06'
    assert by_id['s197-cutoff']['at'] == '2026-11-07T00:00:00+13:00'
    assert by_id['election-day']['date'] == '2026-11-07'
    assert by_id['telephone-registration-closes']['at'] == '2026-11-07T12:00:00+13:00'
    assert by_id['overseas-upload-closes']['at'] == '2026-11-07T19:00:00+13:00'
    assert {r['id'] for r in rows if r['kind'] == 'action'} == {
        'check-or-update-enrolment', 'find-where-to-vote', 'what-to-bring',
        'two-votes', 'overseas-voting', 'accessible-formats', 'assisted-voting',
        'takeaway-voting', 'telephone-dictation',
    }
    assert 'deadline_ids' not in by_id['accessible-formats']
    assert all(r['source_url'] and r['retrieved_at'] and r['licence'] for r in rows)


@pytest.mark.parametrize('loader', [s.load_voting, lambda: s.load('voting')])
def test_reordered_date_fails(monkeypatch, tmp_path, loader):
    def mutate(data):
        data['records'][0], data['records'][1] = data['records'][1], data['records'][0]
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^voting_date_order:'):
        loader()


def test_missing_source_fails(monkeypatch, tmp_path):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].pop('source_url'))
    with pytest.raises(ValueError, match='^voting_source_missing:'):
        s.load_voting()


@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 1.5, 10**100, 'https://example.com',
    'https://vote.nz.example.com/page', 'https://notvote.nz/page',
    'https://vote.nz@example.com', 'https://example.com@vote.nz',
    'https://[broken', 'javascript:alert(1)', 'https://vote.nz/\npath',
])
def test_invalid_sources_fail(monkeypatch, tmp_path, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(source_url=value))
    with pytest.raises(ValueError, match='^voting_source_invalid:'):
        s.load_voting()


@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 1.5, 10**100, '2026-02-30', '2026-13-01',
    '20261021', '2026-1-1', 'yesterday', '2027-10-21',
])
def test_invalid_dates_fail(monkeypatch, tmp_path, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(date=value))
    with pytest.raises(ValueError, match='^voting_date_invalid:'):
        s.load_voting()


@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 1.5, 10**100, '2026-02-30T00:00:00Z',
    '2026-10-20', 'tomorrow',
])
@pytest.mark.parametrize('envelope', [False, True])
def test_invalid_retrieval_times_fail(monkeypatch, tmp_path, value, envelope):
    def mutate(data):
        (data if envelope else data['records'][0])['retrieved_at'] = value
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^voting_retrieved_at:'):
        s.load_voting()


@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 1.5, 10**100, '2026-10-26T00:00:00',
    '2026-10-26T00:00:00Z', '2026-10-26T00:00:00+12:00',
    '2026-10-26T01:00:00+13:00', '2026-10-26T25:00:00+13:00',
])
def test_invalid_nz_times_fail(monkeypatch, tmp_path, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][1].update(at=value))
    with pytest.raises(ValueError, match='^voting_date_invalid:'):
        s.load_voting()


def test_date_time_order_fails(monkeypatch, tmp_path):
    edit(monkeypatch, tmp_path, lambda d: d['records'][6].update(at='2026-11-07T20:00:00+13:00'))
    with pytest.raises(ValueError, match='^voting_date_order:'):
        s.load_voting()


@pytest.mark.parametrize('field', ['retrieved_at', 'licence'])
def test_missing_record_provenance_fails(monkeypatch, tmp_path, field):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].pop(field))
    error = 'voting_retrieved_at' if field == 'retrieved_at' else 'voting_licence'
    with pytest.raises(ValueError, match='^' + error + ':'):
        s.load_voting()


def test_broken_deadline_reference_fails(monkeypatch, tmp_path):
    def mutate(data):
        next(r for r in data['records'] if r['kind'] == 'action')['deadline_ids'] = ['typo']
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^voting_deadline:'):
        s.load_voting()
