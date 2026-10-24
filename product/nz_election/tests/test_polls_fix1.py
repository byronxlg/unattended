"""Regressions for the polls host review and initial night hydration."""
from decimal import Decimal
import json
from pathlib import Path
import re
import subprocess

import pytest

from product.nz_election.pipeline.build import polls_page
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.home import footnote, trend_graphic
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401

PRODUCT = Path(__file__).resolve().parents[1]


def test_labels_cannot_extend_average_lines(populated):
    envs, _ = populated
    for html in (polls_page(envs, NOW), trend_graphic(envs)):
        paths = [n.attrs for n in Tree(html).nodes if n.tag == 'path']
        ticks = [a for a in paths if a.get('class') == 'trend-label-tick']
        assert ticks, 'TREND_LABEL_TICKS_REQUIRED'
        for tick in ticks:
            assert re.fullmatch(r'M342 [\d.]+H350', tick['d'])
            assert tick['stroke'] == 'var(--grey)'
        assert not any(re.search(r'L350 ', a.get('d', '')) for a in paths), 'LABEL_LOOKS_LIKE_DATA'
        assert any(a.get('stroke-width') == '3.5' for a in paths)


@pytest.mark.parametrize('publisher', ['Wikipedia contributors', 'Wikipedia contributors.', 'Wikipedia contributors. '])
def test_footnote_has_one_period(publisher):
    html = footnote('trend', publisher, '')
    assert 'Wikipedia contributors. ' in html
    assert not re.search(r'contributors\.\s*\.', html)


def test_leading_changes_precede_plot_with_since_date(populated):
    envs, _ = populated
    html = polls_page(envs, NOW)
    nodes = Tree(html).nodes
    summary = next((n for n in nodes if n.attrs.get('class') == 'poll-change-summary'), None)
    assert summary is not None, 'POLLS_CHANGE_SUMMARY_REQUIRED'
    first, last = envs['averages']['data'][-29], envs['averages']['data'][-1]
    for party, name in [('nat', 'National'), ('lab', 'Labour')]:
        before, after = (a['descriptive'][party] for a in (first, last))
        delta = Decimal(after['value']) / after['scale'] - Decimal(before['value']) / before['scale']
        assert f'{name} {delta:+.1f} points' in summary.text
        assert any(n.attrs.get('data-change-party') == party for n in nodes)
    assert f'datetime="{first["date"]}"' in html
    assert html.index('class="poll-change-summary"') < html.index('class="trend-layout"')


def serialized(node):
    return dict(tag=node.tag, attrs=node.attrs, children=[c if isinstance(c, str) else serialized(c) for c in node.children])


def test_night_static_text_equals_actual_startup():
    from product.nz_election.pipeline.night import load
    from product.nz_election.pipeline.night_page import page
    payloads, _, _ = load()
    envs = {key: {'data': rows} for key, rows in payloads.items()}
    html = page(envs, NOW)
    result = subprocess.run(['node', str(Path(__file__).with_name('night_hydration.mjs')), str(PRODUCT / 'web')],
                            input=json.dumps(dict(tree=serialized(Tree(html).root), built=NOW)),
                            text=True, capture_output=True, check=True)
    rendered = json.loads(result.stdout)
    assert rendered['before'] == rendered['after'], 'NO_JS_CONTENT_MISMATCH: route=night/'


@pytest.mark.parametrize(('built', 'retrieval'), [
    ('2026-11-07T05:59:59Z', ''), ('2026-11-07T06:00:00Z', ''),
    ('2026-11-07T06:14:59Z', '2026-11-07T06:00:00Z'),
    ('2026-11-07T06:15:00Z', '2026-11-07T06:00:00Z'),
])
def test_server_live_notice_matches_client(built, retrieval):
    from product.nz_election.pipeline.night_page import live_status
    script = '''import {NightLive, OPEN} from MODULE;
const [built, retrieval] = JSON.parse(process.argv[1]);
const live = new NightLive({now: () => Date.parse(built), status: text => process.stdout.write(text)});
if (Date.parse(retrieval) >= OPEN) live.last = {retrieved_at: retrieval};
live.notice();'''.replace('MODULE', json.dumps((PRODUCT / 'web/night-live.mjs').as_uri()))
    result = subprocess.run(['node', '--input-type=module', '-e', script, json.dumps([built, retrieval])],
                            text=True, capture_output=True, check=True)
    assert live_status(built, retrieval) == result.stdout
