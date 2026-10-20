"""Donation snapshot contracts run offline against captured facts."""
from copy import deepcopy
import json

import pytest

from product.nz_election.pipeline import snapshots as s
from product.nz_election.pipeline.donations import amount_cents, load_donations


@pytest.fixture(params=[load_donations, lambda: s.load('donations')])
def loader(request):
    return request.param


def edit(monkeypatch, tmp_path, mutate):
    data = json.loads((s.SNAPSHOTS / 'donations.json').read_text())
    mutate(data)
    (tmp_path / 'donations.json').write_text(json.dumps(data))
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)


def test_valid_file_loads(loader):
    rows = loader()
    assert len(rows) == 146
    assert all(r['document_url'] and r['document_locator'] for r in rows)
    assert all(amount_cents(r['amount_nzd']) >= 2_000_001 for r in rows)
    assert any('replaces' in r for r in rows)
    assert sum(r['party_id'] == 'nat' for r in rows) == 38
    assert sum(r['party_id'] == 'act' for r in rows) == 49
    assert sum(r['party_id'] == 'opp' for r in rows) == 10
    assert {r['party_id'] for r in rows if r['party'] in (
        'Opportunity Party', 'The Opportunities Party')} == {'opp'}
    assert all(type(r['document_checked']) is bool for r in rows)
    assert next(r for r in rows if r['id'] == 'ec-2026-003')['document_checked']
    assert not next(r for r in rows if r['id'] == 'ec-2026-004')['document_checked']


@pytest.mark.parametrize('value', ['0', '19999.99', '20000', '20000.00'])
def test_below_threshold(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(amount_nzd=value))
    with pytest.raises(ValueError, match='^donations_amount_below_threshold:'):
        loader()


@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 2000001, 20000.01, 10**100, '9'*100,
    'NaN', 'Infinity', '2e4', '20,001', '$20001', '-20001', '20000.001',
    '２０００１', '20001\n', ' 20001', '020001',
])
def test_inexact_or_malformed_amount(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(amount_nzd=value))
    with pytest.raises(ValueError, match='^donations_amount_invalid:'):
        loader()


def test_received_after_disclosed(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(
        received='2026-10-20', disclosed='2026-10-19'))
    with pytest.raises(ValueError, match='^donations_date_order:'):
        loader()


@pytest.mark.parametrize('field', ['received', 'disclosed'])
@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100,
                                  '2026-02-30', '20261020', 'yesterday'])
def test_invalid_date(monkeypatch, tmp_path, loader, field, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update({field: value}))
    with pytest.raises(ValueError, match='^donations_date_invalid:'):
        loader()


@pytest.mark.parametrize('field', ['source_url', 'document_url'])
@pytest.mark.parametrize('value', [
    '', None, [], {}, True, 1.5, 10**100, 'https://example.com/return.pdf',
    'https://elections.nz.example.com/a', 'https://example.com@elections.nz/a',
    'https://elections.nz@evil.nz/a', 'https://[bad', 'https://elections.nz/\na',
    'http://elections.nz/a',
    'https://elections.nz:bad/a', 'https://elections.nz:99999/a',
    'https://elections.nz/\\path', 'https://elections.nz/\x00path',
])
def test_non_ec_source(monkeypatch, tmp_path, loader, field, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update({field: value}))
    with pytest.raises(ValueError, match='^donations_source_invalid:'):
        loader()


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100,
                                  '2026-02-30T00:00:00Z', '2026-10-20'])
@pytest.mark.parametrize('envelope', [False, True])
def test_retrieval_time(monkeypatch, tmp_path, loader, value, envelope):
    def mutate(data):
        (data if envelope else data['records'][0])['retrieved_at'] = value
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^donations_retrieved_at:'):
        loader()


def duplicate(data, linked=False):
    row = deepcopy(data['records'][0])
    row['id'] = 'test-correction'
    if linked:
        row['replaces'] = {'record_id': data['records'][0]['id']}
    data['records'].append(row)
    data['listed_return_count'] += 1


def test_unlinked_duplicate(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, duplicate)
    with pytest.raises(ValueError, match='^donations_duplicate:'):
        loader()


def test_identical_duplicate(monkeypatch, tmp_path, loader):
    def mutate(data):
        data['records'].append(deepcopy(data['records'][0]))
        data['listed_return_count'] += 1
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^donations_duplicate:'):
        loader()


@pytest.mark.parametrize('field,error', [
    ('retrieved_at', 'donations_retrieved_at'),
    ('document_url', 'donations_source_invalid'),
    ('source_url', 'donations_source_invalid'),
    ('licence', 'donations_licence'),
    ('document_locator', 'donations_record'),
    ('party_id', 'donations_party_id'),
    ('document_checked', 'donations_document_checked'),
])
def test_required_provenance(monkeypatch, tmp_path, loader, field, error):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].pop(field))
    with pytest.raises(ValueError, match='^' + error + ':'):
        loader()


def test_linked_duplicate_retains_both(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, lambda d: duplicate(d, linked=True))
    rows = loader()
    assert rows[-1]['replaces']['record_id'] == rows[0]['id']


def test_duplicate_uses_exact_numeric_value(monkeypatch, tmp_path, loader):
    def mutate(data):
        data['records'][0]['amount_nzd'] = '20001'
        duplicate(data)
        data['records'][-1]['amount_nzd'] = '20001.00'
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^donations_duplicate:'):
        loader()


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100,
                                  {'record_id': 'no-such-record'},
                                  {'source_url': 'https://example.com', 'source_locator': 'row 1'}])
def test_invalid_correction(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(replaces=value))
    with pytest.raises(ValueError, match='^donations_correction:'):
        loader()


def test_absent_dates_stay_absent(monkeypatch, tmp_path, loader):
    def mutate(data):
        data['records'][0].pop('received', None)
        data['records'][0].pop('disclosed', None)
    edit(monkeypatch, tmp_path, mutate)
    row = loader()[0]
    assert 'received' not in row and 'disclosed' not in row
    assert 'retrieved_at' in row


@pytest.mark.parametrize('value', [None, [], '', 1.5, True, {}, {'schema': 'wrong'}])
def test_invalid_envelope(tmp_path, value):
    path = tmp_path / 'donations.json'
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='^donations_schema:'):
        load_donations(path)


def test_invalid_json(tmp_path):
    path = tmp_path / 'donations.json'
    path.write_text('{')
    with pytest.raises(ValueError, match='^donations_schema:'):
        load_donations(path)


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100,
                                  'other', 'others', 'NAT', 'nat\n', 'lab'])
def test_unknown_or_mismatched_party_id(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(party_id=value))
    with pytest.raises(ValueError, match='^donations_party_id:'):
        loader()


@pytest.mark.parametrize('value', ['', None, [], {}, 0, 1, 1.5, 10**100, 'false', 'true'])
def test_document_checked_is_boolean(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(document_checked=value))
    with pytest.raises(ValueError, match='^donations_document_checked:'):
        loader()


@pytest.mark.parametrize('value', ['', None, [], {}, True, 146.0, 10**100, -1, 145, 147, '146'])
def test_count_mismatch(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d.update(listed_return_count=value))
    with pytest.raises(ValueError, match='^donations_count_mismatch:'):
        loader()


def test_dropped_record_fails_count(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, lambda d: d['records'].pop())
    with pytest.raises(ValueError, match='^donations_count_mismatch:'):
        loader()


@pytest.mark.parametrize('value', ['', None, {}, True, 1.5, 10**100])
def test_skips_must_be_a_list(monkeypatch, tmp_path, loader, value):
    edit(monkeypatch, tmp_path, lambda d: d.update(skipped_returns=value))
    with pytest.raises(ValueError, match='^donations_count_mismatch:'):
        loader()


def test_complete_index_row_cannot_be_skipped(monkeypatch, tmp_path, loader):
    def mutate(data):
        row = data['records'].pop()
        row['reason'] = 'PDF could not be read'
        data['skipped_returns'].append(row)
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^donations_skip_invalid:'):
        loader()


def test_incomplete_index_row_is_accounted_for(monkeypatch, tmp_path, loader):
    def mutate(data):
        row = data['records'].pop()
        row.pop('donor')
        row['reason'] = 'Index row has no donor name'
        data['skipped_returns'].append(row)
    edit(monkeypatch, tmp_path, mutate)
    assert len(loader()) == 145


def test_sourced_date_conflict_is_retained(loader):
    row = next(r for r in loader() if r['id'] == 'ec-2026-065')
    assert row['received'] == '2026-07-08'
    assert row['disclosed'] == '2026-06-30'
    assert row['date_exception'] == 'ec-index-alajamber-2026'
    assert row['date_note'] and row['source_locator']


@pytest.mark.parametrize('field,value', [
    ('received', '2026-07-09'), ('disclosed', '2026-06-29'),
    ('amount_nzd', '21141'), ('donor', 'Someone else'),
    ('source_url', 'https://elections.nz/other'), ('date_exception', True),
    ('date_exception', 'anything'), ('date_note', ''),
])
def test_date_exception_cannot_be_widened(monkeypatch, tmp_path, loader, field, value):
    def mutate(data):
        row = next(r for r in data['records'] if r['id'] == 'ec-2026-065')
        row[field] = value
    edit(monkeypatch, tmp_path, mutate)
    with pytest.raises(ValueError, match='^donations_date_exception:'):
        loader()


def test_exception_cannot_be_copied_to_another_return(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, lambda d: d['records'][0].update(
        date_exception='ec-index-alajamber-2026', date_note='Copied exception'))
    with pytest.raises(ValueError, match='^donations_date_exception:'):
        loader()


def test_existing_product_ids_are_reused():
    from product.nz_election.pipeline.donations import PARTY_IDS
    config = json.loads((s.PRODUCT / 'config/party-map.json').read_text())
    existing = {p['id'] for p in config['parties'] if not p['aggregate']}
    assert set(PARTY_IDS.values()) - {'nzof', 'tttp'} == existing
