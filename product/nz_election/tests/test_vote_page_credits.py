"""Date credits describe every drawn record, including records without source URLs."""
from product.nz_election.pipeline.build import compact_time
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.snapshots import load_voting
from product.nz_election.pipeline.vote_page import page


CLOCK = '2026-10-27T01:00:00Z'
TIMELINE_IDS = {'overseas-opens', 'enrolment-closes', 'advance-opens',
                'advance-closes', 'election-day'}


def descriptions(html):
    nodes = Tree(html).nodes
    targets = {node.attrs['id']: node for node in nodes if 'id' in node.attrs}
    references = [identity for node in nodes
                  for identity in node.attrs.get('aria-describedby', '').split()]
    assert references, 'Expected date provenance descriptions'
    assert set(references) <= targets.keys(), 'Dangling description references'
    return [targets[identity].text for identity in references]


def test_vote_countdown_without_source_url_has_resolved_description():
    rows = [row for row in load_voting() if row['id'] == 'election-day']
    rows[0].pop('source_url')
    credits = descriptions(page(CLOCK, rows))
    assert all('Electoral Commission' in credit for credit in credits)


def test_vote_timeline_without_source_urls_has_resolved_descriptions():
    rows = [row for row in load_voting() if row['id'] in TIMELINE_IDS]
    for row in rows:
        row.pop('source_url')
    credits = descriptions(page(CLOCK, rows))
    assert all('Electoral Commission' in credit for credit in credits)


def test_vote_credits_use_newest_retrieval_among_drawn_records():
    rows = [row for row in load_voting() if row['id'] != 'election-day']
    newest_drawn = '2026-10-26T01:00:00Z'
    for row in rows:
        row['retrieved_at'] = '2026-10-20T01:00:00Z'
        if row['id'] == 'advance-opens':
            row.pop('source_url')
            row['retrieved_at'] = newest_drawn
        elif row['id'] not in TIMELINE_IDS:
            row['retrieved_at'] = '2026-10-27T01:00:00Z'
    credits = descriptions(page(CLOCK, rows))
    assert all(compact_time(newest_drawn) in credit for credit in credits)
