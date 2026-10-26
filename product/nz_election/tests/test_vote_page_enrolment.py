"""Built enrolment guidance follows the sourced close instant."""
import pytest

from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.snapshots import load_voting


def enrolment_answer(html):
    question = 'Am I enrolled, and is it too late?'
    tree = Tree(html)
    heading = next(node for node in tree.nodes if node.text == question)
    answer = next(node for node in tree.nodes if heading in node.children)
    return answer.text, list(answer_links(answer))


def answer_links(node):
    for child in node.children:
        if not isinstance(child, str):
            if child.attrs.get('href'):
                yield child
            yield from answer_links(child)


def test_before_enrolment_close_unchanged(tmp_path):
    site = build(tmp_path / 'absent', tmp_path / 'site/nz-election', built='2026-10-25T10:59:59Z')
    answer, links = enrolment_answer((site / 'vote/index.html').read_text())
    records = {row['id']: row for row in load_voting()}
    assert answer == ('Am I enrolled, and is it too late?' + records['enrolment-closes']['summary']
                      + 'Check or update your enrolment')
    assert [node.attrs['href'] for node in links] == [records['check-or-update-enrolment']['url']]


@pytest.mark.parametrize('clock', ['2026-10-25T11:00:00Z', '2026-10-27T00:00:00Z'])
def test_after_enrolment_close_only_sourced_fallback(tmp_path, clock):
    site = build(tmp_path / 'absent', tmp_path / 'site/nz-election', built=clock)
    html = (site / 'vote/index.html').read_text()
    answer, links = enrolment_answer(html)
    records = {row['id']: row for row in load_voting()}
    assert answer == ('Am I enrolled, and is it too late?'
                      'The enrolment close has passed.'
                      'Electoral Commission enrolment information')
    assert records['enrolment-closes']['summary'] not in html
    assert 'Check or update your enrolment' not in answer
    assert 'not available' not in answer.lower()
    assert [node.attrs['href'] for node in links] == [records['enrolment-closes']['source_url']]
    assert all(node.attrs['href'] in {row['source_url'] for row in records.values()} for node in links)
