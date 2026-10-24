"""Offline contracts for the milestone runner and GitHub history evidence."""
from datetime import datetime, timezone
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
    (directory / 'new-name.yaml').write_text('name: Example schedule\non:\n  schedule:\n    - cron: "0 * * * *"\n')
    (directory / 'manual.yml').write_text('name: Manual\non:\n  workflow_dispatch:\n')
    return tmp_path


def run_record(stamp='2026-10-23T12:00:00Z', event='schedule', conclusion='success', status='completed'):
    return dict(createdAt=stamp, event=event, conclusion=conclusion, status=status)


NOW = datetime(2026, 10, 25, 0, tzinfo=timezone.utc)


def test_workflow_discovery():
    assert {name for _, name in history.scheduled_workflows(history.ROOT)} == {
        'NZ election hourly', 'NZ election daily', 'NZ election social daily'}


def test_history_complete_nz_days_and_manual_coverage(workflows, capsys):
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        day = len(calls) + 20
        return result(json.dumps([run_record(f'2026-10-{day}T12:00:00Z', event='workflow_dispatch'),
                                  run_record(f'2026-10-{day}T13:00:00Z', event='workflow_dispatch', conclusion='failure')]))

    assert history.main(['--days', '3'], runner=runner, now=NOW, root=workflows) == 0
    assert len(calls) == 3
    assert calls[0][calls[0].index('--created') + 1] == '2026-10-21T11:00:00+00:00..2026-10-22T11:00:00+00:00'
    out = capsys.readouterr().out
    assert '2026-10-22: 1 successes, 1 failures; cron did not fire, workflow_dispatch covered it' in out
    assert out.splitlines()[-1] == 'PASS workflow history'


@pytest.mark.parametrize('runs', [[], [run_record(conclusion='failure')], [run_record(status='in_progress')],
                                   [run_record(event='push')], [run_record('2026-10-24T11:00:00Z')],
                                   [run_record('2026-10-23T10:59:59Z')]])
def test_missing_success_fails(workflows, runs, capsys):
    assert history.main(['--days', '1'], runner=lambda *a, **k: result(json.dumps(runs)), now=NOW, root=workflows) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL workflow history: missing daily success'


def test_start_inclusive_and_cron_failure_with_dispatch(workflows, capsys):
    runs = [run_record('2026-10-23T11:00:00Z', event='workflow_dispatch'), run_record(conclusion='failure')]
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
