"""Boundary integrity and independently captured full-detail comparison gates."""
from copy import deepcopy
import json
import math
import pytest
from product.nz_election.pipeline import geography as g
from product.nz_election.pipeline.refresh import config


def test_required_boundary_captures():
    for kind in g.KINDS:
        path = g.ROOT / ('stats-nz/' + kind + '-2025.geojson')
        assert path.is_file(), 'MISSING_CAPTURE: ' + str(path)
        assert path.stat().st_size <= config('geography')[kind + '_capture_max_bytes']
    g.load()


def test_reference_capture_required():
    for kind in g.KINDS:
        path = g.ROOT / ('stats-nz/' + kind + '-2025.reference.json')
        assert path.is_file(), 'MISSING_CAPTURE: ' + str(path)


def test_64_general_7_maori_ids():
    for kind, collection in g.load().items():
        g.validate(collection, kind, config('electorates'))


@pytest.mark.parametrize('bad', [None, {}, [], {'type': 'Point', 'coordinates': [0, 0]},
    {'type': 'Polygon', 'coordinates': []}, {'type': 'Polygon', 'coordinates': [[]]},
    {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [0, 0]]]},
    *[{'type': 'Polygon', 'coordinates': [[[0, 0], [v, 1], [1, 1], [0, 0]]]} for v in [None, '', '∞', True, math.nan, math.inf, 181, 10**1000]],
    {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 91], [1, 1], [0, 0]]]},
    {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1]]]}])
def test_closed_finite_wgs84_rings(bad):
    with pytest.raises(ValueError):
        g.polygons(bad)


def test_duplicate_id():
    c = deepcopy(g.load()['general'])
    c['features'][1] = c['features'][0]
    with pytest.raises(ValueError, match='ID'):
        g.validate(c, 'general')


def test_antimeridian_projection():
    assert abs(g.project([179, -44])[0] - g.project([-179, -44])[0]) < 200000


def test_reference_components_extents_and_area():
    # Absence is asserted by the dedicated host gate; never self-derive a reference.
    for kind, collection in g.load().items():
        path = g.ROOT / ('stats-nz/' + kind + '-2025.reference.json')
        if not path.exists():
            continue
        reference = json.loads(path.read_text())
        from product.nz_election.pipeline.export import digest
        assert reference['input_sha256'] != digest((g.ROOT / ('stats-nz/' + kind + '-2025.geojson')).read_bytes())
        prop = g.KINDS[kind][0]
        actual = {f['properties'][prop]: f for f in collection['features']}
        assert set(actual) == {r['id'] for r in reference['features']}
        total = 0
        for expected in reference['features']:
            feature = actual[expected['id']]
            measured = g.summary(feature, prop)
            assert measured['components'] == expected['components']
            assert all(abs(a-b) <= 250 for a,b in zip(measured['extent'], expected['extent']))
            parts = g.projected(feature['geometry'])
            for point in expected['interior_points']:
                assert any(g.inside(point, p[0]) and not any(g.inside(point, h) for h in p[1:]) for p in parts)
            total += measured['area']
        assert abs(total / sum(r['area'] for r in reference['features']) - 1) <= .01
