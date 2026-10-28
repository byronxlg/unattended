"""Collection deadlines bound required history, including recovery lookahead."""
from datetime import datetime, time, timedelta, timezone
import json
from types import SimpleNamespace

import pytest

from product.nz_election.pipeline import sunsets
from product.nz_election.tools import check_workflow_history as history

CASES = [('hourly', sunsets.HOURLY_CLOSE, '17 * * * *'),
         ('daily', sunsets.DAILY_CLOSE, '43 15 * * *'),
         ('social', sunsets.SOCIAL_CLOSE, '40 13 * * *')]


def workflow(kind, cron, command=None):
    command = command or f'python3 product/nz_election/pipeline/sunsets.py {kind}'
    return (f'name: Collection\non:\n  schedule:\n    - cron: "{cron}"\n'
            f'jobs:\n  window:\n    steps:\n      - run: {command}\n')


@pytest.mark.parametrize('kind,close,cron', CASES)
def test_collection_intervals(kind, close, cron):
    source = workflow(kind, cron)
    before, after = close - timedelta(days=2), close + timedelta(days=2)
    schedules = history.workflow_schedule(source)
    assert history.active_intervals(source, before, close) == [(before, close)]
    assert history.active_intervals(source, before, after) == [(before, close)]
    assert history.active_intervals(source, close, after) == []
    assert history.expected_intervals(source, schedules, before, after) == [
        (before, close, kind == 'hourly')]
    assert history.expected_intervals(source, schedules, close, after) == []


@pytest.mark.parametrize('kind,close,cron', CASES)
def test_collection_history(kind, close, cron, tmp_path):
    directory = tmp_path / '.github/workflows'
    directory.mkdir(parents=True)
    (directory / 'collection.yml').write_text(workflow(kind, cron))
    midnight = datetime.combine(close.astimezone(history.NZ).date(), time.min, history.NZ)
    before = midnight - timedelta(days=2)
    calls = []
    records = []

    def runner(cmd, **kwargs):
        left, right = map(datetime.fromisoformat, cmd[cmd.index('--created') + 1].split('..'))
        calls.append((left, right))
        return SimpleNamespace(returncode=0, stdout=json.dumps([
            record for record in records if left <= datetime.fromisoformat(record['createdAt']) <= right]))

    # Missing pre-sunset coverage remains a failure.
    assert history.main(['--days', '1'], runner=runner, now=midnight, root=tmp_path) == 1
    # A multi-day window crosses the deadline with only pre-sunset successes.
    stamp = before
    while stamp < close:
        records.append(dict(createdAt=stamp.isoformat(), event='schedule',
                            status='completed', conclusion='success'))
        stamp += timedelta(hours=1)
    calls.clear()
    assert history.main(['--days', '4'], runner=runner,
                        now=midnight + timedelta(days=2), root=tmp_path) == 0
    assert calls and all(right <= close for _, right in calls)
    records.clear()
    calls.clear()
    assert history.main(['--days', '1'], runner=runner,
                        now=midnight + timedelta(days=2), root=tmp_path) == 0
    assert calls == []


@pytest.mark.parametrize('kind,close,cron', CASES)
def test_unrecognized_sunset_stays_strict(kind, close, cron):
    before, after = close, close + timedelta(days=1)
    guard = f'python3 product/nz_election/pipeline/sunsets.py {kind}'
    for command in ('echo ' + guard, guard + ' || true', guard + ' --now 2026-01-01',
                    guard + ' extra', guard.replace(kind, 'unknown')):
        assert history.active_intervals(workflow(kind, cron, command), before, after) == [(before, after)]
    # A supported invocation is the only form that grants the exemption.
    assert history.active_intervals(workflow(kind, cron), before, after) == []


@pytest.mark.parametrize('kind,close,cron', CASES)
def test_repository_freeze_and_sunset_intersect(kind, close, cron):
    filename = 'nz-election-social-daily.yml' if kind == 'social' else f'nz-election-{kind}.yml'
    source = (history.ROOT / '.github/workflows' / filename).read_text()
    start, end = history.START - timedelta(days=1), close + timedelta(days=2)
    expected = [(start, history.START)]
    if history.END < close:
        expected.append((history.END, close))
    assert history.active_intervals(source, start, end) == expected


@pytest.mark.parametrize('kind,close,cron', CASES)
@pytest.mark.parametrize('recovery_seconds,covered,passes', [
    (-1, True, False), (-0.5, True, True), (-0.5, False, False),
    (0, True, False), (1, True, False),
], ids=['tied', 'before', 'before-with-gap', 'at-sunset', 'after-sunset'])
def test_sunset_recovery_evidence(kind, close, cron, recovery_seconds, covered, passes,
                                  tmp_path, capsys):
    directory = tmp_path / '.github/workflows'
    directory.mkdir(parents=True)
    # Hourly cadence exercises recovery for each recognised collection deadline.
    (directory / 'collection.yml').write_text(workflow(kind, '17 * * * *'))
    close = close.astimezone(timezone.utc)
    now = datetime.combine((close - timedelta(seconds=1)).astimezone(history.NZ).date()
                           + timedelta(days=1), time.min, history.NZ)
    start = datetime.combine(now.astimezone(history.NZ).date() - timedelta(days=1),
                             time.min, history.NZ).astimezone(timezone.utc)
    records = []
    stamp = start
    while covered and stamp < close - timedelta(seconds=1):
        records.append(dict(createdAt=stamp.isoformat(), event='schedule',
                            status='completed', conclusion='success'))
        stamp += timedelta(hours=1)
    records += [dict(createdAt=(close - timedelta(seconds=1)).isoformat(), event='schedule',
                     status='completed', conclusion='failure'),
                dict(createdAt=(close + timedelta(seconds=recovery_seconds)).isoformat(),
                     event='workflow_dispatch', status='completed', conclusion='success')]
    # Return even out-of-range evidence to exercise the checker's own filtering.
    runner = lambda *a, **k: SimpleNamespace(returncode=0, stdout=json.dumps(records))
    assert history.main(['--days', '1'], runner=runner, now=now, root=tmp_path) == int(not passes)
    output = capsys.readouterr().out
    if recovery_seconds >= 0 or recovery_seconds == -1:
        assert '1 failures without success within 2 hours' in output
    elif not covered:
        assert 'success gap' in output
    else:
        assert '1 recovered' in output
