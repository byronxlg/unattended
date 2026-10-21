"""Voting actions follow NZ midnight and omit absent snapshot facts."""
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest

from product.nz_election.pipeline.vote_page import page
from product.nz_election.pipeline.snapshots import load_voting


@pytest.mark.parametrize(('clock', 'first', 'second'), [
    ('2026-10-25T10:59:59Z', 'enrol', 'places'),
    ('2026-10-25T11:00:00Z', 'places', 'enrol'),
])
def test_order_at_nz_midnight(clock, first, second):
    html = page(clock)
    assert html.index(f'id="{first}"') < html.index(f'id="{second}"') < html.index('id="two-votes"')
    assert html.index('id="two-votes"') < html.index('id="help"') < html.index('id="compare"')
    assert '<strong>13</strong>' in html if first == 'enrol' else '<strong>12</strong>' in html


@pytest.mark.parametrize('identity', ['enrolment-closes', 'advance-opens', 'election-day'])
def test_missing_date_drops_line(identity):
    rows = load_voting()
    removed = next(r for r in rows if r['id'] == identity)
    html = page('2026-10-25T11:00:00Z', [r for r in rows if r['id'] != identity])
    assert removed['summary'] not in html
    assert f'datetime="{removed["date"]}"' not in html
    if identity == 'election-day':
        assert 'days until election day' not in html


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.append(dict(attrs)['href'])


@pytest.mark.parametrize('clock', ['2026-10-25T10:59:59Z', '2026-10-25T11:00:00Z'])
def test_first_screen_links_are_snapshot_ec_actions(clock):
    parser = Links()
    parser.feed(page(clock).split('<section id="help">')[0])
    official = {r['url'] for r in load_voting() if r.get('url')}
    assert parser.hrefs
    assert set(parser.hrefs) <= official
    assert all(urlsplit(url).hostname in {'vote.nz', 'elections.nz'} for url in parser.hrefs)


def test_missing_action_drops_link_and_no_accessible_deadline():
    rows = [r for r in load_voting() if r['id'] != 'find-where-to-vote']
    html = page('2026-10-25T11:00:00Z', rows)
    assert 'Use the official finder' not in html
    accessible = html.split('Accessible formats</a>')[1].split('</div>')[0]
    assert 'Deadline' not in accessible
    assert '12:00 pm, Saturday 7 November 2026 NZDT' in html
    assert '7:00 pm, Saturday 7 November 2026 NZDT' in html


@pytest.mark.parametrize('identity', ['what-to-bring', 'two-votes'])
def test_snapshot_correction_changes_published_guidance(monkeypatch, tmp_path, identity):
    import json
    from html import escape
    from product.nz_election.pipeline import snapshots

    snapshot = json.loads((snapshots.SNAPSHOTS / 'voting.json').read_text())
    record = next(r for r in snapshot['records'] if r['id'] == identity)
    original = record['summary']
    correction = 'Corrected guidance with <reviewed> wording & source context.'
    record['summary'] = correction
    (tmp_path / 'voting.json').write_text(json.dumps(snapshot))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    html = page('2026-10-25T11:00:00Z')
    answer = html.split('<section id="two-votes">')[1].split('</section>')[0]
    assert escape(correction) in answer
    assert escape(original) not in answer


class AnswerFixture:
    def __init__(self, *, visible=True, box=None, text='Voting guidance'):
        self.visible = visible
        self.box = dict(x=16, y=600, width=358, height=200) if box is None else box
        self.text = text

    def is_visible(self):
        return self.visible

    def bounding_box(self):
        return self.box

    def inner_text(self):
        return self.text


def test_hidden_answer_fails_then_visible_answer_passes():
    from product.nz_election.tests.screenshots import vote_answer_check

    # display:none has an empty client rectangle, which passed the old bottom-only gate.
    hidden = AnswerFixture(visible=False, box=dict(x=0, y=0, width=0, height=0), text='')
    assert hidden.box['y'] + hidden.box['height'] <= 844
    with pytest.raises(AssertionError, match='VOTE_ANSWER_NOT_VISIBLE'):
        vote_answer_check(hidden, dict(width=390, height=844))
    vote_answer_check(AnswerFixture(), dict(width=390, height=844))


@pytest.mark.parametrize('box', [
    dict(x=16, y=600, width=0, height=200),
    dict(x=16, y=600, width=358, height=0),
    dict(x=-1, y=600, width=358, height=200),
    dict(x=16, y=-1, width=358, height=200),
    dict(x=16, y=600, width=375, height=200),
    dict(x=16, y=600, width=358, height=245),
])
def test_answer_requires_whole_nonzero_box_in_viewport(box):
    from product.nz_election.tests.screenshots import vote_answer_check

    with pytest.raises(AssertionError, match='VOTE_ANSWER_BOX'):
        vote_answer_check(AnswerFixture(box=box), dict(width=390, height=844))


def test_answer_requires_nonempty_text():
    from product.nz_election.tests.screenshots import vote_answer_check

    with pytest.raises(AssertionError, match='VOTE_ANSWER_EMPTY'):
        vote_answer_check(AnswerFixture(text=' \n '), dict(width=390, height=844))
