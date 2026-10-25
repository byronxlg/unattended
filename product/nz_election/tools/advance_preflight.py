# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Inspect a local 2026 advance capture without writing files or fetching URLs."""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from product.nz_election.pipeline import advance, export

START = '2026-10-26'


def inspect(raw, *, url, archive_url=None):
    """Return a review draft; acquisition time cannot be recovered from CSV bytes."""
    try:
        for index, value in enumerate((url, archive_url)):
            if index == 1 and value is None:
                continue
            if not isinstance(value, str) or any(c.isspace() for c in value):
                raise ValueError(advance.ERROR)
            parsed = urlsplit(value)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError(advance.ERROR)
        headers, records = advance.read_csv(raw)
        dates = [h for h in headers if h.strip().lower() in ('date', 'day', 'voting date')]
        counts = [h for h in headers if h not in dates and (
            h.strip().lower() == '2026 general election' or
            re.search(r'\b(votes?|count|daily|cumulative)\b', h, re.I))]
        if len(dates) != 1 or len(counts) != 1:
            raise ValueError(advance.ERROR)
        column = counts[0]
        daily = bool(re.search(r'\b(daily|per day)\b', column, re.I))
        cumulative = bool(re.search(r'\b(cumulative|running total|to date)\b', column, re.I))
        if daily and cumulative:
            raise ValueError(advance.ERROR)
        kind = 'cumulative' if cumulative else 'daily'
        settings = dict(year=2026, kind=kind, start=START, date_column=dates[0], count_column=column)
        rows = advance.parse_records(records, **{k: settings[k] for k in ('kind', 'start', 'date_column', 'count_column')})
        if not (daily or cumulative):
            raise ValueError(advance.ERROR + ': missing daily or cumulative evidence in count header ' + repr(column))
        observed = {r['date'] for r in rows}
        day, last = date.fromisoformat(START), date.fromisoformat(rows[-1]['date'])
        gaps = []
        while day <= last:
            if day.isoformat() not in observed:
                gaps.append(day.isoformat())
            day += timedelta(days=1)
        digest = export.digest(raw)
        entry = dict(path=f'ec-2026/advance-voting-{digest[:12]}.csv', url=url,
                     archive_url=archive_url, captured_at=None, sha256=digest,
                     reviewer='Supervisor review pending', revision=None,
                     licence='Copyright Electoral Commission. No open licence stated.',
                     notes='Preflight draft. Confirm inferred kind against source documentation; '
                           'set actual captured_at, reviewer, revision and source notes before registration.',
                     bytes=len(raw), advance=settings)
        return dict(headers=headers, date_column=dates[0], count_column=column, kind=kind,
                    kind_inference=f'Inferred from explicit {kind} wording in count header {column!r}.',
                    row_count=len(records), observation_count=len(rows), first_date=rows[0]['date'],
                    last_date=rows[-1]['date'], gaps=gaps, sha256=digest, manifest_entry=entry)
    except ValueError as exc:
        if str(exc).startswith(advance.ERROR + ': missing daily or cumulative evidence'):
            raise
        raise ValueError(advance.ERROR) from None
    except (TypeError, AttributeError, UnicodeError, OverflowError):
        raise ValueError(advance.ERROR) from None


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--url', required=True)
    parser.add_argument('--archive-url')
    args = parser.parse_args(argv)
    try:
        with args.csv.open('rb') as stream:
            raw = stream.read(1000001)
        result = inspect(raw, url=args.url, archive_url=args.archive_url)
    except OSError:
        raise SystemExit(advance.ERROR) from None
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    cli()
