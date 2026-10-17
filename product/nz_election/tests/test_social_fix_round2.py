"""Publication retry and post-checkpoint midnight regressions, using synthetic data."""
import json

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.tests.test_social import fixture, run_row, DAY, NOW


def reserved(tmp_path):
    data, remote = tmp_path / 'data', tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    reservation = fixture(data, reserve=True)
    publish(data, remote, family='social')
    publish(data, remote, family='social', claim=reservation)
    return data, remote, reservation


def ledger_bytes(remote):
    return git(remote, 'show', 'data:' + str(DATA / 'social/credits.json')).stdout


def rewrite_report(data, mutate):
    env = export.validate_bundle(data)['social/credits']
    mutate(env['data'][0])
    # An incoming bundle cannot mint its own receipt for a conflicting report.
    row = env['data'][0]
    env['input_hashes']['social-report/' + row['id']] = export.digest(export.canonical(row).encode())
    export.pair(data, 'social/credits', env)
    export.inventory(data, env['run_url'], env['code_sha'], NOW)


def test_completed_report_retry_is_idempotent_and_lower_spend_refused(tmp_path):
    data, remote, reservation = reserved(tmp_path)
    assert fixture(data, reservation=reservation) == 'ok'
    assert publish(data, remote, family='social')['outcome'] == 'published'
    before = ledger_bytes(remote)
    assert json.loads(before)['data'][0]['spent'] == 7560
    assert publish(data, remote, family='social')['outcome'] == 'unchanged'
    assert ledger_bytes(remote) == before
    rewrite_report(data, lambda row: row.update(spent=row['spent'] - 15))
    with pytest.raises(ValueError, match='SOCIAL_LEDGER_CONFLICT'):
        publish(data, remote, family='social')
    assert ledger_bytes(remote) == before


def test_zero_request_handled_stop_publishes_and_retries(tmp_path):
    data, remote, reservation = reserved(tmp_path)
    def forbidden(*args):
        pytest.fail('transport must not be called')
    result = social.refresh_social(data, DAY, now=NOW, reservation=reservation,
                                   send=forbidden, sleep=lambda _: None,
                                   clock_now=lambda: '2026-10-17T11:00:01Z')
    assert result == 'SOCIAL_UPSTREAM_FAILED'
    assert publish(data, remote, family='social')['outcome'] == 'published'
    before = ledger_bytes(remote)
    row = json.loads(before)['data'][0]
    assert row['requests'] == 0 and row['spent'] == row['reserved'] == 7560
    status = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
    assert status['error_code'] == 'SOCIAL_UPSTREAM_FAILED'
    assert publish(data, remote, family='social')['outcome'] == 'unchanged'
    assert ledger_bytes(remote) == before
    rewrite_report(data, lambda row: row.update(requests=1, spent=15))
    with pytest.raises(ValueError, match='SOCIAL_LEDGER_CONFLICT'):
        publish(data, remote, family='social')


def test_checkpoint_crossing_midnight_never_sends_a_request():
    run = run_row()
    clock = ['2026-10-17T10:58:00Z']
    calls = []
    def checkpoint():
        clock[0] = '2026-10-17T11:00:01Z'
    def send(*args):
        calls.append(clock[0])
        return 200, b'{"tweets":[],"has_next_page":false}'
    with pytest.raises(ValueError, match='SOCIAL_BUDGET_DAY_CHANGED'):
        social.collect(DAY, [run], run, key='fiction', send=send, sleep=lambda _: None,
                       now=lambda: clock[0], checkpoint=checkpoint)
    assert calls == []
