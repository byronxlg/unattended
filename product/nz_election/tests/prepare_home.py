# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Prepare a historical/synthetic demonstration, never a live data substitute."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.social import refresh_social, fixture_send


def main():
    data = Path('artifacts/nz-election/data')
    now = '2026-10-17T01:00:00Z'
    # A fresh output avoids the deliberate repeat-collection credit cap.
    if (data / 'social/daily.json').exists():
        raise SystemExit('Use a fresh artifacts/nz-election/data directory for demonstration preparation.')
    refresh(data, now=now, end_date='2026-07-18')
    daily_refresh(data, now=now)
    outcome = refresh_social(data, '2026-10-16', now=now, fixture=True, send=fixture_send(), sleep=lambda _: None)
    if outcome != 'ok':
        raise SystemExit(outcome)
    print('PASS home fixtures: historical July polls, synthetic October social sample; offline verification')


if __name__ == '__main__':
    main()
