"""Refresh-age semantics shared by the static views and future night view."""
from datetime import datetime

STALE_SECONDS = {'hourly': 3 * 60 * 60, 'daily': 36 * 60 * 60, 'live': 90}


def overdue(last_success, now, cadence):
    if last_success is None:
        return True
    start = datetime.fromisoformat(last_success.replace('Z', '+00:00'))
    end = datetime.fromisoformat(now.replace('Z', '+00:00'))
    return (end - start).total_seconds() > STALE_SECONDS[cadence]
