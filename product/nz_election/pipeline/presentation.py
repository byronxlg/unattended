"""Refresh-age semantics shared by the static views and future night view."""
from datetime import datetime

STALE_SECONDS = {'hourly': 3 * 60 * 60, 'daily': 36 * 60 * 60, 'live': 90}


def overdue(last_success, now, cadence):
    if last_success is None:
        return True
    start = datetime.fromisoformat(last_success.replace('Z', '+00:00'))
    end = datetime.fromisoformat(now.replace('Z', '+00:00'))
    return (end - start).total_seconds() > STALE_SECONDS[cadence]


def election_countdown(built):
    from datetime import date
    from zoneinfo import ZoneInfo
    from .export import timestamp
    timestamp(built, 'countdown.built')
    day = datetime.fromisoformat(built.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland')).date()
    remaining = (date(2026, 11, 7) - day).days
    return (f'{remaining} day{"s" if remaining != 1 else ""} until election day' if remaining > 0
            else 'Election day' if remaining == 0 else 'Results')


def market_price(value):
    from decimal import Decimal, ROUND_HALF_UP, localcontext
    with localcontext() as ctx:
        ctx.prec = 60
        return str((Decimal(value) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)) + '%'
