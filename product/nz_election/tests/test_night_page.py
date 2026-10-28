"""Page checks supplement the immutable night-family contract."""
import pytest
import subprocess
from pathlib import Path
from product.nz_election.pipeline.night_page import page
from product.nz_election.tests.design_checks import provenance


def test_absent_night_page():
    html = page({}, '2026-10-21T00:00:00Z')
    assert '17 days until election day' in html
    assert '/vote/' in html and 'https://www.electionresults.govt.nz/' in html
    provenance(html)


def test_replay_clock_pause_reset():
    module = (Path(__file__).parents[1] / 'web/night.mjs').resolve().as_uri()
    script = '''import {ReplayClock} from MODULE;
import assert from 'node:assert/strict';
let now=0;const c=new ReplayClock([0,300,600],()=>now);
now=100000;assert.equal(c.tick(),0);c.play();now+=1000;assert.equal(c.tick(),0);assert.equal(c.elapsed,1);
c.rate(10);now+=1000;c.tick();assert.equal(c.elapsed,11);
c.pause();now+=90000;c.tick();assert.equal(c.elapsed,11);
c.rate(60);c.play();now+=5000;assert.equal(c.tick(),1);
c.reset();assert.equal(c.elapsed,0);assert.equal(c.running,false);c.play();now+=10000;assert.equal(c.tick(),2);assert.equal(c.running,false);
'''.replace('MODULE', repr(module))
    subprocess.run(['node', '--input-type=module', '-e', script], check=True)


@pytest.fixture(scope="module")
def browser_checks(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("night-browser")
    result = subprocess.run(['uv', 'run', 'product/nz_election/tests/night_browser.py', str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS night browser' in result.stdout
    return result.stdout


def test_xml_python_browser_parity(browser_checks):
    assert 'XML parity' in browser_checks


def test_replay_makes_no_official_feed_request(browser_checks):
    assert 'no official-feed requests' in browser_checks


def test_populated_night_has_backed_results_and_sources():
    from product.nz_election.pipeline.night import load
    from product.nz_election.pipeline.landmark_checks import check_page
    from product.nz_election.pipeline.m3_checks import check_night_markup
    payloads, _, _ = load()
    envs = {key: {'data': rows} for key, rows in payloads.items()}
    html = page(envs, '2026-10-21T00:00:00Z')
    check_page(html)
    check_night_markup(html, envs)
    assert 'House 122' in html and '2,851,211' in html
    assert '62 for a majority' in html
    assert 'These combinations currently reach a majority; government formation is separate.' in html
    assert 'votes counted' not in html
    from product.nz_election.pipeline.content_checks import Tree
    assert any(n.attrs.get('role') == 'group' and 'Electorate provisional leaders' in n.attrs.get('aria-label', '')
               for n in Tree(html).nodes)
    assert 'Electorate provisional leaders' in html
    assert html.count('<template ') == 6


def test_xml_scalar_python_node_parity():
    import json
    from product.nz_election.pipeline import xml_parser
    module = (Path(__file__).parents[1] / 'web/night-parser.mjs').resolve().as_uri()
    values = ['', None, [], {}, True, False, 1.5, 10**100, '１', ' 1', '01', '1e3', '-1',
              '1000000000', '0', '999999999', '100.00', '100.01', '0.01', '1.001', '1\n', '1\r', '1\u2028', '1\u2029']
    script = '''import * as parser from MODULE;
let raw='';for await(const chunk of process.stdin)raw+=chunk;
const values=JSON.parse(raw);
console.log(JSON.stringify(['count','percent'].map(name=>values.map(v=>{
try{return parser[name](v)}catch(e){return e.message}
}))));'''.replace('MODULE', repr(module))
    actual = json.loads(subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps(values), capture_output=True, text=True, check=True).stdout)
    expected = []
    for fn in (xml_parser.count, xml_parser.percent):
        rows = []
        for value in values:
            try:
                rows.append(fn(value))
            except ValueError as exc:
                rows.append(str(exc))
        expected.append(rows)
    assert actual == expected


def test_replay_scheduler_endpoint():
    subprocess.run(['node', '--test', '--test-reporter=tap',
                    str(Path(__file__).with_name('night_scheduler.test.mjs'))], check=True)


@pytest.mark.parametrize('host_installed', [False, True])
def test_browser_launch_uses_playwright_default_without_host_binary(tmp_path, monkeypatch, host_installed):
    from types import SimpleNamespace
    from product.nz_election.tests.night_browser import launch_chromium
    executable = tmp_path / 'Library/Caches/ms-playwright/chromium_headless_shell-123/chrome-headless-shell-mac-arm64/chrome-headless-shell'
    if host_installed:
        executable.parent.mkdir(parents=True)
        executable.touch()
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path))
    calls = []
    pw = SimpleNamespace(chromium=SimpleNamespace(launch=lambda **kwargs: calls.append(kwargs)))
    launch_chromium(pw)
    assert calls == ([{'executable_path': str(executable)}] if host_installed else [{}])


@pytest.fixture
def night_envs():
    from product.nz_election.pipeline.night import load
    payloads, _, _ = load()
    return {key: {'data': rows} for key, rows in payloads.items()}


@pytest.mark.parametrize('populated', [False, True])
@pytest.mark.parametrize('built,before', [('2026-11-05T00:00:00Z', True),
                                        ('2026-11-07T05:59:59Z', True),
                                        ('2026-11-07T06:00:00Z', False),
                                        ('2026-11-07T06:00:01Z', False)])
def test_night_phase_uses_build_time(night_envs, populated, built, before):
    html = page(night_envs if populated else {}, built)
    assert ('class="countdown"' in html) == before
    assert ('href="/unattended/nz-election/vote/"' in html) == before
    if before and populated:
        assert html.index('class="countdown"') < html.index('/vote/') < html.index('id="night-controls"') < html.index('id="night-snapshot"')


def test_replay_frames_explain_coverage_without_inventing_data(night_envs):
    from product.nz_election.pipeline.content_checks import Tree
    from product.nz_election.pipeline.m3_checks import check_night_markup
    html = page(night_envs, '2026-11-05T00:00:00Z')
    check_night_markup(html, night_envs)
    tree = Tree(html)
    replay = next(n for n in tree.nodes if n.tag == 'template' and n.attrs['id'] == 'sequence-illustrative-2023')
    frames = [n for n in replay.children[0].children if not isinstance(n, str) and 'data-frame' in n.attrs]
    for index, frame in enumerate(frames):
        context = next(n for n in frame.children if not isinstance(n, str) and n.attrs.get('class') == 'night-frame-context')
        assert f'Replay frame {index+1} of 3, {index*5}:00 elapsed.' in context.text
        if index < 2:
            assert 'voting-place coverage and seats are published only in the final archive' in context.text
            assert 'Results cover' not in frame.text and 'House 122' not in frame.text
        else:
            assert 'Final archive updated' not in context.text
            assert 'House 122' in frame.text and '2,851,211' in frame.text


@pytest.mark.parametrize('phrase', ['not available', 'not reported', 'pending', 'withheld', 'missing', 'not supplied', 'unavailable'])
def test_night_presence_rejects_placeholder_text(night_envs, phrase):
    from product.nz_election.pipeline.m3_checks import check_night_markup
    html = page(night_envs, '2026-11-05T00:00:00Z')
    check_night_markup(html, night_envs)
    with pytest.raises(ValueError, match='ABSENT_TEXT'):
        check_night_markup(html + '<p>' + phrase + '</p>', night_envs)


def test_elapsed_clock_is_not_live(night_envs):
    from product.nz_election.tests.design_checks import Document
    nodes = {a.get('id'): (tag, a) for tag, a in Document(page(night_envs, '2026-11-05T00:00:00Z')).nodes if a.get('id')}
    tag, clock = nodes['night-clock']
    assert tag == 'span' and clock['aria-live'] == 'off'
    assert 'role' not in clock
    _, announcement = nodes['night-announcement']
    assert announcement['role'] == 'status' and announcement['aria-live'] == 'polite'


def test_nested_numeric_element_uses_xml_count():
    import re
    from product.nz_election.pipeline import fixtures, xml_parser
    prefix = 'ec-2023-xml/'
    paths = [prefix + name + '.xml' for name in ('parties', 'electorates', 'candidates', 'election')]
    raw = fixtures.captures(paths=set(paths))
    refs = xml_parser.references(*(raw[p] for p in paths[:3]))
    malformed = re.sub(rb'<votes>.*?</votes>', b'<votes><x>1</x></votes>', raw[paths[3]], count=1)
    with pytest.raises(ValueError, match='^XML_COUNT$'):
        xml_parser.election(malformed, refs)


FREEZE_NOTICE = 'No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197.'
FREEZE_LAW = 'https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM310065.html'


@pytest.mark.parametrize('populated', [False, True])
@pytest.mark.parametrize('built', ['2026-11-05T00:00:00Z', '2026-11-07T06:00:00Z'])
def test_active_night_build_preserves_publication_freeze(tmp_path, populated, built):
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline import night
    from product.nz_election.pipeline.content_checks import Tree
    data = tmp_path / 'data'
    if populated:
        daily_refresh(data, loaders={'night': night.load})
    site = build(data, tmp_path / 'site/nz-election', built=built)
    tree = Tree((site / 'night/index.html').read_text())
    frames = [n for n in tree.nodes if 'data-frame' in n.attrs]
    assert bool(frames) == populated
    night_sources = [n for n in tree.nodes if n.attrs.get('id') == 'source-night']
    for frame in frames:
        notes = [n for n in frame.children if not isinstance(n, str) and n.attrs.get('class') == 'source-note']
        assert len(notes) == 1
        night_sources.extend(notes)
    assert night_sources, 'Active night renderer must supply a source note'
    for note in night_sources:
        assert FREEZE_NOTICE in note.text
        links = {link.attrs.get('href') for child in note.children
                 if not isinstance(child, str) and child.tag == 'p' and child.attrs.get('class') == 'source-actions'
                 for link in child.children if not isinstance(link, str) and link.tag == 'a'}
        assert FREEZE_LAW in links
        assert 'https://www.electionresults.govt.nz/' in links


@pytest.mark.parametrize('removed', [FREEZE_NOTICE, FREEZE_LAW])
def test_route_gate_independently_requires_night_publication_freeze(tmp_path, monkeypatch, removed):
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline import night_page
    from product.nz_election.pipeline.route_checks import check_site
    built = '2026-11-05T00:00:00Z'
    site = build(tmp_path / 'absent', tmp_path / 'site/nz-election', built=built)
    path = site / 'night/index.html'
    path.write_text(path.read_text().replace(removed, ''))
    original = night_page.page
    monkeypatch.setattr(night_page, 'page', lambda envs, built: original(envs, built).replace(removed, ''))
    with pytest.raises(ValueError, match='night publication freeze notice'):
        check_site(site, {})



def test_night_seat_graphic_uses_source_totals_and_tokens(night_envs):
    from product.nz_election.pipeline.night_page import snapshot
    from product.nz_election.pipeline.content_checks import Tree
    seq = next(s for s in night_envs['night/index']['data'] if s['id'] == '2023')
    row = night_envs[seq['snapshot_paths'][0][:-5]]['data'][0]
    refs = night_envs[seq['reference_path'][:-5]]['data'][0]
    html = snapshot(row, refs, 'proof', seq['snapshot_paths'][0])
    tree = Tree(html)
    assert 'Who is winning?' in tree.root.text and 'Replay of 2023' in tree.root.text
    assert sum(n.tag == 'circle' for n in tree.nodes) == row['reported_house']
    assert 'Majority reached' in tree.root.text
    assert 'Electorate provisional leaders' in tree.root.text
    assert all('var(--' in n.attrs['style'] for n in tree.nodes
               if n.tag in {'circle', 'polygon'} and 'style' in n.attrs)


@pytest.mark.parametrize('raw,expected', [('SMITH, Jane', 'Jane Smith'),
                                        ('MĀORI, Hēmi', 'Hēmi Māori'),
                                        ('Jane McDonald', 'Jane McDonald')])
def test_night_display_names(raw, expected):
    from product.nz_election.pipeline.night_electorates import display_name
    assert display_name(raw) == expected


@pytest.mark.parametrize('sequence', ['2017', '2020', '2023', 'illustrative-2023'])
def test_night_replay_reporting_identifies_final_count_not_update_clock(night_envs, sequence):
    import re
    from product.nz_election.pipeline.night_page import snapshot
    from product.nz_election.pipeline.content_checks import Tree
    seq = next(s for s in night_envs['night/index']['data'] if s['id'] == sequence)
    refs = night_envs[seq['reference_path'][:-5]]['data'][0]
    for frame, path in enumerate(seq['snapshot_paths'], 1):
        row = night_envs[path[:-5]]['data'][0]
        text = Tree(snapshot(row, refs, 'proof', path, frame, len(seq['snapshot_paths']))).root.text
        assert not re.search(r'updated\s+\d{1,2}:\d{2}', text, re.I)
        if row.get('statistics'):
            assert f"{refs['id']} final count" in text
            if 'elapsed_seconds' in row:
                assert f'frame {frame} of {len(seq["snapshot_paths"])}' in text


@pytest.mark.parametrize('built,expected', [
    ('2026-11-07T06:01:00Z', 'Waiting for the first complete results.'),
    ('2026-11-08T06:01:00Z', 'Live updates ended.'),
])
def test_empty_night_status(built, expected):
    from product.nz_election.pipeline.content_checks import Tree
    tree = Tree(page({}, built))
    assert expected in tree.root.text
    assert 'dated packaged snapshot' not in tree.root.text
    assert any(n.tag == 'a' and n.attrs.get('href') == 'https://www.electionresults.govt.nz/'
               and 'Official Electoral Commission results' in n.text for n in tree.nodes)


def test_empty_night_first_capture_and_cutoff(tmp_path):
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('night_empty_browser.py')), str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS empty night browser' in result.stdout


def test_empty_night_polling_status_and_cutoff():
    import json
    from product.nz_election.pipeline.sunsets import NIGHT_CLOSE
    from product.nz_election.pipeline.result_states import live_status
    module = (Path(__file__).parents[1] / 'web/night-live.mjs').resolve().as_uri()
    stop = NIGHT_CLOSE.isoformat()
    ended = live_status(stop, '', has_snapshot=False)
    script = '''import {NightLive} from MODULE;
import assert from 'node:assert/strict';
const stop = Date.parse(STOP);
let now = stop - 300000, requests = [], rendered = [], status, response = {ok:false};
const live = new NightLive({loopEndsAt:STOP, now:()=>now,
  status:text=>status=text, render:pack=>rendered.push(pack),
  fetcher:async()=>{requests.push(now);return response;}});
await live.tick(); assert.equal(requests.length, 1);
response = {ok:true,json:async()=>({available:false,loop_ended:false,loop_ends_at:STOP})};
now += 120000; await live.tick(); assert.equal(rendered.length,0);
const pack = {available:true,mode:'Live preliminary results',retrieved_at:new Date(now).toISOString(),
 reference_version:'a'.repeat(64),html:'<p>Offline verification: 123 valid party votes</p>',
 loop_ended:false,loop_ends_at:STOP};
response = {ok:true,json:async()=>pack}; now += 60000; await live.tick();
assert.deepEqual(rendered,[pack]); assert.equal(requests.length,3);
for (const delta of [0,1,60000,3600000]) {
 now = stop + delta; await live.tick(); assert.equal(requests.length,3);
 assert.match(status,/Live updates ended/);
}
const empty = new NightLive({loopEndsAt:STOP,now:()=>now,
 status:text=>status=text,fetcher:()=>assert.fail('request after cutoff')});
await empty.tick(); assert.equal(status, ENDED);
'''.replace('MODULE', repr(module)).replace('STOP', json.dumps(stop)).replace('ENDED', json.dumps(ended))
    subprocess.run(['node', '--input-type=module', '-e', script], check=True)


def test_night_replay_does_not_present_archive_maintenance_as_count_date(night_envs):
    from product.nz_election.pipeline.content_checks import Tree
    tree = Tree(page(night_envs, '2026-10-28T00:00:00Z'))
    for sequence in ('2023', 'illustrative-2023'):
        replay = next(n for n in tree.nodes if n.attrs.get('id') == 'sequence-' + sequence)
        assert '2024' not in replay.text
        assert 'Results last updated' not in replay.text
        assert 'Final archive updated' not in replay.text
    source = next(r for env in night_envs.values() for r in env['data']
                  if r.get('mode') == 'Final snapshot' and 'ec-2023-xml/election.xml' in r.get('source_ref', []))
    assert source['source_updated_local'] == '2024-11-10T00:00:00'


def test_night_live_retains_real_update_time(night_envs):
    from copy import deepcopy
    from product.nz_election.pipeline.night_page import snapshot
    row = deepcopy(next(r for env in night_envs.values() for r in env['data']
                        if r.get('mode') == 'Final snapshot' and 'ec-2023-xml/election.xml' in r.get('source_ref', [])))
    row.update(mode='Live preliminary results', source_updated_local='2026-11-07T20:30:00')
    refs = night_envs['night/references/2023']['data'][0]
    html = snapshot(row, refs, 'live', 'night/live/current.json')
    assert 'Results last updated 7 November 2026 at 20:30.' in html
    assert 'updated 20:30' in html


def test_night_replay_retains_source_date_from_election_year(night_envs):
    from copy import deepcopy
    from product.nz_election.pipeline.night_page import snapshot
    row = deepcopy(next(r for env in night_envs.values() for r in env['data']
                        if r.get('mode') == 'Final snapshot' and 'ec-2023-xml/election.xml' in r.get('source_ref', [])))
    row['source_updated_local'] = '2023-11-03T14:00:00'
    refs = night_envs['night/references/2023']['data'][0]
    assert 'Results last updated 3 November 2023 at 14:00.' in snapshot(row, refs, '2023', 'night/2023/final.json')
