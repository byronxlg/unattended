"""Exact Sainte-Lague allocation with explicit lot evidence and list exhaustion."""
from fractions import Fraction
import re


def integer(value):
    # JSON.parse erases integral decimal/exponent spelling; normalize before exact arithmetic.
    if type(value) is float and value.is_integer():
        value = int(value)
    if isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]*", value):
        return int(value)
    # Larger JSON numbers lose precision in JS; use decimal strings in both runtimes.
    if type(value) is int and 0 <= value <= 9007199254740991:
        return value
    raise ValueError("INVALID_INPUT")


def validate_shape(data):
    required = {"partyVotes", "electorateWins", "lists", "electorateWinners", "nonListWinners"}
    if type(data) is not dict or not required <= data.keys():
        raise ValueError("INVALID_INPUT")
    if data.keys() - required - {"baseSeats", "tieOrder"}:
        raise ValueError("INVALID_INPUT")
    for key in ("partyVotes", "electorateWins", "lists", "electorateWinners"):
        if type(data[key]) is not dict or any(type(p) is not str for p in data[key]):
            raise ValueError("INVALID_INPUT")
    for key in ("lists", "electorateWinners"):
        for candidates in data[key].values():
            if type(candidates) is not list or any(type(c) is not str or not c for c in candidates):
                raise ValueError("INVALID_INPUT")
    if type(data["nonListWinners"]) is not list or any(
            type(c) is not str or not c for c in data["nonListWinners"]):
        raise ValueError("INVALID_INPUT")
    if "tieOrder" in data:
        lot = data["tieOrder"]
        if type(lot) is not dict or lot.keys() - {"order", "reference"}:
            raise ValueError("INVALID_INPUT")
        if "order" in lot and (type(lot["order"]) is not list or any(
                type(p) is not str for p in lot["order"])):
            raise ValueError("INVALID_INPUT")
        if "reference" in lot and type(lot["reference"]) is not str:
            raise ValueError("INVALID_INPUT")


def allocate(data):
    validate_shape(data)
    votes = {p: integer(v) for p, v in data["partyVotes"].items()}
    wins = {p: integer(v) for p, v in data["electorateWins"].items()}
    lists = data["lists"]
    winners = data["electorateWinners"]
    nonlist = data["nonListWinners"]
    base = integer(data.get("baseSeats", 120))
    parties = sorted(votes)
    if not base or not sum(votes.values()) or set(wins) != set(parties):
        raise ValueError("INVALID_INPUT")
    if set(lists) - set(parties) or set(winners) != set(parties):
        raise ValueError("INVALID_INPUT")
    seen = {}
    elected = []
    for p in parties:
        ls, ws = lists.get(p, []), winners[p]
        if not isinstance(ls, list) or not isinstance(ws, list):
            raise ValueError("INVALID_INPUT")
        if len(set(ls)) != len(ls) or len(set(ws)) != len(ws) or len(ws) != wins[p]:
            raise ValueError("INVALID_INPUT")
        if wins[p] and p not in lists:
            raise ValueError("INVALID_INPUT")
        for c in ls + ws:
            if not isinstance(c, str) or not c or (c in seen and seen[c] != p):
                raise ValueError("INVALID_INPUT")
            seen[c] = p
        elected.extend(ws)
    if not isinstance(nonlist, list) or any(not isinstance(c, str) or not c for c in nonlist):
        raise ValueError("INVALID_INPUT")
    if len(set(nonlist)) != len(nonlist) or set(nonlist) & set(seen):
        raise ValueError("INVALID_INPUT")
    if len(elected) + len(nonlist) > base:
        raise ValueError("INVALID_INPUT")
    count = base - len(nonlist)
    eligible = [p for p in parties if p in lists and lists[p]
                and (100 * votes[p] >= 5 * sum(votes.values()) or wins[p])]
    if count and not eligible:
        raise ValueError("INVALID_INPUT")
    allocation = entitlement(votes, eligible, count, data.get("tieOrder"))
    if allocation['unresolvedTies']:
        return dict(**allocation, listMembers=None, seats=None, overhang=None,
                    vacancies=None, occupiedHouse=None)
    ent, quotients = allocation['entitlements'], allocation['quotients']
    members, seats = {}, {}
    overhang = vacancies = 0
    for p in parties:
        needed = max(0, ent[p] - wins[p])
        members[p] = [c for c in lists.get(p, []) if c not in winners[p]][:needed]
        seats[p] = wins[p] + len(members[p])
        vacancies += needed - len(members[p])
        overhang += max(0, wins[p] - ent[p])
    return dict(entitlements=ent, listMembers=members, seats=seats, overhang=overhang,
                vacancies=vacancies, occupiedHouse=base + overhang - vacancies,
                quotients=quotients, unresolvedTies=[])


def entitlement(votes, eligible, count=120, tie_order=None):
    """Shared exact quotient primitive; eligibility is supplied by the caller."""
    parties = sorted(votes)
    qs = [(Fraction(votes[p], d), p, d) for p in eligible for d in range(1, 2 * count + 2, 2)]
    qs.sort(key=lambda q: q[0], reverse=True)
    selected = qs[:count]
    unresolved = []
    if count and len(qs) > count and qs[count - 1][0] == qs[count][0]:
        boundary = qs[count][0]
        above = [q for q in qs if q[0] > boundary]
        tied = [q for q in qs if q[0] == boundary]
        lot = tie_order or {}
        order = lot.get("order", [])
        if not lot.get("reference") or len(order) != len(set(order)) or set(order) != {q[1] for q in tied}:
            unresolved = [{"rank": len(above) + 1, "places_remaining": count - len(above),
                           "candidates": [q[1] for q in tied], "tie_order_ref": None}]
        else:
            tied.sort(key=lambda q: order.index(q[1]))
            selected = above + tied[:count - len(above)]
    if unresolved:
        return dict(entitlements=None, quotients=[], unresolvedTies=unresolved)
    ent = dict.fromkeys(parties, 0)
    quotients = []
    for rank, (_, p, d) in enumerate(selected, 1):
        ent[p] += 1
        quotients.append(dict(rank=rank, party_id=p, numerator=str(votes[p]), divisor=str(d), selected=True))
    return dict(entitlements=ent, quotients=quotients, unresolvedTies=[])
