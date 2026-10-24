"""Server state rejection and exact conditional seat contracts."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

import pytest
from product.nz_election.pipeline import coalitions as c, export
from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.fixtures import golden
from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.seats import project
from product.nz_election.pipeline.scripts import SCRIPT_ALLOWLIST, validate_scripts


@pytest.fixture
def request_data(tmp_path):
    refresh(tmp_path / 'data', now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    envs = export.validate_bundle(tmp_path / 'data')
    return dict(average=envs['averages']['data'][-1], seats=envs['seats']['data'], fingerprint='a' * 64)


def evaluate(requests):
    expected = []
    for req in requests:
        try:
            if req.get('op') == 'decode':
                result = c.decode(req['hash'], req['parties'])
            else:
                data = c.inputs(req['average'], req['seats'], req['fingerprint'])
                result = data if req.get('op') == 'inputs' else c.scenario(data, req.get('state', data['initial']))
            expected.append(dict(result=result))
        except ValueError as exc:
            expected.append(dict(error=str(exc)))
    return expected


def test_server_scenarios(request_data):
    data = c.inputs(**request_data)
    requests = [request_data]
    for party in data['parties']:
        for n in ('0', '1', '6', '71'):
            state = deepcopy(data['initial'])
            state['selected'] = [party]
            state['counts'] = {p: n if p == party else '0' for p in data['parties']}
            requests.append(dict(request_data, state=state))
    assert all('result' in result for result in evaluate(requests))


def test_unknown_capacity_stays_conditional(request_data):
    r = evaluate([request_data])[0]['result']
    assert r['occupied_house'] is r['vacancies'] is r['majority'] is None
    assert r['capacity_checked'] is False
    assert r['assumed_majority'] == r['assumed_house'] // 2 + 1


def test_no_preselected_coalition(request_data):
    data = c.inputs(**request_data)
    assert data['initial']['selected'] == [] and 'others' not in data['parties']
    r = c.scenario(data, data['initial'])
    assert r['selected_total'] == 0
    assert r['unassigned_electorates'] == 71 - sum(request_data['seats']['assumptions']['electorate_wins'].values())


def test_invalid_state_error_evaluate(request_data):
    data = c.inputs(**request_data)
    state, parties = data['initial'], data['parties']
    hashes = ['', None, 4, [], {}, '#coalition=', '#coalition=null', '#coalition=%ZZ', '#coalition=%FF', '#coalition=' + 'x' * 8193]
    bad = [None, [], '', 1, True, {}, dict(state, version=True), dict(state, version=2), dict(state, version=1.0), dict(state, mode='checked'),
           dict(state, selected=['others']), dict(state, selected=[parties[0]] * 2), dict(state, selected=['__proto__']),
           dict(state, selected=['constructor']), dict(state, selected=['prototype']), dict(state, selected=['nat\n']),
           dict(state, fingerprint='a' * 64 + '\n'), dict(state, selected=['ＮＡＴ']), dict(state, selected=[None]), dict(state, fingerprint='z' * 64)]
    for v in ['', None, True, -1, 0, 1.0, 1.5, 9007199254740992, '1' * 5000, '72', '-1', '1.0', '1e1', '01', ' 1', '1\n', '１', '١', '∞', '__proto__']:
        bad.append(dict(state, counts=dict(state['counts'], **{parties[0]: v})))
    for key in ['__proto__', 'constructor', 'prototype', 'unknown']:
        bad.append(dict(state, **{key: 1}))
        bad.append(dict(state, counts=dict(state['counts'], **{key: '0'})))
    bad.append(dict(state, counts={p: '71' for p in parties}))
    hashes += ['#coalition=' + quote(export.canonical(value), safe='') for value in bad]
    raw = export.canonical(state)
    hashes += ['#coalition=' + quote(raw.replace('"version":1', '"version":1,"version":1'), safe='')]
    results = evaluate([dict(op='decode', hash=h, parties=parties) for h in hashes])
    assert all(r == {'error': c.ERROR} for r in results)
    assert all(r == {'error': c.ERROR} for r in evaluate([dict(request_data, state=s) for s in [None, {}, [], '', 1, True]]))


def test_hash_round_trip(request_data):
    data = c.inputs(**request_data)
    state = data['initial']
    assert evaluate([dict(op='decode', hash=c.encode(state), parties=data['parties'])])[0]['result'] == state


def test_fingerprint_mismatch_warns(request_data):
    state = c.inputs(**request_data)['initial']
    state['fingerprint'] = 'b' * 64
    assert evaluate([dict(request_data, state=state)])[0]['result'] == {'warning': 'INPUT_FINGERPRINT_MISMATCH', 'applied': False}


def test_incomplete_average_disables_explorer(request_data):
    requests = []
    for field, value in [('coherent', False), ('missing', [{'party_id': 'nat'}]), ('denominator', 0)]:
        r = deepcopy(request_data); r['average'][field] = value; requests.append(r)
    r = deepcopy(request_data); r['seats']['average_id'] = 'wrong'; requests.append(r)
    r = deepcopy(request_data); r['average']['shares'].pop('nat'); requests.append(r)
    r = deepcopy(request_data); r['average']['descriptive']['nat']['poll_ids'].pop(); requests.append(r)
    r = deepcopy(request_data); r['average']['shares']['nat'] = None; requests.append(r)
    assert all(r == {'error': 'INCOMPLETE_COALITION_INPUT'} for r in evaluate(requests))


def test_overhang(request_data):
    data = c.inputs(**request_data)
    state = deepcopy(data['initial'])
    state['counts'] = {p: '71' if p == 'tpm' else '0' for p in data['parties']}
    r = evaluate([dict(request_data, state=state)])[0]['result']
    assert r['overhang'] > 0 and r['assumed_house'] == 120 + r['overhang']


def test_real_candidate_vacancies():
    source = golden()['input']
    source['lists'] = {p: list(ws) for p, ws in source['electorateWinners'].items() if ws}
    r = allocate(source)
    assert r['vacancies'] > 0 and r['occupiedHouse'] == 120 + r['overhang'] - r['vacancies']
    runner = Path(__file__).with_name('allocator_runner.mjs')
    actual = subprocess.run(['node', str(runner)], input=json.dumps([source]), capture_output=True, text=True, check=True)
    assert json.loads(actual.stdout) == [{'result': r}]


def test_script_allowlist():
    assert SCRIPT_ALLOWLIST == {'allocator.mjs', 'electorates.mjs', 'night.mjs', 'night-live.mjs'}
    assert validate_scripts('<script type="module" src="/unattended/nz-election/allocator.mjs"></script>')
    for html in ['<script>alert(1)</script>', '<script type="module" src="https://example.com/allocator.mjs"></script>',
                 '<script type="module" src="/unattended/nz-election/allocator.mjs">alert(1)</script>',
                 '<script type="module" src="/unattended/nz-election/other.mjs"></script>',
                 '<script type="module" src="//evil/allocator.mjs"></script>',
                 '<script type="module" src="/unattended/nz-election/allocator.mjs" onload="x"></script>']:
        with pytest.raises(ValueError, match='UNSAFE_SCRIPT'):
            validate_scripts(html)


def test_static_content_preserved(tmp_path, request_data):
    out = build(tmp_path / 'data', tmp_path / 'output', built='2026-10-17T01:00:00Z')
    html = (out / 'polls/index.html').read_text()
    from product.nz_election.pipeline.build import home_presentation
    from product.nz_election.pipeline.home import hero
    envs = export.validate_bundle(tmp_path / 'data')
    home = home_presentation(envs, '2026-10-17T01:00:00Z')
    assert html.count('class="seat"') == home['result']['assumed_house']
    assert 'class="strip"' in hero(envs, '2026-10-17T01:00:00Z', home)
    assert '<fieldset' not in html and '<script' not in html
    assert 'id="coalition-explorer"' in html
    assert {p.name for p in out.glob('*.mjs')} == {
        'allocator.mjs', 'electorates.mjs', 'night.mjs', 'night-live.mjs',
        'night-parser.mjs', 'night-seats.mjs'}


def test_tied_scenario_withholds_totals():
    polls = [dict(id='p', revision='1', fieldwork_end='2026-10-17', shares=dict(a=5000,b=5000,others=0), scale=100)]
    average = trend(polls, ['2026-10-17'])[0]
    seats = project(average)
    seats['assumptions']['electorate_wins'] = {}
    data = c.inputs(average, seats, 'a' * 64)
    # The last available quotient ties at 239/239 versus 1/1.
    data['votes'] = {'a': '239', 'b': '1', 'others': '0'}
    state = data['initial']; state['counts']['b'] = '1'
    average['shares'] = {'a': 239, 'b': 1, 'others': 0}
    average['denominator'] = 240
    request = dict(average=average, seats=seats, fingerprint='a' * 64, state=state)
    r = evaluate([request])[0]['result']
    assert r['seats'] is None and r['selected_total'] is None and r['unresolved_ties']
    average['shares'] = {'a': 0, 'b': 0, 'others': 100}
    average['denominator'] = 100
    state['counts']['b'] = '0'
    assert evaluate([request])[0]['result']['seats'] is None
