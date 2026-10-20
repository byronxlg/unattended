"""Offline EC disclosed-return totals, not a measure of total party funding."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from . import snapshots as s

LICENCE = 'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.'
# EC's return guidance defines exceeding $20,000 as $20,000.01 or more.
MINIMUM_CENTS = 2_000_001
# Reuse product IDs; the last two labels have no ID in its polling party-map.
PARTY_IDS = {
    'The New Zealand National Party': 'nat',
    'New Zealand Labour Party': 'lab',
    'The Green Party of Aotearoa New Zealand': 'grn',
    'ACT New Zealand': 'act',
    'New Zealand First Party': 'nzf',
    'Te Pāti Māori': 'tpm',
    'Opportunity Party': 'opp',
    'The Opportunities Party': 'opp',
    'NZ Outdoors & Freedom Party': 'nzof',
    'Te Tai Tokerau Party': 'tttp',
}
INDEX_URL = ('https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/'
             'donations-exceeding-20000')
# Preserve the index's contradiction without allowing arbitrary chronology bypasses.
DATE_EXCEPTION = {
    'id': 'ec-2026-065',
    'party': 'Opportunity Party',
    'donor': 'Alajamber Limited',
    'amount_nzd': '21140',
    'received': '2026-07-08',
    'disclosed': '2026-06-30',
    'source_url': INDEX_URL,
    'document_url': ('https://elections.nz/assets/2026-20k%2B-donations/'
                     'Alajamber_Limited_30_July_2026.pdf'),
    'date_exception': 'ec-index-alajamber-2026',
}


def _ec_url(value):
    if not s._ec_source(value) or '\\' in value or any(ord(c) < 32 for c in value):
        return False
    try:
        return urlsplit(value).port in (None, 443)
    except ValueError:
        return False


def amount_cents(value):
    """Accept exact NZD decimal strings only; never coerce floats or round cents."""
    s._require(isinstance(value, str) and bool(re.fullmatch(
        r'(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?', value)),
        'donations_amount_invalid: expected exact NZD decimal string')
    whole, _, fraction = value.partition('.')
    cents = int(whole) * 100 + int(fraction.ljust(2, '0'))
    s._require(cents >= MINIMUM_CENTS, 'donations_amount_below_threshold: exceeds $20,000')
    return cents


def _timestamp(value):
    try:
        s._timestamp(value)
    except (ValueError, TypeError):
        raise ValueError('donations_retrieved_at: expected UTC timestamp') from None


def _date(value):
    try:
        s._date(value)
    except (ValueError, TypeError):
        raise ValueError('donations_date_invalid: expected calendar date') from None


def load_donations(path=None):
    """Validate provenance, exact amounts, chronology and explicit correction links.

    received is the last receipt date for an aggregated return. disclosed is the
    date EC received the return, not its signature date or website publication.
    replaces identifies an earlier record by ID, or an EC index URL and locator
    when EC only publishes the amended PDF. Original values are never inferred.
    One pinned index date contradiction is retained explicitly, not corrected.
    """
    path = Path(path) if path is not None else s.SNAPSHOTS / 'donations.json'
    s._require(not path.is_symlink(), 'donations_schema: symlink')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('donations_schema: unreadable JSON snapshot') from None
    s._require(isinstance(data, dict) and data.get('schema') == 'donations-v1',
               'donations_schema: envelope')
    _timestamp(data.get('retrieved_at'))
    s._require(_ec_url(data.get('source_url')), 'donations_source_invalid: EC index URL')
    s._require(data.get('licence') == LICENCE and s._text(data.get('terms_note'))
               and _ec_url(data.get('terms_url')), 'donations_licence: terms required')
    rows = data.get('records')
    s._require(isinstance(rows, list) and bool(rows), 'donations_schema: records')
    skipped = data.get('skipped_returns')
    count = data.get('listed_return_count')
    s._require(isinstance(skipped, list) and type(count) is int and count >= 0
               and len(rows) + len(skipped) == count,
               'donations_count_mismatch: records plus skips must equal listed returns')
    for row in skipped:
        s._require(isinstance(row, dict) and s._text(row.get('reason'))
                   and _ec_url(row.get('source_url')) and s._text(row.get('source_locator'))
                   and any(not s._text(row.get(k)) for k in ('party', 'donor', 'amount_nzd')),
                   'donations_skip_invalid: only incomplete index facts may be skipped')
    identities, duplicates = {}, {}
    for row in rows:
        s._require(isinstance(row, dict), 'donations_record: expected object')
        identity = row.get('id')
        s._require(s._text(identity), 'donations_record: id')
        for field in ('party', 'donor', 'source_locator', 'document_locator'):
            s._require(s._text(row.get(field)), 'donations_record: ' + field)
        party_id = row.get('party_id')
        s._require(isinstance(party_id, str) and party_id in PARTY_IDS.values()
                   and PARTY_IDS.get(row['party']) == party_id,
                   'donations_party_id: unknown or mismatched party id')
        s._require(type(row.get('document_checked')) is bool,
                   'donations_document_checked: expected boolean')
        if row['document_checked']:
            s._require(s._text(row.get('document_check_note')),
                       'donations_document_checked: comparison note required')
            _timestamp(row.get('document_checked_at'))
        for field in ('document_url', 'source_url'):
            s._require(_ec_url(row.get(field)), 'donations_source_invalid: ' + field)
        _timestamp(row.get('retrieved_at'))
        s._require(row.get('licence') == LICENCE, 'donations_licence: record licence')
        cents = amount_cents(row.get('amount_nzd'))
        for field in ('received', 'disclosed'):
            if field in row:
                _date(row[field])
        if 'date_exception' in row:
            s._require(all(row.get(k) == v for k, v in DATE_EXCEPTION.items())
                       and s._text(row.get('date_note')),
                       'donations_date_exception: expected exact sourced conflict')
        elif 'received' in row and 'disclosed' in row:
            s._require(row['received'] <= row['disclosed'],
                       'donations_date_order: received after disclosed')
        previous = row.get('replaces')
        if 'replaces' in row:
            s._require(isinstance(previous, dict), 'donations_correction: expected link')
            if 'record_id' in previous:
                target = previous['record_id']
                s._require(s._text(target) and target in identities
                           and identities[target]['party'] == row['party']
                           and identities[target]['donor'] == row['donor'],
                           'donations_correction: earlier matching record required')
            else:
                s._require(_ec_url(previous.get('source_url'))
                           and s._text(previous.get('source_locator')),
                           'donations_correction: EC source and locator required')
                _date(previous.get('disclosed'))
                s._require('disclosed' in row and previous['disclosed'] < row['disclosed'],
                           'donations_correction: amendment must follow original')
        key = (row['party'], row['donor'], cents, row.get('received'))
        if key in duplicates:
            s._require(isinstance(previous, dict)
                       and previous.get('record_id') == duplicates[key],
                       'donations_duplicate: explicit link to prior record required')
        s._require(identity not in identities, 'donations_record: duplicate id')
        duplicates[key] = identity
        identities[identity] = row
    return rows
