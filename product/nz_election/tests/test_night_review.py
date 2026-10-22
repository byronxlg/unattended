"""PR 62 regressions: clipping, reported ties, and accessible selection targets."""
import json
from pathlib import Path
import re
import subprocess
import pytest
from product.nz_election.pipeline import night, xml_parser
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.night_electorates import electorate_view
from product.nz_election.tests.night_detail_cases import reported_tie, dom_tree

PRODUCT = Path(__file__).resolve().parents[1]


def view(year):
    payloads, _, _ = night.load()
    seq = next(s for s in payloads['night/index'] if s['id'] == year)
    row = payloads[seq['snapshot_paths'][-1][:-5]][0]
    refs = payloads[seq['reference_path'][:-5]][0]
    return Tree(electorate_view(row, refs, 'source-proof', 'proof')), refs


@pytest.mark.parametrize('year', ['2023', '2026-media'])
def test_night_registered_polygons_inside_viewbox(year):
    tree, refs = view(year)
    svg = next(n for n in tree.nodes if n.tag == 'svg')
    x, y, width, height = map(float, svg.attrs['viewbox'].split())
    polygons = [n for n in tree.nodes if n.tag == 'polygon']
    assert len(polygons) == len(refs['electorates'])
    outside = [n.text for n in polygons if any(not (x <= px <= x + width and y <= py <= y + height)
               for px, py in (map(float, point.split(',')) for point in n.attrs['points'].split()))]
    assert not outside, outside


@pytest.mark.parametrize('tied_count', [2, 3])
@pytest.mark.parametrize('final', [False, True])
def test_reported_tie_python_retains_margin_and_names(tied_count, final):
    raw, refs, tied = reported_tie(tied_count, final)
    result = xml_parser.detail(raw, refs)
    assert result['leader'] is None
    assert result['margin'] == 0
    assert result['tied_candidates'] == tied
    assert result['status'] == ('final' if final else 'provisional')
    row = dict(mode='Synthetic tie proof', source_ref=[], leaders={'1':result})
    tree = Tree(electorate_view(row, refs, 'source-proof', 'proof'))
    target = next(n for n in tree.nodes if n.attrs.get('id') == 'night-row-proof-1')
    cells = [c for c in target.children if not isinstance(c, str) and c.tag == 'td']
    assert 'Tied:' in cells[1].text
    assert all(refs['candidates'][c]['candidate_name'] in cells[1].text for c in tied)
    assert cells[2].text == '0'
    assert 'Not yet reported' not in target.text


def test_reported_tie_js_and_python_parity():
    cases, expected, tied_ids = [], [], []
    for count in (2, 3):
        for final in (False, True):
            raw, refs, tied = reported_tie(count, final)
            cases.append(dict(xml=raw.decode(), tree=dom_tree(raw), refs=refs))
            expected.append(xml_parser.detail(raw, refs))
            tied_ids.append(tied)
    runner = Path(__file__).with_name('night_detail_runner.mjs')
    output = subprocess.run(['node', str(runner)], input=json.dumps(cases), text=True, capture_output=True, check=True)
    actual = json.loads(output.stdout)
    for result, tied in zip(actual, tied_ids):
        assert result['margin'] == 0
        assert result['leader'] is None and result['tied_candidates'] == tied
    assert actual == expected


@pytest.mark.parametrize('year', ['2023', '2026-media'])
def test_night_table_is_accessible_selection_route(year):
    tree, refs = view(year)
    svg = next(n for n in tree.nodes if n.tag == 'svg')
    map_nodes = Tree(electorate_view(dict(mode='proof', source_ref=[], leaders={}), refs, 'source-proof', 'proof'))
    # No small duplicate targets remain in the graphic's keyboard or pointer route.
    assert not any(n.tag == 'a' for n in svg.children if not isinstance(n, str))
    rows = [n for n in map_nodes.nodes if n.tag == 'tr' and n.attrs.get('id', '').startswith('night-row-')]
    assert len(rows) == len(refs['electorates'])
    for row in rows:
        first = next(n for n in row.children if not isinstance(n, str) and n.tag == 'td')
        links = [n for n in first.children if not isinstance(n, str) and n.tag == 'a']
        assert links and all('/electorates/' in n.attrs['href'] and n.text.strip() for n in links)
    css = (PRODUCT / 'web/night.css').read_text()
    rule = re.search(r'\.night-page \.night-electorates td a\{([^}]+)\}', css)
    assert rule and 'min-width:24px' in rule[1] and 'min-height:44px' in rule[1]
    assert 'inline-flex' in rule[1]


def test_night_runbook_matches_image_registry():
    from product.nz_election.tests.night_browser import STATES, SIZES
    doc = (PRODUCT / 'runbook/night.md').read_text()
    assert f'{len(STATES) * len(SIZES)}-image night registry' in doc
    assert 'no electorate map/table is rendered' not in doc
    assert 'same ten states' not in doc
