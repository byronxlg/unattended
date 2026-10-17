# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Validated 2025 boundaries; spherical Lambert equal-area at 173 E, 41 S."""
import argparse
from html import escape
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.fixtures import ROOT, captures

PRODUCT = ROOT.parent
KINDS = {'general': ('GED2025_V1_00', 64), 'maori': ('MED2025_V1_00', 7)}
FIELDS = 'name kind slug stats_id search_key baseline_ids boundary_note mapping_status'.split()


def search_key(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.category(c).startswith('M')).casefold().split())


def polygons(geometry):
    if not isinstance(geometry, dict) or geometry.get('type') not in {'Polygon', 'MultiPolygon'}:
        raise ValueError('INVALID_GEOMETRY')
    coords = geometry.get('coordinates')
    result = [coords] if geometry['type'] == 'Polygon' else coords
    if not isinstance(result, list) or not result:
        raise ValueError('EMPTY_POLYGON')
    for polygon in result:
        if not isinstance(polygon, list) or not polygon:
            raise ValueError('EMPTY_POLYGON')
        for ring in polygon:
            if not isinstance(ring, list) or len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError('INVALID_RING')
            for point in ring:
                if (not isinstance(point, list) or len(point) != 2 or
                        any(type(n) not in (int, float) or (type(n) is float and not math.isfinite(n)) for n in point) or
                        not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90):
                    raise ValueError('INVALID_COORDINATE')
            if len({tuple(p) for p in ring}) < 3:
                raise ValueError('INVALID_RING')
    return result


def validate(collection, kind, registry=None, expected=True):
    if not isinstance(collection, dict) or collection.get('type') != 'FeatureCollection' or collection.get('exceededTransferLimit'):
        raise ValueError('INVALID_FEATURE_COLLECTION')
    features = collection.get('features')
    if not isinstance(features, list) or (expected and len(features) != KINDS[kind][1]):
        raise ValueError('INVALID_FEATURE_COUNT')
    prop = KINDS[kind][0]
    seen = {}
    for feature in features:
        if not isinstance(feature, dict) or feature.get('type') != 'Feature':
            raise ValueError('INVALID_FEATURE')
        properties = feature.get('properties', {})
        if not isinstance(properties, dict):
            raise ValueError('INVALID_PROPERTIES')
        identity, name = properties.get(prop), properties.get(prop + '_NAME')
        if not isinstance(identity, str) or not identity or identity in seen or not isinstance(name, str) or not name:
            raise ValueError('INVALID_FEATURE_ID')
        seen[identity] = name
        polygons(feature.get('geometry'))
    if registry is not None and seen != {r['stats_id']: r['name'] for r in registry if r['kind'] == kind}:
        raise ValueError('REGISTRY_MISMATCH')
    return collection


def load():
    paths = {'stats-nz/' + k + '-2025.geojson' for k in KINDS}
    raw = captures(paths=paths)
    return {k: validate(json.loads(raw['stats-nz/' + k + '-2025.geojson']), k) for k in KINDS}


def registry(collections):
    correspondence = json.loads((PRODUCT / 'config/electorate-correspondence.json').read_text())
    mappings = {e['new_id']: e for e in correspondence['entries'] if e['new_id'] is not None}
    manifest = json.loads((ROOT / 'manifest.json').read_text())['entries']
    existing_path = PRODUCT / 'config/electorates.json'
    existing = {r['id']: r['slug'] for r in json.loads(existing_path.read_text())} if existing_path.exists() else {}
    rows = []
    for kind, collection in collections.items():
        prop = KINDS[kind][0]
        path = 'stats-nz/' + kind + '-2025.geojson'
        acquired = next(e['captured_at'] for e in manifest if e['path'] == path)
        for feature in collection['features']:
            code = feature['properties'][prop]
            name = feature['properties'][prop + '_NAME']
            mapping = mappings.get(code)
            key = search_key(name)
            row = dict(id='stats-nz-2025-' + code, name=name, kind=kind,
                       slug=existing.get('stats-nz-2025-' + code, re.sub('[^a-z0-9]+', '-', key).strip('-')), stats_id=code, search_key=key,
                       baseline_ids=mapping['old_ids'] if mapping else [],
                       boundary_note=mapping['note'] if mapping else 'Comparison unresolved',
                       mapping_status=mapping['relationship'] if mapping else 'unresolved', observed_at=acquired)
            row['source_ref'] = [dict(field=f, source_id='G:' + path, locator=prop + '=' + code)
                                 if f not in {'baseline_ids', 'boundary_note', 'mapping_status'} else
                                 dict(field=f, source_id='config/electorate-correspondence.json', locator='new_id=' + code)
                                 for f in ['id', 'observed_at', *FIELDS]]
            rows.append(row)
    return sorted(rows, key=lambda r: (r['kind'], r['search_key']))


def project(point):
    longitude, latitude = point
    delta = (longitude - 173 + 180) % 360 - 180
    standard = math.cos(math.radians(-41))
    return (6371008.8 * math.radians(delta) * standard,
            6371008.8 * math.sin(math.radians(latitude)) / standard)


def projected(geometry):
    return [[list(map(project, ring)) for ring in polygon] for polygon in polygons(geometry)]


def inside(point, ring):
    x, y = point
    hit = False
    for (a, b), (c, d) in zip(ring, ring[1:]):
        if (b > y) != (d > y) and x < (c - a) * (y - b) / (d - b) + a:
            hit = not hit
    return hit


def interior(polygon):
    # Scan between vertex heights, where crossings cannot coincide with vertices.
    ys = sorted({y for x, y in polygon[0]})
    candidates = sorted(zip(ys, ys[1:]), key=lambda pair: pair[1] - pair[0], reverse=True)
    for low, high in candidates:
        y = (low + high) / 2
        xs = sorted(a + (c - a) * (y - b) / (d - b)
                    for ring in polygon for (a, b), (c, d) in zip(ring, ring[1:]) if (b > y) != (d > y))
        for left, right in sorted(zip(xs[::2], xs[1::2]), key=lambda pair: pair[1] - pair[0], reverse=True):
            p = ((left + right) / 2, y)
            if inside(p, polygon[0]) and not any(inside(p, hole) for hole in polygon[1:]):
                return p
    raise ValueError('NO_INTERIOR_POINT')


def summary(feature, prop):
    parts = projected(feature['geometry'])
    points = [p for poly in parts for ring in poly for p in ring]
    def area(ring):
        return abs(sum(a * d - c * b for (a, b), (c, d) in zip(ring, ring[1:]))) / 2
    return dict(id=feature['properties'][prop], components=len(parts),
                extent=[min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)],
                area=sum(area(poly[0]) - sum(map(area, poly[1:])) for poly in parts),
                interior_points=[interior(poly) for poly in parts])


def svg(collections, rows, only=None):
    features = [(k, f) for k, c in collections.items() for f in c['features']
                if only is None or 'stats-nz-2025-' + f['properties'][KINDS[k][0]] == only]
    if not features:
        return '<p>Map not available</p>'
    all_points = [p for _, f in features for poly in projected(f['geometry']) for ring in poly for p in ring]
    xmin, xmax = min(p[0] for p in all_points), max(p[0] for p in all_points)
    ymin, ymax = min(p[1] for p in all_points), max(p[1] for p in all_points)
    scale = 900 / max(xmax - xmin, ymax - ymin)
    width, height = (xmax - xmin) * scale + 20, (ymax - ymin) * scale + 20
    result = [f'<svg xmlns="http://www.w3.org/2000/svg" class="electorate-map" viewBox="0 0 {width:.1f} {height:.1f}" aria-labelledby="map-title map-description">',
              '<title id="map-title">2025 electorate boundaries</title><desc id="map-description">General and Māori electorates. Use the adjacent directory to select small areas. Source: Stats NZ.</desc>',
              '<defs><pattern id="selected-hatch" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 0L6 6" stroke="currentColor"/></pattern></defs>']
    by_id = {r['id']: r for r in rows}
    for kind in KINDS:
        result.append('<g class="map-layer layer-' + kind + '">')
        for k, feature in features:
            if k != kind:
                continue
            row = by_id['stats-nz-2025-' + feature['properties'][KINDS[k][0]]]
            commands = []
            for poly in projected(feature['geometry']):
                for ring in poly:
                    points = [f'{(x-xmin)*scale+10:.1f},{(ymax-y)*scale+10:.1f}' for x, y in ring[:-1]]
                    commands.append('M' + ' '.join(points) + 'Z')
            result.append(f'<a href="/unattended/nz-election/electorates/{row["slug"]}/" tabindex="-1"><path data-electorate="{row["slug"]}" fill-rule="evenodd" d="{"".join(commands)}"><title>{escape(row["name"])}</title></path></a>')
        result.append('</g>')
    result.append('</svg>')
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['registry'])
    args = parser.parse_args()
    if args.command == 'registry':
        (PRODUCT / 'config/electorates.json').write_text(json.dumps(registry(load()), ensure_ascii=False, indent=2) + '\n')
        print('PASS registry: 71 rows')


if __name__ == '__main__':
    main()
