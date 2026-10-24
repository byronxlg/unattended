"""Accepted polls question order, boundary sentences and retained destinations."""
from copy import deepcopy
from fractions import Fraction
import re

import pytest

from product.nz_election.pipeline.build import home_presentation, polls_page
from product.nz_election.pipeline.polls_page import threshold_sentences
from product.nz_election.tests.design_checks import Document, provenance
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401


def test_answer_order_and_marks(populated):
    envs, site = populated
    html = (site / 'polls/index.html').read_text()
    sections = [a['id'] for tag, a in Document(html).nodes if tag == 'section']
    assert sections == ['polls', 'trend', 'seats', 'thresholds', 'recent-polls']
    assert 'methods/#average' in html
    assert html.index('id="recent-polls"') < html.index('class="polls-method"')
    assert '<script' not in html and '<fieldset' not in html
    assert '<circle ' in html and 'fill-opacity="0.3"' in html
    assert 'stroke-dasharray="4 3"' in html and 'class="majority"' in html
    average = envs['averages']['data'][-1]
    expected = sorted((p for p, d in average['descriptive'].items() if d['value'] is not None),
                      key=lambda p: (-Fraction(average['descriptive'][p]['value'], average['descriptive'][p]['scale']), p))
    assert re.findall(r'class="average-row" data-party="([^"]+)"', html) == expected
    assert html.count('class="seat"') == home_presentation(envs, NOW)['result']['assumed_house']
    provenance(html)


@pytest.mark.parametrize(('value', 'included'), [(None, False), (299, False), (300, True), (500, True), (700, True), (701, False)])
def test_threshold_exact_boundaries(value, included):
    html = threshold_sentences({'descriptive': {'act': {'value': value, 'scale': 100}, 'others': {'value': 500, 'scale': 100}}})
    assert ('data-threshold-party="act"' in html) is included
    assert 'data-threshold-party="others"' not in html
    assert html.count('<p') == int(included)
    if included:
        assert 'electorate win' in html and 'below 5%' in html


def test_absence_and_legacy_fragments(populated):
    envs, _ = populated
    envs = deepcopy(envs)
    for d in envs['averages']['data'][-1]['descriptive'].values():
        d.update(value=8, scale=1)
    html = polls_page(envs, NOW, home_presentation(envs, NOW))
    assert '<section id="thresholds"' not in html
    ids = {a['id'] for _, a in Document(html).nodes if 'id' in a}
    assert {'seats', 'polls', 'explorer', 'coalition-explorer', 'coalition-title', 'source-seats',
            'source-grouping', 'source-thresholds', 'source-average', 'source-history'} <= ids
    assert {i for p in envs['polls']['data'] for i in (p['id'], 'source-' + p['id'])} <= ids
    empty = polls_page({}, NOW, home_presentation({}, NOW))
    assert '<figure' not in empty and '<table' not in empty and '<section' not in empty
    assert 'not available' not in empty.lower()
    provenance(empty)


def test_recent_polls_newest_first_with_original_reports(populated):
    from product.nz_election.pipeline.content_checks import Tree
    envs, site = populated
    tree = Tree((site / 'polls/index.html').read_text())
    rows = [n for n in tree.nodes if n.tag == 'tr'][1:]
    recent = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:10]
    assert len(rows) == len(recent)
    for row, poll in zip(rows, recent):
        assert poll['fieldwork_start'] + ' to ' + poll['fieldwork_end'] in row.text
        assert str(poll['sample']) in row.text if poll['sample'] is not None else True
        # Each row's report belongs to that poll, rather than the collection source.
        def descendants(node):
            for child in node.children:
                if not isinstance(child, str):
                    yield child
                    yield from descendants(child)
        links = [n.attrs.get('href') for n in descendants(row) if n.tag == 'a']
        assert set(poll['reference_urls']) <= set(links)
