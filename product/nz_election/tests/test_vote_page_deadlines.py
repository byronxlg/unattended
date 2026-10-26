"""Visible voting deadlines survive phase changes and incomplete provenance."""
from datetime import datetime, timedelta
import re

import pytest

from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.snapshots import load_voting
from product.nz_election.pipeline.vote_page import page


PHASES = [
    '2026-10-25T10:59:59Z',
    '2026-10-25T11:00:00Z',
    '2026-11-06T21:00:00Z',
    '2026-11-07T21:00:00Z',
]


def visible_text(html):
    def text(node):
        if isinstance(node, str):
            return node
        if (node.tag in {'script', 'style', 'template'} or 'hidden' in node.attrs
                or node.attrs.get('aria-hidden') == 'true'
                or 'display:none' in node.attrs.get('style', '').replace(' ', '')):
            return ''
        return ' '.join(text(child) for child in node.children)
    return ' '.join(text(Tree(html).root).split())


def assert_resolved_descriptions(html):
    tree = Tree(html)
    targets = {node.attrs['id']: node for node in tree.nodes if 'id' in node.attrs}
    for node in tree.nodes:
        for identity in node.attrs.get('aria-describedby', '').split():
            assert identity in targets
            assert targets[identity].text.strip()


@pytest.mark.parametrize('clock', PHASES)
def test_vote_exact_enrolment_deadline_visible_once(clock):
    row = next(row for row in load_voting() if row['id'] == 'enrolment-closes')
    previous = datetime.fromisoformat(row['at']) - timedelta(days=1)
    text = visible_text(page(clock)).lower()
    assert text.count('midnight') == 1
    assert re.search(r'midnight[^.]*' + previous.strftime('%-d %B').lower(), text)


@pytest.mark.parametrize('clock', PHASES)
def test_vote_shared_closing_instant_visible_once(clock):
    text = visible_text(page(clock)).lower()
    closing = re.findall(r'\b7(?::00)?\s*pm\b', text)
    assert len(closing) == 1
    assert re.search(r'7(?::00)?\s*pm[^.]*7 november', text)
    assert len(re.findall(r'\bnoon\b|\b12(?::00)?\s*pm\b', text)) == 1
    assert re.search(r'(noon|12(?::00)?\s*pm)[^.]*7 november', text)
    assert 'completed overseas voting papers' in text
    assert 'registered telephone-dictation voters' in text
    assert 'including if you have used it before' in text


@pytest.mark.parametrize('clock', PHASES)
@pytest.mark.parametrize('missing', ['election-day', 'overseas-voting', 'all'])
def test_vote_missing_retrieval_keeps_visible_facts_and_resolved_sources(clock, missing):
    rows = load_voting()
    for row in rows:
        if missing == 'all' or row['id'] == missing:
            row.pop('retrieved_at')
    html = page(clock, rows)
    text = visible_text(html)
    assert 'Electoral Commission' in text
    assert '7 November' in text
    assert_resolved_descriptions(html)
    assert not re.search(r'Retrieved\s*(?:\.|$)', text)
    if missing == 'all':
        assert 'Retrieved' not in text


def test_vote_absent_shared_close_leaves_no_seven_pm():
    rows = [row for row in load_voting() if row['id'] not in
            {'voting-closes', 'overseas-upload-closes', 'telephone-voting-closes'}]
    text = visible_text(page(PHASES[2], rows)).lower()
    assert not re.search(r'\b7(?::00)?\s*pm\b', text)


@pytest.mark.parametrize('clock', PHASES)
@pytest.mark.parametrize('identity', ['election-day', 'overseas-voting', 'ec-terms'])
def test_vote_single_record_without_retrieval_has_no_empty_credit(clock, identity):
    row = next(row for row in load_voting() if row['id'] == identity)
    row.pop('retrieved_at')
    html = page(clock, [row])
    text = visible_text(html)
    assert 'Electoral Commission' in text
    assert 'Retrieved' not in text
    assert_resolved_descriptions(html)
