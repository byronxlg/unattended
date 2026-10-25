"""Offline, hand-reviewed facts. This module never acquires source data."""
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

PRODUCT = Path(__file__).resolve().parents[1]
SNAPSHOTS = PRODUCT / 'snapshots'
NAMES = frozenset({'leaders', 'candidates-2026', 'enrolment', 'port-waikato-2023',
                   'history', 'hexmap', 'positions', 'voting', 'donations', 'boundaries-2025',
                   'candidate-reconciliation-2026', 'pollster-record', 'policy-links', 'party-list-tops'})
BOUNDARY_BYTE_LIMIT = 400_000
BANNED = re.compile(r'\b(?:not available|unavailable|pending|missing)\b', re.I)
PHOTO_LICENCES = frozenset({'CC0', 'CC BY 4.0', 'CC BY-SA 4.0', 'CC BY 3.0',
                            'CC BY-SA 3.0', 'Public domain', 'NZ Crown copyright'})
RECORD_LICENCES = PHOTO_LICENCES | frozenset({
    'CC BY 4.0 (Stats NZ)',
    'Links only; no policy text reused and no reuse licence claimed.',
    'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.',
    'Copyright ACT New Zealand; no open licence stated. Short attributed quotation.',
    'Copyright NZME; no open licence stated. Short attributed quotation.',
    'Copyright News Wire; no open licence stated. Short attributed quotation.',
    'Copyright TVNZ; no open licence stated. Short attributed quotation.',
})


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


def _boundaries(data):
    """Validate locator geometry and its exact registry join, returning feature records."""
    _require(data.get('type') == 'FeatureCollection', 'Expected FeatureCollection')
    _require(data.get('licence') == 'CC BY 4.0 (Stats NZ)', 'Invalid boundary licence')
    _require(data.get('licence_url') == 'https://creativecommons.org/licenses/by/4.0/',
             'Invalid boundary licence URL')
    _require(_text(data.get('method')), 'Boundary requires simplification method')
    sources = data.get('sources')
    _require(isinstance(sources, list) and len(sources) == 2, 'Boundary requires sources')
    for source in sources:
        _require(isinstance(source, dict) and _url(source.get('source_url')),
                 'Boundary requires source_url')
        _timestamp(source.get('retrieved_at'))
        _require(source.get('licence') == data['licence'], 'Invalid source licence')
        _require(isinstance(source.get('sha256'), str) and bool(re.fullmatch(
            r'[a-f0-9]{64}', source['sha256'])), 'Invalid source digest')
    source_urls = {source['source_url'] for source in sources}
    _require(len(source_urls) == 2, 'Duplicate boundary source')
    registry = {r['id']: r for r in json.loads(
        (PRODUCT / 'config/electorates.json').read_text())}
    features = data.get('features')
    _require(isinstance(features, list) and features, 'Boundary requires features')
    rows, seen = [], set()
    for feature in features:
        _require(isinstance(feature, dict) and feature.get('type') == 'Feature',
                 'Invalid boundary feature')
        identity = feature.get('id')
        _require(isinstance(identity, str) and identity in registry, 'Unknown electorate id')
        _require(identity not in seen, 'Duplicate boundary electorate')
        seen.add(identity)
        row = feature.get('properties')
        _require(isinstance(row, dict), 'Boundary requires properties')
        for field, expected in [('electorate_slug', 'slug'), ('name', 'name'),
                                ('group', 'kind'), ('stats_id', 'stats_id')]:
            _require(row.get(field) == registry[identity][expected],
                     'Boundary electorate identity mismatch')
        _require(_url(row.get('source_url')) and row['source_url'] in source_urls,
                 'Boundary requires source_url')
        _require(row.get('licence') == data['licence'], 'Invalid boundary record licence')
        _timestamp(row.get('retrieved_at'))
        geometry = feature.get('geometry')
        _require(isinstance(geometry, dict), 'Invalid boundary geometry')
        kind = geometry.get('type')
        _require(kind in ('Polygon', 'MultiPolygon'), 'Invalid boundary geometry type')
        coordinates = geometry.get('coordinates')
        _require(isinstance(coordinates, list) and coordinates, 'Invalid boundary coordinates')
        polygons = [coordinates] if kind == 'Polygon' else coordinates
        for polygon in polygons:
            _require(isinstance(polygon, list) and polygon, 'Invalid boundary polygon')
            for ring in polygon:
                _require(isinstance(ring, list) and len(ring) >= 4, 'Invalid boundary ring')
                for point in ring:
                    _require(isinstance(point, list) and len(point) == 2,
                             'Invalid boundary point')
                    for value, limit in zip(point, (180, 90)):
                        _require(type(value) in (int, float) and -limit <= value <= limit
                                 and math.isfinite(value) and value == round(value, 4),
                                 'Invalid boundary coordinate')
                _require(ring[0] == ring[-1] and len({tuple(p) for p in ring}) >= 3,
                         'Invalid boundary ring closure')
        rows.append({**row, 'electorate_id': identity, 'geometry': geometry})
    _require(seen == set(registry), 'Boundaries must cover every electorate')
    return rows


def _reconciliation(row, electorate):
    _require(row.get('electorate_id') == electorate['id'], 'Unknown electorate id')
    _require(_url(row.get('party_list_source_url')), 'Reconciliation requires party list source')
    identities = set()
    for category in ('matched', 'added_by_ec', 'absent_from_ec', 'corrections'):
        items = row[category]
        _require(isinstance(items, list), 'Invalid reconciliation category')
        for item in items:
            _require(isinstance(item, dict), 'Invalid reconciliation entry')
            if category == 'corrections':
                _require(item.get('field') in ('name', 'party', 'list_rank'),
                         'Invalid correction field')
                _require(all(_text(item.get(k)) for k in ('snapshot_name', 'reason'))
                         and _url(item.get('source_url')), 'Correction requires evidence')
                _require('before' in item and 'after' in item
                         and item['before'] != item['after'], 'Invalid correction')
                for value in (item['before'], item['after']):
                    if item['field'] == 'list_rank':
                        valid = _integer(value, 1)
                    else:
                        # Source affiliations need not appear in party-map.
                        valid = _text(value) and value == value.strip()
                    _require(valid, f"Invalid correction {item['field']} value")
            elif category == 'absent_from_ec':
                _require(_text(item.get('name')) and _text(item.get('party')),
                         'Invalid absent candidate')
            else:
                _require(all(_text(item.get(k)) for k in (
                    'snapshot_name', 'snapshot_party', 'ec_name', 'party')),
                    'Invalid reconciled candidate')
                _require(_integer(item.get('ec_row'), 2), 'Invalid EC row')
                identity = (item['party'], item['ec_name'])
                _require(identity not in identities, 'Duplicate reconciled candidate')
                identities.add(identity)
                for key in ('list_rank', 'snapshot_list_rank'):
                    if key in item:
                        _require(_integer(item[key], 1), 'Invalid reconciliation list rank')
                if 'snapshot_list_rank' in item:
                    _require(item.get('list_rank') == item['snapshot_list_rank'],
                             'Unresolved list rank correction')


def load(name):
    """Return validated record dictionaries for one allowlisted snapshot stem.

    Optional facts are absent. Parties outside party-map retain their source label
    in ``party`` and omit ``party_id``; they are never assigned the Others aggregate.
    Percentages are decimal strings. Tile x/y are square-grid column/row indices.
    Invalid envelopes, records, identifiers and photo metadata raise ValueError.
    """
    _require(isinstance(name, str) and name in NAMES, 'Unknown snapshot name')
    if name in {'policy-links', 'party-list-tops'}:
        return load_party_details(name)
    if name == 'pollster-record':
        from .pollster_scorecard import load_pollster_record
        return load_pollster_record()
    if name == 'donations':
        from .donations import load_donations
        return load_donations()
    if name == 'voting':
        return load_voting()
    path = SNAPSHOTS / (name + '.json')
    _require(not path.is_symlink(), 'Snapshot must not be a symlink')
    if name == 'boundaries-2025':
        _require(path.stat().st_size < BOUNDARY_BYTE_LIMIT, 'Boundary exceeds byte budget')
    raw = path.read_text(encoding='utf-8')
    _require(not BANNED.search(raw), 'Snapshot contains a banned phrase')
    data = json.loads(raw)
    _require(isinstance(data, dict) and data.get('schema') == name + '-v1',
             'Invalid snapshot schema')
    _timestamp(data.get('retrieved_at'))
    if name == 'boundaries-2025':
        return _boundaries(data)
    if name == 'candidate-reconciliation-2026':
        for field in ('source_url', 'party_list_source_url'):
            _require(_url(data.get(field)), 'Reconciliation requires ' + field)
        _require(_text(data.get('method')), 'Reconciliation requires method')
        for field in ('compared_snapshot_sha256', 'electorate_release_sha256'):
            _require(isinstance(data.get(field), str) and bool(re.fullmatch(
                r'[a-f0-9]{64}', data[field])), 'Invalid reconciliation source digest')
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
        'candidate-reconciliation-2026': (
            'electorate_slug', 'electorate_id', 'matched', 'added_by_ec',
            'absent_from_ec', 'corrections', 'party_list_source_url'),
    }[name]
    for record_number, row in enumerate(rows, 1):
        _require(isinstance(row, dict) and all(k in row for k in required),
                 'Record lacks required fields')
        _require(all(v is not None for v in row.values()), 'Omit unsourced fields')
        _require(_url(row.get('source_url')), 'Record requires source_url')
        _timestamp(row.get('retrieved_at'))
        _require(_text(row.get('licence')) and row['licence'] in RECORD_LICENCES,
                 f'{path.name}: record {record_number}: Unknown record licence')
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
        if name == 'candidate-reconciliation-2026':
            _require(row['licence'] ==
                     'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.',
                     'Invalid reconciliation licence')
            _reconciliation(row, electorates[row['electorate_slug']])
        if name in {'enrolment', 'hexmap'}:
            kind = row['roll' if name == 'enrolment' else 'group']
            _require(kind == electorates[row['electorate_slug']]['kind'], 'Wrong electorate group')
        if name == 'hexmap':
            cell = (row['x'], row['y'])
            _require(cell not in cells, 'Duplicate tile cell')
            cells.add(cell)
        identity = (row.get('electorate_slug'), row.get('party_id'), row.get('party'),
                    row.get('name'), row.get('year'))
        if name in {'hexmap', 'enrolment', 'candidate-reconciliation-2026'}:
            identity = row['electorate_slug']
        _require(identity not in seen, 'Duplicate record')
        seen.add(identity)
    if name == 'hexmap':
        _require(seen == set(electorates), 'Tile layout must cover every electorate')
    if name == 'candidate-reconciliation-2026':
        _require(seen == set(electorates), 'Reconciliation must cover every electorate')
    if name == 'port-waikato-2023':
        _require(len(rows) >= 2 and all(r['electorate_slug'] == 'port-waikato'
                 and r['election_date'] == '2023-11-25' for r in rows), 'Invalid by-election')
        ranked = sorted(rows, key=lambda r: r['votes'], reverse=True)
        _require(sum(r['winner'] for r in rows) == 1 and ranked[0]['winner']
                 and ranked[0].get('margin') == ranked[0]['votes'] - ranked[1]['votes'] > 0,
                 'Invalid winner or margin')
    return rows


def _ec_source(value):
    if not _url(value):
        return False
    parsed = urlsplit(value)
    return (parsed.scheme == 'https'
            and any(parsed.hostname == domain or parsed.hostname.endswith('.' + domain)
                    for domain in ('vote.nz', 'elections.nz')))


def _voting_timestamp(value):
    try:
        _timestamp(value)
    except ValueError:
        raise ValueError('voting_retrieved_at: expected a valid UTC timestamp') from None


def load_voting():
    """Load the offline EC snapshot, preserving source precision.

    Date records are ordered by NZ calendar date. Optional ``at`` gives an
    EC-published time in Pacific/Auckland; end-of-day midnight is represented
    as 00:00 on the following day. A date alone never implies opening hours.
    Actions reference dated records via deadline_ids, sharing their provenance.
    """
    path = SNAPSHOTS / 'voting.json'
    _require(not path.is_symlink(), 'voting_schema: symlink')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('voting_schema: unreadable JSON snapshot') from None
    _require(isinstance(data, dict) and data.get('schema') == 'voting-v1'
             and data.get('timezone') == 'Pacific/Auckland', 'voting_schema: envelope')
    _voting_timestamp(data.get('retrieved_at'))
    rows = data.get('records')
    _require(isinstance(rows, list) and bool(rows), 'voting_schema: records')
    seen, dates, actions = set(), {}, []
    previous = previous_instant = None
    for row in rows:
        _require(isinstance(row, dict), 'voting_record: expected object')
        identity = row.get('id')
        _require(_text(identity) and re.fullmatch(r'[a-z][a-z0-9-]*', identity)
                 and identity not in seen, 'voting_record: invalid or duplicate id')
        seen.add(identity)
        _require('source_url' in row, 'voting_source_missing: source_url required')
        _require(_ec_source(row['source_url']), 'voting_source_invalid: expected EC URL')
        _voting_timestamp(row.get('retrieved_at'))
        _require(_text(row.get('licence')) and row['licence'] in RECORD_LICENCES,
                 'voting_licence: unknown licence')
        _require(_text(row.get('summary')) and '\n' not in row['summary']
                 and not BANNED.search(json.dumps(row)), 'voting_record: summary')
        kind = row.get('kind')
        _require(isinstance(kind, str) and kind in {'date', 'action', 'terms'},
                 'voting_record: kind')
        if kind == 'date':
            try:
                _date(row.get('date'))
            except ValueError:
                raise ValueError('voting_date_invalid: expected calendar date') from None
            day = date.fromisoformat(row['date'])
            _require(day.year == 2026, 'voting_date_invalid: expected 2026')
            _require(previous is None or previous <= day, 'voting_date_order: dates reordered')
            previous = day
            dates[identity] = day
            local = datetime(day.year, day.month, day.day, tzinfo=ZoneInfo('Pacific/Auckland'))
            if 'at' in row:
                value = row['at']
                _require(isinstance(value, str) and re.fullmatch(
                    r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+(?:0[0-9]|1[0-4]):[0-5][0-9]', value),
                    'voting_date_invalid: expected NZ timestamp')
                try:
                    instant = datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError('voting_date_invalid: invalid time') from None
                local = instant.astimezone(ZoneInfo('Pacific/Auckland'))
                _require(instant.utcoffset() == local.utcoffset()
                         and (local.date() == day or
                              (local.date() == day + timedelta(days=1)
                               and local.hour == local.minute == local.second == 0)),
                         'voting_date_invalid: time must match NZ date or end-of-day midnight')
            _require(previous_instant is None or previous_instant <= local,
                     'voting_date_order: times reordered')
            previous_instant = local
        elif kind == 'action':
            _require(_ec_source(row.get('url')), 'voting_source_invalid: action URL')
            refs = row.get('deadline_ids', [])
            _require(isinstance(refs, list) and all(_text(ref) for ref in refs),
                     'voting_deadline: expected date references')
            actions.append(refs)
        else:
            _require(_text(row.get('copyright_notice')) and _text(row.get('terms_note')),
                     'voting_licence: terms required')
        _require(all(v is not None for v in row.values()), 'voting_record: omit unsourced fields')
    # Keep the chronology meaningful even if an editor re-sorts incorrect dates.
    milestones = [dates[key] for key in (
        'overseas-opens', 'enrolment-closes', 'advance-opens', 'advance-closes',
        's197-cutoff', 'election-day') if key in dates]
    _require(milestones == sorted(milestones), 'voting_date_order: milestone order')
    _require(bool(dates), 'voting_date_invalid: no dates')
    for refs in actions:
        _require(all(ref in dates for ref in refs), 'voting_deadline: unknown date')
    return rows


def load_party_details(name):
    _require(name in {'policy-links', 'party-list-tops'}, 'Unknown party snapshot')
    from .refresh import config
    path = SNAPSHOTS / (name + '.json')
    _require(not path.is_symlink(), 'Party snapshot must not be a symlink')
    raw = path.read_text()
    _require(not BANNED.search(raw), 'Party snapshot contains a banned phrase')
    data = json.loads(raw)
    _require(isinstance(data, dict), 'Invalid party snapshot envelope')
    _require(data.get('schema') == name + '-v1', 'Invalid party snapshot schema')
    _timestamp(data.get('retrieved_at'))
    rows = data.get('records')
    _require(isinstance(rows, list), 'Invalid party records')
    parties = {p['id'] for p in config('party-map')['parties'] if not p['aggregate']}
    seen = set()
    for row in rows:
        _require(isinstance(row, dict), 'Invalid party record')
        p = row.get('party_id')
        electorate = row.get('electorate_slug') if name == 'policy-links' else None
        if name == 'policy-links' and 'electorate_slug' in row:
            _require(isinstance(electorate, str) and electorate in {r['slug'] for r in config('electorates')}
                     and 'party_id' not in row and electorate not in seen, 'Invalid electorate identity')
            seen.add(electorate)
        elif name == 'party-list-tops' and 'party_id' not in row:
            _require(_text(row.get('party')) and row['party'] not in seen,
                     'Invalid party identity')
            seen.add(row['party'])
        else:
            _require(isinstance(p, str) and p in parties and p not in seen, 'Invalid party identity')
            seen.add(p)
        _require(_url(row.get('source_url')), 'Invalid party source')
        source = urlsplit(row['source_url'])
        _timestamp(row.get('retrieved_at'))
        if name == 'policy-links':
            _require(set(row) <= {'party_id', 'electorate_slug', 'url', 'source_url', 'licence',
                                  'source_locator', 'retrieved_at'}, 'Policy records must be links only')
            _require(source.scheme == 'https' and source.netloc == 'policy.nz',
                     'Invalid policy source')
            _require(row.get('licence') ==
                     'Links only; no policy text reused and no reuse licence claimed.',
                     'Invalid policy licence')
            if 'source_locator' in row:
                _require(_text(row['source_locator']), 'Invalid policy source locator')
            _require(isinstance(row.get('url'), str) and re.fullmatch(
                (r'https://policy\.nz/2026/electorate-vote/' + re.escape(electorate) if electorate else
                 r'https://policy\.nz/2026/party-vote/parties/[a-z0-9]+(?:-[a-z0-9]+)*'),
                row['url']) is not None, 'Invalid policy URL')
        else:
            _require(source.scheme == 'https'
                     and source.netloc in {'vote.nz', 'www.vote.nz', 'elections.nz', 'www.elections.nz'}
                     and source.path == '/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf'
                     and not source.query and not source.fragment, 'Invalid EC party list source')
            _require(row.get('licence') ==
                     'Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.',
                     'Invalid EC party list licence')
            _require(_text(row.get('source_locator')), 'Invalid list source locator')
            _require(row.get('completeness') in ('confirmed', 'partial'), 'Invalid list completeness')
            total = row.get('list_size')
            if 'list_size' in row:
                _require(type(total) is int and 0 < total <= 120, 'Invalid list size')
            if 'list_size' in row or 'list_size_source_url' in row:
                _require(row.get('list_size_source_url') ==
                         'https://elections.nz/media-and-news/2026/candidate-and-party-lists-released',
                         'Invalid EC list size source')
            candidates = row.get('candidates')
            _require(isinstance(candidates, list) and 0 < len(candidates) <= 5, 'Invalid list top')
            if row['completeness'] == 'confirmed':
                _require(total is not None and len(candidates) == min(5, total),
                         'Incomplete confirmed list')
            for rank, candidate in enumerate(candidates, 1):
                _require(isinstance(candidate, dict) and type(candidate.get('rank')) is int
                         and candidate['rank'] == rank and _text(candidate.get('name')), 'Invalid list rank')
                _require(total is None or candidate['rank'] <= total, 'List rank exceeds size')
                _require(_text(candidate.get('source_name')), 'Invalid EC candidate name')
    return rows
