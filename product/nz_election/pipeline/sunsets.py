"""Shared acquisition deadlines; daily manual imports remain possible."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.deployment_guard import END

NIGHT_CLOSE = datetime.fromisoformat('2026-11-08T06:00:00Z')
HOURLY_CLOSE = END
SOCIAL_CLOSE = datetime.fromisoformat('2026-11-15T00:00:00+13:00')
DAILY_CLOSE = datetime.fromisoformat('2026-11-15T00:00:00+13:00')


def instant(now=None):
    return datetime.fromisoformat(now.replace('Z', '+00:00')) if isinstance(now, str) else now or datetime.now(timezone.utc)


def post_election(now):
    return instant(now) >= END


def allowed(kind, now=None, event=None):
    if kind == 'pages':
        if (event or os.environ.get('GITHUB_EVENT_NAME')) != 'workflow_run':
            return True
        upstream = os.environ.get('UPSTREAM_WORKFLOW')
        kind = {'NZ election hourly': 'hourly', 'NZ election daily': 'daily'}[upstream]
    deadline = {'hourly': HOURLY_CLOSE, 'daily': DAILY_CLOSE, 'social': SOCIAL_CLOSE, 'night': NIGHT_CLOSE}[kind]
    event = event or os.environ.get('GITHUB_EVENT_NAME', 'schedule')
    return (kind == 'daily' and event == 'workflow_dispatch') or instant(now) < deadline


class SunsetReached(Exception):
    """Normal collection termination, separate from source/validation failures."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind.upper() + '_CLOSED')


def require_collection(kind, now=None, event=None):
    if not allowed(kind, now, event):
        raise SunsetReached(kind)


def ended(kind):
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('skipped=true\n')
    print(f'{kind.capitalize()} scheduled collection has ended.')


def skip(kind, now=None, event=None):
    if allowed(kind, now, event):
        return False
    ended(kind)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['hourly', 'daily', 'social', 'night', 'pages'])
    parser.add_argument('--now')
    args = parser.parse_args()
    active = not skip(args.kind, args.now)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('allowed=' + str(active).lower() + '\n')


if __name__ == '__main__':
    main()
