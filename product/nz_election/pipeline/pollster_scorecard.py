"""Validate an offline historical scorecard without rounding or network access."""
from calendar import monthrange
from datetime import date, datetime
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from . import snapshots as s
from .poll_parser import MONTHS

DAYS = {2017: '2017-09-23', 2020: '2020-10-17', 2023: '2023-10-14'}
EC_LICENCE = 'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.'


def require(condition, code):
    s._require(condition, 'scorecard_' + code)


def decimal(value, code='decimal'):
    """Bounded decimal strings only; Fraction avoids Decimal context rounding."""
    require(isinstance(value, str) and bool(re.fullmatch(
        r'-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,12})?', value)), code)
    return Fraction(value)


def ratio(value, code):
    require(isinstance(value, dict) and set(value) == {'numerator', 'denominator'}, code)
    n, d = value['numerator'], value['denominator']
    require(isinstance(n, str) and bool(re.fullmatch(r'-?(?:0|[1-9][0-9]{0,29})', n))
            and isinstance(d, str) and bool(re.fullmatch(r'[1-9][0-9]{0,29}', d)), code)
    return Fraction(int(n), int(d))


def timestamp(value):
    try:
        s._timestamp(value)
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (TypeError, ValueError):
        raise ValueError('scorecard_retrieved_at') from None


def calendar_date(value):
    try:
        s._date(value)
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError('scorecard_fieldwork') from None


def source_url(value, ec=False):
    require(s._url(value) and '\\' not in value and not any(ord(c) < 32 for c in value),
            'source')
    try:
        u = urlsplit(value)
        valid = u.scheme == 'https' and u.port in (None, 443) and not u.fragment
        if ec:
            valid = valid and u.hostname in {'electionresults.govt.nz', 'www.electionresults.govt.nz'}
        else:
            query = parse_qs(u.query)
            valid = (valid and u.hostname == 'en.wikipedia.org' and u.path == '/w/index.php'
                     and len(query.get('oldid', [])) == 1
                     and bool(re.fullmatch(r'[1-9][0-9]{0,11}', query['oldid'][0])))
        require(valid, 'source')
    except ValueError:
        raise ValueError('scorecard_source') from None


def provenance(row, ec=False):
    require(isinstance(row, dict), 'record')
    source_url(row.get('source_url'), ec)
    timestamp(row.get('retrieved_at'))
    require(row.get('licence') == (EC_LICENCE if ec else 'CC BY-SA 4.0'), 'licence')


def identity(row):
    y, p = row.get('year'), row.get('pollster_id')
    require(type(y) is int and y in DAYS and isinstance(p, str)
            and bool(re.fullmatch(r'[a-z]+(?:-[a-z]+)*', p)), 'record')
    return y, p


def shares(value):
    require(isinstance(value, dict), 'coverage')
    for party, share in value.items():
        require(isinstance(party, str) and bool(re.fullmatch(r'[a-z0-9-]+', party))
                and party != 'others', 'coverage')
        require(0 <= decimal(share) <= 100, 'decimal')
    require(sum(map(Fraction, value.values())) <= 105, 'decimal')
    return value


def poll(row, sources, selected=False):
    provenance(row)
    year, _ = identity(row)
    require(row['source_url'] == sources[year]['source_url'], 'revision')
    require(s._text(row.get('id')) and s._text(row.get('source_locator'))
            and s._text(row.get('pollster')) and s._text(row.get('fieldwork_label')), 'record')
    try:
        published = timestamp(row.get('published_by'))
    except ValueError:
        raise ValueError('scorecard_publication') from None
    require(published.isoformat() == timestamp(sources[year]['revision_at']).isoformat(),
            'publication')
    local_day = published.astimezone(ZoneInfo('Pacific/Auckland')).date()
    require(local_day < date.fromisoformat(DAYS[year]), 'publication')
    shares(row.get('poll_shares'))
    if 'fieldwork_end' not in row:
        require(not selected and s._text(row.get('excluded_reason')), 'fieldwork')
        return False
    end = calendar_date(row['fieldwork_end'])
    require(end < date.fromisoformat(DAYS[year]) and end <= local_day, 'fieldwork')
    require(row.get('fieldwork_precision') in ('day', 'month-upper-bound'), 'fieldwork')
    month = re.fullmatch(r'([A-Za-z]+) ([0-9]{4})', row['fieldwork_label'])
    if month or row['fieldwork_precision'] == 'month-upper-bound':
        require(month is not None and month[1] in MONTHS, 'fieldwork')
        year, number = int(month[2]), MONTHS[month[1]]
        require(year > 0 and row['fieldwork_precision'] == 'month-upper-bound'
                and end == date(year, number, monthrange(year, number)[1]), 'fieldwork')
    require('excluded_reason' not in row, 'fieldwork')
    if selected:
        require(bool(row['poll_shares']), 'absent_comparable_input')
    return bool(row['poll_shares'])


def load_pollster_record(path=None):
    """Return final records. All failures use a scorecard_* ValueError name.

    Exact ratios encode repeating percentages without pretending finite decimal
    strings are exact. published_by proves a cutoff, not an original release date.
    The candidate ledger makes the latest eligible fieldwork selection auditable.
    """
    path = Path(path) if path is not None else s.SNAPSHOTS / 'pollster-record.json'
    require(not path.is_symlink(), 'schema')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('scorecard_schema') from None
    require(isinstance(data, dict) and data.get('schema') == 'pollster-record-v1', 'schema')
    timestamp(data.get('retrieved_at'))
    require(data.get('licence') == 'CC BY-SA 4.0' and s._text(data.get('attribution'))
            and data.get('licence_url') == 'https://creativecommons.org/licenses/by-sa/4.0/',
            'licence')
    require(isinstance(data.get('method'), dict) and all(s._text(data['method'].get(k))
            for k in ('scope', 'selection', 'publication', 'revisions', 'arithmetic',
                      'rounding', 'naming', 'comparison')), 'schema')
    for key in ('records', 'sources', 'official_results', 'candidates', 'skipped'):
        require(isinstance(data.get(key), list), 'schema')
    require(bool(data['records']), 'absent_comparable_input')
    sources, official = {}, {}
    for row in data['sources']:
        provenance(row)
        year = row.get('year')
        require(type(year) is int and year in DAYS and year not in sources, 'revision')
        require(row.get('source_url') == 'https://en.wikipedia.org/w/index.php?oldid='
                + str(row.get('revision_id')), 'revision')
        timestamp(row.get('revision_at'))
        expected = f'pollster-record-sources/wikipedia-{year}.json.gz'
        require(row.get('capture') == expected and s._text(row.get('attribution'))
                and s._url(row.get('history_url')), 'revision')
        capture = path.parent / expected
        require(not capture.is_symlink(), 'capture')
        try:
            raw = gzip.decompress(capture.read_bytes())
            page = next(iter(json.loads(raw)['query']['pages'].values()))
            revision = page['revisions'][0]
            require(hashlib.sha256(raw).hexdigest() == row.get('sha256')
                    and str(revision['revid']) == row['revision_id']
                    and revision['timestamp'] == row['revision_at'], 'capture')
        except (OSError, EOFError, ValueError, KeyError, TypeError, IndexError, StopIteration):
            raise ValueError('scorecard_capture') from None
        sources[year] = row
    require(set(sources) == set(DAYS), 'revision')
    for row in data['official_results']:
        provenance(row, ec=True)
        y = row.get('year')
        require(type(y) is int and y in DAYS and y not in official
                and row.get('election_day') == DAYS[y], 'official')
        total = decimal(row.get('valid_party_votes'), 'official')
        require(total.denominator == 1 and total > 0, 'official')
        require(isinstance(row.get('parties'), list) and row['parties'], 'official')
        parties, votes = {}, 0
        for party in row['parties']:
            require(isinstance(party, dict) and s._text(party.get('party_id')), 'official')
            pid = party['party_id']
            require(pid not in parties, 'official')
            n = decimal(party.get('votes'), 'official')
            require(n.denominator == 1 and 0 <= n <= total, 'official')
            share = ratio(party.get('share'), 'official')
            require(share == 100 * n / total, 'official')
            parties[pid] = share
            votes += n
        require(votes == total, 'official')
        official[y] = parties
    require(set(official) == set(DAYS), 'official')
    candidates, eligible = {}, {}
    for row in data['candidates']:
        valid = poll(row, sources)
        key = identity(row)
        require(row['id'] not in candidates, 'candidate')
        candidates[row['id']] = row
        if valid:
            eligible.setdefault(key, []).append(row)
    seen = set()
    for row in data['records']:
        poll(row, sources, selected=True)
        key = identity(row)
        require(key not in seen, 'duplicate')
        seen.add(key)
        require(row.get('election_day') == DAYS[key[0]], 'fieldwork')
        comparable = set(row['poll_shares']) & set(official[key[0]])
        require(bool(comparable), 'absent_comparable_input')
        require(comparable == set(row['poll_shares']), 'coverage')
        for field, expected in [('compared_parties', comparable),
                                ('not_reported_parties', set(official[key[0]]) - comparable)]:
            actual = row.get(field)
            require(isinstance(actual, list) and all(isinstance(p, str) for p in actual)
                    and len(actual) == len(set(actual)) and set(actual) == expected, 'coverage')
        errors = row.get('party_errors')
        require(isinstance(errors, dict) and set(errors) == comparable, 'error')
        official_shares = row.get('official_shares')
        require(isinstance(official_shares, dict) and set(official_shares) == comparable, 'official')
        absolute = Fraction(0)
        for p in comparable:
            require(ratio(official_shares[p], 'official') == official[key[0]][p], 'official')
            error = Fraction(row['poll_shares'][p]) - official[key[0]][p]
            require(ratio(errors[p], 'error') == error, 'error')
            absolute += abs(error)
        require(ratio(row.get('mean_absolute_error'), 'mean') == absolute / len(comparable), 'mean')
        require(key in eligible, 'final_poll')
        latest = max(eligible[key], key=lambda c: (c['fieldwork_end'], c['published_by']))
        require(row['id'] == latest['id'] and all(row.get(k) == v for k, v in latest.items()),
                'final_poll')
    require(seen == set(eligible), 'final_poll')
    for row in data['skipped']:
        provenance(row)
        key = identity(row)
        require(key not in seen and s._text(row.get('reason'))
                and row['source_url'] == sources[key[0]]['source_url'], 'skip')
        seen.add(key)
    pollsters = {p for _, p in seen}
    require(seen == {(y, p) for y in DAYS for p in pollsters}, 'skip')
    return data['records']
