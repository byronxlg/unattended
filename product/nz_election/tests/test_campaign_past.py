"""Retained advance-vote observations change tense at the voting close."""
from copy import deepcopy
from datetime import date
from html.parser import HTMLParser

import pytest

from product.nz_election.pipeline import advance, build, campaign_page, export
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.m3_checks import check_markup

CLOCKS = [
    ('2026-11-06T12:00:00Z', False),
    ('2026-11-07T06:00:00Z', True),
    ('2026-11-07T10:00:00Z', True),
    ('2026-11-14T00:00:00Z', True),
    ('2026-11-27T00:00:00Z', True),
]


def payload():
    data, sources, hashes = deepcopy(advance.load(historical=True))
    shift = date(2026, 10, 26) - date(2023, 10, 2)
    for row in data['advance-voting']:
        for key in ('date', 'observed_at', 'span_start'):
            row[key] = (date.fromisoformat(row[key]) + shift).isoformat()
        row['id'] = 'advance-' + row['date']
    return data, sources, hashes


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.parts = []
        self.feed(html)

    def handle_data(self, data):
        self.parts.append(data)


def text(html):
    return ' '.join(' '.join(Text(html).parts).split())


@pytest.mark.parametrize('built,closed', CLOCKS)
@pytest.mark.parametrize('populated', [False, True])
def test_campaign_observation_copy(tmp_path, built, closed, populated):
    data = tmp_path / 'data'
    daily_refresh(data, loaders={'advance': lambda: payload() if populated else None})
    envs = export.validate_bundle(data)
    original = deepcopy(envs)
    html = campaign_page.page(envs, built)
    visible = text(html)
    assert check_markup(html, envs)
    assert envs == original
    if populated:
        question = 'How many people voted early?' if closed else 'How many people have voted early?'
        assert question in visible
        if closed:
            assert 'Retained observations of 2026 advance votes through 2026-11-06' in visible
            assert '2026 cumulative advance votes observed through 2026-11-06' in visible
            assert 'running total' not in visible
            assert 'have voted early' not in visible
        else:
            assert 'National daily votes and the running total.' in visible
        for row in campaign_page.eligible(envs):
            assert row['date'] in visible
            for key in ('daily', 'cumulative'):
                assert f'{row[key]:,}' in visible
        before = campaign_page.page(envs, CLOCKS[0][0])
        # The full table and provenance follow the copy and must remain byte-identical.
        assert html[html.index('<table'):] == before[before.index('<table'):]
    else:
        assert ('The retained record contained no 2026 advance-voting observations.' in visible) is closed
        assert 'How many people' not in visible
        assert 'not available' not in visible and 'yet' not in visible
    # The pre-close renderer clock is inside the publication freeze; use an allowed
    # pre-close build clock for the outer heading without bypassing the guard.
    build_clock = built if closed else '2026-11-06T10:00:00Z'
    site = build.build(data, tmp_path / 'site/nz-election', built=build_clock)
    full = text((site / 'campaign/index.html').read_text())
    heading = 'What happened in the campaign?' if closed else 'What is happening in the campaign?'
    assert heading in full
    if closed:
        assert 'What is happening' not in full
