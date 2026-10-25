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
    assert runner.tick() == 'unchanged' and clock.seconds == 300 and len(commits) == 2
    before = {p.relative_to(tmp_path): p.read_bytes() for p in (tmp_path / 'data').rglob('*') if p.is_file()}
    raw['e33/e33.xml'] = b'<broken>'
    assert runner.tick() == 'retained' and clock.seconds == 600
    assert before == {p.relative_to(tmp_path): p.read_bytes() for p in (tmp_path / 'data').rglob('*') if p.is_file()}
    assert len(commits) == 2
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
    assert 'workflow_dispatch:' in text and 'schedule:' in text
    from product.nz_election.tests.test_workflows import workflow
    triggers = workflow('nz-election-night-live.yml')[True]
    assert set(triggers) == {'workflow_dispatch', 'schedule'}
    assert triggers['schedule'] == [{'cron': '2 6 7 11 *'}, {'cron': '7 6 7 11 *'}]
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


def test_live_dom_resume_fetches_synchronously():
    result = subprocess.run(['node', '--input-type=module', '-e', '''
import assert from 'node:assert/strict';
let now = Date.parse('2026-11-07T06:01:00Z');
Date.now = () => now;
const listeners = {}, intervals = [], requests = [];
const target = {dataset:{}, querySelector:()=>null, querySelectorAll:()=>[]};
const notice = {textContent:''}, controls = {hidden:false};
globalThis.location = {href:'https://example.test/unattended/nz-election/night/'};
globalThis.document = {
  hidden:false, activeElement:null,
  querySelector:s=>({'#night-snapshot':target,'#night-live-status':notice,'#night-controls':controls}[s]),
  querySelectorAll:()=>[], addEventListener:(name,fn)=>{listeners[name]=fn}
};
globalThis.setInterval = fn => intervals.push(fn);
globalThis.fetch = url => {
  requests.push({url:String(url), at:now, hidden:document.hidden});
  return Promise.resolve({ok:true,json:async()=>({available:true,mode:'Live preliminary results',
    retrieved_at:'2026-11-07T06:00:00Z',reference_version:'a'.repeat(64),html:'<p>Result</p>'})});
};
await import('./product/nz_election/web/night-live.mjs');
await new Promise(resolve=>setImmediate(resolve));
assert.equal(requests.length,1);
document.hidden=true; listeners.visibilitychange();
for (let i=0;i<120;i++) {now+=1000; intervals.forEach(fn=>fn());}
assert.equal(requests.length,1);
document.hidden=false; listeners.visibilitychange();
// The real DOM handler must invoke fetch before returning, without firing a timer.
assert.equal(requests.length,2);
assert.deepEqual(requests[1],{url:requests[0].url,at:now,hidden:false});
await new Promise(resolve=>setImmediate(resolve));
now+=1000; intervals.forEach(fn=>fn());
assert.equal(requests.length,2);
'''], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_restart_recovers_published_but_undeployed_data(tmp_path, monkeypatch):
    from datetime import datetime
    from types import SimpleNamespace
    import sys
    clock = Clock()
    captured = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
    published_sha, deployed_sha = 'a'*40, 'b'*40
    dispatches = []
    class InjectedDateTime(datetime):
        @classmethod
        def now(cls, zone=None):
            return clock.now()
    def acquire_cycle(**kwargs):
        clock.seconds = 18001
        return captured
    def run(command, **kwargs):
        if 'publish.py' in ' '.join(command):
            return SimpleNamespace(stdout=json.dumps(dict(outcome='unchanged', sha=published_sha)))
        if 'pages.yml' in command:
            dispatches.append(command)
        return SimpleNamespace(returncode=0)
    def output(command, **kwargs):
        if 'api' in command:
            return json.dumps([dict(ref='refs/heads/data', object=dict(sha=published_sha))]).encode()
        key = dispatches[-1][-1].removeprefix('night_cycle=')
        return json.dumps([dict(displayTitle=key, status='completed', conclusion='success')]).encode()
    monkeypatch.setattr(night_live, 'datetime', InjectedDateTime)
    monkeypatch.setattr(night_live.time, 'monotonic', clock.monotonic)
    monkeypatch.setattr(night_live.time, 'sleep', clock.sleep)
    monkeypatch.setattr(night_live, 'cycle', acquire_cycle)
    monkeypatch.setattr(night_live.subprocess, 'run', run)
    monkeypatch.setattr(night_live.subprocess, 'check_output', output)
    monkeypatch.setattr(night_live.fetch, 'deployed_data_sha', lambda: deployed_sha, raising=False)
    for key, value in dict(GITHUB_SERVER_URL='https://github.com', GITHUB_REPOSITORY='example/test', GITHUB_RUN_ID='successor', GITHUB_SHA='c'*40).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, 'argv', ['night_live.py'])
    night_live.main()
    assert len(dispatches) == 1, 'restart must deploy the durable pending data even when publication is unchanged'
    assert 'data_sha=' + published_sha in dispatches[0]


def test_unchanged_acquisition_advances_published_freshness(tmp_path):
    from product.nz_election.pipeline.night_page import live_package
    clock, raw = Clock(), captures()
    remote, bundle = tmp_path / 'remote.git', tmp_path / 'bundle'
    subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
    packages = []
    def commit(captured):
        daily_refresh(bundle, loaders={'night': lambda: night_live.loaded(captured)}, now=captured['retrieved_at'])
        publish.publish(bundle, remote, family='night', now=lambda: night_live.stamp(clock.now))
        envs = {}
        for stem in ('night/index', 'night/references/live', 'night/live/current'):
            envs[stem] = json.loads(subprocess.check_output(['git', '--git-dir', str(remote), 'show', 'data:product/nz_election/data/' + stem + '.json']))
        packages.append(live_package(envs))
    runner = night_live.Runner(acquire=raw.__getitem__, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commit)
    assert [runner.tick() for _ in range(4)] == ['changed', 'unchanged', 'unchanged', 'unchanged']
    assert packages[-1]['retrieved_at'] == '2026-11-07T06:15:00Z'
    assert [p['retrieved_at'] for p in packages] == ['2026-11-07T06:00:00Z', '2026-11-07T06:05:00Z', '2026-11-07T06:10:00Z', '2026-11-07T06:15:00Z']
    js("time=OPEN+STALE;pack.retrieved_at=" + json.dumps(packages[-1]['retrieved_at']) + ";await live.tick();assert.doesNotMatch(texts.at(-1),/Stale/);")


def test_deployment_failure_retries_from_durable_state(monkeypatch):
    clock, dispatches = Clock(), []
    head, served = 'a'*40, ['b'*40]
    fail = [True]
    monkeypatch.setenv('GITHUB_REPOSITORY', 'example/test')
    monkeypatch.setenv('GITHUB_RUN_ID', 'recovery')
    monkeypatch.setattr(night_live.fetch, 'deployed_data_sha', lambda: served[0])
    monkeypatch.setattr(night_live.subprocess, 'run', lambda command, **kwargs: dispatches.append(command))
    def output(command, **kwargs):
        if 'api' in command:
            return json.dumps([dict(ref='refs/heads/data', object=dict(sha=head))]).encode()
        if not fail[0]:
            served[0] = head
        return json.dumps([dict(displayTitle=dispatches[-1][-1].removeprefix('night_cycle='),
                                status='completed', conclusion='failure' if fail[0] else 'success')]).encode()
    monkeypatch.setattr(night_live.subprocess, 'check_output', output)
    with pytest.raises(OSError, match='PAGES_DEPLOYMENT_FAILED'):
        night_live.Deployment(clock.now).recover()
    fail[0] = False
    assert night_live.Deployment(clock.now).recover() is True
    assert len(dispatches) == 2
    assert night_live.Deployment(clock.now).recover() is False
    assert len(dispatches) == 2


def test_served_manifest_requires_valid_bounded_evidence():
    from io import BytesIO
    from product.nz_election.pipeline import fetch
    class Response(BytesIO):
        status = 200
    for payload, expected in (({'data': {'data_sha': 'a'*40}}, 'a'*40),
                              ({'data': {'data_sha': None}}, None),
                              ({'data': {'data_sha': 'bad'}}, None), ([], None)):
        def transport(request, *, timeout):
            assert timeout == 20
            assert request.full_url.startswith('https://byronxlg.github.io/unattended/nz-election/build-manifest.json?reconcile=')
            assert request.get_header('Cache-control') == 'no-cache'
            return Response(json.dumps(payload).encode())
        assert fetch.deployed_data_sha(transport) == expected
    assert fetch.deployed_data_sha(lambda *a, **k: Response(b'x'*(fetch.LIMIT+1))) is None


def test_recovery_uses_one_cycle_without_acquiring_or_faking_freshness():
    clock = Clock()
    recoveries = iter([True, False])
    acquisitions = []
    def acquire(path):
        acquisitions.append(path)
        raise OSError('upstream unavailable')
    runner = night_live.Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic,
                              sleep=clock.sleep, commit=lambda _: pytest.fail('failed acquisition published'),
                              recover=lambda: next(recoveries))
    assert runner.tick() == 'recovered'
    assert not acquisitions and runner.last_good is None
    assert runner.tick() == 'retained'
    assert clock.seconds == 300 and runner.last_good is None


@pytest.mark.parametrize('instant', [
    '2026-11-06T10:29:59Z', '2026-11-07T05:59:59Z',
    '2026-11-08T06:00:00Z', '2026-11-08T06:00:01Z', '2027-11-07T06:02:00Z',
])
@pytest.mark.parametrize('rehearsal', [False, True])
def test_scheduled_outside_window_does_nothing(monkeypatch, instant, rehearsal):
    from datetime import datetime
    import sys
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'schedule')
    monkeypatch.setattr(sys, 'argv', ['night_live.py'] + (['--rehearsal'] if rehearsal else []))
    def forbidden(*args, **kwargs):
        pytest.fail('closed scheduled run performed external work')
    monkeypatch.setattr(night_live.fetch, 'night_xml', forbidden)
    monkeypatch.setattr(night_live.subprocess, 'run', forbidden)
    monkeypatch.setattr(night_live.subprocess, 'check_output', forbidden)
    assert night_live.main(now=lambda: datetime.fromisoformat(instant)) == 0


def test_scheduled_open_acquires_production(monkeypatch):
    from datetime import datetime
    import sys
    class Acquired(BaseException):
        pass
    calls = []
    def acquire(root, path):
        calls.append((root, path))
        raise Acquired
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'schedule')
    for key in ('GITHUB_SERVER_URL', 'GITHUB_REPOSITORY', 'GITHUB_RUN_ID'):
        monkeypatch.setenv(key, 'test')
    monkeypatch.setattr(sys, 'argv', ['night_live.py', '--rehearsal'])
    monkeypatch.setattr(night_live.Deployment, 'recover', lambda _: False)
    monkeypatch.setattr(night_live.fetch, 'night_xml', acquire)
    with pytest.raises(Acquired):
        night_live.main(now=lambda: datetime.fromisoformat('2026-11-07T06:02:00Z'))
    assert calls == [(night_live.fetch.NIGHT_ROOTS[0], 'electorates.xml')]


@pytest.mark.parametrize('instant,eligible', [
    ('2026-11-07T05:59:59Z', False), ('2026-11-07T06:00:00Z', False),
    ('2026-11-07T06:09:59Z', False), ('2026-11-07T06:10:00Z', True),
    ('2026-11-08T05:59:59Z', True), ('2026-11-08T06:00:00Z', False),
    ('2027-11-07T06:10:00Z', False),
])
def test_night_watchdog_window(monkeypatch, instant, eligible):
    from datetime import datetime
    from product.nz_election.pipeline import night_start
    calls = []
    def output(*args, **kwargs):
        calls.append(args)
        return b'[]'
    monkeypatch.setattr(night_start.subprocess, 'check_output', output)
    assert (night_start.main(lambda: datetime.fromisoformat(instant)) == 0) == eligible
    assert bool(calls) == eligible


@pytest.mark.parametrize('status,created,expected', [
    ('completed', '2026-11-07T05:59:59Z', True),
    ('completed', '2026-11-07T06:00:00Z', False),
    ('completed', '2026-11-07T06:02:00Z', False),
    ('queued', '2026-11-07T05:59:59Z', False),
    ('in_progress', '2026-11-07T05:59:59Z', False),
    ('waiting', '2026-11-07T05:59:59Z', False),
])
def test_night_watchdog_run_history(status, created, expected):
    from datetime import datetime
    from product.nz_election.pipeline.night_start import should_start
    now = lambda: datetime.fromisoformat('2026-11-07T06:10:00Z')
    assert should_start(now, [dict(status=status, createdAt=created)]) == expected


def test_night_watchdog_query_failure_is_not_permission(monkeypatch):
    from datetime import datetime
    from product.nz_election.pipeline import night_start
    def failed(*args, **kwargs):
        raise subprocess.CalledProcessError(1, 'gh')
    monkeypatch.setattr(night_start.subprocess, 'check_output', failed)
    assert night_start.main(lambda: datetime.fromisoformat('2026-11-07T06:10:00Z')) == 1


def test_tick_wires_watchdog_before_supervisor_skip():
    source = (ROOT / 'bin/tick').read_text()
    assert 'python3 bin/night-watchdog "$STATE"' in source
    wrapper = (ROOT / 'bin/night-watchdog').read_text()
    assert "['uv', 'run', 'product/nz_election/pipeline/night_start.py', '--dispatch']" in wrapper
    assert source.index('|| night_watchdog') < source.index('# 1. a supervisor already running?')


def test_live_loop_stops_at_close_without_chaining(monkeypatch):
    from datetime import datetime
    import sys
    instant = [datetime.fromisoformat('2026-11-08T05:59:59Z')]
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'schedule')
    for key in ('GITHUB_SERVER_URL', 'GITHUB_REPOSITORY', 'GITHUB_RUN_ID'):
        monkeypatch.setenv(key, 'test')
    monkeypatch.setattr(sys, 'argv', ['night_live.py'])
    def tick(_):
        instant[0] = night_live.CLOSE
        return 'retained'
    monkeypatch.setattr(night_live.Runner, 'tick', tick)
    monkeypatch.setattr(night_live.subprocess, 'run', lambda *a, **k: pytest.fail('chained after close'))
    assert night_live.main(now=lambda: instant[0]) == 0


def watchdog_command(state, worker, timeout=2):
    import sys
    code = ("import runpy; from pathlib import Path; "
            "m = runpy.run_path('bin/night-watchdog'); "
            f"m['watchdog'](Path({str(state)!r}), command={worker!r}, timeout={timeout!r}); "
            "print('tick continued', flush=True)")
    return [sys.executable, '-c', code]


@pytest.mark.parametrize('stage', ['startup', 'eligibility', 'dispatch'])
def test_watchdog_bounds_whole_operation(tmp_path, stage):
    import sys
    import time
    # Startup models uv blocking before the worker can apply any per-command timeout.
    code = "import subprocess, sys; subprocess.run([sys.executable, '-c', 'import time; time.sleep(30)'])"
    if stage != 'startup':
        code = f"""
import time
from datetime import datetime
from product.nz_election.pipeline import night_start
night_start.subprocess.check_output = lambda *a, **k: {'time.sleep(30)' if stage == 'eligibility' else "b'[]'"}
night_start.subprocess.run = lambda *a, **k: time.sleep(30)
night_start.main(lambda: datetime.fromisoformat('2026-11-07T06:10:00Z'), dispatch=True)
"""
    started = time.monotonic()
    result = subprocess.run(watchdog_command(tmp_path, [sys.executable, '-c', code], .5),
                            cwd=ROOT, capture_output=True, text=True, timeout=5)
    assert time.monotonic() - started < 3
    assert result.returncode == 0
    assert 'timed out; continuing tick' in result.stdout
    assert 'tick continued' in result.stdout
    assert not (tmp_path / 'night-start-2026.dispatched').exists()
    # A later invocation can acquire the same lock after timeout.
    retry = subprocess.run(watchdog_command(tmp_path, [sys.executable, '-c', 'pass']),
                           cwd=ROOT, capture_output=True, text=True, timeout=5)
    assert 'dispatched' in retry.stdout


def test_watchdog_serializes_and_marker_covers_visibility_lag(tmp_path):
    import sys
    import time
    entered = tmp_path / 'entered'
    calls = tmp_path / 'dispatches'
    worker = [sys.executable, '-c', f"""
import time
from pathlib import Path
from datetime import datetime
from product.nz_election.pipeline import night_start

def output(*args, **kwargs):
    Path({str(entered)!r}).touch()
    time.sleep(.5)
    return b'[]'

def dispatch(*args, **kwargs):
    with Path({str(calls)!r}).open('a') as f:
        f.write('dispatch\\n')

night_start.subprocess.check_output = output
night_start.subprocess.run = dispatch
raise SystemExit(night_start.main(lambda: datetime.fromisoformat('2026-11-07T06:10:00Z'), dispatch=True))
"""]
    command = watchdog_command(tmp_path, worker)
    first = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 3
        while not entered.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        assert entered.exists()
        second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=3)
        assert second.returncode == 0 and 'dispatched' not in second.stdout
        stdout, stderr = first.communicate(timeout=3)
        assert first.returncode == 0, stderr
        assert 'dispatched' in stdout
        # GitHub still returns [], but the durable marker blocks a sequential retry too.
        third = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=3)
        assert third.returncode == 0 and 'dispatched' not in third.stdout
        assert calls.read_text() == 'dispatch\n'
        assert (tmp_path / 'night-start-2026.dispatched').exists()
    finally:
        if first.poll() is None:
            first.kill()
        first.wait()


def test_watchdog_rechecks_close_immediately_before_dispatch(monkeypatch):
    from datetime import datetime
    from product.nz_election.pipeline import night_start
    instants = iter(['2026-11-08T05:59:59Z', '2026-11-08T05:59:59Z', '2026-11-08T06:00:00Z'])
    monkeypatch.setattr(night_start.subprocess, 'check_output', lambda *a, **k: b'[]')
    monkeypatch.setattr(night_start.subprocess, 'run', lambda *a, **k: pytest.fail('dispatched after close'))
    assert night_start.main(lambda: datetime.fromisoformat(next(instants)), dispatch=True) == 1
