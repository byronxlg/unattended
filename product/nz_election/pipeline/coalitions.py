"""Bounded share state and exact, conditional coalition scenarios."""
import json
import re
from urllib.parse import quote, unquote

from .allocator import entitlement
from .export import canonical

ERROR = 'INVALID_COALITION_STATE'
LIMIT = 8192
KEYS = {'version', 'selected', 'counts', 'mode', 'fingerprint'}


def fail():
    raise ValueError(ERROR)


def count(value):
    if type(value) is not str or len(value) > 2 or not re.fullmatch(r'0|[1-9][0-9]?', value):
        fail()
    result = int(value)
    if result > 71:
        fail()
    return result


def validate(state, parties):
    if type(state) is not dict or set(state) != KEYS:
        fail()
    if state['version'] != 1 or isinstance(state['version'], bool) or state['mode'] != 'unchecked':
        fail()
    if type(state['fingerprint']) is not str or not re.fullmatch('[0-9a-f]{64}', state['fingerprint']):
        fail()
    selected, counts = state['selected'], state['counts']
    if type(selected) is not list or any(type(p) is not str or p not in parties for p in selected):
        fail()
    if len(selected) != len(set(selected)) or type(counts) is not dict or set(counts) != set(parties):
        fail()
    if sum(count(v) for v in counts.values()) > 71:
        fail()
    return state


def decode(value, parties):
    try:
        if type(value) is not str or len(value) > LIMIT or not value.startswith('#coalition='):
            fail()
        raw = value[len('#coalition='):]
        if re.search(r'%(?![0-9a-fA-F]{2})', raw):
            fail()
        raw = unquote(raw, errors='strict')
        state = validate(json.loads(raw), parties)
        # Canonical JSON also rejects duplicate object keys before they can be hidden by parsing.
        if canonical(dict(state, version=1)) != raw:
            fail()
        return state
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail()


def encode(state):
    return '#coalition=' + quote(canonical(state), safe='')


def inputs(average, seats, fingerprint):
    """Fail closed on incoherent vectors, coverage or mismatched publication rows."""
    try:
        votes = average['shares']
        parties = sorted(p for p in votes if p != 'others')
        if (not parties or any(not re.fullmatch('[a-z][a-z0-9-]{0,31}', p) or
                              p in {'constructor', 'prototype', '__proto__'} for p in votes)
                or average['coherent'] is not True or average['missing'] != []
                or seats['average_id'] != average['id'] or seats['capacity_checked'] is not False
                or seats['assumptions']['non_list_winners'] != []
                or seats['assumptions']['base_seats'] != 120):
            fail()
        if any(type(v) is not int or not 0 <= v <= 9007199254740991 for v in votes.values()):
            fail()
        if (type(average['denominator']) is not int or not 0 < average['denominator'] <= 9007199254740991
                or sum(votes.values()) != average['denominator']):
            fail()
        poll_ids = average['poll_ids']
        if not poll_ids or len(set(poll_ids)) != len(poll_ids) or set(average['descriptive']) != set(votes):
            fail()
        if any(sorted(average['descriptive'][p]['poll_ids']) != sorted(poll_ids) for p in votes):
            fail()
        wins = seats['assumptions']['electorate_wins']
        if set(wins) - set(parties) or any(type(v) is not int or not 0 <= v <= 71 for v in wins.values()):
            fail()
        state = dict(version=1, selected=[], counts={p: str(wins.get(p, 0)) for p in parties},
                     mode='unchecked', fingerprint=fingerprint)
        validate(state, parties)
        return dict(parties=parties, votes={p: str(v) for p, v in votes.items()}, initial=state)
    except (KeyError, TypeError, ValueError):
        raise ValueError('INCOMPLETE_COALITION_INPUT') from None


def scenario(data, state):
    validate(state, data['parties'])
    if state['fingerprint'] != data['initial']['fingerprint']:
        return dict(warning='INPUT_FINGERPRINT_MISMATCH', applied=False)
    votes = {p: int(v) for p, v in data['votes'].items()}
    wins = {p: count(v) for p, v in state['counts'].items()}
    total = sum(votes.values())
    eligible = [p for p in sorted(votes) if p != 'others' and (votes[p] * 100 >= total * 5 or wins[p])]
    result = entitlement(votes, eligible)
    base = dict(occupied_house=None, vacancies=None, majority=None, capacity_checked=False,
                unassigned_electorates=71 - sum(wins.values()), unresolved_ties=result['unresolvedTies'])
    if result['unresolvedTies'] or not eligible:
        return dict(base, seats=None, entitlements=None, overhang=None, assumed_house=None,
                    assumed_majority=None, selected_total=None)
    ent = result['entitlements']
    seats = {p: max(ent[p], wins[p]) for p in data['parties']}
    overhang = sum(seats[p] - ent[p] for p in seats)
    house = 120 + overhang
    return dict(base, seats=seats, entitlements=ent, overhang=overhang, assumed_house=house,
                assumed_majority=house // 2 + 1, selected_total=sum(seats[p] for p in state['selected']))
