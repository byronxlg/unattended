"""Offline contracts for the milestone runner and GitHub history evidence."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from product.nz_election.tools import check_workflow_history as history
from product.nz_election.tools import harden

FAMILIES = harden.verifier_families(harden.ROOT / 'product/nz_election/pipeline/verify.py')
VERIFIED = '\n'.join('PASS ' + name for name in FAMILIES) + '\nPASS all\n'


def result(output='', code=0):
    return SimpleNamespace(stdout=output, returncode=code)


def test_harden_discovers_and_runs_all_steps(capsys):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        assert kwargs['cwd'] == harden.ROOT
        return result(VERIFIED if 'all' in cmd else '')

    assert harden.main(['--data', 'bundle', '--site', 'site', '--history'], runner=runner) == 0
    assert [Path(c[1]) for c in calls if c[0] == 'bash'] == sorted((harden.ROOT / 'evals').glob('*/check.sh'))
    assert calls[-1][-2:] == ['--days', '3']
    assert [Path(p).name for p in calls[-2][-3:]] == ['test_social.py', 'test_social_fix_round1.py', 'test_night_operation.py']
    assert capsys.readouterr().out.splitlines()[-1] == 'PASS harden'


@pytest.mark.parametrize('missing', FAMILIES)
def test_requires_every_registered_family(missing):
    output = VERIFIED.replace('PASS ' + missing + '\n', '')
    assert missing in harden.verification_error(output, FAMILIES)


@pytest.mark.parametrize('output', ['PASS all\n' + VERIFIED, VERIFIED + 'extra\n', VERIFIED.replace('PASS night', 'PASS nightly'), VERIFIED.replace('PASS night', 'FAIL night'), VERIFIED.replace('PASS night', 'PASS night\nPASS night')])
def test_rejects_false_verifier_success(output):
    assert harden.verification_error(output, FAMILIES)


def test_verifier_accepts_annotations():
    assert harden.verification_error(VERIFIED.replace('PASS geography', 'PASS geography: 64 general, 7 Māori'), FAMILIES) is None


def test_offline_skips_only_network_and_still_runs_freeze(capsys):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return result(VERIFIED if 'all' in cmd else '')

    assert harden.main(['--offline', '--history', '--data', 'd', '--site', 's'], runner=runner) == 1
    assert not any('pages-home-bytes-live' in ' '.join(c) or 'check_workflow_history.py' in ' '.join(c) for c in calls)
    assert len([c for c in calls if c[0] == 'bash']) == len(list((harden.ROOT / 'evals').glob('*/check.sh'))) - 1
    out = capsys.readouterr().out
    assert 'SKIP workflow history: --offline' in out
    assert out.splitlines()[-1] == 'FAIL harden: eval pages-home-bytes-live (SKIP)'
    assert 'test_night_operation.py' in ' '.join(calls[-1])


def test_first_failure_retained_and_later_steps_run(capsys):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return result(VERIFIED, 9)

    assert harden.main(['--data', 'd', '--site', 's'], runner=runner) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL harden: eval pages-home-bytes-live'
    assert 'pytest' in calls[-1]


def test_spawn_failure_and_missing_families_fail_gate(capsys):
    def runner(cmd, **kwargs):
        if cmd[0] == 'bash':
            raise OSError('cannot execute')
        return result('PASS all\n')

    assert harden.main(['--data', 'd', '--site', 's'], runner=runner) == 1
    out = capsys.readouterr().out
    assert 'missing or duplicate family lines' in out
    assert 'PASS freeze tests' in out


@pytest.fixture
def workflows(tmp_path):
    directory = tmp_path / '.github/workflows'
    directory.mkdir(parents=True)
    (directory / 'new-name.yaml').write_text('name: Example schedule\non:\n  schedule:\n    - cron: "0 0 * * *"\n')
    (directory / 'manual.yml').write_text('name: Manual\non:\n  workflow_dispatch:\n')
    return tmp_path


def run_record(stamp='2026-10-23T12:00:00Z', event='schedule', conclusion='success', status='completed'):
    return dict(createdAt=stamp, event=event, conclusion=conclusion, status=status)


NOW = datetime(2026, 10, 25, 0, tzinfo=timezone.utc)


def test_workflow_discovery():
    assert {name for _, name in history.scheduled_workflows(history.ROOT)} == {
        'NZ election hourly', 'NZ election daily', 'NZ election social daily', 'NZ election night live'}


def test_history_complete_nz_days_and_manual_coverage(workflows, capsys):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        day = len(calls) + 20
        return result(json.dumps([run_record(f'2026-10-{day}T13:00:00Z', event='workflow_dispatch'),
                                  run_record(f'2026-10-{day}T12:00:00Z', event='workflow_dispatch', conclusion='failure')]))

    assert history.main(['--days', '3'], runner=runner, now=NOW, root=workflows) == 0
    assert len(calls) == 3
    assert calls[0][calls[0].index('--created') + 1] == '2026-10-21T11:00:00+00:00..2026-10-22T11:00:00+00:00'
    out = capsys.readouterr().out
    assert '2026-10-22: 2 runs, 1 successes, 1 failures, 1 recovered; cron did not fire, workflow_dispatch covered it' in out
    assert out.splitlines()[-1] == 'PASS workflow history'


@pytest.mark.parametrize('runs', [[], [run_record(conclusion='failure')], [run_record(status='in_progress')],
                                   [run_record(event='push')], [run_record('2026-10-24T11:00:00Z')],
                                   [run_record('2026-10-23T10:59:59Z')]])
def test_missing_success_fails(workflows, runs, capsys):
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW, root=workflows) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL workflow history: daily policy not met'


def test_start_inclusive_and_cron_failure_with_dispatch(workflows, capsys):
    runs = [run_record('2026-10-23T11:00:00Z', conclusion='failure'), run_record(event='workflow_dispatch')]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW, root=workflows) == 0
    out = capsys.readouterr().out
    assert '1 successes, 1 failures' in out
    assert 'cron did not fire' not in out


@pytest.mark.parametrize('raw', ['', 'null', '{}', '1', '1.5', '"unusual"', '[null]', '[{}]', json.dumps([run_record()] * 1000)])
def test_bad_or_truncated_history_fails(workflows, raw):
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(raw), now=NOW, root=workflows) == 1


def test_gh_failure(workflows):
    assert history.main([], runner=lambda *a, **k: result('', 1), now=NOW, root=workflows) == 1


@pytest.mark.parametrize('days', ['', '0', '-1', '1.5', '999999999999999999999', 'null', '三'])
def test_bad_days(days):
    with pytest.raises(SystemExit) as exc:
        history.main(['--days', days])
    assert exc.value.code == 2


def test_dst_day_uses_calendar_boundaries(workflows):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return result('[]')

    history.main(['--days', '1'], runner=runner, root=workflows,
                 now=datetime(2026, 9, 28, 0, tzinfo=timezone.utc))
    assert calls[0][calls[0].index('--created') + 1] == '2026-09-26T12:00:00+00:00..2026-09-27T11:00:00+00:00'


@pytest.fixture
def gate_root(tmp_path):
    for name in ('social-retry-budget', 'another-eval'):
        directory = tmp_path / 'evals' / name
        directory.mkdir(parents=True)
        (directory / 'check.sh').write_text('#!/bin/sh\n')
    verifier = tmp_path / 'product/nz_election/pipeline/verify.py'
    verifier.parent.mkdir(parents=True)
    verifier.write_text('checks = ' + repr(dict.fromkeys(FAMILIES)))
    return tmp_path


def green_runner(cmd, **kwargs):
    return result(VERIFIED if 'all' in cmd else 'PASS step\n')


def test_fix_round_missing_eval_cannot_pass(gate_root, capsys):
    (gate_root / 'evals/social-retry-budget/check.sh').unlink()
    assert harden.main(['--history', '--data', 'd', '--site', 's'], runner=green_runner, root=gate_root) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL harden: eval social-retry-budget'


@pytest.mark.parametrize('line', ['SKIP missing prerequisite', 'FAIL broken assertion', '  SKIP: offline', 'FAIL'])
def test_fix_round_zero_exit_result_cannot_pass(gate_root, capsys, line):
    def runner(cmd, **kwargs):
        if cmd[0] == 'bash' and 'social-retry-budget' in cmd[1]:
            return result(line + '\nPASS later\n')
        return green_runner(cmd, **kwargs)

    assert harden.main(['--history', '--data', 'd', '--site', 's'], runner=runner, root=gate_root) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL harden: eval social-retry-budget'


def test_fix_round_without_history_is_partial(gate_root, capsys):
    assert harden.main(['--data', 'd', '--site', 's'], runner=green_runner, root=gate_root) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'PARTIAL harden (history not checked)'


def hourly_root(workflows):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Example hourly\non:\n  schedule:\n    - cron: "17 * * * *"\n')
    return workflows


def hourly_runs(hours, failures=()):
    start = datetime(2026, 10, 23, 11, tzinfo=timezone.utc)
    return [run_record((start + timedelta(hours=hour)).isoformat(),
                       conclusion='failure' if hour in failures else 'success') for hour in hours]


@pytest.mark.parametrize('hourly', [False, True])
def test_fix_round_one_success_and_23_failures_cannot_pass(workflows, capsys, hourly):
    if hourly:
        hourly_root(workflows)
    runs = hourly_runs(range(24), failures=range(1, 24))
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW, root=workflows) == 1
    out = capsys.readouterr().out
    assert '24 runs, 1 successes, 23 failures' in out
    assert ('success gap' if hourly else 'last run did not conclude success') in out


@pytest.mark.parametrize('hours,failures,passes,reason', [
    ([0, 3, 6, 9, 12, 15, 18, 21], [], True, ''),
    ([3, 6, 9, 12, 15, 18, 21], [], True, ''),
    ([3.01, 6, 9, 12, 15, 18, 21], [], False, 'success gap'),
    ([0, 3, 6, 9.01, 12, 15, 18, 21], [], False, 'success gap'),
    ([0, 3, 6, 9, 12, 15, 18, 20.99], [], False, 'success gap'),
    ([0, 1, 3, 6, 9, 12, 15, 18, 21], [1], True, '1 recovered'),
    ([0, .99, 3, 6, 9, 12, 15, 18, 21], [.99], False, 'without success within 2 hours'),
    ([0, 3, 6, 9, 12, 15, 18, 21, 23], [23], False, 'without success within 2 hours'),
])
def test_hourly_gap_and_recovery_boundaries(workflows, capsys, hours, failures, passes, reason):
    runs = hourly_runs(hours, failures)
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(list(reversed(runs)))),
                        now=NOW, root=hourly_root(workflows)) == int(not passes)
    assert reason in capsys.readouterr().out


@pytest.mark.parametrize('latest_status,latest_conclusion,passes', [
    ('completed', 'success', True), ('completed', 'failure', False),
    ('in_progress', None, False), ('completed', 'cancelled', False), ('completed', 'skipped', False),
])
def test_daily_last_run_controls_result(workflows, capsys, latest_status, latest_conclusion, passes):
    runs = [run_record(), run_record('2026-10-23T13:00:00Z', conclusion='failure'),
            run_record('2026-10-23T14:00:00Z', event='workflow_dispatch', status=latest_status, conclusion=latest_conclusion)]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(list(reversed(runs)))),
                        now=NOW, root=workflows) == int(not passes)
    out = capsys.readouterr().out
    assert ('1 recovered' if passes else 'last run did not conclude success') in out


def test_daily_tied_latest_failure_cannot_hide(workflows):
    runs = [run_record(), run_record(conclusion='failure')]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW, root=workflows) == 1


def test_history_help_states_policy(capsys):
    with pytest.raises(SystemExit) as exc:
        history.main(['--help'])
    assert exc.value.code == 0
    out = ' '.join(capsys.readouterr().out.split())
    for phrase in ('3 hours', '2 hours', 'last run', 'creation timestamps',
                   'gaps between consecutive successful runs are measured across midnight'):
        assert phrase in out


@pytest.mark.parametrize('recovery_hour,passes', [(24, True), (25, True), (25.01, False)])
def test_hourly_recovery_across_midnight(workflows, capsys, recovery_hour, passes):
    runs = hourly_runs([0, 3, 6, 9, 12, 15, 18, 21, 23, recovery_hour], failures=[23])
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return result(json.dumps(runs))

    assert history.main(['--days', '1'], runner=runner, now=NOW, root=hourly_root(workflows)) == int(not passes)
    out = capsys.readouterr().out
    assert '9 runs, 8 successes, 1 failures' in out
    assert ('1 recovered' if passes else 'without success within 2 hours') in out
    assert calls[0][calls[0].index('--created') + 1].endswith('2026-10-24T13:00:00+00:00')


def test_hourly_next_day_success_does_not_fill_day_gap(workflows, capsys):
    runs = hourly_runs([0, 3, 6, 9, 12, 15, 18, 24])
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW,
                        root=hourly_root(workflows)) == 1
    assert 'success gap 6 hours exceeds 3 hours' in capsys.readouterr().out


@pytest.mark.parametrize('hours,passes', [
    ([3, 6, 9, 12, 15, 18, 21], False),
    ([0, 3, 6, 9, 12, 15, 18, 21], True),
])
def test_fix_round2_three_day_midnight_gaps(workflows, capsys, hours, passes):
    start = datetime(2026, 10, 21, 11, tzinfo=timezone.utc)
    records = [run_record((start + timedelta(days=day, hours=hour)).isoformat())
               for day in range(3) for hour in hours]

    def runner(cmd, **kwargs):
        lower, upper = cmd[cmd.index('--created') + 1].split('..')
        return result(json.dumps([run for run in reversed(records)
                                  if datetime.fromisoformat(lower) <= datetime.fromisoformat(run['createdAt'])
                                  <= datetime.fromisoformat(upper)]))

    assert history.main(['--days', '3'], runner=runner, now=NOW, root=hourly_root(workflows)) == int(not passes)
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if 'Example hourly' in line]
    assert len(lines) == 3
    assert all(f'{len(hours)} runs, {len(hours)} successes, 0 failures' in line for line in lines)
    if not passes:
        assert all(line.startswith('FAIL') and 'success gap 6 hours exceeds 3 hours' in line for line in lines)


def test_hourly_gap_crosses_empty_day(workflows, capsys):
    start = datetime(2026, 10, 21, 11, tzinfo=timezone.utc)
    records = [run_record((start + timedelta(days=day, hours=hour)).isoformat())
               for day in (0, 2) for hour in range(0, 24, 3)]
    assert history.main(['--days', '3'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=NOW, root=hourly_root(workflows)) == 1
    out = capsys.readouterr().out
    assert out.count('success gap 27 hours exceeds 3 hours') == 3


@pytest.mark.parametrize('missing,passes', [(False, True), (True, False)])
def test_annual_history_only_requires_firing_days(workflows, capsys, missing, passes):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Annual\non:\n  schedule:\n    - cron: "2 6 7 11 *"\n')
    records = [] if missing else [run_record('2026-11-07T06:02:00Z')]
    assert history.main(['--days', '3'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 9, tzinfo=timezone.utc), root=workflows) == int(not passes)
    out = capsys.readouterr().out
    assert 'PASS Annual 2026-11-06: not scheduled' in out
    if missing:
        assert 'FAIL Annual 2026-11-07: 0 runs, 0 successes, 0 failures, 0 recovered; cron did not fire; no runs' in out


def test_pre_night_annual_history_needs_no_runs(workflows, capsys):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Annual\non:\n  schedule:\n    - cron: "2 6 7 11 *"\n')

    def runner(*args, **kwargs):
        pytest.fail('inactive schedule must not query history')

    assert history.main(['--days', '3'], runner=runner,
                        now=datetime(2026, 11, 4, tzinfo=timezone.utc), root=workflows) == 0


def test_daily_history_missing_middle_day(workflows, capsys):
    records = [run_record('2026-10-22T00:00:00Z'), run_record('2026-10-24T00:00:00Z')]
    assert history.main(['--days', '3'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=NOW, root=workflows) == 1
    assert 'FAIL Example schedule 2026-10-23: 0 runs, 0 successes, 0 failures, 0 recovered; cron did not fire; no runs' in capsys.readouterr().out


@pytest.mark.parametrize('required,passes', [(None, True), ('night,waterfall', False)])
def test_harden_optional_night_context(gate_root, capsys, required, passes):
    output = VERIFIED.replace('PASS night', 'SKIP night: family absent (night/index.json)').replace(
        'PASS waterfall', 'SKIP waterfall: family absent (night/index.json)')
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return result(output if 'all' in cmd else 'PASS step\n')

    args = ['--history', '--data', 'd', '--site', 's']
    if required:
        args += ['--require', required]
    assert harden.main(args, runner=runner, root=gate_root) == int(not passes)
    command = next(cmd for cmd in calls if 'all' in cmd)
    if required:
        assert command[-2:] == ['--require', required]
    assert ('PASS harden' if passes else 'FAIL harden: verify all') in capsys.readouterr().out


@pytest.mark.parametrize('line', ['SKIP polls: family absent (night/index.json)',
                                  'SKIP night: unavailable', '  SKIP night: family absent (night/index.json)',
                                  'FAIL night: broken'])
def test_optional_context_rejects_other_omissions(gate_root, line):
    output = VERIFIED.replace('PASS ' + ('polls' if 'polls' in line else 'night'), line)
    assert harden.main(['--history', '--data', 'd', '--site', 's'], root=gate_root,
                       runner=lambda cmd, **k: result(output if 'all' in cmd else 'PASS step')) == 1


@pytest.mark.parametrize('required', ['', 'null', '1', '1.5', '999999999999999999999', '三', 'night,unknown'])
def test_harden_invalid_required_checks(gate_root, required, capsys):
    assert harden.main(['--history', '--data', 'd', '--site', 's', '--require', required],
                       runner=green_runner, root=gate_root) == 1
    assert 'INVALID_REQUIRED_CHECK' in capsys.readouterr().out


@pytest.mark.parametrize('cron,expected', [
    ('2 23 7 11 *', ['2026-11-07T23:02:00+00:00']),
    ('2 6 7 11 *', []),
    ('0 12-14/2 * NOV SUN', ['2026-11-08T12:00:00+00:00', '2026-11-08T14:00:00+00:00']),
    ('0 12 7,8 NOV MON', ['2026-11-07T12:00:00+00:00', '2026-11-08T12:00:00+00:00']),
])
def test_cron_utc_dates_ranges_steps_and_weekdays(cron, expected):
    schedules = history.workflow_schedule(f'    - cron: "{cron}"\n')
    start = datetime(2026, 11, 7, 11, tzinfo=timezone.utc)
    end = datetime(2026, 11, 8, 15, tzinfo=timezone.utc)
    assert [s.isoformat() for s in history.scheduled_times(schedules, start, end)] == expected


@pytest.mark.parametrize('cron', ['', '* * * *', '60 * * * *', '0 */0 * * *',
                                  '0 99999999999999 * * *', 'null', '0 1.5 * * *', '0 三 * * *'])
def test_invalid_cron_fails_closed(workflows, cron, capsys):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        f'name: Invalid\non:\n  schedule:\n    - cron: "{cron}"\n')
    assert history.main(['--days', '1'], runner=green_runner, now=NOW, root=workflows) == 1
    assert 'FAIL workflow history:' in capsys.readouterr().out


def test_dated_hourly_cron_has_no_gap_outside_utc_date(workflows):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Dated hourly\non:\n  schedule:\n    - cron: "17 */1 7 NOV *"\n')
    records = [run_record(f'2026-11-07T{hour:02}:17:00Z') for hour in range(24)]
    assert history.main(['--days', '3'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 9, tzinfo=timezone.utc), root=workflows) == 0


@pytest.mark.parametrize('hourly', [False, True])
def test_declared_freeze_guard_bounds_expected_history(workflows, hourly):
    cron = '17 * * * *' if hourly else '43 15 * * *'
    (workflows / '.github/workflows/new-name.yaml').write_text(
        f'name: Guarded\non:\n  schedule:\n    - cron: "{cron}"\n'
        'jobs:\n  refresh:\n    steps:\n'
        '      - run: python3 product/nz_election/pipeline/deployment_guard.py\n')
    start = datetime(2026, 11, 5, 11, tzinfo=timezone.utc)
    records = [run_record((start + timedelta(hours=hour, minutes=17)).isoformat())
               for hour in range(72) if not 24 <= hour < 43]
    # The last pre-freeze success is 13 minutes before the guard closes.
    assert history.main(['--days', '3'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 9, tzinfo=timezone.utc), root=workflows) == 0


def test_night_entry_point_guard_excludes_future_annual_firing(workflows):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Closed night\non:\n  schedule:\n    - cron: "2 6 7 11 *"\n'
        'jobs:\n  live:\n    steps:\n'
        '      - run: uv run product/nz_election/pipeline/night_live.py\n')

    def runner(*args, **kwargs):
        pytest.fail('closed night window must not query history')

    assert history.main(['--days', '3'], runner=runner,
                        now=datetime(2027, 11, 9, tzinfo=timezone.utc), root=workflows) == 0


def test_repository_healthy_pre_night_history():
    def runner(cmd, **kwargs):
        start, end = map(datetime.fromisoformat, cmd[cmd.index('--created') + 1].split('..'))
        records = [run_record((start + timedelta(hours=h, minutes=17)).isoformat())
                   for h in range(int((end - start).total_seconds() / 3600))]
        return result(json.dumps(records))

    assert history.main(['--days', '3'], runner=runner,
                        now=datetime(2026, 11, 4, tzinfo=timezone.utc)) == 0


@pytest.mark.parametrize('release', [False, True])
def test_polls_only_eval_expected_omission_in_both_contexts(gate_root, release):
    directory = gate_root / 'evals/pages-verify-polls-only'
    directory.mkdir()
    (directory / 'check.sh').write_text('#!/bin/sh\n')
    output = VERIFIED.replace('PASS night', 'SKIP night: family absent (night/index.json)').replace(
        'PASS waterfall', 'SKIP waterfall: family absent (night/index.json)')

    def runner(cmd, **kwargs):
        if cmd[0] == 'bash' and Path(cmd[1]).parent == directory:
            return result(output)
        return green_runner(cmd, **kwargs)

    args = ['--history', '--data', 'd', '--site', 's']
    if release:
        args += ['--require', 'night,waterfall']
    assert harden.main(args, runner=runner, root=gate_root) == 0


def test_polls_only_eval_skip_cannot_hide_incomplete_verification(gate_root):
    directory = gate_root / 'evals/pages-verify-polls-only'
    directory.mkdir()
    (directory / 'check.sh').write_text('#!/bin/sh\n')

    def runner(cmd, **kwargs):
        if cmd[0] == 'bash' and Path(cmd[1]).parent == directory:
            return result('SKIP night: family absent (night/index.json)\nPASS all\n')
        return green_runner(cmd, **kwargs)

    assert harden.main(['--history', '--data', 'd', '--site', 's'], runner=runner, root=gate_root) == 1


@pytest.mark.parametrize('hourly_cron', ['17 * * 7 *', '17 * 7 * *', '17 * * * MON'])
def test_review_cadence_uses_only_matching_dates(workflows, capsys, hourly_cron):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        f'name: Mixed cadence\non:\n  schedule:\n    - cron: "{hourly_cron}"\n'
        '    - cron: "0 0 * 11 *"\n')
    records = [run_record('2026-11-04T00:00:00Z')]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 5, tzinfo=timezone.utc), root=workflows) == 0
    assert 'success gap' not in capsys.readouterr().out


@pytest.mark.parametrize('hours,passes', [(range(11), True), ([10], False), ([0], False)])
def test_review_restricted_hourly_window(workflows, capsys, hours, passes):
    (workflows / '.github/workflows/new-name.yaml').write_text(
        'name: Restricted hourly\non:\n  schedule:\n    - cron: "0 0-10 * * *"\n')
    records = [run_record(f'2026-11-04T{hour:02}:00:00Z') for hour in hours]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 5, tzinfo=timezone.utc), root=workflows) == int(not passes)
    if not passes:
        assert 'success gap' in capsys.readouterr().out


@pytest.mark.parametrize('mention', [
    '# See product/nz_election/pipeline/night_live.py\n',
    'jobs:\n  check:\n    steps:\n      - name: See product/nz_election/pipeline/night_live.py\n'
    '        run: echo checking\n',
    'jobs:\n  check:\n    steps:\n      - run: echo product/nz_election/pipeline/night_live.py\n',
    'jobs:\n  check:\n    steps:\n      - run: |\n'
    '          # python3 product/nz_election/pipeline/night_live.py\n          echo checking\n',
])
def test_review_incidental_guard_mention_cannot_exempt_history(workflows, capsys, mention):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text(path.read_text() + mention)
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 1
    assert '; no runs' in capsys.readouterr().out


@pytest.mark.parametrize('step', [
    '- name: Run checker\n        env:\n          run: python3 product/nz_election/pipeline/night_live.py\n'
    '        run: echo checking',
    '- name: |\n          run: python3 product/nz_election/pipeline/night_live.py\n'
    '        run: echo checking',
    '- run: |\n          echo \'documentation\n          python3 product/nz_election/pipeline/night_live.py\n          \'',
    '- run: |\n          cat <<EOF\n          python3 product/nz_election/pipeline/night_live.py\n          EOF',
    '- run: python3 product/nz_election/pipeline/night_live.py||true',
])
def test_review_guard_requires_execution_not_nested_values(workflows, step):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      ' + step + '\n')
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 1


@pytest.mark.parametrize('value', [
    'python3 product/nz_election/pipeline/night_live.py',
    '"python3 product/nz_election/pipeline/night_live.py"',
    "'uv run product/nz_election/pipeline/night_live.py'",
    '|\n          set -euo pipefail\n          uv run product/nz_election/pipeline/night_live.py',
    '>-\n          uv run\n          product/nz_election/pipeline/night_live.py',
])
def test_review_actual_guard_commands_keep_window(workflows, value):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      - run: ' + value + '\n')

    def runner(*args, **kwargs):
        pytest.fail('guarded night command is outside its active window')

    assert history.main(['--days', '1'], runner=runner, now=NOW, root=workflows) == 0


@pytest.mark.parametrize('missing,passes', [(False, True), (True, False)])
def test_review_cadence_transition_within_nz_day(workflows, capsys, missing, passes):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text('name: Transition\non:\n  schedule:\n'
                    '    - cron: "17 * * * MON"\n    - cron: "0 0 * * TUE"\n')
    # Tuesday NZ starts on Monday UTC: the first 13 hours remain hourly.
    records = [run_record('2026-11-03T00:00:00Z')]
    if not missing:
        records += [run_record(f'2026-11-02T{hour:02}:17:00Z') for hour in range(11, 24)]
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 4, tzinfo=timezone.utc), root=workflows) == int(not passes)
    if missing:
        assert 'success gap 13 hours exceeds 3 hours' in capsys.readouterr().out


@pytest.mark.parametrize('recovery_hour,passes', [(12, True), (12.01, False)])
def test_review_restricted_window_keeps_two_hour_recovery(workflows, recovery_hour, passes):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text('name: Restricted recovery\non:\n  schedule:\n    - cron: "0 0-10 * * *"\n')
    start = datetime(2026, 11, 3, tzinfo=timezone.utc)
    records = [run_record((start + timedelta(hours=hour)).isoformat(),
                          conclusion='failure' if hour == 10 else 'success') for hour in range(11)]
    records.append(run_record((start + timedelta(hours=recovery_hour)).isoformat(), event='workflow_dispatch'))
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(records)),
                        now=datetime(2026, 11, 4, tzinfo=timezone.utc), root=workflows) == int(not passes)


@pytest.mark.parametrize('script,guarded', [
    ("echo '\n' python3 product/nz_election/pipeline/night_live.py", False),
    ('set -e # setup\npython3 product/nz_election/pipeline/night_live.py', True),
    ('python3 \\\nproduct/nz_election/pipeline/night_live.py', True),
    ('# setup\npython3 product/nz_election/pipeline/night_live.py', True),
    ('set -e # setup\n# comment\npython3 product/nz_election/pipeline/night_live.py', True),
    ('uv \\\nrun \\\nproduct/nz_election/pipeline/night_live.py', True),
    ('python3 product/nz_election/pipeline/night_\\\nlive.py', True),
    ('python3 "product/nz_election/pipeline/night_\\\nlive.py"', True),
    ("echo '\n python3 product/nz_election/pipeline/night_live.py'", False),
    ('echo "\n" python3 product/nz_election/pipeline/night_live.py', False),
    ('echo \\\npython3 product/nz_election/pipeline/night_live.py', False),
    ('echo "# not a comment\npython3 product/nz_election/pipeline/night_live.py"', False),
    ('python3 product/nz_election/pipeline/night_live.py#not-a-comment', False),
    ("python3 'product/nz_election/pipeline/night_\\\nlive.py'", False),
], ids=['quoted-newline', 'trailing-comment', 'backslash-continuation',
        'comment-line', 'consecutive-comments', 'uv-continuations', 'path-continuation',
        'double-quoted-continuation', 'quoted-command-text', 'double-quoted-newline',
        'continued-echo', 'quoted-comment', 'literal-hash', 'single-quoted-backslash'])
def test_review2_guard_shell_boundaries(workflows, capsys, script, guarded):
    path = workflows / '.github/workflows/new-name.yaml'
    body = '\n'.join('          ' + line for line in script.split('\n'))
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      - run: |\n' + body + '\n')
    calls = []

    def runner(*args, **kwargs):
        calls.append(args)
        return result('[]')

    assert history.main(['--days', '1'], runner=runner, now=NOW, root=workflows) == int(not guarded)
    assert bool(calls) == (not guarded)
    assert ('not scheduled' if guarded else '; no runs') in capsys.readouterr().out


def test_review3_ansi_c_string_cannot_declare_guard(workflows, capsys):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text(path.read_text() + r"""jobs:
  check:
    steps:
      - run: |
          echo $'a\'
          python3 product/nz_election/pipeline/night_live.py
          #'
""")
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 1
    assert '; no runs' in capsys.readouterr().out
    assert list(history.workflow_commands(path.read_text())) == []


@pytest.mark.parametrize('script,guarded', [
    ("python3 product/nz_election/pipeline/night_live.py\necho $'text'", False),
    ("echo $'text'\npython3 product/nz_election/pipeline/night_live.py", False),
    ("python3 product/nz_election/pipeline/night_live.py $'text'", False),
])
def test_review3_ansi_c_syntax_rejects_whole_step(workflows, script, guarded):
    path = workflows / '.github/workflows/new-name.yaml'
    body = '\n'.join('          ' + line for line in script.split('\n'))
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      - run: |\n' + body + '\n')
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == int(not guarded)


@pytest.mark.parametrize('script', [
    'args=(\npython3 product/nz_election/pipeline/night_live.py\n)',
    'unused() {\npython3 product/nz_election/pipeline/night_live.py\n}',
    '(\npython3 product/nz_election/pipeline/night_live.py\n)',
    'if false; then\npython3 product/nz_election/pipeline/night_live.py\nfi',
], ids=['array', 'uncalled-function', 'subshell', 'if-body'])
def test_review4_enclosing_construct_is_not_guard_evidence(workflows, capsys, script):
    path = workflows / '.github/workflows/new-name.yaml'
    body = '\n'.join('          ' + line for line in script.split('\n'))
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      - run: |\n' + body + '\n')
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 1
    assert '; no runs' in capsys.readouterr().out
    assert list(history.workflow_commands(path.read_text())) == []


@pytest.mark.parametrize('unsupported', [
    'args=(one two)', 'unused() { echo data; }', '(echo data)', '{ echo data; }',
    'echo "$(echo data)"', 'echo `echo data`', 'cat <<EOF\ndata\nEOF',
    'if false; then echo data; fi', 'for x in one; do echo data; done',
    'while false; do echo data; done', 'case value in value) echo data;; esac',
    'echo data && echo more', 'echo data || echo more', 'echo data | cat',
    'echo data > output', 'exit 0', 'eval "echo data"', 'source helper.sh',
])
@pytest.mark.parametrize('guard_first', [False, True])
def test_review4_unsupported_step_is_rejected_as_a_whole(workflows, unsupported, guard_first):
    guard = 'python3 product/nz_election/pipeline/night_live.py'
    script = '\n'.join([guard, unsupported] if guard_first else [unsupported, guard])
    path = workflows / '.github/workflows/new-name.yaml'
    body = '\n'.join('          ' + line for line in script.split('\n'))
    path.write_text(path.read_text() + 'jobs:\n  check:\n    steps:\n      - run: |\n' + body + '\n')
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 1
    assert list(history.workflow_commands(path.read_text())) == []


def test_review4_rejected_step_does_not_discard_separate_simple_guard(workflows):
    path = workflows / '.github/workflows/new-name.yaml'
    path.write_text(path.read_text() + '''jobs:
  check:
    steps:
      - run: |
          args=()
          echo data
      - run: python3 product/nz_election/pipeline/night_live.py
''')
    assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                        now=NOW, root=workflows) == 0


@pytest.mark.parametrize('separator', ['\r', '\v', '\f', '\x00', '\u00a0'],
                         ids=['CR', 'VT', 'FF', 'NUL', 'NBSP'])
def test_review5_unsupported_characters_reject_whole_step(workflows, capsys, separator):
    path = workflows / '.github/workflows/new-name.yaml'
    original = path.read_text()
    guard = 'python3 product/nz_election/pipeline/night_live.py'
    malformed = 'python3' + separator + 'product/nz_election/pipeline/night_live.py'
    # Unsupported characters invalidate both a command word and literal data
    # in a step that otherwise contains a valid guard invocation.
    for script in (malformed, guard + '\necho "' + malformed + '"'):
        path.write_text(original + 'jobs:\n  check:\n    steps:\n      - run: ' + json.dumps(script) + '\n')
        assert history.main(['--days', '1'], runner=lambda *a, **k: result('[]'),
                            now=NOW, root=workflows) == 1
        assert '; no runs' in capsys.readouterr().out
        assert list(history.workflow_commands(path.read_text())) == []


@pytest.mark.parametrize('char', [chr(n) for n in range(32) if n not in (9, 10)] +
                         ['\x7f', '\x85', '\u00a0', '\u2028', '\u2029', '\u4e09'])
def test_review5_forbidden_characters_cannot_hide_in_comments(char):
    script = 'python3 product/nz_election/pipeline/night_live.py\n# ' + char
    with pytest.raises(ValueError, match='unsupported shell character'):
        history.shell_commands(script)


@pytest.mark.parametrize('style', ['|', '>'])
@pytest.mark.parametrize('char', ['\v', '\f', '\x00', '\u00a0', '\u2028'])
def test_review5_block_scalars_preserve_forbidden_characters(style, char):
    source = ('jobs:\n  check:\n    steps:\n      - run: ' + style + '\n'
              '          python3 product/nz_election/pipeline/night_live.py\n'
              '          # ' + char + '\n')
    assert list(history.workflow_commands(source)) == []


@pytest.mark.parametrize('separator', [' ', '\t', ' \\\n'])
def test_review5_supported_whitespace_still_recognizes_guard(separator):
    command = 'python3' + separator + 'product/nz_election/pipeline/night_live.py'
    source = 'jobs:\n  check:\n    steps:\n      - run: ' + json.dumps(command) + '\n'
    assert list(history.workflow_commands(source)) == [['product/nz_election/pipeline/night_live.py']]
