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
    for node in nodes:
        identities = node.attrs.get('aria-describedby', '').split()
        if identities:
            assert any('Source: Electoral Commission.' in targets[identity].text for identity in identities)
    return [targets[identity].text for identity in references
            if 'Source: Electoral Commission.' in targets[identity].text]


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
    expected = {f'Source: Electoral Commission. Retrieved {compact_time(when)}.'
                for when in (newest_drawn, '2026-10-27T01:00:00Z')}
    assert set(credits) == expected
    nodes = Tree(page(CLOCK, rows)).nodes
    targets = {node.attrs['id']: node for node in nodes if 'id' in node.attrs}
    timeline = next(node for node in nodes if 'Advance voting opens' in node.text
                    and 'aria-describedby' in node.attrs)
    assert all(compact_time(newest_drawn) in targets[identity].text
               for identity in timeline.attrs['aria-describedby'].split())


def test_shared_date_credit_describes_countdown_and_timeline():
    rows = [row for row in load_voting() if row['id'] == 'election-day']
    html = page(CLOCK, rows)
    credits = descriptions(html)
    assert len(credits) >= 2
    assert len(set(credits)) == 1
    assert html.count(credits[0]) == 1


def test_help_actions_keep_sources_and_all_descriptions_resolve():
    rows = load_voting()
    html = page(CLOCK, rows)
    descriptions(html)
    nodes = Tree(html).nodes
    targets = {node.attrs['id']: node for node in nodes if 'id' in node.attrs}
    for row in rows:
        if row['id'] not in {'overseas-voting', 'accessible-formats', 'assisted-voting',
                             'takeaway-voting', 'telephone-dictation'}:
            continue
        answer = next(node for node in nodes if row['summary'] in node.text
                      and 'aria-describedby' in node.attrs)
        credits = [targets[identity].text for identity in answer.attrs['aria-describedby'].split()]
        assert any('Source: Electoral Commission.' in credit for credit in credits)
        assert row['url'] in html


def test_absent_help_actions_leave_no_action_guidance():
    rows = [row for row in load_voting() if row['kind'] != 'action']
    html = page(CLOCK, rows)
    assert all(row['summary'] not in html for row in load_voting() if row['kind'] == 'action')
    descriptions(html)
