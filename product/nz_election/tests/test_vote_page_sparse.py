"""Sparse voting facts retain their question and one primary heading."""
import pytest

from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.snapshots import load_voting
from product.nz_election.pipeline.vote_page import page


CLOCKS = [
    '2026-10-24T21:00:00Z',
    '2026-10-29T21:00:00Z',
    '2026-11-06T21:00:00Z',
    '2026-11-07T21:00:00Z',
]


def headings_by_role(html, *, name=None, level=None):
    """Read heading roles, accessible names and levels from static page semantics."""
    matches = []
    for node in Tree(html).nodes:
        native_level = int(node.tag[1]) if node.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'} else None
        role = node.attrs.get('role', 'heading' if native_level else None)
        accessible_name = ' '.join(node.attrs.get('aria-label', node.text).split())
        heading_level = int(node.attrs.get('aria-level', native_level or 2))
        if role == 'heading' and (name is None or accessible_name == name) and (level is None or heading_level == level):
            matches.append(accessible_name)
    return matches


@pytest.mark.parametrize('clock', CLOCKS)
@pytest.mark.parametrize('identity', ['advance-opens', 'advance-closes'])
def test_sparse_dates_keep_the_answered_question(clock, identity):
    rows = [row for row in load_voting() if row['id'] == identity]
    html = page(clock, rows)
    question = ('Where can I find election results?' if clock == CLOCKS[-1]
                else 'Where can I vote, and when?')
    assert headings_by_role(html, name=question) == [question]
    assert headings_by_role(html, level=1) == [question]


@pytest.mark.parametrize('clock', CLOCKS)
@pytest.mark.parametrize('identity', [None] + [row['id'] for row in load_voting()])
def test_each_sparse_answer_state_has_one_primary_heading(clock, identity):
    rows = [row for row in load_voting() if row['id'] == identity]
    html = page(clock, rows)
    assert len(headings_by_role(html, level=1)) == 1
    assert headings_by_role(html, name='Where can I compare candidates and policies?')
