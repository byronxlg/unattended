"""Snapshot acceptance runs solely against committed data and local photos."""
from copy import deepcopy
import json
import struct

import pytest

from product.nz_election.pipeline import snapshots as s


@pytest.mark.parametrize('name', sorted(s.NAMES))
def test_every_snapshot_loads(name):
    rows = s.load(name)
    assert rows
    assert all(r['source_url'] and r['retrieved_at'] and r['licence'] for r in rows)


def test_snapshot_inventory_and_no_banned_words():
    assert {p.stem for p in s.SNAPSHOTS.glob('*.json')} == s.NAMES
    for path in s.SNAPSHOTS.glob('*.json'):
        assert not s.BANNED.search(json.dumps(json.loads(path.read_text()), ensure_ascii=False))


def test_portraits_are_local_licensed_square_and_small():
    paths = set()
    for name in s.NAMES:
        for row in s.load(name):
            if 'photo' not in row:
                continue
            photo = row['photo']
            assert all(photo[k] for k in ('source_url', 'author', 'licence', 'licence_url', 'changes'))
            assert photo['source_url'].startswith('https://commons.wikimedia.org/wiki/File:')
            path = s.PRODUCT / photo['path']
            assert path.is_file() and 0 < path.stat().st_size < 40_000
            raw = path.read_bytes()
            assert raw[:4] == b'RIFF' and raw[8:16] == b'WEBPVP8 '
            assert raw[23:26] == b'\x9d\x01\x2a'
            assert tuple(n & 0x3fff for n in struct.unpack('<HH', raw[26:30])) == (320, 320)
            paths.add(path)
    assert paths
    assert paths == set((s.PRODUCT / 'web/people').glob('*.webp'))
    assert sum(p.stat().st_size for p in paths) < 2_000_000


def test_electorate_coverage_and_tile_uniqueness():
    config = json.loads((s.PRODUCT / 'config/electorates.json').read_text())
    expected = {r['slug'] for r in config}
    rows = s.load('hexmap')
    assert len(rows) == len(expected) == len({(r['x'], r['y']) for r in rows})
    assert {r['electorate_slug'] for r in rows} == expected
    assert {r['electorate_slug'] for r in s.load('candidates-2026')} == expected
    general = [r for r in rows if r['group'] == 'general']
    maori = [r for r in rows if r['group'] == 'maori']
    assert max(r['x'] for r in general) < min(r['x'] for r in maori)
    by_slug = {r['electorate_slug']: r for r in rows}
    assert by_slug['northland']['y'] < by_slug['auckland-central']['y']
    assert by_slug['wellington-north']['y'] < by_slug['invercargill']['y']


def test_port_waikato_official_result():
    rows = s.load('port-waikato-2023')
    winner, runner_up = sorted(rows, key=lambda r: r['votes'], reverse=True)[:2]
    assert winner['name'] == 'Andrew Bayly'
    assert winner['winner'] and winner['party_id'] == 'nat'
    assert winner['margin'] == winner['votes'] - runner_up['votes'] == 11_432
    assert sum(r['votes'] for r in rows) == 18_652


def test_coverage_of_leaders_and_quoted_positions():
    expected = {'nat', 'lab', 'grn', 'act', 'nzf', 'tpm', 'opp'}
    assert {r['party_id'] for r in s.load('leaders') if 'party_id' in r} == expected
    assert {r['party_id'] for r in s.load('positions')} == expected
    assert len(s.load('leaders')) == 10
    assert all(len(r['quote'].split()) < 30 for r in s.load('positions'))


def test_enrolment_roll_basis_and_historical_precision():
    botany = next(r for r in s.load('enrolment') if r['electorate_slug'] == 'botany')
    assert botany['enrolled'] == 52_737
    assert botany['as_at'] == '2026-09-30' and botany['roll'] == 'general'
    rows = s.load('history')
    assert {r['year'] for r in rows} == set(range(1999, 2024, 3))
    national = next(r for r in rows if r['year'] == 2023 and r.get('party_id') == 'nat')
    assert national['party_vote_share'] == '38.08' and national['seats'] == 48


def test_candidates_have_boolean_mp_status_and_ec_list_rank_evidence():
    rows = s.load('candidates-2026')
    assert len(rows) == 469
    assert all(type(r['sitting_mp']) is bool for r in rows)
    assert sum(r['sitting_mp'] for r in rows) == 105
    ranked = [r for r in rows if 'list_rank' in r]
    assert len(ranked) == 332
    assert all(r['list_rank_source_url'].endswith('Party-lists-for-the-2026-General-Election.pdf')
               and r['list_rank_licence'] for r in ranked)
    assert all(r.get('sitting_mp') is True for r in rows if r.get('sitting_electorate_mp'))


def edit_snapshot(monkeypatch, tmp_path, name, edit):
    data = json.loads((s.SNAPSHOTS / (name + '.json')).read_text())
    edit(data)
    (tmp_path / (name + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)


@pytest.mark.parametrize('field', ['source_url', 'retrieved_at', 'licence'])
def test_reject_record_without_provenance(monkeypatch, tmp_path, field):
    edit_snapshot(monkeypatch, tmp_path, 'leaders', lambda d: d['records'][0].pop(field))
    with pytest.raises(ValueError):
        s.load('leaders')


@pytest.mark.parametrize('field', ['source_url', 'author', 'licence', 'licence_url', 'retrieved_at'])
def test_reject_photo_without_attribution(monkeypatch, tmp_path, field):
    edit_snapshot(monkeypatch, tmp_path, 'leaders', lambda d: d['records'][0]['photo'].pop(field))
    with pytest.raises(ValueError):
        s.load('leaders')


@pytest.mark.parametrize(('name', 'field', 'value'), [
    ('leaders', 'party_id', 'other-party'),
    ('leaders', 'party_id', []),
    ('leaders', 'electorate_slug', 'old-electorate'),
    ('leaders', 'electorate_slug', None),
    ('leaders', 'source_url', 'javascript:alert(1)'),
    ('leaders', 'retrieved_at', '2026-02-30T00:00:00Z'),
    ('leaders', 'photo', None),
    ('enrolment', 'enrolled', 1.5),
    ('enrolment', 'enrolled', True),
    ('enrolment', 'enrolled', -1),
    ('enrolment', 'enrolled', 10**100),
    ('enrolment', 'roll', 'maori'),
    ('history', 'party_vote_share', 'NaN'),
    ('history', 'party_vote_share', '100.01'),
    ('history', 'party_vote_share', 3.2),
    ('history', 'year', 2022),
    ('positions', 'quote', 'word ' * 30),
])
def test_reject_invalid_record(monkeypatch, tmp_path, name, field, value):
    edit_snapshot(monkeypatch, tmp_path, name,
                  lambda d: d['records'][0].__setitem__(field, value))
    with pytest.raises(ValueError):
        s.load(name)


@pytest.mark.parametrize('value', ['', None, [], 1, 1.5, '../leaders', 'leaders.json'])
def test_reject_unknown_snapshot_name(value):
    with pytest.raises(ValueError):
        s.load(value)


@pytest.mark.parametrize('field,value', [
    ('path', '../secrets.jpg'), ('path', 'web/people/absent.webp'),
    ('licence', 'All rights reserved'), ('licence_url', ''),
])
def test_reject_unsafe_photo(monkeypatch, tmp_path, field, value):
    edit_snapshot(monkeypatch, tmp_path, 'leaders',
                  lambda d: d['records'][0]['photo'].__setitem__(field, value))
    with pytest.raises(ValueError):
        s.load('leaders')


@pytest.mark.parametrize('mutation', ['drop', 'duplicate', 'cell'])
def test_reject_invalid_tile_coverage(monkeypatch, tmp_path, mutation):
    def edit(data):
        rows = data['records']
        if mutation == 'drop':
            rows.pop()
        elif mutation == 'duplicate':
            rows.append(deepcopy(rows[0]))
        else:
            rows[1].update(x=rows[0]['x'], y=rows[0]['y'])
    edit_snapshot(monkeypatch, tmp_path, 'hexmap', edit)
    with pytest.raises(ValueError):
        s.load('hexmap')


def test_reject_wrong_margin(monkeypatch, tmp_path):
    edit_snapshot(monkeypatch, tmp_path, 'port-waikato-2023',
                  lambda d: d['records'][0].__setitem__('margin', 1))
    with pytest.raises(ValueError):
        s.load('port-waikato-2023')
