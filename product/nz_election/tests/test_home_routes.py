"""H-b route metadata, detail order and deployment image contracts."""
import json
import shutil
import struct
import pytest
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.route_cards import route_key, night
from product.nz_election.pipeline.route_checks import check_site, check_images
from product.nz_election.tests.test_home import populated


def test_route_keys():
    assert [route_key(p) for p in ('', 'polls/', 'social/poc/', 'electorates/wellington-north/')] == ['home', 'polls', 'social--poc', 'electorates--wellington-north']


def test_route_cards_and_detail_order(populated):
    envs, site = populated
    check_site(site, envs)
    cards = json.loads((site / 'og-manifest.json').read_text())
    assert len(cards) == 79
    assert len(list((site / 'og').glob('*.html'))) == 79
    assert len(list(site.rglob('index.html'))) == 79
    for card in cards:
        if card['route'].startswith('electorates/') and card['route'] != 'electorates/':
            assert card['description'].startswith(card['title'].split(':')[0])
    east = next(c for c in cards if c['key'] == 'electorates--east-cape')
    assert 'National Party' in east['title'] and '3,199 vote majority in East Coast in 2023' in east['description']
    changed = next(c for c in cards if c['key'] == 'electorates--wellington-north')
    assert 'vote majority in Wellington Central in 2023' in changed['description']


@pytest.mark.parametrize('instant,text', [('2026-11-06T10:59:59Z', '1 day until election day'), ('2026-11-06T11:00:00Z', 'Election day'), ('2026-11-07T11:00:00Z', 'Results')])
def test_night_transition_without_bypassing_freeze(instant, text):
    html = night(instant)
    from html import unescape
    import re
    plain = unescape(re.sub('<[^>]+>', ' ', html))
    assert text in ' '.join(plain.split()) and 'No results feed is published yet.' in html
    assert '00:00 and 19:00 NZDT' in html and 'Electoral Act s197' in html
    assert 'https://www.electionresults.govt.nz/' in html


def test_empty_route_cards(tmp_path):
    site = build(tmp_path / 'absent', tmp_path / 'site/nz-election', built='2026-10-17T01:00:00Z')
    check_site(site, {})
    assert 'class="local-margin"' not in (site / 'electorates/east-cape/index.html').read_text()


@pytest.mark.parametrize('damage', ['metadata', 'manifest', 'order', 'source'])
def test_supplied_routes_reject_damage(populated, tmp_path, damage):
    envs, original = populated
    site = tmp_path / 'site'
    shutil.copytree(original, site)
    if damage == 'manifest':
        path = site / 'og-manifest.json'
        path.write_text(json.dumps(json.loads(path.read_text())[:-1]))
    else:
        path = site / 'electorates/east-cape/index.html'
        html = path.read_text()
        if damage == 'metadata':
            html = html.replace('og/electorates--east-cape.png', 'og/home.png')
        elif damage == 'order':
            html = html.replace('id="candidates-title"', 'id="wrong-order"')
        else:
            html = html.replace('id="source-baseline-2023"', 'id="lost-source"')
        path.write_text(html)
    with pytest.raises((AssertionError, ValueError, SystemExit)):
        check_site(site, envs)


def test_deploy_requires_every_referenced_png(populated, tmp_path):
    _, original = populated
    site = tmp_path / 'site'
    shutil.copytree(original, site)
    with pytest.raises((AssertionError, ValueError, SystemExit)):
        check_images(site)
    cards = json.loads((site / 'og-manifest.json').read_text())
    # Header-only fixtures exercise the deployment dimension gate, not browser rendering.
    for card in cards:
        (site / card['png']).write_bytes(b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', 1200, 630))
    check_images(site)
    (site / cards[-1]['png']).unlink()
    with pytest.raises((AssertionError, ValueError, SystemExit)):
        check_images(site)


def test_workflow_og_before_upload_and_freeze_unchanged():
    from pathlib import Path
    text = Path('.github/workflows/pages.yml').read_text()
    steps = ['pipeline/build.py', 'pipeline/verify.py all', 'playwright install --with-deps chromium', 'screenshots.py --site site --out artifacts/nz-election/og --og-only', 'check_images(', 'bin/blog build', 'actions/upload-pages-artifact@v3']
    assert [text.index(s) for s in steps] == sorted(text.index(s) for s in steps)
    assert text.index('Enforce election freeze at deployment time') < text.index('actions/deploy-pages@v4')
    assert "datetime.fromisoformat('2026-11-06T10:30:00+00:00') <= now < datetime.fromisoformat('2026-11-07T06:00:00+00:00')" in text
