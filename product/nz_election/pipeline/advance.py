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


def read_csv(raw):
    """Validate all CSV syntax before consumers can discard columns or total rows."""
    try:
        if not isinstance(raw, bytes) or len(raw) > 1000000:
            raise ValueError(ERROR)
        text = raw.decode('utf-8-sig')
        # csv's strict mode still accepts quotes inside unquoted fields.
        state = 'start'
        for char in text:
            if state == 'quoted':
                if char == '"':
                    state = 'closed'
            elif char == '"':
                if state not in ('start', 'closed'):
                    raise ValueError(ERROR)
                state = 'quoted'
            elif char in ',\r\n':
                state = 'start'
            elif state == 'closed':
                raise ValueError(ERROR)
            else:
                state = 'unquoted'
        if state == 'quoted':
            raise ValueError(ERROR)
        reader = csv.DictReader(io.StringIO(text, newline=''), strict=True)
        headers = reader.fieldnames
        if not headers or len(headers) != len(set(headers)) or any(not h.strip() for h in headers):
            raise ValueError(ERROR)
        records = list(reader)
        if not records or any(None in row or any(v is None for v in row.values()) for row in records):
            raise ValueError(ERROR)
        return headers, records
    except (ValueError, TypeError, UnicodeError, csv.Error):
        raise ValueError(ERROR) from None


def parse(raw, *, kind, start, date_column='Date', count_column='2023 General Election'):
    return parse_records(read_csv(raw)[1], kind=kind, start=start,
                         date_column=date_column, count_column=count_column)


def parse_records(records, *, kind, start, date_column, count_column):
    """Interpret records already validated by read_csv."""
    try:
        if not records or date_column not in records[0] or count_column not in records[0]:
            raise ValueError(ERROR)
        observations = []
        for row in records:
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
            if day[:4] != start[:4]:
                raise ValueError(ERROR)
            observations.append((day, int(value.replace(',', ''))))
        return normalize(observations, kind=kind, start=start)
    except (ValueError, TypeError, AttributeError, UnicodeError, csv.Error):
        raise ValueError(ERROR) from None


def descriptor(value):
    """Reject malformed capture metadata before selecting or reading a source."""
    required = {'year', 'kind', 'start', 'date_column', 'count_column'}
    if not isinstance(value, dict) or not required <= value.keys():
        raise ValueError(ERROR)
    if (type(value['year']) is not int or not 1 <= value['year'] <= 9999 or
            value['kind'] not in ('daily', 'cumulative') or
            any(not isinstance(value[k], str) or not value[k].strip() for k in ('date_column', 'count_column')) or
            value['date_column'] == value['count_column']):
        raise ValueError(ERROR)
    try:
        export.calendar_date(value['start'], 'advance start')
    except ValueError:
        raise ValueError(ERROR) from None
    if value['start'][:4] != f"{value['year']:04d}":
        raise ValueError(ERROR)
    return value


def load(*, historical=False, year=None):
    year = (2023 if historical else 2026) if year is None else year
    if type(year) is not int or not 1 <= year <= 9999:
        raise ValueError(ERROR)
    entries = json.loads((ROOT / 'manifest.json').read_text())['entries']
    selected = []
    for entry in entries:
        if 'advance' in entry:
            settings = descriptor(entry['advance'])
            if settings['year'] == year:
                selected.append(entry)
    if not selected:
        return None
    for candidate in selected:
        export.timestamp(candidate['captured_at'], 'advance capture')
    selected.sort(key=lambda e: e['captured_at'])
    if len({e['captured_at'] for e in selected}) != len(selected):
        raise ValueError('AMBIGUOUS_ADVANCE_CAPTURE')
    raw_captures = captures(ROOT, paths={e['path'] for e in selected})
    previous_length = 0
    for entry in selected:
        settings = entry['advance']
        rows = parse(raw_captures[entry['path']],
                     **{k: settings[k] for k in ('kind', 'start', 'date_column', 'count_column')})
        if len(rows) < previous_length:
            raise ValueError('SHORTER_ADVANCE_CAPTURE')
        previous_length = len(rows)
    source = dict(id='V:advance-voting', url=entry['url'], revision=entry['revision'], licence=entry['licence'],
                  fetched_at=entry['captured_at'], history_url=entry['archive_url'])
    if 'caveat' in entry:
        source.update(caveat=entry['caveat'], provenance=entry['notes'])
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
