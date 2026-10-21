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
    assert all(tag not in html for tag in ('<figure', '<table', '<progress', '<script'))
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
    assert 'electorate_results' not in html and '<svg' not in html
    assert html.count('<template ') == 5


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
