"""Fail closed before building or deploying during the election publication freeze."""
import argparse
from datetime import datetime, timezone

# Thirty minutes also covers the deployment action's ten-minute timeout and queue margin.
START = datetime.fromisoformat('2026-11-06T10:30:00+00:00')
END = datetime.fromisoformat('2026-11-07T06:00:00+00:00')


def require_publication_allowed(now):
    instant = datetime.fromisoformat(now.replace('Z', '+00:00'))
    if instant.tzinfo is None:
        raise ValueError('INVALID_TIMESTAMP')
    if START <= instant < END:
        raise ValueError('PUBLICATION_FROZEN')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--now', default=None)
    args = parser.parse_args()
    try:
        require_publication_allowed(args.now or datetime.now(timezone.utc).isoformat())
    except ValueError:
        raise SystemExit('PUBLICATION_FROZEN') from None
    print('PASS publication time')


if __name__ == '__main__':
    main()
