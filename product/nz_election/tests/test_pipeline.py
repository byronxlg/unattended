"""Publication transports use only temporary local bare repositories."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import threading
import pytest
from product.nz_election.pipeline import export
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.pipeline.storage import replace_directory


def fail(*args):
    raise ParseDrift('synthetic drift')


def make_bundle(root, hour=1):
    out = root / ('bundle-' + str(hour))
    refresh(out, now=f'2026-10-17T{hour:02d}:00:00Z')
    return out


def repository(tmp_path, bundle):
    remote = tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    seed = tmp_path / 'seed'
    seed.mkdir()
    git(seed, 'init', '-q', '-b', 'data')
    git(seed, 'config', 'user.name', 'Offline test')
    git(seed, 'config', 'user.email', 'test@example.invalid')
    shutil.copytree(bundle, seed / DATA)
    git(seed, 'add', str(DATA))
    git(seed, 'commit', '-qm', 'Seed local test repository')
    git(seed, 'push', str(remote), 'data')
    return remote


def test_atomic_poll_bundle(tmp_path):
    bundle = make_bundle(tmp_path)
    old = export.validate_bundle(bundle)
    refresh(bundle, now='2026-10-18T01:00:00Z')
    new = export.validate_bundle(bundle)
    assert old['averages']['data'][-1]['date'] == '2026-10-17'
    assert new['averages']['data'][-1]['date'] == '2026-10-18'
    assert new['seats']['data']['average_id'] == new['averages']['data'][-1]['id']
    stage = tmp_path / 'bad-stage'
    stage.mkdir()
    link = tmp_path / 'link'
    link.symlink_to(bundle, target_is_directory=True)
    with pytest.raises(ValueError, match='UNSAFE'):
        replace_directory(stage, link)
    assert export.validate_bundle(bundle) == new


def test_last_good_retained(tmp_path):
    bundle = make_bundle(tmp_path)
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in {'polls', 'averages', 'seats'}}
    status = refresh(bundle, now='2026-10-17T02:00:00Z', parse=fail)
    assert status['state'] == 'stale' and status['error_code'] == 'parse_drift'
    assert all((bundle / name).read_bytes() == raw for name, raw in before.items())
    export.validate_bundle(bundle)


def test_first_failure_unavailable(tmp_path):
    bundle = tmp_path / 'unavailable'
    status = refresh(bundle, now='2026-10-17T01:00:00Z', parse=fail)
    assert status['state'] == 'unavailable' and status['last_success_at'] is None
    assert not (bundle / 'polls.json').exists()
    export.validate_bundle(bundle)


def test_partial_failure_preserves_unowned_files(tmp_path):
    bundle = make_bundle(tmp_path)
    env = json.loads((bundle / 'status.json').read_text())
    other = dict(env['data'][0], id='status-other', dataset='other', message='Unowned state')
    env['data'].append(other)
    export.pair(bundle, 'status', env)
    export.inventory(bundle, env['run_url'], env['code_sha'], '2026-10-17T01:00:00Z')
    remote = repository(tmp_path, bundle)
    newer = make_bundle(tmp_path, 2)
    refresh(newer, now='2026-10-17T03:00:00Z', parse=fail)
    publish(newer, remote)
    result = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)
    assert other in result['data']


def test_invalid_bundle_never_published(tmp_path):
    bundle = make_bundle(tmp_path)
    remote = repository(tmp_path, bundle)
    before = git(remote, 'rev-parse', 'data').stdout
    (bundle / 'rogue.json').write_text('{}')
    with pytest.raises(ValueError, match='INVENTORY'):
        publish(bundle, remote)
    assert git(remote, 'rev-parse', 'data').stdout == before
    (bundle / 'rogue.json').unlink()
    (bundle / 'polls.json').unlink()
    (bundle / 'polls.json').symlink_to(tmp_path / 'secret')
    with pytest.raises(ValueError, match='UNSAFE'):
        publish(bundle, remote)


def test_concurrent_publishers(tmp_path):
    base = make_bundle(tmp_path)
    remote = repository(tmp_path, base)
    second, third = make_bundle(tmp_path, 2), make_bundle(tmp_path, 3)
    barrier = threading.Barrier(2)
    def race(bundle):
        return publish(bundle, remote, before_push=lambda attempt: barrier.wait(timeout=10) if attempt == 0 else None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(race, [second, third]))
    assert all(r['outcome'] in {'published', 'older-run-retained'} for r in results)
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status['last_attempt_at'] == '2026-10-17T03:00:00Z'


def test_non_fast_forward_retry(tmp_path):
    remote = repository(tmp_path, make_bundle(tmp_path))
    second, third = make_bundle(tmp_path, 2), make_bundle(tmp_path, 3)
    def intervene(attempt):
        if attempt == 0:
            publish(second, remote)
    result = publish(third, remote, before_push=intervene)
    assert result['attempts'] == 2 and result['outcome'] == 'published'
    assert publish(third, remote)['outcome'] == 'unchanged'


def test_older_run_cannot_replace_newer_data(tmp_path):
    old = make_bundle(tmp_path)
    remote = repository(tmp_path, old)
    publish(make_bundle(tmp_path, 3), remote)
    before = git(remote, 'rev-parse', 'data').stdout
    assert publish(make_bundle(tmp_path, 2), remote)['outcome'] == 'older-run-retained'
    assert before == git(remote, 'rev-parse', 'data').stdout


def test_correction_history_keeps_exact_previous_shares(tmp_path):
    from decimal import Decimal
    from product.nz_election.pipeline.poll_parser import parse_polls
    bundle = make_bundle(tmp_path)
    before = export.validate_bundle(bundle)['polls']['data'][0]
    def corrected(*args):
        parsed = parse_polls(*args)
        parsed.polls[0]['shares']['nat'] += Decimal('0.1')
        return parsed
    refresh(bundle, now='2026-10-17T02:00:00Z', parse=corrected)
    after = export.validate_bundle(bundle)['polls']['data'][0]
    previous = after['history'][-1]
    assert previous['shares'] == before['shares'] and previous['scale'] == before['scale']
    refresh(bundle, now='2026-10-17T03:00:00Z', parse=corrected)
    assert export.validate_bundle(bundle)['polls']['data'][0]['history'] == after['history']
