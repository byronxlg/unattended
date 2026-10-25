"""The page supplies the deadline even when no package request succeeds."""
from datetime import timedelta
import json
from pathlib import Path
import re
import subprocess

import pytest

from product.nz_election.pipeline import night, night_live, night_page
from product.nz_election.tests.night_live_cases import Clock

ROOT = Path(__file__).resolve().parents[3]


def run_js(script):
    result = subprocess.run(['node', '--input-type=module', '-e', script],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_constructor_knows_deadline_before_first_tick():
    deadline = night_live.stamp(lambda: night_live.CLOSE)
    run_js("""
import assert from 'node:assert/strict';
import {NightLive} from './product/nz_election/web/night-live.mjs';
const deadline = """ + json.dumps(deadline) + """;
let calls = 0, notice = '';
const live = new NightLive({loopEndsAt:deadline, now:()=>Date.parse(deadline),
  fetcher:async()=>{calls++; throw Error('offline')}, status:text=>notice=text});
await live.tick();
assert.equal(calls, 0);
assert.match(notice, /Live updates ended/);
""")


@pytest.mark.parametrize('scenario', ['first_visit', 'offline_resume', 'failures'])
def test_dom_deadline_needs_no_successful_response(scenario):
    deadline = night_live.stamp(lambda: night_live.CLOSE)
    run_js("""
import assert from 'node:assert/strict';
const deadline = Date.parse(""" + json.dumps(deadline) + """);
const scenario = """ + json.dumps(scenario) + """;
let now = scenario === 'first_visit' ? deadline + 1 : deadline - 1000;
Date.now = () => now;
const listeners = {}, intervals = [], requests = [];
const target = {dataset:{loopEndsAt:new Date(deadline).toISOString()},
  querySelector:()=>null, querySelectorAll:()=>[]};
const notice = {textContent:''};
globalThis.location = {href:'https://example.test/unattended/nz-election/night/'};
globalThis.document = {
  hidden:false, activeElement:null,
  querySelector:s=>({'#night-snapshot':target,'#night-live-status':notice}[s]),
  querySelectorAll:()=>[], addEventListener:(name,fn)=>{listeners[name]=fn}
};
globalThis.setInterval = fn => intervals.push(fn);
globalThis.fetch = async()=>{requests.push(now); throw Error('offline')};
await import('./product/nz_election/web/night-live.mjs');
await new Promise(resolve=>setImmediate(resolve));
assert.equal(requests.length, scenario === 'first_visit' ? 0 : 1);
if (scenario === 'offline_resume') {
  document.hidden = true; listeners.visibilitychange();
}
now = deadline + 20 * 60000;
if (scenario === 'offline_resume') {
  document.hidden = false; listeners.visibilitychange();
}
intervals.forEach(fn=>fn());
await new Promise(resolve=>setImmediate(resolve));
now += 20 * 60000;
intervals.forEach(fn=>fn());
await new Promise(resolve=>setImmediate(resolve));
assert.deepEqual(requests.filter(at=>at>=deadline), []);
assert.match(notice.textContent, /Live updates ended/);
assert.match(notice.textContent, /official results due 27 November/);
""")


def test_page_embeds_shared_cutoff(tmp_path, monkeypatch):
    clock = Clock()
    night.prepare(tmp_path, night.load(), 'offline-verification', 'a' * 40,
                  night_live.stamp(clock.now))
    envs = {p.relative_to(tmp_path).as_posix()[:-5]: json.loads(p.read_text())
            for p in tmp_path.rglob('*.json')}
    for cutoff in (night_live.CLOSE, night_live.CLOSE + timedelta(hours=1)):
        monkeypatch.setattr(night_live, 'CLOSE', cutoff)
        markup = night_page.page(envs, night_live.stamp(clock.now))
        embedded = re.search(r'id="night-snapshot"[^>]*data-loop-ends-at="([^"]+)"', markup)
        assert embedded is not None, 'night page omits the client cutoff'
        assert embedded.group(1) == night_live.stamp(lambda: cutoff)
