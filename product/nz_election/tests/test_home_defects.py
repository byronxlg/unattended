"""Issue 34 regressions over built HTML and its shipped layout rules, without Chromium."""
from copy import deepcopy
from html import escape
import re

import pytest

from product.nz_election.pipeline.build import label
from product.nz_election.tests.test_home import populated  # noqa: F401


def section(html, identity):
    return html.split(f'id="{identity}"', 1)[1].split('</section>', 1)[0]


def records(html):
    return [re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', row, re.S)
            for row in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)]


def test_5_threshold_status_uses_share(populated):
    envs, site = populated
    from product.nz_election.pipeline.home import thresholds
    rows = records(thresholds(envs))
    average = envs['averages']['data'][-1]['descriptive']
    for row in rows[1:]:
        party = next(p for p in average if escape(label(p)) == row[0])
        d = average[party]
        if d['value'] >= 5 * d['scale']:
            assert row[2] == 'At or above 5%'
    assert rows[0][2] == 'Qualification'


def test_6_latest_includes_qualifying_parties_in_trend_order(populated):
    envs, site = populated
    from product.nz_election.pipeline.home_graphics import SHORT, PARTIES
    from product.nz_election.pipeline.average import display
    html = (site / 'index.html').read_text()
    latest = records(section(html, 'polls'))
    trend = records(section(html, 'trend'))
    selected = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:8]
    # Every party any shown poll reports gets a column, in the trend table's party order.
    expected = [p for p in PARTIES if any(poll['shares'].get(p) is not None for poll in selected)]
    assert [re.sub(r'<[^>]+>', '', c) for c in latest[0][2:]] == [SHORT[p] for p in expected]
    assert [escape(label(p)) for p in expected] == [c for c in trend[0][1:] if c in {escape(label(p)) for p in expected}]
    average = envs['averages']['data'][-1]['descriptive']
    assert latest[1][0] == 'Average'
    assert latest[1][2:] == [display(average[p]['value'], average[p]['scale']) if average.get(p, {}).get('value') is not None else '' for p in expected]
    assert len(latest) == len(selected) + 2
    for cells, poll in zip(latest[2:], selected):
        assert cells[2:] == [display(poll['shares'][p], poll['scale']) if poll['shares'].get(p) is not None else '' for p in expected]


def test_7_pollster_source_names_and_text_face(populated):
    envs, site = populated
    from product.nz_election.pipeline.build import config
    names = {v: k for k, v in config('party-map')['pollsters'].items()}
    polls = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:8]
    cells = records(section((site / 'index.html').read_text(), 'polls'))[2:]
    assert [r[0] for r in cells] == [escape(names[p['pollster']]) for p in polls]
    # Pollster names are set in the text face; mono is for code-like strings only.
    css = (site / 'styles.css').read_text()
    assert not re.search(r'\.poll-table[^{]*\{[^}]*Mono', css)
