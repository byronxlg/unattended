"""Cross-runtime state rejection and exact conditional seat contracts."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

import pytest
from product.nz_election.pipeline import coalitions as c, export
from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.build import build, strip
from product.nz_election.pipeline.fixtures import golden
from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.seats import project
from product.nz_election.pipeline.scripts import validate_scripts

RUNNER = Path(__file__).with_name('coalitions_runner.mjs')


@pytest.fixture
def request_data(tmp_path):
    refresh(tmp_path / 'data', now='2026-10-17T01:00:00Z', end_date='2026-07-18')
    envs = export.validate_bundle(tmp_path / 'data')
    return dict(average=envs['averages']['data'][-1], seats=envs['seats']['data'], fingerprint='a' * 64)


def parity(requests):
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
    actual = subprocess.run(['node', str(RUNNER)], input=json.dumps(requests), text=True, capture_output=True, check=True).stdout
    assert actual == export.canonical(expected)
    return expected


def test_scenario_python_js_parity(request_data):
    data = c.inputs(**request_data)
    requests = [request_data]
    for party in data['parties']:
        for n in ('0', '1', '6', '71'):
            state = deepcopy(data['initial'])
            state['selected'] = [party]
            state['counts'] = {p: n if p == party else '0' for p in data['parties']}
            requests.append(dict(request_data, state=state))
    parity(requests)


def test_unknown_capacity_stays_conditional(request_data):
    r = parity([request_data])[0]['result']
    assert r['occupied_house'] is r['vacancies'] is r['majority'] is None
    assert r['capacity_checked'] is False
    assert r['assumed_majority'] == r['assumed_house'] // 2 + 1


def test_no_preselected_coalition(request_data):
    data = c.inputs(**request_data)
    assert data['initial']['selected'] == [] and 'others' not in data['parties']
    r = c.scenario(data, data['initial'])
    assert r['selected_total'] == 0
    assert r['unassigned_electorates'] == 71 - sum(request_data['seats']['assumptions']['electorate_wins'].values())


def test_invalid_state_error_parity(request_data):
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
    results = parity([dict(op='decode', hash=h, parties=parties) for h in hashes])
    assert all(r == {'error': c.ERROR} for r in results)
    assert all(r == {'error': c.ERROR} for r in parity([dict(request_data, state=s) for s in [None, {}, [], '', 1, True]]))


def test_hash_round_trip(request_data):
    data = c.inputs(**request_data)
    state = data['initial']
    assert parity([dict(op='decode', hash=c.encode(state), parties=data['parties'])])[0]['result'] == state


def test_fingerprint_mismatch_warns(request_data):
    state = c.inputs(**request_data)['initial']
    state['fingerprint'] = 'b' * 64
    assert parity([dict(request_data, state=state)])[0]['result'] == {'warning': 'INPUT_FINGERPRINT_MISMATCH', 'applied': False}


def test_incomplete_average_disables_explorer(request_data):
    requests = []
    for field, value in [('coherent', False), ('missing', [{'party_id': 'nat'}]), ('denominator', 0)]:
        r = deepcopy(request_data); r['average'][field] = value; requests.append(r)
    r = deepcopy(request_data); r['seats']['average_id'] = 'wrong'; requests.append(r)
    r = deepcopy(request_data); r['average']['shares'].pop('nat'); requests.append(r)
    r = deepcopy(request_data); r['average']['descriptive']['nat']['poll_ids'].pop(); requests.append(r)
    r = deepcopy(request_data); r['average']['shares']['nat'] = None; requests.append(r)
    assert all(r == {'error': 'INCOMPLETE_COALITION_INPUT'} for r in parity(requests))


def test_overhang(request_data):
    data = c.inputs(**request_data)
    state = deepcopy(data['initial'])
    state['counts'] = {p: '71' if p == 'tpm' else '0' for p in data['parties']}
    r = parity([dict(request_data, state=state)])[0]['result']
    assert r['overhang'] > 0 and r['assumed_house'] == 120 + r['overhang']


def test_real_candidate_vacancies():
    source = golden()['input']
    source['lists'] = {p: list(ws) for p, ws in source['electorateWinners'].items() if ws}
    r = allocate(source)
    assert r['vacancies'] > 0 and r['occupiedHouse'] == 120 + r['overhang'] - r['vacancies']
    runner = RUNNER.with_name('allocator_runner.mjs')
    actual = subprocess.run(['node', str(runner)], input=json.dumps([source]), capture_output=True, text=True, check=True)
    assert json.loads(actual.stdout) == [{'result': r}]


def test_script_allowlist():
    assert validate_scripts('<script type="module" src="/unattended/nz-election/coalitions.mjs"></script>')
    for html in ['<script>alert(1)</script>', '<script type="module" src="https://example.com/coalitions.mjs"></script>',
                 '<script type="module" src="/unattended/nz-election/coalitions.mjs">alert(1)</script>',
                 '<script type="module" src="/unattended/nz-election/other.mjs"></script>',
                 '<script type="module" src="//evil/coalitions.mjs"></script>',
                 '<script type="module" src="/unattended/nz-election/coalitions.mjs" onload="x"></script>']:
        with pytest.raises(ValueError, match='UNSAFE_SCRIPT'):
            validate_scripts(html)


def test_static_content_preserved(tmp_path, request_data):
    out = build(tmp_path / 'data', tmp_path / 'output', built='2026-10-17T01:00:00Z')
    html = (out / 'polls/index.html').read_text()
    from product.nz_election.pipeline.build import home_presentation
    home = home_presentation(export.validate_bundle(tmp_path / 'data'), '2026-10-17T01:00:00Z')
    from product.nz_election.pipeline.markup import open_prose
    assert open_prose(strip(request_data['seats'], home['source'])) in html
    assert '<fieldset hidden disabled>' in html and 'requires JavaScript' in html
    assert 'source-seats' in html and 'data-select="others"' not in html
    assert 'data-select="nat" checked' not in html


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
    r = parity([request])[0]['result']
    assert r['seats'] is None and r['selected_total'] is None and r['unresolved_ties']
    average['shares'] = {'a': 0, 'b': 0, 'others': 100}
    average['denominator'] = 100
    state['counts']['b'] = '0'
    assert parity([request])[0]['result']['seats'] is None
