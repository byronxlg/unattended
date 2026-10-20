"""National advance observations, with explicit column semantics and gap preservation."""
import csv
from datetime import date, timedelta
import io
import json
import re
from . import export
from .fixtures import ROOT, captures

ATTRIBUTION = 'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.'
ERROR = 'INVALID_ADVANCE'


def normalize(observations, *, kind, start):
    """A complete replacement capture supplies one observation per date."""
    try:
        export.calendar_date(start, 'advance start')
        if kind not in ('daily', 'cumulative') or not isinstance(observations, list) or not observations:
            raise ValueError(ERROR)
        values = {}
        for day, count in observations:
            export.calendar_date(day, 'advance date')
            if day < start or day in values or type(count) is not int or not 0 <= count <= 10000000:
                raise ValueError(ERROR)
            values[day] = count
        previous, total, complete = None, 0, True
        result = []
        for day, count in sorted(values.items()):
            adjacent = previous is not None and date.fromisoformat(day) - date.fromisoformat(previous) == timedelta(days=1)
            if kind == 'daily':
                complete = complete and (adjacent if previous else day == start)
                total += count
                daily, cumulative = count, total if complete else None
            else:
                if previous and count < values[previous]:
                    raise ValueError(ERROR)
                daily = count - values[previous] if adjacent else count if day == start else None
                cumulative = count
            result.append(dict(date=day, daily=daily, cumulative=cumulative))
            previous = day
        return result
    except (ValueError, TypeError, OverflowError):
        raise ValueError(ERROR) from None


def parse(raw, *, kind, start, date_column='Date', count_column='2023 General Election'):
    try:
        if not isinstance(raw, bytes) or len(raw) > 1000000:
            raise ValueError(ERROR)
        records = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        if not records or date_column not in records[0] or count_column not in records[0]:
            raise ValueError(ERROR)
        observations = []
        for row in records:
            if None in row or any(v is None for v in row.values()):
                raise ValueError(ERROR)
            day, value = row[date_column].strip(), row[count_column].strip()
            if day.lower() in ('total', 'totals'):
                continue
            if value in ('', '-', 'closed'):
                continue
            if not re.fullmatch(r'[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+', value):
                raise ValueError(ERROR)
            if not re.fullmatch(export.DATE_PATTERN, day):
                from datetime import datetime
                day = datetime.strptime(day + ' ' + start[:4], '%d %B %Y').date().isoformat()
            observations.append((day, int(value.replace(',', ''))))
        return normalize(observations, kind=kind, start=start)
    except (ValueError, TypeError, AttributeError, UnicodeError, csv.Error):
        raise ValueError(ERROR) from None


def load(*, historical=False):
    entries = json.loads((ROOT / 'manifest.json').read_text())['entries']
    selected = [e for e in entries if e.get('advance', {}).get('year') == (2023 if historical else 2026)]
    if not selected:
        return None
    for candidate in selected:
        export.timestamp(candidate['captured_at'], 'advance capture')
    newest = max(e['captured_at'] for e in selected)
    selected = [e for e in selected if e['captured_at'] == newest]
    if len(selected) != 1:
        raise ValueError('AMBIGUOUS_ADVANCE_CAPTURE')
    entry = selected[0]
    raw = captures(ROOT, paths={entry['path']})[entry['path']]
    settings = entry['advance']
    if settings['start'][:4] != str(settings['year']):
        raise ValueError(ERROR)
    rows = parse(raw, **{k: settings[k] for k in ('kind', 'start', 'date_column', 'count_column')})
    if any(r['date'][:4] != str(settings['year']) for r in rows):
        raise ValueError(ERROR)
    source = dict(id='V:advance-voting', url=entry['url'], revision=entry['revision'], licence=entry['licence'],
                  fetched_at=entry['captured_at'], history_url=entry['archive_url'])
    for row in rows:
        row.update(id='advance-' + row['date'], observed_at=row['date'],
                   source_ref=[dict(source_id=source['id'], locator='date=' + row['date'],
                                    field=field) for field in ('date', 'daily', 'cumulative')],
                   input_kind=settings['kind'], span_start=settings['start'])
    return {'advance-voting': rows}, [source], {'fixtures/' + entry['path']: entry['sha256']}


def validate(rows):
    if not rows:
        raise ValueError(ERROR)
    try:
        kind, start = rows[0]['input_kind'], rows[0]['span_start']
        expected = normalize([(r['date'], r[kind]) for r in rows], kind=kind, start=start)
        for row, derived in zip(rows, expected):
            if (any(row[k] != v for k, v in derived.items()) or row['input_kind'] != kind or
                    row['span_start'] != start or row['observed_at'] != row['date'] or
                    row['id'] != 'advance-' + row['date']):
                raise ValueError(ERROR)
    except (KeyError, TypeError, ValueError):
        raise ValueError(ERROR) from None
