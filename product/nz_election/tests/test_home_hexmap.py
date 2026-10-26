"""Hex geometry follows the snapshot grid without pinning SVG serialization."""
from math import dist
from xml.etree import ElementTree

import pytest

from product.nz_election.pipeline import home_graphics, snapshots
from product.nz_election.pipeline.build import config


def test_native_layout_has_connected_islands_and_maori_cluster():
    rows = snapshots.load('hexmap')
    remaining = {(r['x'], r['y']): r['group'] for r in rows}
    components = []
    while remaining:
        pending = [next(iter(remaining))]
        component = []
        while pending:
            x, y = pending.pop()
            if (x, y) not in remaining:
                continue
            component.append(remaining.pop((x, y)))
            side = 1 if y % 2 else -1
            pending.extend([(x - 1, y), (x + 1, y), (x, y - 1),
                            (x + side, y - 1), (x, y + 1), (x + side, y + 1)])
        components.append(component)
    assert sorted(len(c) for c in components) == [7, 16, 48]
    assert all(len(set(c)) == 1 for c in components)


@pytest.mark.parametrize('viewport', [360, 390])
def test_regular_hexes_preserve_grid_and_phone_target_geometry(viewport):
    cells = snapshots.load('hexmap')
    rows = {r['slug']: r for r in config('electorates')}
    svg, _ = home_graphics.hex_map({}, cells, rows, lambda _: None)
    root = ElementTree.fromstring(svg)
    view_width = float(root.attrib['viewBox'].split()[2])
    centres = {}
    for cell, link in zip(cells, root.findall('a'), strict=True):
        points = [tuple(map(float, p.split(','))) for p in link.find('polygon').attrib['points'].split()]
        assert len(points) == 6
        edges = [dist(p, points[(i + 1) % 6]) for i, p in enumerate(points)]
        assert max(edges) - min(edges) < .15
        xs, ys = zip(*points)
        for span in (max(xs) - min(xs), max(ys) - min(ys)):
            assert span * (viewport - 32) / view_width >= 24
        centres[cell['electorate_slug']] = (sum(xs) / 6, sum(ys) / 6)
    # Consecutive northern rows alternate east and west by half a hex width.
    north, whangarei, kaipara = (centres[s] for s in ('northland', 'whangarei', 'kaipara-ki-mahurangi'))
    assert whangarei[0] > north[0]
    assert north[0] == pytest.approx(kaipara[0], abs=.1)
    assert dist(north, whangarei) == pytest.approx(dist(whangarei, kaipara), abs=.1)
