"""Absent values and source anchors must be meaningful in built pages."""
from copy import deepcopy

import pytest

from product.nz_election.pipeline.content_checks import Tree, check_sources, check_empty_headings
from product.nz_election.pipeline.build import polls_page, config
from product.nz_election.pipeline.snapshot_views import map_graphic, sources
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401


@pytest.mark.parametrize('html', ['<figure><h3>Closest seats</h3></figure>',
                                 '<section><h2>Results</h2><span></span></section>',
                                 '<section><h2>Results</h2><div class="source-note">Source</div></section>'])
def test_empty_heading_rejected(html):
    with pytest.raises(ValueError, match='EMPTY_MODULE'):
        check_empty_headings(html)


@pytest.mark.parametrize('target', ['', '<span id="source-result"></span>', '<div id="source-result"> </div>'])
def test_empty_source_rejected(target):
    with pytest.raises(ValueError, match='EMPTY_PROVENANCE'):
        check_sources('<table aria-describedby="source-result"></table>' + target)


def test_nonempty_content_and_source():
    html = '<section><h2>Results</h2><p>Labour: 18 votes</p><div id="source-result">Electoral Commission</div></section>'
    check_empty_headings(html)
    check_sources('<table aria-describedby="source-result"></table>' + html)


def test_map_equivalent_on_every_electorate(populated):
    envs, site = populated
    for row in config('electorates'):
        html = map_graphic(envs, row['slug'])
        assert 'class="map-key"' in html and 'class="chart-data"' in html
        assert html.count('<tr>') == 72
        check_sources((site / 'electorates' / row['slug'] / 'index.html').read_text())
    port = (site / 'electorates/port-waikato/index.html').read_text()
    assert '2025 locator, not a legal boundary. Stats NZ, CC BY 4.0.' in port
    assert 'class="result-bars"' in port and 'by-election' in port
    assert 'Nineteen electorates are unchanged' not in port
    method = sources(envs).split('<section id="home-leaders">')[0]
    assert '#records-baseline-2023' in method and '#home-port-waikato' in method
    for entry in envs['baseline-2023']['source']:
        assert entry['licence'] in method


def test_absent_sample_has_empty_cell(populated):
    envs, _ = populated
    envs = deepcopy(envs)
    for poll in envs['polls']['data']:
        poll['sample'] = None
    html = polls_page(envs, NOW)
    tree = Tree(html)
    history = next(n for n in tree.nodes if n.tag == 'table' and 'Ten most recent national polls' in n.text)
    rows = [n for n in history.children if not isinstance(n, str)]
    def samples(node):
        if node.tag == 'tr':
            cells = [c for c in node.children if not isinstance(c, str) and c.tag == 'td']
            if cells:
                assert cells[2].text == ''
                return 1
        return sum(samples(c) for c in node.children if not isinstance(c, str))
    assert sum(samples(row) for row in rows) == min(10, len(envs['polls']['data']))
    assert 'Not reported' not in html
