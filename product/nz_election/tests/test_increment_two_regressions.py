"""Regression cases from the increment-two CI failure and confirmed review."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
from html import unescape
import importlib
import json
from pathlib import Path
import re
import subprocess
import pytest
from product.nz_election.pipeline import export
from product.nz_election.pipeline.average import mean_vector, trend, threshold_watch, display, values
from product.nz_election.pipeline.build import build, downloads, label_lanes, polls_page, strip
from product.nz_election.pipeline.refresh import normalize, previous_parser_rows, refresh
from product.nz_election.pipeline.seats import project
from product.nz_election.tests.test_pipeline import make_bundle, repository, git, DATA, fail

publisher = importlib.import_module('product.nz_election.pipeline.publish')


def test_ci_incorrect_old_value_retries(tmp_path, monkeypatch):
    remote = repository(tmp_path, make_bundle(tmp_path))
    second, third = make_bundle(tmp_path, 2), make_bundle(tmp_path, 3)
    original = publisher.git
    injected = False
    rejection = ("remote: error: cannot lock ref 'refs/heads/data': is at <b0067> but expected <bbfe2>\n"
                 "! [remote rejected] HEAD -> data (incorrect old value provided)")
    def race(root, *args, **kwargs):
        nonlocal injected
        if args[0] == 'push' and not injected:
            injected = True
            publisher.publish(second, remote)
            return subprocess.CompletedProcess(args, 1, '', rejection)
        return original(root, *args, **kwargs)
    monkeypatch.setattr(publisher, 'git', race)
    result = publisher.publish(third, remote)
    assert result['outcome'] == 'published' and result['attempts'] == 2


def test_push_failure_without_ref_movement_is_fatal(tmp_path, monkeypatch):
    remote = repository(tmp_path, make_bundle(tmp_path))
    original = publisher.git
    def denied(root, *args, **kwargs):
        if args[0] == 'push':
            return subprocess.CompletedProcess(args, 1, '', '! [remote rejected] HEAD -> data (hook declined)')
        return original(root, *args, **kwargs)
    monkeypatch.setattr(publisher, 'git', denied)
    with pytest.raises(RuntimeError, match='PUBLICATION_FAILED'):
        publisher.publish(make_bundle(tmp_path, 2), remote)


def test_large_scale_never_rounds_into_qualification(tmp_path):
    scale = 10 ** 30
    row = dict(id='exact', revision='1', fieldwork_start='2026-10-17', fieldwork_end='2026-10-17',
               observed_at='2026-10-17', shares={'opp': 5 * scale - 1, 'others': 95 * scale + 1},
               scale=scale, source_ref=[], reference_urls=[], history=[], pollster='synthetic', sample=None)
    env = export.envelope([row], [], 'offline-verification', 'test')
    export.pair(tmp_path, 'polls', env)
    with localcontext() as context:
        context.prec = 6
        avg = mean_vector(json.loads((tmp_path / 'polls.json').read_text())['data'])
        assert avg['shares'] == row['shares'] and avg['scale'] == scale
        assert 100 * avg['shares']['opp'] < 5 * avg['denominator']
        assert values(row)['opp'] < 5
        assert normalize(row)['shares'] == row['shares']
        assert normalize(previous_parser_rows([row])[0])['shares'] == row['shares']
        assert display(avg['shares']['opp'], avg['scale']) == '5.0%'
    mixed = mean_vector([row, dict(row, id='other', shares={'opp': 4, 'others': 96}, scale=1)])
    assert mixed['shares']['opp'] == 9 * scale - 1 and mixed['scale'] == 2 * scale
    parsed = dict(row, shares={'opp': Decimal('4.999999999999999999999999999999'), 'others': Decimal('95.000000000000000000000000000001')})
    parsed.pop('scale')
    assert mean_vector([parsed]) == avg


def test_threshold_uses_only_average_ids_including_missing_coverage(tmp_path):
    envs = export.validate_bundle(make_bundle(tmp_path))
    polls = deepcopy(envs['polls']['data'][:3])
    for row, value in zip(polls, [9, 6, None]):
        row['fieldwork_start'] = row['fieldwork_end'] = '2026-10-17'
        row['scale'] = 1
        row['shares'] = {'nat': 91 if value else 100, 'opp': value, 'others': 0}
    review = {'exclusions': {p['id']: {'revision': p['revision'], 'reason': 'Synthetic review', 'review_ref': 'regression'} for p in polls[1:]}}
    avg = trend(polls, ['2026-10-17'], review=review)[0]
    assert threshold_watch(polls, avg, {'electorate_wins': {}}) == []
    envs['polls']['data'] = polls
    envs['averages']['data'] = [avg]
    envs['seats']['data'] = project(avg)
    html = polls_page(envs, '2026-10-17T01:00:00Z')
    assert '<h2>Which parties are near the 5 percent threshold?</h2>' not in html
    assert 'id="source-thresholds"' in html
    polls[0]['shares']['opp'], polls[1]['shares']['opp'] = 6, 9
    avg = trend(polls, ['2026-10-17'], review=review)[0]
    watched = threshold_watch(polls, avg, {'electorate_wins': {}})
    assert len(watched) == 1 and watched[0]['poll_ids'] == [polls[0]['id']]
    assert watched[0]['missing_poll_ids'] == []


def acquired_bundle(root, hour):
    path = make_bundle(root, hour)
    envs = export.validate_bundle(path)
    acquired = f'2026-10-17T{hour:02d}:00:00Z'
    for stem in ('polls', 'averages', 'seats'):
        env = envs[stem]
        env['run_url'] = 'success-' + str(hour)
        for source in env['source']:
            if source['id'] == 'P':
                source['fetched_at'] = acquired
        env['fetched_at'] = max(s['fetched_at'] for s in env['source'])
        if stem != 'polls':
            dependency = 'polls.json' if stem == 'averages' else 'averages.json'
            env['input_hashes'][dependency] = export.digest((path / dependency).read_bytes())
        export.pair(path, stem, env)
    status = envs['status']
    status['data'][0].update(last_success_at=acquired, last_good_run_url='success-' + str(hour))
    export.pair(path, 'status', status)
    export.inventory(path, status['run_url'], status['code_sha'], acquired)
    export.validate_bundle(path)
    return path


def test_later_failure_merges_status_without_replacing_newer_data(tmp_path):
    old = acquired_bundle(tmp_path, 1)
    current = acquired_bundle(tmp_path, 2)
    remote = repository(tmp_path, current)
    before = {name: git(remote, 'show', 'data:' + str(DATA / name)).stdout for name in publisher.OWNED}
    refresh(old, now='2026-10-17T03:00:00Z', parse=fail)
    assert publisher.publish(old, remote)['outcome'] == 'published'
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status['last_attempt_at'] == '2026-10-17T03:00:00Z'
    assert status['state'] == 'stale' and status['error_code'] == 'parse_drift'
    assert status['last_success_at'] == '2026-10-17T02:00:00Z'
    assert status['last_good_run_url'] == 'success-2'
    assert all(git(remote, 'show', 'data:' + str(DATA / name)).stdout == raw for name, raw in before.items())
    checkout = tmp_path / 'checkout'
    git(tmp_path, 'clone', '-q', '-b', 'data', str(remote), str(checkout))
    export.validate_bundle(checkout / DATA)


def test_blog_output_allowlist_preserves_every_sibling(tmp_path):
    site = tmp_path / 'site'
    for name in ('posts', 'about', 'data', 'metrics', 'new-blog-route'):
        target = site / name
        target.mkdir(parents=True)
        (target / 'keep.txt').write_text(name)
    (site / 'index.html').write_text('blog')
    before = {p: p.read_bytes() for p in site.rglob('*') if p.is_file()}
    for target in [site, *(site / name for name in ('posts', 'about', 'data', 'metrics', 'new-blog-route')), site / 'nz-election/methods']:
        with pytest.raises(ValueError, match='UNSAFE_OUTPUT_PATH'):
            build(tmp_path / 'absent', target)
    alias = tmp_path / 'alias'
    alias.symlink_to(site, target_is_directory=True)
    with pytest.raises(ValueError, match='UNSAFE_OUTPUT_PATH'):
        build(tmp_path / 'absent', alias / 'posts')
    outside = tmp_path / 'outside'
    outside.mkdir()
    (site / 'alias-outside').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='UNSAFE_OUTPUT_PATH'):
        build(tmp_path / 'absent', site / 'alias-outside/nested')
    assert not (outside / 'nested').exists()
    assert all(p.read_bytes() == raw for p, raw in before.items())
    build(tmp_path / 'absent', site / 'nz-election')
    assert all(p.read_bytes() == raw for p, raw in before.items())


def test_downloads_render_each_manifest_record_and_run(tmp_path):
    data = make_bundle(tmp_path)
    out = build(data, tmp_path / 'output')
    html = (out / 'downloads/index.html').read_text()
    entries = export.validate_bundle(data)['manifest']['data']
    for entry in entries:
        row = html.split(f'data-file="{entry["path"]}"')[1].split('</tr>')[0]
        for label in ('Rows', 'Retrieved (UTC)', 'Producing run'):
            assert '<dt>' + label + '</dt>' in row
        assert ('<dt>Licence</dt>' in row) is bool(entry['licences'])
        assert json.loads(unescape(row.split('<pre>')[1].split('</pre>')[0])) == entry
        for key in ('sha256', 'bytes', 'observation_start', 'observation_end', 'fetched_at'):
            assert str(entry[key]) in unescape(row) if entry[key] is not None else 'Not available' not in row
        for key, label in [('observation_start', 'Observation start'), ('observation_end', 'Observation end'), ('bytes', 'Size'), ('sha256', 'SHA-256')]:
            assert ('<dt>' + label + '</dt>' in row) is (entry[key] is not None)
    envs = export.validate_bundle(data)
    for entry in envs['manifest']['data']:
        entry['producing_run_url'] = 'https://github.com/example/repo/actions/runs/123'
    assert 'href="https://github.com/example/repo/actions/runs/123"' in downloads(envs, None)


def test_strip_labels_are_below_fills_in_reading_order():
    seats = {'seats': {'nat': 47, 'lab': 35, 'grn': 15, 'act': 10, 'nzf': 9, 'tpm': 6},
             'entitlements': {'nat': 47, 'lab': 35, 'grn': 15, 'act': 10, 'nzf': 9, 'tpm': 4},
             'assumed_house': 122, 'assumed_majority': 62, 'overhang': 2}
    html = strip(seats)
    lanes = re.findall(r'<div class="lane" role="group" data-party="([^"]+)"[^>]*>(.*?)</div>', html)
    assert [p for p, _ in lanes] == ['nat', 'act', 'nzf', 'lab', 'grn', 'tpm']
    for party, content in lanes:
        assert f'<strong>{seats["seats"][party]}</strong>' in content
        assert f'<span>{party.upper()}</span>' in content
    segments = re.findall(r'<div class="segment"[^>]*>(.*?)</div>', html)
    assert len(segments) == 6 and all(content == '' for content in segments)
    assert html.index('class="lanes"') > html.index('class="majority"')
    assert '62 for a majority' in html and 'segment overhang' in html
    # Independently calculate the reserved-label geometry and every connector.
    offset, expected_connectors = 0, []
    ordered = [p for p, _ in lanes]
    for width, mode, prop in [(328, 'phone', '--left'), (1072, 'wide', '--large-left')]:
        cursor, offset = 0, 0
        columns = 3 if mode == 'phone' else 6
        for index, party in enumerate(ordered):
            row = index // columns
            if index % columns == 0:
                cursor = 0
            anchor = Fraction(offset * 100, 122)
            left_px = min(max(cursor, float(anchor) * width / 100 if row == 0 else 0),
                          width - min(columns - index % columns, len(ordered) - index) * 68 + 8)
            left = left_px * 100 / width
            style = re.search(r'data-party="' + party + r'" style="(--row:[^"]+)"', html)[1]
            assert f'{prop}:{left:.6f}%' in style
            if mode == 'phone':
                assert f'--row:{row};' in style
            if abs(left - float(anchor)) > .01 or row:
                side = 'right' if anchor > left else 'left'
                expected_connectors.append((mode, f'left:{min(left, float(anchor)):.6f}%;width:{abs(left-float(anchor)):.6f}%;height:{6+row*21}px;border-{side}:1px solid var(--ink)'))
            cursor = left_px + 68
            offset += seats['seats'][party]
    actual_connectors = re.findall(r'class="label-connector (phone|wide)" aria-hidden="true" style="([^"]+)"', html)
    assert sorted(actual_connectors) == sorted(expected_connectors)
    widths = re.findall(r'class="segment" data-party="([^"]+)" style="width:([\d.]+)%', html)
    assert widths == [(p, f'{Decimal(seats["entitlements"][p])*100/122:.6f}') for p in ordered]
    assert f'class="majority" style="left:{Decimal(62)*100/122:.6f}%' in html

    css = (Path(__file__).resolve().parents[1] / 'web/styles.css').read_text()
    assert 'height:72px' in css and 'height:120px' in css
    assert 'border:1px solid var(--ink)' in css
    rows = label_lanes([(p, Fraction(90)) for p in seats['seats']], 288)
    assert set(rows.values()) == {0, 1}
    assert set(label_lanes([(p, Fraction(90)) for p in seats['seats']], 736).values()) == {0}
