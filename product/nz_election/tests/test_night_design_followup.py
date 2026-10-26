"""Review regressions for the night layout and shared seat graphic."""
from collections import Counter
import json
import math
import subprocess

import pytest

from product.nz_election.pipeline import home_graphics as g, night, night_page
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.tests.screenshots import CONTRAST, contrast


@pytest.mark.parametrize('seats', [dict(tpm=6, grn=15, lab=34, nzf=8, act=11, nat=48),
                                   dict(tpm=4, grn=13, lab=36, nzf=9, act=8, nat=50),
                                   dict(lab=60, nat=59, opp=1)])
def test_party_wedges_are_contiguous_and_dots_do_not_overlap(seats):
    total = sum(seats.values())
    tree = Tree(g.hemicycle(dict(seats=seats, assumed_house=total, assumed_majority=total // 2 + 1)))
    dots = [n.attrs for n in tree.nodes if n.tag == 'circle']
    assert Counter(d['style'] for d in dots) == Counter({f'fill:{g.pc(p)}': n for p, n in seats.items()})
    ordered = sorted(dots, key=lambda d: -math.atan2(316 - float(d['cy']), float(d['cx']) - 320))
    runs = [d['style'] for i, d in enumerate(ordered) if not i or d['style'] != ordered[i - 1]['style']]
    assert len(runs) == len(set(runs)) == len(seats)
    for i, dot in enumerate(dots):
        for other in dots[i + 1:]:
            distance = math.hypot(float(dot['cx']) - float(other['cx']), float(dot['cy']) - float(other['cy']))
            assert distance + .2 >= float(dot['r']) + float(other['r'])
    paths = {n.attrs.get('class'): n.attrs['d'] for n in tree.nodes if n.tag == 'path'}
    assert paths['majority-underlay'] == paths['majority-mark']


def test_normalized_srgb_contrast_matches_rgb_without_relaxing_threshold():
    script = '''const el = {childNodes:[{nodeType:3,textContent:'Chlöe'}],getClientRects:()=>[{}],textContent:'Chlöe',parentElement:null};
    globalThis.Node={TEXT_NODE:3};globalThis.document={querySelectorAll:()=>[el]};
    globalThis.getComputedStyle=()=>({visibility:'visible',color:'rgb(22, 24, 29)',backgroundColor:'color(srgb 0.853176 0.917412 0.863765)'});
    console.log(JSON.stringify((CONTRAST)()));'''.replace('CONTRAST', CONTRAST)
    pair = json.loads(subprocess.check_output(['node', '-e', script], text=True))[0]
    assert pair['bg'] == pytest.approx([217.55988, 233.94006, 220.260075])
    assert contrast(pair['fg'], pair['bg']) >= 4.5
    assert contrast([150, 150, 150], [255, 255, 255]) < 4.5


def test_night_countdown_hook_and_early_electorate_jump():
    payloads, _, _ = night.load()
    envs = {key: {'data': rows} for key, rows in payloads.items()}
    html = night_page.page(envs, '2026-10-26T00:00:00Z')
    tree = Tree(html)
    page = next(n for n in tree.nodes if n.attrs.get('class') == 'night-page')
    assert any(not isinstance(n, str) and n.attrs.get('class') == 'countdown' for n in page.children)
    seq = next(s for s in payloads['night/index'] if s['id'] == '2023')
    row, refs = payloads[seq['snapshot_paths'][0][:-5]][0], payloads[seq['reference_path'][:-5]][0]
    html = night_page.snapshot(row, refs, 'proof', seq['snapshot_paths'][0])
    assert html.index('Find your electorate') < html.index('Who has enough seats?')
    tree = Tree(html)
    assert sum(n.attrs.get('class') == 'night-combination' for n in tree.nodes) == 3
    assert 'All 8 majority combinations' in html
    assert 'href="#night-search-proof"' in html and 'id="night-search-proof"' in html
    assert 'timezone unverified' not in html
    assert 'Results last updated 10 November 2024 at 00:00.' in html


def test_electorate_precedes_detailed_arithmetic_in_live_and_terminal_states(tmp_path):
    from product.nz_election.pipeline import fixtures, night_live, result_states

    def capture(name):
        path = 'result-states/' + name + '.json'
        return json.loads(fixtures.captures(paths={path})[path])

    def prepare(loaded, state, now):
        folder = tmp_path / state
        night.prepare(folder, loaded, 'offline-verification', 'a' * 40, now)
        return {p.relative_to(folder).as_posix()[:-5]: json.loads(p.read_text()) for p in folder.rglob('*.json')}

    envs = prepare(night_live.loaded(capture('2026-11-07-preliminary-final')), 'live', '2026-11-07T10:35:00Z')
    for state, now in [('live', '2026-11-07T10:35:00Z'), ('settled', '2026-11-08T06:00:00Z'), ('official', '2026-11-27T11:00:00Z')]:
        if state != 'live':
            loaded = result_states.transition(envs, state, now=now,
                                               captured=capture('2026-11-27-official') if state == 'official' else None)
            envs = prepare(loaded, state, now)
        html = night_page.live_package(envs)['html']
        assert html.index('Who is winning?') < html.index('class="night-search"')
        assert html.index('class="night-search"') < html.index('class="night-map-key map-key"')
        assert html.index('class="night-search"') < html.index('Who has enough seats?') < html.index('class="night-votes"')
        tree = Tree(html)
        row = next(n for n in tree.nodes if n.tag == 'tr' and 'Auckland Central' in n.text)
        assert 'Johan Chang' in row.text and 'CHANG, Johan' in row.text
