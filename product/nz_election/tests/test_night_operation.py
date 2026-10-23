"""Injected Actions transport and clock, publication and browser scheduler proofs."""
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import subprocess
import pytest
from product.nz_election.pipeline import night_live, night, export, publish, social
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.deployment_guard import require_publication_allowed
from product.nz_election.tests.night_live_cases import Clock, captures

ROOT = Path(__file__).resolve().parents[3]


def test_live_serial_poll_budget(tmp_path):
    clock, raw, calls, commits = Clock(), captures(), [], []
    from io import BytesIO
    from product.nz_election.pipeline import fetch
    class Response(BytesIO):
        status = 200
        headers = {}
    def transport(request, *, timeout):
        path = request.full_url.removeprefix(fetch.NIGHT_ROOTS[0])
        calls.append((clock.seconds, path))
        return Response(raw[path])
    def acquire(path):
        return fetch.night_xml(fetch.NIGHT_ROOTS[0], path, transport=transport, now=clock.now, sleep=clock.sleep)
    def commit(value):
        daily_refresh(tmp_path / 'data', loaders={'night': lambda: night_live.loaded(value)}, now=value['retrieved_at'])
        commits.append(value)
    runner = night_live.Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commit)
    assert runner.tick() == 'changed'
    assert [p for _, p in calls] == list(night_live.REFERENCES) + ['election.xml'] + [f'e{i:02}/e{i:02}.xml' for i in range(1, 72)] + list(night_live.REFERENCES)
    assert all(d['leader'] is None and d['status'] == 'not yet reported' for d in commits[0]['result']['leaders'].values())
    before = {p.relative_to(tmp_path): p.read_bytes() for p in (tmp_path / 'data').rglob('*') if p.is_file()}
    assert runner.tick() == 'unchanged' and clock.seconds == 300 and len(commits) == 1
    raw['e33/e33.xml'] = b'<broken>'
    assert runner.tick() == 'retained' and clock.seconds == 600
    assert before == {p.relative_to(tmp_path): p.read_bytes() for p in (tmp_path / 'data').rglob('*') if p.is_file()}
    assert len(commits) == 1
    export.validate_bundle(tmp_path / 'data')


def test_live_reference_change_atomicity():
    raw, clock, commits = captures(), Clock(), []
    count = 0
    def acquire(path):
        nonlocal count
        count += 1
        return raw[path] + (b' ' if count > 75 else b'')
    runner = night_live.Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commits.append)
    assert runner.tick() == 'retained' and not commits
    raw = captures(demo=True)
    runner = night_live.Runner(acquire=raw.__getitem__, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commits.append, rehearsal=True)
    assert runner.tick() == 'changed'
    first = commits[-1]['result']['valid_party_votes']
    raw.update(captures(demo=True, observation=2))
    assert runner.tick() == 'changed'
    assert commits[-1]['result']['valid_party_votes'] != first


def js(case):
    result = subprocess.run(['node', '--input-type=module', '-e', '''
import assert from 'node:assert/strict';
import {NightLive, OPEN, FLOOR, STALE} from './product/nz_election/web/night-live.mjs';
let time=OPEN, visible=true, calls=0, texts=[], rendered=[];
const pack={available:true, mode:'Live preliminary results', retrieved_at:new Date(OPEN).toISOString(), html:'<p>Validated result</p>', reference_version:'a'.repeat(64)};
let fetcher=async()=>{calls++;return {ok:true,json:async()=>pack}};
const live=new NightLive({fetcher:()=>fetcher(),now:()=>time,visible:()=>visible,render:p=>rendered.push(p),status:t=>texts.push(t)});
''' + case], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_live_visibility_and_selection_races():
    js('''
let resolve;
fetcher=()=>{calls++;return new Promise(r=>resolve=r)};
const pending=live.tick();
await live.tick(); assert.equal(calls,1);
visible=false; live.invalidate();
resolve({ok:true,json:async()=>pack}); await pending;
assert.equal(rendered.length,0);
visible=true; await live.tick(); assert.equal(calls,1);
time+=FLOOR; fetcher=async()=>{calls++;return {ok:true,json:async()=>pack}};
await live.tick(); assert.equal(calls,2); assert.equal(rendered.length,1);
''')


def test_live_backoff_and_stale_snapshot():
    js('''
await live.tick(); time+=FLOOR;
fetcher=async()=>{calls++;throw Error('Actions unavailable')};
await live.tick(); time+=FLOOR; await live.tick(); assert.equal(calls,2);
time=OPEN+STALE; await live.tick(); assert.match(texts.at(-1),/Stale/);
assert.equal(rendered.length,1); assert.equal(live.last,pack);
''')


def test_live_cors_waf_packaged_fallback():
    clock, raw, commits = Clock(), captures(), []
    runner = night_live.Runner(acquire=raw.__getitem__, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commits.append)
    assert runner.tick() == 'changed'
    runner.acquire = lambda _: b'<html>upstream WAF response</html>'
    assert runner.tick() == 'retained' and len(commits) == 1
    assert runner.last_good is commits[0]
    # A successful package fetch can still serve stale bytes after Actions acquisition fails.
    js('await live.tick(); time=OPEN+STALE; await live.tick(); assert.match(texts.at(-1),/Stale/);')
    js('''
fetcher=async()=>{calls++;return {ok:false,headers:{get:()=>"300"}}};
await live.tick(); assert.match(texts.at(-1),/dated packaged snapshot/);
time+=4*FLOOR; await live.tick(); assert.equal(calls,1);
time+=FLOOR; fetcher=async()=>{calls++;return {ok:true,json:async()=>pack}};
await live.tick(); assert.equal(live.last,pack);
''')


def test_browser_export_provenance(tmp_path):
    from product.nz_election.pipeline.night_page import live_package
    clock, raw = Clock(), captures()
    captured = night_live.cycle(acquire=raw.__getitem__, now=clock.now)
    night.prepare(tmp_path, night_live.loaded(captured), 'https://github.com/example/actions/runs/1', 'a'*40, captured['retrieved_at'])
    envs = {p.relative_to(tmp_path).as_posix()[:-5]: json.loads(p.read_text()) for p in tmp_path.rglob('*.json')}
    pack = live_package(envs)
    assert pack['provenance']['label'] == 'Packaged by the site'
    assert pack['provenance']['retrieved_at'] == '2026-11-07T06:00:00Z'
    assert any(s['url'] == 'https://media.election.net.nz/xml/e71/e71.xml' for s in pack['provenance']['sources'])
    assert pack['json_path'] == 'data/night/live/current.json'
    broken = deepcopy(captured)
    broken['result']['valid_party_votes'] = 20
    # Validation derives results from raw XML rather than trusting the transport's parsed copy.
    assert night_live.loaded(broken)[0]['night/live/current'][0]['valid_party_votes'] == 0
    row = envs['night/live/current']['data'][0]
    row['leaders']['1']['leader'] = '1'
    with pytest.raises(ValueError, match='NIGHT_LIVE'):
        night_live.validate_row(row, envs['night/live/current'], envs['night/references/live']['data'][0])


def test_freeze_all_publication_paths(tmp_path):
    # This assertion fails on base 0a94cba: social leaves the 23:30 safety margin open.
    assert social.frozen('2026-11-06T10:30:00Z')
    for instant in ('2026-11-06T10:30:00Z', '2026-11-06T23:00:00Z', '2026-11-07T05:59:59Z'):
        for family in ('hourly', 'daily', 'social', 'night'):
            with pytest.raises(ValueError, match='PUBLICATION_FROZEN'):
                publish.publish(tmp_path / 'missing', tmp_path / 'remote', family=family, now=lambda: instant)
        with pytest.raises(ValueError, match='PUBLICATION_FROZEN'):
            require_publication_allowed(instant)
    for instant in ('2026-11-06T10:29:59Z', '2026-11-07T06:00:00Z'):
        require_publication_allowed(instant)
    for name in ('hourly', 'daily', 'social-daily'):
        workflow = (ROOT / f'.github/workflows/nz-election-{name}.yml').read_text()
        assert workflow.count('deployment_guard.py') == workflow.count('uses: astral-sh/setup-uv')
    pages = (ROOT / '.github/workflows/pages.yml').read_text()
    assert pages.index('Preserve current publication guard') < pages.index('ref: ${{ inputs.code_sha }}')
    deploy = pages.split('  deploy:', 1)[1]
    assert deploy.index('deployment_guard.py') < deploy.index('actions/deploy-pages')


def test_live_opens_at_poll_close():
    clock = Clock()
    clock.origin -= timedelta(seconds=1)
    with pytest.raises(ValueError, match='PUBLICATION_FROZEN'):
        night_live.cycle(acquire=lambda _: pytest.fail('pre-close fetch'), now=clock.now)
    clock.origin -= timedelta(days=1)
    with pytest.raises(ValueError, match='NIGHT_NOT_OPEN'):
        night_live.cycle(acquire=lambda _: pytest.fail('early fetch'), now=clock.now)
    clock = Clock()
    night_live.require_open(clock.now)
    js('''time=OPEN-1; await live.tick(); assert.equal(calls,0);
time=OPEN; await live.tick(); assert.equal(calls,1);''')


def test_live_atomic_data_commit_and_queued_freeze(tmp_path):
    clock, raw = Clock(), captures()
    captured = night_live.cycle(acquire=raw.__getitem__, now=clock.now)
    bundle, remote = tmp_path / 'bundle', tmp_path / 'remote.git'
    subprocess.run(['git','init','--bare','-q',str(remote)],check=True)
    daily_refresh(bundle, loaders={'night': lambda: night_live.loaded(captured)}, now=captured['retrieved_at'])
    result = publish.publish(bundle, remote, family='night', now=lambda: '2026-11-07T06:00:00Z')
    assert result['outcome'] == 'published'
    tree = subprocess.check_output(['git','--git-dir',str(remote),'ls-tree','-r','--name-only','data'],text=True).splitlines()
    assert 'product/nz_election/data/night/live/current.json' in tree
    assert 'product/nz_election/data/night/references/live.json' in tree
    before = subprocess.check_output(['git','--git-dir',str(remote),'rev-parse','data'])
    assert publish.publish(bundle, remote, family='night', now=lambda: '2026-11-07T06:00:00Z')['outcome'] == 'unchanged'
    assert subprocess.check_output(['git','--git-dir',str(remote),'rev-parse','data']) == before
    # A poll job collected before the freeze must be checked again after a queued push.
    from product.nz_election.pipeline.refresh import refresh
    poll = tmp_path / 'poll'
    refresh(poll, now='2026-11-06T10:29:00Z')
    instant = ['2026-11-06T10:29:59Z']
    with pytest.raises(ValueError, match='PUBLICATION_FROZEN'):
        publish.publish(poll, remote, now=lambda: instant[0], before_push=lambda _: instant.__setitem__(0,'2026-11-06T10:30:00Z'))
    assert subprocess.check_output(['git','--git-dir',str(remote),'rev-parse','data']) == before


def test_live_workflow_contract():
    text = (ROOT / '.github/workflows/nz-election-night-live.yml').read_text()
    assert 'workflow_dispatch:' in text and 'schedule:' not in text
    assert 'cancel-in-progress: false' in text and 'timeout-minutes: 350' in text
    assert 'secrets.' not in text
    assert 'inputs.rehearsal && always()' in text
    source = (ROOT / 'product/nz_election/pipeline/night_live.py').read_text()
    assert "'nz-election-night-live.yml'" in source and '300 * 60' in source


def test_live_http_bounds_and_retry_after():
    from io import BytesIO
    from urllib.error import HTTPError
    from product.nz_election.pipeline import fetch
    clock, requests = Clock(), []
    class Response(BytesIO):
        status = 200
        headers = {}
    def transport(request, *, timeout):
        assert timeout == 20
        requests.append(request.full_url)
        if len(requests) == 1:
            raise HTTPError(request.full_url, 429, 'test', {'Retry-After':'3'}, None)
        return Response(b'<captured/>')
    assert fetch.night_xml(fetch.NIGHT_ROOTS[0], 'e71/e71.xml', transport=transport, now=clock.now, sleep=clock.sleep) == b'<captured/>'
    assert clock.seconds == 3 and len(requests) == 2
    assert fetch.night_xml(fetch.NIGHT_ROOTS[1], 'e72/e72.xml', transport=lambda *a, **k: Response(b'demo-72')) == b'demo-72'
    for path in ('../election.xml','e72/e72.xml','e01/e02.xml','e00/e00.xml','https://other/election.xml'):
        with pytest.raises(ValueError, match='UNAPPROVED_SOURCE'):
            fetch.night_xml(fetch.NIGHT_ROOTS[0], path, transport=lambda *a, **k: pytest.fail('unapproved fetch'))
    with pytest.raises(ValueError, match='RESPONSE_TOO_LARGE'):
        fetch.night_xml(fetch.NIGHT_ROOTS[0], 'election.xml', transport=lambda *a, **k: Response(b'x'*2_000_001))


def test_rehearsal_cli_artifacts_only(tmp_path, monkeypatch):
    from datetime import datetime
    import sys
    clock = Clock()
    clock.origin -= timedelta(days=15)
    class InjectedDateTime(datetime):
        @classmethod
        def now(cls, zone=None):
            return clock.now()
    first, second = captures(demo=True), captures(demo=True, observation=2)
    monkeypatch.setattr(night_live, 'datetime', InjectedDateTime)
    monkeypatch.setattr(night_live.time, 'monotonic', clock.monotonic)
    monkeypatch.setattr(night_live.time, 'sleep', clock.sleep)
    monkeypatch.setattr(night_live.fetch, 'night_xml', lambda root, path: (first if clock.seconds < 300 else second)[path])
    monkeypatch.setattr(night_live.subprocess, 'run', lambda *a, **k: pytest.fail('rehearsal attempted remote publication or chaining'))
    for key, value in dict(GITHUB_SERVER_URL='https://github.com', GITHUB_REPOSITORY='example/test', GITHUB_RUN_ID='123', GITHUB_SHA='a'*40).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, 'argv', ['night_live.py', '--rehearsal', '--out', str(tmp_path)])
    night_live.main()
    bundles = sorted(p for p in tmp_path.iterdir() if p.is_dir())
    assert len(bundles) == 2
    rows = [export.validate_bundle(p)['night/live/current']['data'][0] for p in bundles]
    assert all(row['rehearsal'] and row['mode'] == 'Recorded demo' for row in rows)
    assert rows[0]['valid_party_votes'] != rows[1]['valid_party_votes']
