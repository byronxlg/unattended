"""Remainders are explicit, bounded, and traceable through the published bundle."""
from copy import deepcopy
from pathlib import Path
import re

import pytest

from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.build import build, config, strip, seat_topline
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline import export
from product.nz_election.pipeline.social_page import page
from product.nz_election.tests.test_social import fixture, NOW


def row(**shares):
    return dict(id='test', revision='1', pollster='Example', fieldwork_end='2026-10-19',
                scale=100, shares=dict(nat=shares.get('nat', 5000), lab=shares.get('lab', 4500), others=None))


@pytest.mark.parametrize('lab,expected', [(4000, 1000), (4500, 500), (5000, 0), (3999, None), (5001, None), (None, None)])
def test_bounded_others(lab, expected):
    original = row(lab=lab)
    before = deepcopy(original)
    average = trend([original], ['2026-10-19'])[0]
    assert original == before
    assert average['coherent'] == (expected is not None)
    if expected is None:
        assert average['shares'] is None and average['derivations'] == []
        assert {'poll_id': 'test', 'party_id': 'others'} in average['missing']
    else:
        assert average['shares']['others'] * 100 == expected * average['scale']
        assert average['denominator'] == 100 * average['scale']
        assert average['derivations'] == [dict(poll_id='test', revision='1', pollster='Example',
                                             party_id='others', rule='others-remainder-0-to-10-v1',
                                             value=expected, scale=100)]


def test_named_party_missing_from_one_row_is_never_derived():
    a, b = row(), dict(row(), id='second')
    b['shares'] = dict(b['shares'], grn=100)
    average = trend([a, b], ['2026-10-19'])[0]
    assert not average['coherent']
    assert {'poll_id': 'test', 'party_id': 'grn'} in average['missing']
    assert all(d['party_id'] == 'others' and d['poll_id'] == 'second' for d in average['derivations'])


def test_live_capture_seats_and_published_derivations(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-19T01:00:00Z')
    envs = export.validate_bundle(data)
    average = envs['averages']['data'][-1]
    assert average['coherent'] and envs['seats']['data']['available']
    derived = [d for a in envs['averages']['data'] for d in a['derivations']]
    assert {d['pollster'] for d in derived} == {'anacta', 'talbot-mills'}
    assert all(p['shares']['others'] is None for p in envs['polls']['data'] if p['id'] in {d['poll_id'] for d in derived})
    assert 'others-remainder-0-to-10-v1' in (data / 'averages.csv').read_text()
    site = build(data, tmp_path / 'site/nz-election', built='2026-10-19T01:00:00Z')
    polls = (site / 'polls/index.html').read_text()
    assert polls.count('Others derived:') == len({d['poll_id'] for d in derived})
    methods = (site / 'methods/index.html').read_text()
    assert 'Affected pollsters: Anacta, Talbot Mills.' in methods
    home = (site / 'index.html').read_text()
    assert 'Government parties: 67 seats' in home
    assert 'Opposition parties: 58 seats' in home and '67 needed' in home
    assert re.findall(r'data-(?:overhang-)?party="([^"]+)"', home.split('class="lanes"')[0]) == ['nat', 'nat', 'act', 'nzf', 'opp', 'lab', 'grn', 'tpm', 'tpm']


def test_group_colours_and_segment_order():
    seats = dict(lab=38, grn=16, nat=42, opp=2, act=9, nzf=9, tpm=4)
    result = dict(seats=seats, entitlements=seats, assumed_house=120, assumed_majority=61, overhang=0)
    html = strip(result)
    assert re.findall(r'class="segment" data-party="([^"]+)"', html) == ['nat', 'act', 'nzf', 'opp', 'lab', 'grn', 'tpm']
    assert 'data-party="opp" style="width:1.666667%;background:#595959' in html
    css = (Path(__file__).resolve().parents[1] / 'web/styles.css').read_text()
    for group, party, token, dominant in [('government', 'nat', 'left', 2), ('opposition', 'lab', 'right', 0)]:
        assert config('seat-groups')[group]['token'] == token
        assert f'class="bloc-{token}"' in seat_topline(result)
        colour = config('party-colours')[party]['colour']
        assert f'background:{colour}' in html
        bloc = re.search('--' + token + r':(#[A-Fa-f0-9]{6})', css)[1]
        for value in (colour, bloc):
            rgb = [int(value[i:i+2], 16) for i in (1, 3, 5)]
            assert rgb[dominant] == max(rgb)
    assert 'body:has(:target) .section-links' not in css
    assert '.section-links a:first-child' not in css


def test_social_notice_for_populated_empty_and_stale(tmp_path):
    data = tmp_path / 'data'
    fixture(data)
    envs = export.validate_bundle(data)
    for built in (NOW, '2026-10-19T01:00:00Z'):
        html = page(envs, built)
        assert '<p class="state">Proof of concept. 240 posts sampled from X; 2026-10-16 to 2026-10-16.' in html
    assert '<p class="state">Proof of concept. Sample size unavailable; date range unavailable.' in page({}, NOW)


def test_v1_bundle_remains_readable_and_refreshes_to_v2(tmp_path):
    from product.nz_election.pipeline.seats import project
    data = tmp_path / 'data'
    refresh(data, now='2026-10-19T01:00:00Z')
    envs = export.validate_bundle(data)
    averages = envs['averages']
    averages['data'] = trend(envs['polls']['data'], [a['date'] for a in averages['data']],
                             config('party-map'), config('poll-review'), derive=False)
    averages['method_version'] = 'window-mean-30d-v1'
    export.pair(data, 'averages', averages)
    seats = envs['seats']
    seats['data'] = project(averages['data'][-1])
    seats['method_version'] = 'window-mean-30d-v1'
    seats['input_hashes']['averages.json'] = export.digest((data / 'averages.json').read_bytes())
    export.pair(data, 'seats', seats)
    export.inventory(data, 'offline-verification', seats['code_sha'], '2026-10-19T01:00:00Z')
    assert not export.validate_bundle(data)['seats']['data']['available']
    refresh(data, now='2026-10-19T02:00:00Z')
    current = export.validate_bundle(data)
    assert current['averages']['method_version'] == 'window-mean-30d-v2'
    assert current['seats']['data']['available']


def test_derived_input_disclosure_on_every_affected_module(tmp_path):
    from html.parser import HTMLParser
    class VisibleText(HTMLParser):
        def __init__(self, html):
            super().__init__()
            self.depth, self.text = 0, ''
            self.feed(html)

        def handle_starttag(self, tag, attrs):
            if tag == 'details':
                self.depth += 1

        def handle_endtag(self, tag):
            if tag == 'details':
                self.depth -= 1

        def handle_data(self, text):
            if not self.depth:
                self.text += text

    from product.nz_election.pipeline.build import derivation_note, home_presentation, explorer
    from product.nz_election.pipeline.home import poll_figures
    data = tmp_path / 'data'
    built = '2026-10-19T01:00:00Z'
    refresh(data, now=built)
    envs = export.validate_bundle(data)
    average = envs['averages']['data'][-1]
    n = len({d['poll_id'] for d in average['derivations']})
    m = len(average['poll_ids'])
    assert 0 < n < m
    expected = f'Others derived as 100 minus the named parties for {n} of {m} polls; '
    target = '/unattended/nz-election/methods/#derived-polls'
    presentation = home_presentation(envs, built)
    for module in (presentation['source'], poll_figures(envs, presentation), explorer(envs)):
        assert expected in module and f'href="{target}"' in module
        assert expected in VisibleText(module).text
    site = build(data, tmp_path / 'output', built=built)
    for route in ('index.html', 'polls/index.html', 'og/home.html', 'og/polls.html'):
        html = (site / route).read_text()
        assert expected in html and f'href="{target}"' in html
    polls = (site / 'polls/index.html').read_text()
    for heading, end in [('Which parties are near the 5 percent threshold?', '</section>'),
                         ('What is the average party vote?', '</section>')]:
        module = polls.split(heading, 1)[1].split(end, 1)[0]
        assert expected in module
    methods = (site / 'methods/index.html').read_text().split('id="derived-polls"', 1)[1].split('</section>', 1)[0]
    affected = {d['poll_id'] for a in envs['averages']['data'] for d in a['derivations']}
    assert set(re.findall(r'href="/unattended/nz-election/polls/#source-([^"]+)"', methods)) == affected
    for poll in envs['polls']['data']:
        if poll['id'] in affected:
            assert poll['fieldwork_start'] in methods and poll['fieldwork_end'] in methods
    assert derivation_note(dict(average, derivations=[])) == ''
    assert derivation_note(dict(average, poll_ids=[])) == ''


def test_stale_social_counts_keep_fixture_notice_and_provenance(tmp_path):
    data = tmp_path / 'data'
    fixture(data)
    envs = export.validate_bundle(data)
    html = page(envs, '2026-10-19T01:00:00Z')
    assert '240 posts sampled from X; 2026-10-16 to 2026-10-16' in html
    assert 'Offline verification: synthetic examples, not live data.' in html
    assert '<svg' not in html and '<details' not in html
    assert 'From twitterapi.io' in html and 'X terms apply; no CC licence asserted for X data.' in html
    assert 'Retrieved ' in html and 'id="source-social"' in html
    assert 'href="https://twitterapi.io/"' in html
    assert 'href="/unattended/nz-election/data/social/daily.json"' in html
    assert html.index('240 posts') < html.index('Offline verification:') < html.index('id="source-social"')
    live = deepcopy(envs)
    for row in live['social/daily']['data']:
        row['provenance']['fixture'] = False
    assert 'synthetic examples' not in page(live, '2026-10-19T01:00:00Z')
    assert 'data/social/daily.json' not in page({}, '2026-10-19T01:00:00Z')
