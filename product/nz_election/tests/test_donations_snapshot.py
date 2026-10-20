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
    assert rows
    assert all(r['document_url'] and r['document_locator'] for r in rows)
    assert all(amount_cents(r['amount_nzd']) >= 2_000_001 for r in rows)
    assert any('replaces' in r for r in rows)


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


def test_unlinked_duplicate(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, duplicate)
    with pytest.raises(ValueError, match='^donations_duplicate:'):
        loader()


def test_identical_duplicate(monkeypatch, tmp_path, loader):
    edit(monkeypatch, tmp_path, lambda d: d['records'].append(deepcopy(d['records'][0])))
    with pytest.raises(ValueError, match='^donations_duplicate:'):
        loader()


@pytest.mark.parametrize('field,error', [
    ('retrieved_at', 'donations_retrieved_at'),
    ('document_url', 'donations_source_invalid'),
    ('source_url', 'donations_source_invalid'),
    ('licence', 'donations_licence'),
    ('document_locator', 'donations_record'),
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
