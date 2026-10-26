"""Offline regressions for the deployed rehearsal's evidence and synthetic transitions."""
import json
import subprocess
from types import SimpleNamespace

import pytest

from product.nz_election.pipeline import export, night
from product.nz_election.tests import night_deployed as deployed


def test_synthetic_transition_packages():
    from product.nz_election.tests.night_live_browser import transition_packages
    before = night.load()
    cases = transition_packages()
    assert night.load() == before, 'Synthetic frames must never enter the historical replay'
    assert cases['old'] != cases['new']
    assert cases['initial']['reference_version'] == cases['leader']['reference_version']
    assert cases['complete']['reference_version'] != cases['leader']['reference_version']
    assert cases['incomplete']['reference_version'] == cases['complete']['reference_version']
    assert cases['incomplete']['available'] is False and 'html' not in cases['incomplete']
    for key in ('initial', 'leader', 'complete'):
        assert 'Synthetic transition: offline verification' in cases[key]['html']
        assert 'night-waterfall' in cases[key]['html']
    assert cases['renamed'] in cases['complete']['html']
    # Execute the actual client with injected time/transport, with no sockets.
    result = subprocess.run(['node', '--input-type=module', '-e', '''
import assert from 'node:assert/strict';
import {NightLive, OPEN} from './product/nz_election/web/night-live.mjs';
let input=''; for await (const chunk of process.stdin) input += chunk;
const cases=JSON.parse(input), rendered=[];
let pack=cases.initial, time=OPEN+60000;
const live=new NightLive({now:()=>time, fetcher:async()=>({ok:true,json:async()=>pack}),
  render:p=>rendered.push(p)});
await live.tick(); assert.deepEqual(live.last,cases.initial);
pack=cases.leader; time+=125000; await live.tick();
assert.deepEqual(live.last,cases.leader);
pack=cases.incomplete; time+=125000; await live.tick();
assert.deepEqual(live.last,cases.leader); assert.equal(rendered.length,2);
pack=cases.complete; time+=125000; await live.tick();
assert.deepEqual(live.last,cases.complete); assert.equal(rendered.length,3);
console.log('PASS synthetic leader and reference transitions');
'''], input=json.dumps(cases), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'PASS synthetic' in result.stdout


@pytest.mark.parametrize('broken', [None, 'csv', 'provenance', 'waterfall', 'source-links', 'places', 'tables'])
def test_rehearsal_populated_evidence(tmp_path, broken):
    payloads, sources, hashes = night.load()
    row = payloads['night/illustrative-2023/step-2'][0]
    env = export.envelope([row], sources, 'offline-verification', 'a'*40,
                          inputs=hashes, method='night-v2', generated='2026-11-03T00:00:00Z')
    if broken == 'provenance':
        env['source'] = []
    urls = ['https://site.example/data/night/illustrative-2023/step-2.' + ext for ext in ('json', 'csv')]
    links = [dict(text=label, url=url) for label, url in zip(
        ('Snapshot JSON', 'CSV', 'Official results', 'Electoral Act s197'),
        urls + ['https://www.electionresults.govt.nz/', 'https://www.legislation.govt.nz/'])]
    class Locator:
        def locator(self, selector):
            return LocatorFor(selector)
        def inner_text(self):
            return 'Results cover 100 percent of ' + ('votes counted' if broken == 'places' else 'voting places')
    class LocatorFor(Locator):
        def __init__(self, selector):
            self.selector = selector
        def is_visible(self):
            return broken != 'waterfall'
        def inner_text(self):
            return 'Calculated occupied House: 122'
        def count(self):
            return 0 if broken == 'tables' else 72 if 'tbody' in self.selector else 3
        def evaluate_all(self, script):
            return [] if broken == 'source-links' else links
    def evaluate(script, url):
        return dict(status=200, body=json.dumps(env) if url.endswith('.json') else
                    'broken' if broken == 'csv' else export.csv_bytes(env).decode())
    page = SimpleNamespace(locator=lambda selector: Locator(), evaluate=evaluate)
    record = deployed.Record('rehearse', 'https://site.example/', tmp_path)
    deployed.populated_evidence(page, record)
    assert record.write()[1] is (broken is not None)
    if broken is None:
        assert (record.out / 'replay-export.json').is_file()
        assert (record.out / 'replay-export.csv').read_bytes() == export.csv_bytes(env)


@pytest.mark.parametrize('replacement', [b'<invalid>', b'', 'wrong-electorate', 'negative-votes'])
def test_selected_detail_probe_rejects_invalid(monkeypatch, tmp_path, replacement):
    from product.nz_election.tests import test_night_deployed as contract
    captured = contract.national_captures()
    if replacement == 'wrong-electorate':
        raw = captured['e01/e01.xml'].replace(b'e_no="1"', b'e_no="2"')
    elif replacement == 'negative-votes':
        raw = captured['e01/e01.xml'].replace(b'<votes>0</votes>', b'<votes>-1</votes>', 1)
    else:
        raw = replacement
    assert raw != captured['e01/e01.xml']
    captured['e01/e01.xml'] = raw
    monkeypatch.setattr(contract, 'national_captures', lambda: captured)
    checks, record = contract.probe_evidence(monkeypatch, tmp_path, 'readable')
    detail = next(check for check in checks if check['check'] == 'cors-evidence-e01/e01.xml')
    assert detail['status'] == 'FAIL'
    assert record.write()[1]
