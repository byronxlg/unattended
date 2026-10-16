"""Exact equal-weight calendar windows. Missing observations never become zero."""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

METHOD = 'window-mean-30d-v1'
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
    return {p: None if v is None else Decimal(v) / scale for p, v in poll['shares'].items()}


def check_vector(polls, mapping=None, review=None):
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
    missing = [dict(poll_id=row['id'], party_id=p) for row in included
               for p in sorted(parties) if row['shares'].get(p) is None]
    return included, exclusions, missing


def mean_vector(polls):
    vectors = [values(p) for p in polls]
    precision = max((max(0, -v.as_tuple().exponent) for row in vectors for v in row.values()
                     if v is not None), default=0)
    unit = 10 ** precision
    parties = sorted({p for row in vectors for p in row})
    descriptive = {}
    for party in parties:
        covered = [(p, row[party]) for p, row in zip(polls, vectors) if row.get(party) is not None]
        descriptive[party] = dict(value=sum(int(v * unit) for _, v in covered),
                                  scale=len(covered) * unit, poll_ids=[p['id'] for p, _ in covered])
    coherent = bool(polls) and all(d['scale'] == len(polls) * unit for d in descriptive.values())
    shares = {p: d['value'] for p, d in descriptive.items()} if coherent else None
    return dict(coherent=coherent, shares=shares, scale=len(polls) * unit,
                denominator=sum(shares.values()) if shares else None, descriptive=descriptive)


def trend(polls, dates, mapping=None, review=None):
    result = []
    for day in dates:
        day = str(day)
        selected, exclusions, missing = check_vector(select_window(deduplicate(polls), day), mapping, review)
        mean = mean_vector(selected)
        if missing:
            mean.update(coherent=False, shares=None, denominator=None)
        result.append(dict(id='average-' + day, source_ref=[dict(source_id='P', poll_id=p['id'],
                           revision=p['revision']) for p in selected], observed_at=day, date=day,
                           window_start=str(date.fromisoformat(day) - timedelta(days=29)), window_end=day,
                           **mean, poll_ids=[p['id'] for p in selected],
                           excluded_ids=[e['poll_id'] for e in exclusions], exclusions=exclusions,
                           missing=missing, rounding_policy=ROUNDING))
    return result


def threshold_watch(polls, average, assumptions):
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
    return str((Decimal(value) / Decimal(scale)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)) + '%'
