"""Offline checks for the EC comparison and its correction ledger."""
import json

import pytest

from product.nz_election.pipeline import snapshots as s

NAME = 'candidate-reconciliation-2026'


def mutate(monkeypatch, tmp_path, edit):
    data = json.loads((s.SNAPSHOTS / (NAME + '.json')).read_text())
    edit(data)
    (tmp_path / (NAME + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)


def test_reconciliation_accounts_for_every_candidate_and_correction():
    rows = s.load(NAME)
    candidates = s.load('candidates-2026')
    assert len(rows) == 71
    assert sum(len(r['matched']) for r in rows) == 467
    assert sum(len(r['added_by_ec']) for r in rows) == 2
    assert sum(len(r['absent_from_ec']) for r in rows) == 2
    assert sum(len(r['corrections']) for r in rows) == 62
    official = [i for r in rows for k in ('matched', 'added_by_ec') for i in r[k]]
    assert len(official) == len(candidates) == 469
    assert len({i['ec_row'] for i in official}) == 469
    assert sum('list_rank' in i for i in official) == 382
    assert sum('snapshot_list_rank' in i for i in official) == 332
    for row in rows:
        expected = []
        for item in row['matched'] + row['added_by_ec']:
            candidate = {'name': item['snapshot_name'], 'party': item['snapshot_party']}
            for correction in row['corrections']:
                if correction['snapshot_name'] == item['snapshot_name']:
                    assert candidate[correction['field']] == correction['before']
                    candidate[correction['field']] = correction['after']
            expected.append((candidate['name'], candidate['party']))
        actual = [(c['name'], c['party']) for c in candidates
                  if c['electorate_slug'] == row['electorate_slug']]
        assert sorted(actual) == sorted(expected)


@pytest.mark.parametrize('field', ['source_url', 'party_list_source_url'])
@pytest.mark.parametrize('level', ['envelope', 'record'])
def test_missing_reconciliation_source(monkeypatch, tmp_path, field, level):
    def edit(data):
        (data if level == 'envelope' else data['records'][0]).pop(field)
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError):
        s.load(NAME)


@pytest.mark.parametrize('value', ['', None, [], 1, 1.5, 10**100, 'unknown\u200b'])
def test_unknown_reconciliation_electorate(monkeypatch, tmp_path, value):
    mutate(monkeypatch, tmp_path, lambda d: d['records'][0].update(electorate_id=value))
    with pytest.raises(ValueError):
        s.load(NAME)


@pytest.mark.parametrize('value', ['', None, [], 'CC BY 4.0', 'nonsense'])
def test_bad_reconciliation_licence(monkeypatch, tmp_path, value):
    mutate(monkeypatch, tmp_path, lambda d: d['records'][0].update(licence=value))
    with pytest.raises(ValueError):
        s.load(NAME)


@pytest.mark.parametrize('change', ['drop', 'duplicate', 'rank', 'null_category'])
def test_reconciliation_integrity(monkeypatch, tmp_path, change):
    def edit(data):
        if change == 'drop':
            data['records'].pop()
        elif change == 'duplicate':
            data['records'].append(data['records'][0])
        elif change == 'rank':
            data['records'][0]['matched'][0]['list_rank'] = 999
        else:
            data['records'][0]['matched'] = None
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError):
        s.load(NAME)


def edit_correction(monkeypatch, tmp_path, field, side, value):
    def edit(data):
        correction = next(c for row in data['records'] for c in row['corrections'])
        correction.update(field=field, before=7 if field == 'list_rank' else 'Original',
                          after=9 if field == 'list_rank' else 'Corrected')
        correction[side] = value
    mutate(monkeypatch, tmp_path, edit)


@pytest.mark.parametrize('field', ['name', 'party'])
@pytest.mark.parametrize('side', ['before', 'after'])
@pytest.mark.parametrize('value', [
    '', None, [], {}, 1, 1.5, 10**100, True, ' \t', ' padded', 'padded\u00a0',
])
def test_reject_invalid_correction_text(monkeypatch, tmp_path, field, side, value):
    edit_correction(monkeypatch, tmp_path, field, side, value)
    with pytest.raises(ValueError, match=f'Invalid correction {field} value'):
        s.load(NAME)


@pytest.mark.parametrize('side', ['before', 'after'])
@pytest.mark.parametrize('value', ['', None, [], {}, True, 0, -1, 1.5, 10**100])
def test_reject_invalid_correction_rank(monkeypatch, tmp_path, side, value):
    edit_correction(monkeypatch, tmp_path, 'list_rank', side, value)
    with pytest.raises(ValueError, match='Invalid correction list_rank value'):
        s.load(NAME)


@pytest.mark.parametrize('side', ['before', 'after'])
@pytest.mark.parametrize(('field', 'value'), [
    ('name', 'Hūhana Lyndon'), ('party', 'A new source party label'), ('list_rank', 3),
])
def test_accept_valid_correction_values(monkeypatch, tmp_path, side, field, value):
    edit_correction(monkeypatch, tmp_path, field, side, value)
    assert s.load(NAME)
