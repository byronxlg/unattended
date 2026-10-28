# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fail-closed eligibility and dispatch under the outer watchdog deadline and lock."""
from datetime import datetime, timedelta, timezone
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.night_live import END, require_open


GRACE = timedelta(minutes=10)
MAX_ATTEMPTS = 6


def timestamp(value):
    instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if instant.tzinfo is None:
        raise ValueError('Invalid timestamp')
    return instant


def should_start(now, runs):
    instant = now()
    if not isinstance(instant, datetime) or instant.tzinfo is None or type(runs) is not list:
        raise ValueError('Invalid clock or history')
    require_open(lambda: instant)
    if instant < END + GRACE:
        return False
    if any(run['status'] != 'completed' for run in runs):
        return False
    recent = [run for run in runs if timestamp(run['createdAt']) >= END]
    if not recent:
        return True
    newest = max(recent, key=lambda run: timestamp(run['createdAt']))
    # Incomplete history cannot establish a terminal outcome or successor age.
    if not newest.get('conclusion') or not newest.get('updatedAt'):
        return False
    finished = timestamp(newest['updatedAt'])
    if finished > instant:
        return False
    return newest['conclusion'] != 'success' or instant - finished >= GRACE


def reserve(state, instant):
    """Called under the shared lock, before dispatch, including uncertain failures."""
    path = state / 'night-recovery-2026.json'
    attempts = json.loads(path.read_text()) if path.exists() else []
    if not isinstance(attempts, list):
        raise ValueError('Invalid recovery ledger')
    dates = [timestamp(value) for value in attempts]
    if len(dates) >= MAX_ATTEMPTS or any(instant - value < GRACE for value in dates):
        return False
    attempts.append(instant.isoformat())
    pending = path.with_suffix('.tmp')
    with pending.open('w') as stream:
        json.dump(attempts, stream)
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(path)
    return True


@contextmanager
def dispatch_lock(state):
    inherited_state = os.environ.get('NIGHT_WATCHDOG_STATE')
    state = Path(state) if state is not None else Path(inherited_state) if inherited_state else None
    if state is None:
        raise ValueError('Dispatch requires shared state')
    path = state / 'night-start.lock'
    inherited_fd = os.environ.get('NIGHT_WATCHDOG_LOCK_FD')
    if inherited_fd is not None:
        # Reuse the wrapper's open file description so its inherited lock survives SIGKILL.
        lock = os.fdopen(os.dup(int(inherited_fd)), 'a')
    else:
        lock = path.open('a')
    with lock:
        actual, expected = os.fstat(lock.fileno()), path.stat()
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise ValueError('Wrong watchdog lock')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield state, lock.fileno()


def main(now=lambda: datetime.now(timezone.utc), *, dispatch=False, state=None):
    try:
        if dispatch:
            with dispatch_lock(state) as (locked_state, lock_fd):
                return _check(now, dispatch=True, state=locked_state, lock_fd=lock_fd)
        return _check(now)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.SubprocessError):
        return 1


def _check(now, *, dispatch=False, state=None, lock_fd=None):
    try:
        if not should_start(now, []):
            return 1
        runs = json.loads(subprocess.check_output([
            'gh', 'run', 'list', '--workflow', 'nz-election-night-live.yml',
            '--limit', '100', '--json', 'status,createdAt,conclusion,updatedAt'], timeout=60))
        if not should_start(now, runs):
            return 1
        if dispatch:
            # Re-read the clock after the potentially slow run-list request, at dispatch.
            if not should_start(now, []):
                return 1
            if not reserve(state, now()):
                return 1
            require_open(now)
            subprocess.run(['gh', 'workflow', 'run', 'nz-election-night-live.yml', '--ref', 'main'],
                           check=True, timeout=60, pass_fds=(lock_fd,))
        return 0
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.SubprocessError):
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dispatch', action='store_true')
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    sys.exit(main(dispatch=args.dispatch, state=args.state))
