"""Reviewed identity, static directory, SVG budgets and evidence contracts."""
from collections import Counter
import json
import re
import xml.etree.ElementTree as ET
from product.nz_election.pipeline import geography as g
from product.nz_election.pipeline.build import electorates_page
from product.nz_election.pipeline.fixtures import captures
from product.nz_election.pipeline.refresh import config


def test_slug_registry_and_macron_search():
    rows = config('electorates')
    mappings = config('electorate-correspondence')['entries']
    assert len(rows) == 71
    assert {(r['stats_id'], r['name']) for r in rows} == {(r['new_id'], r['new_name']) for r in mappings if r['new_id'] is not None}
    assert len({r['slug'] for r in rows}) == 71
    assert rows == g.registry(g.load())
    for r in rows:
        assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', r['slug'])
        assert r['search_key'] == g.search_key(r['name'])
    assert g.search_key('  TĀMAKI  Makaurau ') == 'tamaki makaurau'


def test_correspondence_evidence():
    data = config('electorate-correspondence')
    entries, totals = data['entries'], data['totals']
    old = {int(e.attrib['e_no']) for e in ET.fromstring(captures(paths={'ec-2023-xml/electorates.xml'})['ec-2023-xml/electorates.xml'])}
    assert len(entries) == totals['entry_count'] == 77
    assert {i for e in entries for i in e['old_ids']} == old
    assert len(old) == totals['distinct_old_ids_covered']
    for e in entries:
        assert e['evidence'] and e['reviewer'] and e['review_date']
        assert e['relationship'] in {'unchanged', 'boundary_changed', 'renamed', 'created', 'abolished'}
        assert (e['new_id'] is None) == (e['relationship'] == 'abolished')
    current = [e for e in entries if e['new_id'] is not None]
    assert len(current) == totals['new_total']
    assert Counter(e['relationship'] for e in current) == totals['new_relationship_counts']
    assert sum(len(e['new_id']) == 3 for e in current) == totals['new_general']
    assert sum(len(e['new_id']) != 3 for e in current) == totals['new_maori']
    assert sum(e['new_id'] is None for e in entries) == totals['replacement_predecessor_records']


def test_svg_links_titles_and_holes():
    rows = config('electorates')
    svg = g.svg(g.load(), rows)
    root = ET.fromstring(svg)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    links = root.findall('.//s:a', ns)
    assert len(links) == 71
    assert {a.attrib['href'] for a in links} == {'#electorate-' + r['slug'] for r in rows}
    assert all(a.find('s:path/s:title', ns).text for a in links)
    assert all(a.find('s:path', ns).attrib['fill-rule'] == 'evenodd' for a in links)
    expected = sum(len(poly) for c in g.load().values() for f in c['features'] for poly in g.polygons(f['geometry']))
    assert sum(a.find('s:path', ns).attrib['d'].count('M') for a in links) == expected


def test_svg_page_budget(tmp_path):
    collections, rows = g.load(), config('electorates')
    svg = g.svg(collections, rows)
    assert len(svg.encode()) <= config('geography')['index_svg_max_bytes']
    assert 'src=' not in svg and '.svg' not in svg
    assert max(len(g.svg(collections, rows, r['id']).encode()) for r in rows) <= config('geography')['outline_svg_max_bytes']
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.tests.svg_budget import svg_page_bytes
    data, site = tmp_path / 'data', tmp_path / 'site'
    daily_refresh(data, now='2026-10-18T01:00:00Z')
    build(data, site / 'nz-election')
    html = (site / 'nz-election/electorates/index.html').read_text()
    assert svg_page_bytes(html, site) <= config('geography')['index_svg_max_bytes']


def test_missing_geometry_is_unavailable(monkeypatch):
    html = electorates_page({})
    assert 'Map not available' in html
    assert html.count('data-search-key=') == 71
    assert html.index('<h2>General electorates') < html.index('<h2>Māori electorates')
    from product.nz_election.pipeline import build
    monkeypatch.setattr(build, 'config', lambda name: {'entries': []} if name == 'electorate-correspondence' else config(name))
    assert electorates_page({}).count('Comparison unresolved') == 71


def test_party_colour_evidence():
    entries = {e['path'] for e in json.loads((g.ROOT / 'manifest.json').read_text())['entries']}
    for value in config('party-colours').values():
        assert re.fullmatch('#[0-9a-fA-F]{6}', value['colour'])
        evidence = value['evidence']
        path = evidence['path'].removeprefix('product/nz_election/').removeprefix('fixtures/')
        assert path in entries
        assert captures(paths={path})[path]
        assert evidence['locator'] and value['reviewer'] and value['review_date']


def test_svg_budget_counts_duplicate_and_linked_maps(tmp_path):
    from product.nz_election.tests.svg_budget import svg_page_bytes
    svg = g.svg(g.load(), config('electorates'))
    assert svg_page_bytes(svg + svg, tmp_path) == 2 * len(svg.encode())
    assert svg_page_bytes(svg + svg, tmp_path) > config('geography')['index_svg_max_bytes']
    path = tmp_path / 'nz-election/maps/general.svg'
    path.parent.mkdir(parents=True)
    path.write_text(svg)
    html = svg + '<img src="../maps/general.svg"><object data="../maps/general.svg#map-title"></object>'
    assert svg_page_bytes(html, tmp_path) == 2 * len(svg.encode())
    assert svg_page_bytes(html, tmp_path) > config('geography')['index_svg_max_bytes']


def test_search_key_python_js_parity():
    import subprocess
    probes = [r['name'] for r in config('electorates')]
    probes += ['  TĀMAKI  Makaurau ', 'ſ', 'ß', 'ẞ', 'Straße', 'STRASSE', 'ΟΣ', 'οσ', 'ος',
               'a\u034fb', 'a\u0903b', 'A\u001c  B\u0085 C', '\ufeffA\ufeff', 'Ꭰꭰ', 'ﬃ']
    script = "import {searchKey} from './product/nz_election/web/electorates.mjs'; let s=''; for await (const c of process.stdin) s+=c; console.log(JSON.stringify(JSON.parse(s).map(searchKey)));"
    result = subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps(probes),
                            text=True, capture_output=True, check=True, cwd=g.PRODUCT.parents[1])
    assert json.loads(result.stdout) == [g.search_key(p) for p in probes]
    for a, b in [('ſ', 's'), ('ß', 'SS'), ('Straße', 'STRASSE'), ('ΟΣ', 'ος')]:
        assert g.search_key(a) == g.search_key(b)
