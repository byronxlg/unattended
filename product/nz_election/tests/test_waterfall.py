"""Seat and leader contracts, with synthetic comparisons explicitly separate from captures."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import pytest
from product.nz_election.pipeline import fixtures, night, xml_parser
from product.nz_election.pipeline.night_seats import waterfall, official_change
from product.nz_election.pipeline.night_page import snapshot

WEB = Path(__file__).resolve().parents[1] / 'web'


def test_waterfall_matches_2023_golden():
    golden = fixtures.golden()
    result = waterfall(golden['input'], complete=True, capacity_verified=True)['calculation']
    assert result['seats'] == golden['expectedSeats']
    assert result['occupiedHouse'] == 122
    assert result['overhang'] == 2 and result['vacancies'] == 0


def test_waterfall_python_js_parity():
    source = fixtures.golden()['input']
    cases = [(source, dict(complete=c, capacity_verified=v)) for c in (False, True) for v in (False, True)]
    cases += [(v, dict(complete=True)) for v in ('', None, [], {}, True, 1.5, 10**100, '異')]
    expected = []
    for data, options in cases:
        try:
            expected.append(waterfall(data, **options))
        except ValueError as exc:
            expected.append(str(exc))
    script = "import {waterfall} from " + json.dumps((WEB / 'night-seats.mjs').as_uri()) + ";let s='';for await(const c of process.stdin)s+=c;console.log(JSON.stringify(JSON.parse(s).map(([d,o])=>{try{return waterfall(d,o)}catch(e){return e.message}})));"
    actual = subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps(cases), text=True, capture_output=True, check=True)
    assert json.loads(actual.stdout) == expected


def test_waterfall_overhang_vacancies_and_ties():
    source = dict(partyVotes={'a':60,'b':40}, electorateWins={'a':0,'b':2}, lists={'a':['a1'], 'b':['b1','b2']}, electorateWinners={'a':[], 'b':['b1','b2']}, nonListWinners=[], baseSeats=3)
    calc = waterfall(source, complete=True, capacity_verified=True)['calculation']
    assert (calc['overhang'], calc['vacancies'], calc['occupiedHouse']) == (1, 1, 3)
    assert 'occupiedHouse' not in waterfall(source, complete=True)['calculation']
    source.update(partyVotes={'a':50,'b':50}, electorateWins={'a':0,'b':0}, electorateWinners={'a':[], 'b':[]}, baseSeats=1)
    assert waterfall(source, complete=True)['status'] == 'unresolved tie'
    assert waterfall(source)['calculation'] is None


def test_places_are_not_votes():
    payloads, _, _ = night.load()
    row = payloads['night/illustrative-2023/step-2'][0]
    refs = payloads['night/references/2023'][0]
    html = snapshot(row, refs, 'proof', 'night/illustrative-2023/step-2.json')
    assert 'percent</strong> of voting places' in html
    assert 'votes counted' not in html
    assert 'Source-reported seats' in html


def test_leaders_are_not_winners():
    payloads, _, _ = night.load()
    row = payloads['night/illustrative-2023/step-2'][0]
    refs = payloads['night/references/2023'][0]
    assert len(row['leaders']) == 72
    assert row['leaders']['1']['leader'] and row['leaders']['1']['margin'] == 3896
    assert row['leaders']['39']['leader'] is None
    html = snapshot(row, refs, 'proof', 'night/illustrative-2023/step-2.json')
    assert 'Provisional leader' in html and 'not elected members' in html
    assert html.index('night-leader-map') < html.index('<caption>Electorate provisional leaders:')


def pair():
    return (dict(status='preliminary', election='synthetic-2026', reference_version='synthetic', date='2026-11-08', seats={'a':60,'b':60}),
            dict(status='official', election='synthetic-2026', reference_version='synthetic', date='2026-11-27', seats={'a':61,'b':59}))


def test_official_change_requires_compatible_baseline():
    before, after = pair()
    assert official_change(before, after)['changes'] == {'a':1,'b':-1}
    assert official_change(None, after) is None
    for key, value in [('election','other'), ('reference_version','other'), ('date','2026-11-01'), ('status','preliminary')]:
        broken = dict(after, **{key:value})
        assert official_change(before, broken) is None


def test_specials_requires_explicit_evidence():
    before, after = pair()
    assert 'specials' not in official_change(before, after)
    after['specials'] = {'votes':{'a':200,'b':100}}
    assert 'specials' not in official_change(before, after)
    after['specials']['source'] = 'https://example.org/labelled-synthetic-specials'
    assert official_change(before, after)['specials']['votes'] == {'a':200,'b':100}


def test_2026_detail_captures_have_no_leader_or_final_status():
    raw = fixtures.captures(paths={e['path'] for e in json.loads((fixtures.ROOT / 'manifest.json').read_text())['entries'] if e['path'].startswith('ec-2026-media-xml/')})
    refs = xml_parser.references(*(raw['ec-2026-media-xml/' + n + '.xml'] for n in ('parties','electorates','candidates')))
    paths = [p for p in raw if '/e' in p and p.count('/') == 2]
    assert len(paths) == 6
    for p in paths:
        result = xml_parser.detail(raw[p], refs)
        assert result['leader'] is None and result['status'] == 'not yet reported'


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100, '異'])
def test_incomplete_waterfall_never_allocates(value):
    assert waterfall(value) == dict(status='incomplete', calculation=None)


@pytest.mark.parametrize('field', ['votes', 'total_voting_places', 'total_candidates'])
@pytest.mark.parametrize('token', ['', 'null', 'true', '1.5', '1000000000', '異', '<x>1</x>'])
def test_detail_malformed_counts(field, token):
    import re
    prefix = 'ec-2026-media-xml/'
    raw = fixtures.captures(paths={prefix+n+'.xml' for n in ('parties','electorates','candidates')} | {prefix+'e01/e01.xml'})
    refs = xml_parser.references(*(raw[prefix+n+'.xml'] for n in ('parties','electorates','candidates')))
    malformed = re.sub('<'+field+'>.*?</'+field+'>', '<'+field+'>'+token+'</'+field+'>', raw[prefix+'e01/e01.xml'].decode(), count=1)
    with pytest.raises(ValueError, match='^XML_COUNT$'):
        xml_parser.detail(malformed.encode(), refs)


def test_supplementary_facts_cannot_be_rewritten(tmp_path):
    from product.nz_election.tests.test_night import write_unchecked_night
    loaded = night.load()
    loaded[0]['night/illustrative-2023/step-2'][0]['leaders']['1']['margin'] = 999999
    write_unchecked_night(tmp_path, loaded)
    with pytest.raises(ValueError, match='^NIGHT_CAPTURE_MISMATCH$'):
        night.validate(tmp_path)


def test_detail_tie_is_reported_without_a_leader():
    import xml.etree.ElementTree as ET
    prefix = 'ec-2026-media-xml/'
    raw = fixtures.captures(paths={prefix+n+'.xml' for n in ('parties','electorates','candidates')} | {prefix+'e01/e01.xml'})
    refs = xml_parser.references(*(raw[prefix+n+'.xml'] for n in ('parties','electorates','candidates')))
    root = ET.fromstring(raw[prefix+'e01/e01.xml'])
    for tag, value in [('total_voting_places', '1'), ('total_voting_places_counted', '1'), ('total_votes_cast', '200')]:
        root.find('statistics/' + tag).text = value
    for candidate in list(root.find('candidatevotes'))[:2]:
        candidate.find('votes').text = '100'
    detail = xml_parser.detail(ET.tostring(root), refs)
    assert detail['leader'] is None and detail['status'] == 'final'
    from product.nz_election.pipeline.night_electorates import electorate_view
    row = dict(mode='Packaged 2026 preliminary snapshot', source_ref=[prefix+'election.xml'], leaders={'1':detail})
    assert detail['margin'] == 0
    html = electorate_view(row, refs, 'source-test', 'test')
    assert 'Tied:' in html
    assert all(refs['candidates'][c]['candidate_name'] in html for c in detail['tied_candidates'])


def test_legacy_national_package_can_upgrade(tmp_path):
    from product.nz_election.tests.test_night import write_unchecked_night
    payloads, sources, hashes = night.load()
    payloads['night/index'] = [s for s in payloads['night/index'] if s['id'] != '2026-media']
    payloads = {k:v for k,v in payloads.items() if not k.startswith('night/2026-media/') and k != 'night/references/2026-media'}
    for rows in payloads.values():
        for row in rows:
            for key in ('leaders', 'allocation_input', 'capacity_verified'):
                row.pop(key, None)
    hashes = {k:v for k,v in hashes.items() if not k.startswith(('ec-2023/', 'ec-2026-media-xml/'))}
    sources = [s for s in sources if s['id'] in hashes]
    write_unchecked_night(tmp_path, (payloads, sources, hashes))
    before = night.validate(tmp_path)
    night.prepare(tmp_path, night.load(), 'offline-verification', 'test', '2026-10-22T00:00:00Z')
    assert before < night.validate(tmp_path)
