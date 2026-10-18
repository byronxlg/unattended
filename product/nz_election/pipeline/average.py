"""Exact equal-weight calendar windows. Missing observations never become zero."""
from datetime import date, timedelta
from decimal import Decimal

METHOD = 'window-mean-30d-v2'
OTHERS_RULE = 'others-remainder-0-to-10-v1'
ROUNDING = 'display-only-half-up-1dp'


def select_window(polls, end_date):
    end = date.fromisoformat(str(end_date))
    start = end - timedelta(days=29)
    return [p for p in polls if start <= date.fromisoformat(p['fieldwork_end']) <= end]


def deduplicate(polls, identities=None):
    latest = {}
    for poll in polls:
        previous = latest.get(poll['id'])
        if previous is None or int(poll['revision']) >= int(previous['revision']):
            latest[poll['id']] = poll
    return sorted(latest.values(), key=lambda p: (p['fieldwork_end'], p['id']))


def values(poll):
    scale = poll.get('scale', 1)
    if type(scale) is not int or scale < 1 or str(scale).strip('0') != '1':
        raise ValueError('INVALID_POLL_SCALE')
    places = len(str(scale)) - 1
    result = {}
    for party, value in poll['shares'].items():
        if value is None:
            result[party] = None
        else:
            sign, digits, exponent = Decimal(value).as_tuple()
            # Tuple construction adjusts the decimal point without applying a context.
            result[party] = Decimal((sign, digits, exponent - places))
    return result


def scaled_vector(poll):
    vector = values(poll)
    precision = max((max(0, -v.as_tuple().exponent) for v in vector.values() if v is not None), default=0)
    unit = 10 ** precision
    result = {}
    for party, value in vector.items():
        if value is None:
            result[party] = None
        else:
            numerator, denominator = value.as_integer_ratio()
            result[party] = numerator * (unit // denominator)
    return result, unit


def derive_others(poll, parties):
    """Keep captured shares intact; only a complete named vector permits a remainder."""
    if poll['shares'].get('others') is not None:
        return poll
    named = set(parties) - {'others'}
    if not named or any(poll['shares'].get(p) is None for p in named):
        return poll
    vector, scale = scaled_vector(poll)
    remainder = 100 * scale - sum(v for p, v in vector.items() if p != 'others' and v is not None)
    if not 0 <= remainder <= 10 * scale:
        return poll
    vector['others'] = remainder
    return dict(poll, shares=vector, scale=scale,
                derivation=dict(poll_id=poll['id'], revision=poll['revision'],
                                pollster=poll.get('pollster', ''), party_id='others',
                                rule=OTHERS_RULE, value=remainder, scale=scale))


def check_vector(polls, mapping=None, review=None, *, derive=True):
    exclusions = []
    included = []
    for poll in polls:
        decision = (review or {}).get('exclusions', {}).get(poll['id'])
        if decision and decision.get('revision') == poll['revision']:
            if not decision.get('reason') or not decision.get('review_ref'):
                raise ValueError('UNREVIEWED_EXCLUSION')
            exclusions.append(dict(poll_id=poll['id'], reason=decision['reason'], review_ref=decision['review_ref']))
        else:
            included.append(poll)
    parties = {'others'} | {p for row in included for p, v in row['shares'].items() if v is not None}
    named = set((mapping or {}).get('headers', {}).values()) | {p for row in included for p in row['shares']}
    if derive:
        included = [derive_others(row, named) for row in included]
    missing = [dict(poll_id=row['id'], party_id=p) for row in included
               for p in sorted(parties) if row['shares'].get(p) is None]
    return included, exclusions, missing


def mean_vector(polls):
    vectors = [scaled_vector(p) for p in polls]
    unit = max((scale for _, scale in vectors), default=1)
    parties = sorted({p for row, _ in vectors for p in row})
    descriptive = {}
    for party in parties:
        covered = [(p, row[party] * (unit // scale)) for p, (row, scale) in zip(polls, vectors)
                   if row.get(party) is not None]
        descriptive[party] = dict(value=sum(v for _, v in covered),
                                  scale=len(covered) * unit, poll_ids=[p['id'] for p, _ in covered])
    coherent = bool(polls) and all(d['scale'] == len(polls) * unit for d in descriptive.values())
    shares = {p: d['value'] for p, d in descriptive.items()} if coherent else None
    return dict(coherent=coherent, shares=shares, scale=len(polls) * unit,
                denominator=sum(shares.values()) if shares else None, descriptive=descriptive)


def trend(polls, dates, mapping=None, review=None, *, derive=True):
    result = []
    for day in dates:
        day = str(day)
        selected, exclusions, missing = check_vector(select_window(deduplicate(polls), day), mapping, review, derive=derive)
        mean = mean_vector(selected)
        if missing:
            mean.update(coherent=False, shares=None, denominator=None)
        result.append(dict(id='average-' + day, source_ref=[dict(source_id='P', poll_id=p['id'],
                           revision=p['revision']) for p in selected], observed_at=day, date=day,
                           window_start=str(date.fromisoformat(day) - timedelta(days=29)), window_end=day,
                           **mean, poll_ids=[p['id'] for p in selected],
                           excluded_ids=[e['poll_id'] for e in exclusions], exclusions=exclusions,
                           missing=missing, derivations=[p['derivation'] for p in selected if 'derivation' in p],
                           rounding_policy=ROUNDING))
    if not derive:
        for row in result:
            del row['derivations']
    return result


def threshold_watch(polls, average, assumptions):
    included = set(average['poll_ids'])
    polls = [p for p in deduplicate(polls) if p['id'] in included]
    if {p['id'] for p in polls} != included:
        raise ValueError('MISSING_AVERAGE_INPUT')
    result = []
    for party, d in average['descriptive'].items():
        if party == 'others':
            continue
        observations = [values(p).get(party) for p in polls]
        in_average = d['scale'] and 2 * d['scale'] <= d['value'] <= 7 * d['scale']
        if in_average or any(v is not None and 2 <= v <= 7 for v in observations):
            result.append(dict(party_id=party, **d, missing_poll_ids=[p['id'] for p, v in zip(polls, observations)
                               if v is None], electorate_qualifies=assumptions['electorate_wins'].get(party, 0) > 0))
    return result


def display(value, scale):
    if not scale or value is None:
        return 'Not reported'
    tenths = (20 * value + scale) // (2 * scale)
    return f'{tenths // 10}.{tenths % 10}%'
