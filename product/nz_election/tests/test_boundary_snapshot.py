"""Boundary validation uses only committed captures and temporary local mutations."""
import json

import pytest

from product.nz_election.pipeline import snapshots as s


def mutate(monkeypatch, tmp_path, edit):
    data = json.loads((s.SNAPSHOTS / 'boundaries-2025.json').read_text())
    edit(data)
    path = tmp_path / 'boundaries-2025.json'
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)
    return path


def test_boundary_coverage_matches_hexmap():
    boundaries = s.load('boundaries-2025')
    tiles = s.load('hexmap')
    assert {r['electorate_slug'] for r in boundaries} == {
        r['electorate_slug'] for r in tiles}
    assert len(boundaries) == 71
    assert sum(r['group'] == 'general' for r in boundaries) == 64
    assert sum(r['group'] == 'maori' for r in boundaries) == 7
    assert (s.SNAPSHOTS / 'boundaries-2025.json').stat().st_size < 400_000


@pytest.mark.parametrize('target', ['source', 'feature'])
def test_missing_source(monkeypatch, tmp_path, target):
    def edit(data):
        row = data['sources'][0] if target == 'source' else data['features'][0]['properties']
        row.pop('source_url')
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError, match='source_url'):
        s.load('boundaries-2025')


@pytest.mark.parametrize('target', ['envelope', 'source', 'feature'])
@pytest.mark.parametrize('value', ['', None, [], 1, 1.5, 'All rights reserved'])
def test_bad_licence(monkeypatch, tmp_path, target, value):
    def edit(data):
        row = (data if target == 'envelope' else data['sources'][0]
               if target == 'source' else data['features'][0]['properties'])
        row['licence'] = value
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError, match='licence'):
        s.load('boundaries-2025')


@pytest.mark.parametrize('value', ['', None, [], {}, 1, 1.5, 10**100, 'stats-nz-2025-999',
                                 'stats-nz-2025-001\u200b'])
def test_unknown_electorate_id(monkeypatch, tmp_path, value):
    mutate(monkeypatch, tmp_path, lambda d: d['features'][0].update(id=value))
    with pytest.raises(ValueError, match='Unknown electorate id'):
        s.load('boundaries-2025')


@pytest.mark.parametrize('size', [400_000, 400_001])
def test_oversize_before_json_parsing(monkeypatch, tmp_path, size):
    path = tmp_path / 'boundaries-2025.json'
    path.write_bytes(b'x' * size)
    monkeypatch.setattr(s, 'SNAPSHOTS', tmp_path)
    with pytest.raises(ValueError, match='byte budget'):
        s.load('boundaries-2025')


@pytest.mark.parametrize('value', ['', None, [], True, 10**100, float('nan'),
                                 float('inf'), 181, 174.12345])
def test_invalid_coordinate(monkeypatch, tmp_path, value):
    def edit(data):
        data['features'][0]['geometry']['coordinates'][0][0][1][0] = value
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError, match='coordinate'):
        s.load('boundaries-2025')


@pytest.mark.parametrize('change', ['drop', 'duplicate', 'name', 'slug', 'open_ring'])
def test_identity_and_geometry_integrity(monkeypatch, tmp_path, change):
    def edit(data):
        if change == 'drop':
            data['features'].pop()
        elif change == 'duplicate':
            data['features'].append(data['features'][0])
        elif change in ('name', 'slug'):
            field = 'electorate_slug' if change == 'slug' else 'name'
            data['features'][0]['properties'][field] = 'wrong'
        else:
            data['features'][0]['geometry']['coordinates'][0][0].pop()
    mutate(monkeypatch, tmp_path, edit)
    with pytest.raises(ValueError):
        s.load('boundaries-2025')
