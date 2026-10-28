# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Offline boundary drill: injected clocks, local Git, no production capabilities."""
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timedelta
from functools import partial
import io
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from unittest.mock import patch

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import deployment_guard, night_live, night_start, publish, result_import, sunsets
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.night_live_cases import Clock, captures

# Independent acceptance instants: deriving these from production constants hides drift.
OPEN = datetime.fromisoformat('2026-11-07T06:00:00Z')
FREEZE = datetime.fromisoformat('2026-11-06T10:30:00Z')
STOP = datetime.fromisoformat('2026-11-08T06:00:00Z')
SUNSETS = {'hourly': OPEN, 'night': STOP,
           'daily': datetime.fromisoformat('2026-11-14T11:00:00Z'),
           'social': datetime.fromisoformat('2026-11-14T11:00:00Z')}


def check(value, code):
    if not value:
        raise AssertionError(code)


def refused(code, action):
    try:
        action()
    except ValueError as exc:
        check(str(exc) == code, 'WRONG_REFUSAL')
    else:
        raise AssertionError('GUARD_REMOVED')


def forbidden(*args, **kwargs):
    raise AssertionError('ISOLATION_VIOLATION')


def clock_at(instant):
    clock = Clock()
    clock.origin = instant
    return clock


@contextmanager
def isolated(root):
    """Remove credentials, deny sockets/commands, and confine Git to temporary paths."""
    original_git, popen = publish.git, subprocess.Popen
    def local_git(directory, *args, **kwargs):
        check(Path(directory).resolve().is_relative_to(root.resolve()), 'NONLOCAL_GIT')
        # Keep production freeze checks active; only the disposable ref name changes.
        args = tuple(a.replace('refs/heads/data', 'refs/heads/rehearsal-data') for a in args)
        return original_git(directory, *args, **kwargs)
    def local_process(command, *args, **kwargs):
        check(isinstance(command, list) and command[:4] == ['git', '-c', 'core.hooksPath=/dev/null', '-C']
              and not kwargs.get('shell'), 'COMMAND_DENIED')
        check(Path(command[4]).resolve().is_relative_to(root.resolve()), 'NONLOCAL_GIT')
        return popen(command, *args, **kwargs)
    env = dict(PATH=os.environ.get('PATH', ''), HOME=str(root), TMPDIR=str(root),
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_ALLOW_PROTOCOL='file',
               GIT_TERMINAL_PROMPT='0')
    with patch.dict(os.environ, env, clear=True), patch.object(tempfile, 'tempdir', str(root)), \
            patch.object(socket, 'socket', forbidden), patch.object(subprocess, 'Popen', local_process), \
            patch.object(publish, 'git', local_git):
        yield


def startup(root):
    raw, calls = captures(), []
    clock = clock_at(OPEN - timedelta(seconds=1))
    refused('PUBLICATION_FROZEN', lambda: night_live.cycle(acquire=forbidden, now=clock.now))
    clock.sleep(1)
    def acquire(path):
        calls.append(path)
        return raw[path]
    captured = night_live.cycle(acquire=acquire, now=clock.now, monotonic=clock.monotonic)
    check(captured['retrieved_at'] == '2026-11-07T06:00:00Z' and len(calls) == 78, 'STARTUP_BOUNDARY')
    clock = clock_at(OPEN + timedelta(minutes=10) - timedelta(seconds=1))
    check(night_start.should_start(clock.now, []) is False, 'WATCHDOG_EARLY')
    clock.sleep(1)
    check(night_start.should_start(clock.now, []) is True, 'WATCHDOG_START')


def freeze_edges(root):
    for instant, frozen in ((FREEZE - timedelta(seconds=1), False), (FREEZE, True),
                            (OPEN - timedelta(seconds=1), True), (OPEN, False)):
        action = lambda: deployment_guard.require_publication_allowed(instant.isoformat())
        if frozen:
            refused('PUBLICATION_FROZEN', action)
        else:
            action()


def seeded(root):
    clock = clock_at(OPEN)
    captured = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
    checkout, remote = root / 'seed', root / 'remote.git'
    checkout.mkdir()
    daily_refresh(checkout / publish.DATA, loaders={'night': lambda: night_live.loaded(captured)},
                  now=night_live.stamp(clock.now), sha='a' * 40)
    publish.git(checkout, 'init', '-q', '-b', 'rehearsal-data')
    publish.git(checkout, 'config', 'user.name', 'Boundary drill')
    publish.git(checkout, 'config', 'user.email', 'boundary@example.invalid')
    publish.git(checkout, 'add', '--', str(publish.DATA))
    publish.git(checkout, 'commit', '-qm', 'Offline boundary baseline')
    baseline = publish.git(checkout, 'rev-parse', 'HEAD').stdout.strip()
    clock.sleep(1)
    daily_refresh(checkout / publish.DATA, loaders={'night': lambda: night_live.loaded(captured)},
                  now=night_live.stamp(clock.now), sha='a' * 40)
    publish.git(checkout, 'add', '--', str(publish.DATA))
    publish.git(checkout, 'commit', '-qm', 'Offline boundary newer status')
    publish.git(root, 'clone', '--bare', str(checkout), str(remote))
    return checkout / publish.DATA, remote, baseline, captured


def queued(root, *, rollback, offset):
    bundle, remote, baseline, captured = seeded(root)
    before = publish.git(remote, 'show-ref').stdout
    clock = clock_at(FREEZE - timedelta(seconds=2))
    pushed = []
    def queue(attempt):
        pushed.append(attempt)
        clock.seconds = 2 + offset
    def publisher(data, repository, **kwargs):
        return publish.publish(data, repository, before_push=queue, **kwargs)
    if rollback:
        # Real pinning, validation and rollback orchestration; no Pages adapter exists.
        def verify(data):
            from product.nz_election.pipeline import verify as verifier
            from product.nz_election.pipeline import export
            envs = export.validate_bundle(data)
            verifier.verify_night(envs, root, data=data)
            verifier.verify_waterfall(envs, root, data=data)
            return ['PASS night', 'PASS waterfall']
        action = lambda: result_import.run('settled', '', baseline, repository=remote,
            now=lambda: night_live.stamp(clock.now), run_url='offline-boundary', rollback=True,
            verifier=verify, publisher=publisher)
    else:
        # A new attempt status ensures the queued job reaches the leased push boundary.
        daily_refresh(bundle, loaders={'night': lambda: night_live.loaded(captured)},
                      now='2026-11-07T06:00:02Z', sha='a' * 40)
        action = lambda: publisher(bundle, remote, family='night', now=lambda: night_live.stamp(clock.now))
    if offset == 0:
        refused('PUBLICATION_FROZEN', action)
        check(publish.git(remote, 'show-ref').stdout == before, 'FROZEN_REF_CHANGED')
    else:
        # Successful local publication is a positive control for the exact freeze second.
        result = action()
        if not rollback:
            check(result['outcome'] == 'published', 'PRE_FREEZE_NOT_PUBLISHED')
        check(publish.git(remote, 'show-ref').stdout != before, 'POSITIVE_CONTROL_NO_CHANGE')
    check(pushed == [0], 'QUEUE_NOT_REACHED')
    refs = publish.git(remote, 'for-each-ref', '--format=%(refname)').stdout.splitlines()
    check(refs == ['refs/heads/rehearsal-data'], 'PRODUCTION_REF_CREATED')


def frozen_entry(root, *, rollback):
    clock = clock_at(FREEZE - timedelta(seconds=1))
    deployment_guard.require_publication_allowed(night_live.stamp(clock.now))
    clock.sleep(1)
    # Queued entry must stop before even reading a capture or pinning a repository.
    refused('PUBLICATION_FROZEN', lambda: result_import.run('settled', '', 'a' * 40,
        repository=root / 'absent.git', now=lambda: night_live.stamp(clock.now),
        run_url='offline-boundary', rollback=rollback, capture_reader=forbidden,
        pin_data=forbidden, publisher=forbidden, deploy=forbidden))


def inflight(root, *, phase):
    clock = clock_at(STOP - timedelta(seconds=1))
    raw, calls, commits, recovered, deployed = captures(), [], [], [], []
    last_good = night_live.cycle(acquire=raw.__getitem__, now=lambda: STOP - timedelta(seconds=2))
    def acquire(path):
        calls.append(path)
        if phase == 'acquisition':
            clock.sleep(1)
        return raw[path]
    class LocalDeployment(night_live.Deployment):
        def served(self):
            return None

        def deploy(self, sha):
            check(clock.now() == STOP, 'FINISHING_CLOCK')
            deployed.append(sha)

    def commit(captured):
        check(clock.now() < STOP, 'LATE_COMMIT')
        commits.append(captured)
        def publication(bundle):
            from product.nz_election.pipeline import export
            export.validate_bundle(bundle)
            clock.sleep(1)
            return {'sha': 'b' * 40}
        night_live.publish_cycle(captured, rehearsal=False, publication=publication,
            deployment=LocalDeployment(clock.now), code_sha='a' * 40, run_url='offline-boundary')
    runner = night_live.Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic,
        sleep=clock.sleep, commit=commit, recover=lambda: recovered.append(True), log=lambda *a, **k: None)
    runner.last_good = last_good
    if phase == 'wait':
        runner.next_cycle = 1
    outcomes = night_live.run_until(runner, 600, successor=forbidden)
    expected = {'wait': ['ended'], 'acquisition': ['retained'], 'publication': ['changed']}[phase]
    check(outcomes == expected and clock.now() == STOP, 'INFLIGHT_STOP')
    check(len(calls) == {'wait': 0, 'acquisition': 1, 'publication': 78}[phase], 'LATE_ACQUISITION')
    check(len(commits) == (phase == 'publication'), 'PARTIAL_COMMIT')
    check(deployed == (['b' * 40] if phase == 'publication' else []), 'FINISHING_DEPLOYMENT')
    check(len(recovered) == (phase != 'wait'), 'LATE_RECOVERY')
    if phase != 'publication':
        check(runner.last_good is last_good, 'LAST_GOOD_CHANGED')
    check(night_live.chain(clock.now) is False, 'LATE_SUCCESSOR')


def watchdog(root, *, queued=False):
    clock = clock_at(STOP - timedelta(seconds=1))
    calls = []
    def history(*args, **kwargs):
        calls.append('history')
        if queued:
            clock.sleep(1)
        return b'[]'
    def dispatch(*args, **kwargs):
        calls.append('dispatch')
    with patch.object(night_start.subprocess, 'check_output', history), patch.object(night_start.subprocess, 'run', dispatch):
        check(night_start.main(clock.now, dispatch=True) == (1 if queued else 0), 'WATCHDOG_CUTOFF')
        check(calls == (['history'] if queued else ['history', 'dispatch']), 'WATCHDOG_CALLS')
        clock.origin = STOP
        calls.clear()
        check(night_start.main(clock.now, dispatch=True) == 1 and not calls, 'WATCHDOG_LATE_WORK')


def sunset(root, *, kind, event, offset):
    clock = clock_at(SUNSETS[kind] + timedelta(seconds=offset))
    expected = offset == -1 or (kind == 'daily' and event == 'workflow_dispatch')
    check(sunsets.allowed(kind, clock.now(), event) is expected, 'SUNSET_ALLOWED')
    with patch.dict(os.environ, GITHUB_EVENT_NAME=event, GITHUB_OUTPUT=str(root / 'output')):
        check(sunsets.skip(kind, clock.now()) is not expected, 'SUNSET_SKIP')
        if expected:
            sunsets.require_collection(kind, clock.now(), event)
        else:
            try:
                sunsets.require_collection(kind, clock.now(), event)
            except sunsets.SunsetReached as exc:
                check(str(exc) == kind.upper() + '_CLOSED', 'SUNSET_CODE')
            else:
                raise AssertionError('SUNSET_GUARD_REMOVED')


def scenarios():
    cases = {'startup': startup, 'freeze-edges': freeze_edges}
    for rollback in (False, True):
        cases['queued-' + ('rollback' if rollback else 'import') + '-entry-freeze'] = partial(frozen_entry, rollback=rollback)
        for offset, label in ((-1, 'before'), (0, 'at')):
            cases[f'queued-{"rollback" if rollback else "publish"}-{label}-freeze'] = partial(queued, rollback=rollback, offset=offset)
    for phase in ('wait', 'acquisition', 'publication'):
        cases['inflight-' + phase] = partial(inflight, phase=phase)
    cases['watchdog-cutoff'] = watchdog
    cases['watchdog-queued-cutoff'] = partial(watchdog, queued=True)
    for kind in SUNSETS:
        for event, label in (('schedule', 'schedule'), ('workflow_dispatch', 'manual')):
            for offset, position in ((-1, 'before'), (0, 'at')):
                cases[f'sunset-{kind}-{label}-{position}'] = partial(sunset, kind=kind, event=event, offset=offset)
    return cases


def run_scenario(name):
    with tempfile.TemporaryDirectory(prefix='nz-boundary-') as tmp:
        with isolated(Path(tmp)), redirect_stdout(io.StringIO()):
            scenarios()[name](Path(tmp))


def main():
    failed = False
    for name in scenarios():
        try:
            run_scenario(name)
        except Exception as exc:
            code = str(exc) if isinstance(exc, AssertionError) and str(exc).isidentifier() else type(exc).__name__
            print(f'FAIL {name} {code}')
            failed = True
        else:
            print(f'PASS {name}')
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
