"""Equal-acquisition publication and local-time download regressions for PR 10."""
import re
from html import unescape
import json

from product.nz_election.pipeline import export
from product.nz_election.pipeline.build import build, downloads, local_time
from product.nz_election.pipeline.publish import DATA, OWNED, publish
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.tests.test_pipeline import fail, git, repository


def test_equal_acquisition_keeps_latest_successful_generation(tmp_path):
    old, newer = tmp_path / 'old', tmp_path / 'newer'
    refresh(old, now='2026-10-17T01:00:00Z', run_url='success-17')
    refresh(newer, now='2026-10-18T01:00:00Z', run_url='success-18')
    old_env, new_env = export.validate_bundle(old), export.validate_bundle(newer)
    assert old_env['polls']['fetched_at'] == new_env['polls']['fetched_at']
    assert old_env['averages']['generated_at'] < new_env['averages']['generated_at']
    remote = repository(tmp_path, newer)
    before = {name: git(remote, 'show', 'data:' + str(DATA / name)).stdout for name in OWNED}
    refresh(old, now='2026-10-19T01:00:00Z', parse=fail, run_url='failure-19')
    assert publish(old, remote)['outcome'] == 'published'
    assert all(git(remote, 'show', 'data:' + str(DATA / name)).stdout == raw for name, raw in before.items())
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status['last_attempt_at'] == '2026-10-19T01:00:00Z'
    assert status['state'] == 'stale' and status['error_code'] == 'parse_drift'
    assert status['last_good_run_url'] == 'success-18'
    assert status['last_success_at'] == new_env['polls']['fetched_at']
    checkout = tmp_path / 'checkout'
    git(tmp_path, 'clone', '-q', '-b', 'data', str(remote), str(checkout))
    export.validate_bundle(checkout / DATA)
    # A genuinely later successful generation of that same capture must still advance.
    refresh(newer, now='2026-10-20T01:00:00Z', run_url='success-20')
    assert publish(newer, remote)['outcome'] == 'published'
    avg = json.loads(git(remote, 'show', 'data:' + str(DATA / 'averages.json')).stdout)
    assert avg['data'][-1]['date'] == '2026-10-20'
    assert avg['generated_at'] == '2026-10-20T01:00:00Z'


def test_download_retrieval_summary_is_auckland_and_records_stay_utc(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-17T01:00:00Z')
    original = (data / 'manifest.json').read_bytes()
    out = build(data, tmp_path / 'output')
    html = (out / 'downloads/index.html').read_text()
    envs = export.validate_bundle(data)
    for entry in envs['manifest']['data']:
        row = html.split(f'data-file="{entry["path"]}"')[1].split('</tr>')[0]
        summary, raw_record = row.split('<div><p><strong>Full manifest record (stored UTC)</strong></p>', 1)
        assert 'Retrieved (UTC)' not in summary
        if entry['fetched_at']:
            assert '<dt>Retrieved (Pacific/Auckland)</dt>' in summary
            assert local_time(entry['fetched_at']) in summary
            assert entry['fetched_at'] not in summary
        else:
            assert '<dt>Retrieved (Pacific/Auckland)</dt>' not in summary
        for key in ('observation_start', 'observation_end'):
            if entry[key] and 'T' in entry[key]:
                assert f'<time datetime="{entry[key]}">{local_time(entry[key])}</time>' in summary
                assert entry[key] not in re.sub(r'<[^>]+>', '', summary)
        assert json.loads(unescape(raw_record.split('<pre>')[1].split('</pre>')[0])) == entry
    assert (out / 'data/manifest.json').read_bytes() == original
    for utc, expected in [('2026-07-01T01:00:00Z', '1:00 pm, Wednesday 1 July 2026 NZST'),
                          ('2026-10-16T12:49:36Z', '1:49 am, Saturday 17 October 2026 NZDT')]:
        envs['manifest']['data'][0]['fetched_at'] = utc
        summary = downloads(envs, None).split('<div><p><strong>Full manifest record (stored UTC)</strong></p>', 1)[0]
        assert expected in summary and utc not in summary
