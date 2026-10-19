"""Offline, hand-reviewed facts. This module never acquires source data."""
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PRODUCT = Path(__file__).resolve().parents[1]
SNAPSHOTS = PRODUCT / 'snapshots'
NAMES = frozenset({'leaders', 'candidates-2026', 'enrolment', 'port-waikato-2023',
                   'history', 'hexmap', 'positions'})
BANNED = re.compile(r'\b(?:not available|unavailable|pending|missing)\b', re.I)
PHOTO_LICENCES = frozenset({'CC0', 'CC BY 4.0', 'CC BY-SA 4.0', 'CC BY 3.0',
                            'CC BY-SA 3.0', 'Public domain', 'NZ Crown copyright'})


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _url(value):
    if not _text(value):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme in {'http', 'https'} and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and not any(c.isspace() for c in value))
    except ValueError:
        return False


def _timestamp(value):
    _require(isinstance(value, str) and bool(re.fullmatch(
        r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', value)), 'Invalid retrieval timestamp')
    datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')


def _date(value):
    _require(isinstance(value, str) and bool(re.fullmatch(r'\d{4}-\d\d-\d\d', value)),
             'Invalid observation date')
    date.fromisoformat(value)


def _integer(value, minimum=0):
    return type(value) is int and minimum <= value <= 10**12


def _photo(photo):
    _require(isinstance(photo, dict), 'Photo must be an object')
    for key in ('path', 'author', 'licence', 'changes'):
        _require(_text(photo.get(key)), 'Photo requires ' + key)
    for key in ('source_url', 'licence_url'):
        _require(_url(photo.get(key)), 'Photo requires ' + key)
    _timestamp(photo.get('retrieved_at'))
    _require(photo['licence'] in PHOTO_LICENCES, 'Photo licence does not permit reuse')
    _require(bool(re.fullmatch(r'web/people/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:webp|jpg)',
                              photo['path'])), 'Invalid photo path')
    path = PRODUCT / photo['path']
    _require(path.resolve().is_relative_to((PRODUCT / 'web/people').resolve())
             and not path.is_symlink() and path.is_file(), 'Photo file must exist locally')
    _require(0 < path.stat().st_size < 40_000, 'Photo exceeds byte budget')


def load(name):
    """Return validated record dictionaries for one allowlisted snapshot stem.

    Optional facts are absent. Parties outside party-map retain their source label
    in ``party`` and omit ``party_id``; they are never assigned the Others aggregate.
    Percentages are decimal strings. Tile x/y are square-grid column/row indices.
    Invalid envelopes, records, identifiers and photo metadata raise ValueError.
    """
    _require(isinstance(name, str) and name in NAMES, 'Unknown snapshot name')
    path = SNAPSHOTS / (name + '.json')
    _require(not path.is_symlink(), 'Snapshot must not be a symlink')
    raw = path.read_text(encoding='utf-8')
    _require(not BANNED.search(raw), 'Snapshot contains a banned phrase')
    data = json.loads(raw)
    _require(isinstance(data, dict) and data.get('schema') == name + '-v1',
             'Invalid snapshot schema')
    _timestamp(data.get('retrieved_at'))
    rows = data.get('records')
    _require(isinstance(rows, list), 'Records must be an array')
    electorates = {r['slug']: r for r in json.loads(
        (PRODUCT / 'config/electorates.json').read_text())}
    parties = {r['id'] for r in json.loads((PRODUCT / 'config/party-map.json').read_text())
               ['parties'] if not r['aggregate']}
    seen, cells = set(), set()
    required = {
        'leaders': ('name', 'role'),
        'candidates-2026': ('name', 'party', 'electorate_slug'),
        'enrolment': ('electorate_slug', 'enrolled', 'as_at', 'roll'),
        'port-waikato-2023': ('name', 'party', 'votes', 'winner', 'electorate_slug', 'election_date'),
        'history': ('year', 'party', 'party_vote_share', 'seats'),
        'hexmap': ('electorate_slug', 'x', 'y', 'group', 'method'),
        'positions': ('party_id', 'quote', 'date', 'speaker'),
    }[name]
    for row in rows:
        _require(isinstance(row, dict) and all(k in row for k in required),
                 'Record lacks required fields')
        _require(all(v is not None for v in row.values()), 'Omit unsourced fields')
        _require(_url(row.get('source_url')), 'Record requires source_url')
        _timestamp(row.get('retrieved_at'))
        _require(_text(row.get('licence')), 'Record requires licence')
        if name == 'leaders':
            _require('party_id' in row or _text(row.get('party')), 'Leader requires party identity')
        for key in ('name', 'party', 'role', 'method', 'speaker', 'quote'):
            if key in row:
                _require(_text(row[key]), 'Invalid ' + key)
        if 'party_id' in row:
            _require(isinstance(row['party_id'], str) and row['party_id'] in parties,
                     'Unknown party id')
        if 'electorate_slug' in row:
            _require(isinstance(row['electorate_slug'], str)
                     and row['electorate_slug'] in electorates, 'Unknown electorate slug')
        for key in ('list_rank', 'enrolled', 'votes', 'seats', 'party_votes', 'margin', 'x', 'y'):
            if key in row:
                _require(_integer(row[key], 1 if key in {'list_rank', 'margin'} else 0),
                         'Invalid ' + key)
        for key in ('sitting_mp', 'sitting_electorate_mp', 'winner'):
            if key in row:
                _require(type(row[key]) is bool, 'Invalid ' + key)
        for key in ('as_at', 'date', 'election_date'):
            if key in row:
                _date(row[key])
        if 'list_rank' in row:
            _require(_url(row.get('list_rank_source_url')), 'List rank requires source')
        if 'photo' in row:
            _require(name in {'leaders', 'candidates-2026'}, 'Unexpected photo')
            if name == 'candidates-2026':
                _require(row.get('sitting_electorate_mp') is True, 'Photo requires electorate MP')
            _photo(row['photo'])
        if name == 'history':
            _require(type(row['year']) is int and row['year'] in range(1996, 2024, 3),
                     'Invalid general election year')
            share = row['party_vote_share']
            _require(isinstance(share, str) and bool(re.fullmatch(r'\d{1,3}\.\d{1,2}', share)),
                     'Invalid vote share')
            _require(0 <= Decimal(share) <= 100, 'Invalid vote share')
        if name == 'positions':
            _require(len(row['quote'].split()) < 30, 'Quote is too long')
        if name in {'enrolment', 'hexmap'}:
            kind = row['roll' if name == 'enrolment' else 'group']
            _require(kind == electorates[row['electorate_slug']]['kind'], 'Wrong electorate group')
        if name == 'hexmap':
            cell = (row['x'], row['y'])
            _require(cell not in cells, 'Duplicate tile cell')
            cells.add(cell)
        identity = (row.get('electorate_slug'), row.get('party_id'), row.get('party'),
                    row.get('name'), row.get('year'))
        if name in {'hexmap', 'enrolment'}:
            identity = row['electorate_slug']
        _require(identity not in seen, 'Duplicate record')
        seen.add(identity)
    if name == 'hexmap':
        _require(seen == set(electorates), 'Tile layout must cover every electorate')
    if name == 'port-waikato-2023':
        _require(len(rows) >= 2 and all(r['electorate_slug'] == 'port-waikato'
                 and r['election_date'] == '2023-11-25' for r in rows), 'Invalid by-election')
        ranked = sorted(rows, key=lambda r: r['votes'], reverse=True)
        _require(sum(r['winner'] for r in rows) == 1 and ranked[0]['winner']
                 and ranked[0].get('margin') == ranked[0]['votes'] - ranked[1]['votes'] > 0,
                 'Invalid winner or margin')
    return rows
