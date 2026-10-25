"""Post-night packages retain a dated baseline and stop client requests."""
import subprocess
from pathlib import Path


def test_settled_client_stops_polling():
    module = (Path(__file__).parents[1] / 'web/night-live.mjs').resolve().as_uri()
    script = '''import {NightLive, OPEN, FLOOR} from MODULE;
import assert from 'node:assert/strict';
let now=OPEN+86400000, calls=0, rendered=0, notice='';
const live=new NightLive({now:()=>now, fetcher:async()=>{
 calls++; return {ok:true,json:async()=>({available:true,mode:'Settled preliminary results',
 retrieved_at:new Date(OPEN+3600000).toISOString(),reference_version:'a'.repeat(64),
 state_sentence:'Preliminary results; live updates ended. Official results due 27 November.',html:'retained'})};
},render:()=>rendered++,status:t=>notice=t});
await live.tick(); now+=FLOOR*100; await live.tick();
assert.equal(rendered,1); assert.equal(calls,1); assert.match(notice,/live updates ended/);
assert.doesNotMatch(notice,/Stale/);
'''.replace('MODULE', repr(module))
    subprocess.run(['node', '--input-type=module', '-e', script], check=True)

import json
from copy import deepcopy
import pytest
from product.nz_election.pipeline import export, fixtures, night, night_live, result_states
from product.nz_election.pipeline.night_page import page, live_package
from product.nz_election.pipeline.home import night_summary


def capture(state):
    name = 'result-states/2026-11-' + ('07-preliminary-final' if state == 'preliminary' else '27-official') + '.json'
    return json.loads(fixtures.captures(paths={name})[name])


def prepare(tmp_path, loaded, now):
    night.prepare(tmp_path, loaded, 'offline-verification', 'a'*40, now)
    return {p.relative_to(tmp_path).as_posix()[:-5]: json.loads(p.read_text()) for p in tmp_path.rglob('*.json')}


@pytest.fixture
def live(tmp_path):
    return prepare(tmp_path / 'live', night_live.loaded(capture('preliminary')), '2026-11-07T10:35:00Z')


def test_live_settled_official_and_pinned_baseline(tmp_path, live):
    original = deepcopy(live['night/live/current'])
    settled = prepare(tmp_path / 'settled', result_states.transition(live, 'settled', now='2026-11-08T06:00:00Z'), '2026-11-08T06:00:00Z')
    official = prepare(tmp_path / 'official', result_states.transition(settled, 'official', now='2026-11-27T11:00:00Z', captured=capture('official')), '2026-11-27T11:00:00Z')
    for envs, mode in [(live, night_live.MODE), (settled, result_states.SETTLED), (official, result_states.OFFICIAL)]:
        assert live_package(envs)['mode'] == mode
        assert mode in night_summary(envs, '2026-11-28T00:00:00Z') or 'live updates ended' in night_summary(envs, '2026-11-28T00:00:00Z')
        html = page(envs, '2026-11-28T00:00:00Z')
        if envs is not live:
            assert envs['night/live/current']['data'][0]['preliminary_package'] == original
            assert 'Stale:' not in html
        assert ('Change since preliminary result' in html) == (envs is official)
        assert 'Special votes' not in html
    assert '7 November 23:30' in page(settled, '2026-11-28T00:00:00Z')
    assert 'official results due' not in page(official, '2026-11-28T00:00:00Z')
    assert live['night/live/current'] == original


def test_absent_feed_cannot_be_settled():
    assert live_package({}) == {'available': False}
    with pytest.raises(ValueError, match='NIGHT_BASELINE'):
        result_states.transition({}, 'settled', now='2026-11-08T06:00:00Z')


def test_state_order_and_reference_compatibility(tmp_path, live):
    with pytest.raises(ValueError, match='NIGHT_NOT_SETTLED'):
        result_states.transition(live, 'settled', now='2026-11-07T11:00:00Z')
    with pytest.raises(ValueError, match='NIGHT_STATE'):
        result_states.transition(live, 'official', now='2026-11-27T11:00:00Z', captured=capture('official'))
    settled = prepare(tmp_path / 'settled', result_states.transition(live, 'settled', now='2026-11-08T06:00:00Z'), '2026-11-08T06:00:00Z')
    changed = capture('official')
    changed['raw']['parties.xml'] = changed['raw']['parties.xml'].replace('<short_name>', '<short_name>Changed ', 1)
    with pytest.raises(ValueError, match='NIGHT_LIVE'):
        result_states.transition(settled, 'official', now='2026-11-27T11:00:00Z', captured=changed)
    damaged = deepcopy(settled['night/live/current']['data'][0])
    damaged['preliminary_package']['data'][0]['valid_party_votes'] += 1
    with pytest.raises(ValueError):
        result_states.validate(damaged, settled['night/live/current'], settled['night/references/live']['data'][0])


def test_late_live_publication_does_not_reopen_settled(tmp_path):
    from product.nz_election.pipeline import publish
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    live_data, settled_data, remote = (tmp_path / name for name in ['live', 'settled', 'remote.git'])
    raw = capture('preliminary')
    daily_refresh(live_data, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'])
    original = export.validate_bundle(live_data)
    settled = result_states.transition(original, 'settled', now='2026-11-08T06:00:00Z')
    daily_refresh(settled_data, loaders={'night': lambda: settled}, now='2026-11-08T06:00:00Z')
    subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
    publish.publish(settled_data, remote, family='night', now=lambda: '2026-11-08T06:00:00Z')
    raw['retrieved_at'] = '2026-11-08T05:59:00Z'
    daily_refresh(live_data, loaders={'night': lambda: night_live.loaded(raw)}, now='2026-11-08T06:01:00Z')
    publish.publish(live_data, remote, family='night', now=lambda: '2026-11-08T06:01:00Z')
    current = json.loads(subprocess.check_output(['git', '--git-dir', str(remote), 'show', 'data:product/nz_election/data/night/live/current.json']))
    assert current['data'][0]['result_state'] == 'settled'
    assert current['data'][0]['preliminary_package'] == original['night/live/current']


def test_result_states_browser(tmp_path):
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('result_states_browser.py')), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS result states browser: 8 images' in result.stdout


@pytest.mark.parametrize('fault', ['early', 'future', 'partial', 'malformed'])
def test_official_rejects_bad_capture_without_changing_baseline(tmp_path, live, fault):
    settled = prepare(tmp_path / 'settled', result_states.transition(live, 'settled', now='2026-11-08T06:00:00Z'), '2026-11-08T06:00:00Z')
    original = deepcopy(settled)
    raw = capture('official')
    if fault == 'early':
        raw['retrieved_at'] = '2026-11-25T10:35:00Z'
    elif fault == 'future':
        raw['retrieved_at'] = '2026-11-28T10:35:00Z'
    elif fault == 'partial':
        del raw['raw']['e71/e71.xml']
    else:
        raw['raw']['election.xml'] = '<broken>'
    with pytest.raises(ValueError):
        result_states.transition(settled, 'official', now='2026-11-27T11:00:00Z', captured=raw)
    assert settled == original


def test_client_live_to_terminal_states():
    from product.nz_election.tests.test_night_operation import js
    for mode in (result_states.SETTLED, result_states.OFFICIAL):
        js('''
await live.tick(); assert.equal(calls,1);
time+=FLOOR;
const terminal={...pack,mode:MODE,state_sentence:'A dated terminal result.'};
fetcher=async()=>{calls++;return {ok:true,json:async()=>terminal}};
await live.tick(); assert.equal(calls,2); assert.equal(rendered.length,2);
time+=STALE*10; visible=false; live.invalidate(); await live.tick();
visible=true; await live.tick(); assert.equal(calls,2);
assert.equal(texts.at(-1),'A dated terminal result.');
'''.replace('MODE', json.dumps(mode)))
