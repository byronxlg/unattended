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
    html = (site / 'index.html').read_text()
    latest = records(section(html, 'latest-polls'))
    trend = records(section(html, 'trend').split('<div id="latest-polls"')[0])
    selected = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    wins = envs['seats']['data']['assumptions']['electorate_wins']
    expected = [p for p in ('nat', 'lab', 'grn', 'act', 'nzf', 'tpm', 'opp')
                if wins.get(p, 0) or any(poll['shares'].get(p) is not None and
                                        poll['shares'][p] >= 5 * poll['scale'] for poll in selected)]
    assert latest[0][1:] == [escape(label(p)) for p in expected]
    assert latest[0][1:] == [p for p in trend[0][1:] if p in latest[0][1:]]
    from product.nz_election.pipeline.average import display
    for cells, poll in zip(latest[1:], selected):
        assert cells[1:] == [display(poll['shares'].get(p), poll['scale']) for p in expected]


def test_7_pollster_source_names_and_text_face(populated):
    envs, site = populated
    from product.nz_election.pipeline.build import config
    names = {v: k for k, v in config('party-map')['pollsters'].items()}
    polls = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    cells = records(section((site / 'index.html').read_text(), 'latest-polls'))[1:]
    assert [r[0].split('<br>')[0] for r in cells] == [escape(names[p['pollster']]) for p in polls]
    assert '.home-module td:first-child{font-family:inherit;font-size:16px}' in (site / 'styles.css').read_text()


def test_8_electorate_baseline_and_text_links(populated):
    _, site = populated
    css = (site / 'styles.css').read_text()
    assert '.home-module .watch-rows td{vertical-align:baseline}' in css
    assert '.home-module td:first-child{font-family:inherit;font-size:16px}' in css
    assert '.home-module .watch-rows a{text-decoration:none}' in css
    assert '.home-module .watch-rows a:focus-visible{text-decoration:underline}' in css
    assert 'min-height:44px' in css and 'outline:3px solid var(--focus)' in css


def test_9_market_propositions_before_prices(populated):
    envs, site = populated
    html = section((site / 'methods/index.html').read_text(), 'markets')
    assert html.count('data-market-id="') == 4
    assert 'Leading market choices: price for Yes' in html
    for row in re.findall(r'<tr data-market-id="([^"]+)">(.*?)</tr>', html):
        market = next(m for m in envs['markets']['data'] if m['id'] == row[0])
        cells = records('<tr>' + row[1] + '</tr>')[0]
        assert cells[0].startswith('Will ') and '?' in cells[0]
        if market['family'] == 'next-pm':
            assert 'next Prime Minister?' in cells[0]
        elif market['family'] == 'government-membership':
            assert 'part of the next Government?' in cells[0]
        else:
            assert ' win ' in cells[0] and ' seats?' in cells[0]
        assert cells[1].endswith('%')


def test_11_seat_bar_has_explicit_column_bounds(populated):
    _, site = populated
    css = (site / 'styles.css').read_text()
    assert '.home-hero{width:100%;min-width:0}' in css
    assert '.home-hero figure,.home-hero .strip{width:100%;max-width:100%;min-width:0}' in css
    assert '*{box-sizing:border-box}' in css


@pytest.mark.parametrize(('value', 'status'), [(499, 'Needs 5%'), (500, 'At or above 5%'), (620, 'At or above 5%')])
def test_threshold_exact_cutoff(populated, value, status):
    envs, _ = populated
    envs = deepcopy(envs)
    envs['averages']['data'][-1]['descriptive']['opp'].update(value=value, scale=100)
    from product.nz_election.pipeline.home import thresholds
    rows = records(thresholds(envs))
    assert next(row[2] for row in rows[1:] if row[0] == escape(label('opp'))) == status
