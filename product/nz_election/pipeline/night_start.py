# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fail-closed watchdog decision; dispatch remains in bin/tick."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.night_live import END, require_open


def should_start(now, runs):
    instant = now()
    require_open(lambda: instant)
    if instant < END + timedelta(minutes=10):
        return False
    return not any(run['status'] != 'completed' or
                   datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00')) >= END
                   for run in runs)


def main(now=lambda: datetime.now(timezone.utc)):
    try:
        if not should_start(now, []):
            return 1
        runs = json.loads(subprocess.check_output([
            'gh', 'run', 'list', '--workflow', 'nz-election-night-live.yml',
            '--limit', '100', '--json', 'status,createdAt'], timeout=60))
        return 0 if should_start(now, runs) else 1
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        return 1


if __name__ == '__main__':
    sys.exit(main())
