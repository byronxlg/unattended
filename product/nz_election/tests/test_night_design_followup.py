"""Review regressions for the night layout and shared seat graphic."""
from collections import Counter
import json
import math
import subprocess

import pytest

from product.nz_election.pipeline import home_graphics as g
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


def test_normalized_srgb_contrast_matches_rgb_without_relaxing_threshold():
    script = '''const el = {childNodes:[{nodeType:3,textContent:'Chlöe'}],getClientRects:()=>[{}],textContent:'Chlöe',parentElement:null};
    globalThis.Node={TEXT_NODE:3};globalThis.document={querySelectorAll:()=>[el]};
    globalThis.getComputedStyle=()=>({visibility:'visible',color:'rgb(22, 24, 29)',backgroundColor:'color(srgb 0.853176 0.917412 0.863765)'});
    console.log(JSON.stringify((CONTRAST)()));'''.replace('CONTRAST', CONTRAST)
    pair = json.loads(subprocess.check_output(['node', '-e', script], text=True))[0]
    assert pair['bg'] == pytest.approx([217.55988, 233.94006, 220.260075])
    assert contrast(pair['fg'], pair['bg']) >= 4.5
    assert contrast([150, 150, 150], [255, 255, 255]) < 4.5


def test_night_design_browser(tmp_path):
    from pathlib import Path
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('night_design_browser.py')), str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS night design behavior: replay, live, settled, official' in result.stdout
