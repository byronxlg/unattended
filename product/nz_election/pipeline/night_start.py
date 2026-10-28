# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fail-closed eligibility and dispatch under the outer watchdog deadline and lock."""
from datetime import datetime, timedelta, timezone
import argparse
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
    """Called under the wrapper lock, before dispatch, including uncertain failures."""
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


def main(now=lambda: datetime.now(timezone.utc), *, dispatch=False, state=None):
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
            if state is not None and not reserve(state, now()):
                return 1
            require_open(now)
            subprocess.run(['gh', 'workflow', 'run', 'nz-election-night-live.yml', '--ref', 'main'],
                           check=True, timeout=60)
        return 0
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.SubprocessError):
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dispatch', action='store_true')
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    sys.exit(main(dispatch=args.dispatch, state=args.state))
