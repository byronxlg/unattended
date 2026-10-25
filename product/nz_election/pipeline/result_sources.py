"""Declared result acquisition sources, independent of operator state labels."""
from datetime import date, datetime
from zoneinfo import ZoneInfo
from .fetch import NIGHT_ROOTS

OFFICIAL_RESULTS_DATE = date(2026, 11, 27)
# Inferred URL: confirm against the EC once official results are published.
OFFICIAL_RESULTS_ROOT = 'https://electionresults.govt.nz/electionresults_2026/xml/'
ROOTS = dict(preliminary=NIGHT_ROOTS[0], demo=NIGHT_ROOTS[1], official=OFFICIAL_RESULTS_ROOT)


def source(kind):
    return dict(kind=kind, url=ROOTS[kind] + 'election.xml')


def root(record):
    if (type(record) is not dict or set(record) != {'kind', 'url'}
            or type(record['kind']) is not str or record['kind'] not in ROOTS
            or record != source(record['kind'])):
        raise ValueError('NIGHT_STATE')
    return ROOTS[record['kind']]


def official_date_reached(retrieved_at):
    try:
        instant = datetime.fromisoformat(retrieved_at.replace('Z', '+00:00'))
        return instant.tzinfo is not None and instant.astimezone(ZoneInfo('Pacific/Auckland')).date() >= OFFICIAL_RESULTS_DATE
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def due_date():
    return f'{OFFICIAL_RESULTS_DATE.day} {OFFICIAL_RESULTS_DATE:%B}'


def official_results_notice(built, rows=()):
    if any(row.get('result_state') == 'official' for row in rows):
        return 'Official results are published.'
    if official_date_reached(built):
        return 'Check the Electoral Commission for official results.'
    return f'Official results due {due_date()}.'
