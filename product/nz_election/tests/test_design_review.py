"""Regressions from the fresh-context design review."""
import json
from pathlib import Path
import subprocess

import pytest

from product.nz_election.pipeline import export
from product.nz_election.pipeline.build import build, config, home_presentation, polls_page, strip
from product.nz_election.pipeline.refresh import refresh


@pytest.mark.parametrize('extra', [0, 2, 17])
def test_client_server_strip_dom_and_accessibility_parity(extra):
    seats = dict(seats=dict(nat=47, lab=35, grn=15, act=10, nzf=9, tpm=4+extra),
                 entitlements=dict(nat=47, lab=35, grn=15, act=10, nzf=9, tpm=4),
                 assumed_house=120+extra, assumed_majority=(120+extra)//2+1, overhang=extra)
    labels = {p: dict(name=c['label'], colour=c['colour']) for p, c in config('party-colours').items()}
    module = Path(__file__).resolve().parents[1] / 'web/coalitions.mjs'
    script = "import {stripHTML} from " + json.dumps(module.as_uri()) + ";import fs from 'node:fs';const x=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(stripHTML(x.seats,x.labels));"
    actual = subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps(dict(seats=seats, labels=labels)), text=True, capture_output=True, check=True)
    # Exact markup includes all text, ARIA names, styles, table cells and open seat section.
    assert actual.stdout == strip(seats)


def test_empty_thirty_day_window_builds(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-12-01T01:00:00Z', end_date='2026-12-01')
    envs = export.validate_bundle(data)
    assert envs['polls']['data'] and not envs['averages']['data'][-1]['poll_ids']
    site = build(data, tmp_path / 'output', built='2026-12-01T01:00:00Z')
    html = (site / 'polls/index.html').read_text()
    assert 'class="strip"' not in html and 'No seat estimate' not in html
    assert 'How have the polls moved?' in html
    visible = html.split('<p><strong>Why seats are unavailable')[0]
    assert 'id="source-seats"' in visible and 'Read how seats are calculated.</a>' in (site / 'methods/index.html').read_text()
    assert json.loads((site / 'home-presentation.json').read_text())['result'] is None


def test_page_and_card_share_availability_and_selected_provenance(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    envs = export.validate_bundle(data)
    for built, available in [('2026-10-17T01:00:00Z', True), ('2026-10-17T04:00:01Z', False)]:
        presentation = home_presentation(envs, built)
        assert bool(presentation['result']) is available
        site = build(data, tmp_path / 'output', built=built)
        stored = json.loads((site / 'home-presentation.json').read_text())
        assert stored == presentation
        html = (site / 'index.html').read_text()
        assert stored['source'] in (site / 'methods/index.html').read_text()
        assert ('class="strip"' in html) is available
        if available:
            assert {p['id'] for p in stored['selected']} == set(envs['averages']['data'][-1]['poll_ids'])
            latest = max(p['fieldwork_end'] for p in stored['selected'])
            assert f'datetime="{latest}"' in stored['source']
        else:
            assert 'id="home-seats"' not in html and 'id="seats"' in html
    assert 'class="strip"' not in polls_page({}, '2026-10-17T01:00:00Z')


def test_source_publishers_and_licences_visible_per_entry():
    from product.nz_election.pipeline.electorate_pages import source
    entries = [dict(id='G:stats-nz/general-2025.geojson', url='https://services2.arcgis.com/example', licence='CC BY 4.0 (Stats NZ)'),
               dict(id='G:representation-commission/report-2025.pdf', url='https://elections.nz/report.pdf', licence='Crown copyright; CC BY 4.0'),
               dict(id='wikipedia/candidates-2026.wikitext', url='https://en.wikipedia.org/w/api.php', licence='CC BY-SA 4.0 (Wikipedia contributors)')]
    for entry in entries:
        entry.update(fetched_at='2026-10-17T01:00:00Z', history_url=None)
    html = source({'electorates': dict(source=entries, run_url='offline-verification')}, 'electorates', full=True)
    visible = html.split('<div><p><strong>Source history and producing run')[0]
    for entry, name in zip(entries, ['Stats NZ', 'Representation Commission', 'Wikipedia contributors']):
        assert f'href="{entry["url"]}">{name}</a>' in visible
        assert entry['licence'] in visible
    assert 'id="source-electorates"' in html
