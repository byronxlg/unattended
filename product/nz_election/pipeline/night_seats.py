"""Conservative seat calculation and explicitly dated result comparisons."""
from .allocator import allocate


def waterfall(inputs, *, complete=False, capacity_verified=False):
    if complete is not True:
        return dict(status='incomplete', calculation=None)
    result = allocate(inputs)
    if result['unresolvedTies']:
        return dict(status='unresolved tie', calculation=None)
    if capacity_verified is not True:
        result = {k: v for k, v in result.items() if k not in {'seats', 'listMembers', 'occupiedHouse', 'vacancies'}}
    return dict(status='calculated' if capacity_verified is True else 'unchecked list capacity', calculation=result)


def official_change(preliminary, official):
    from datetime import datetime
    if not isinstance(preliminary, dict) or not isinstance(official, dict):
        return None
    try:
        if any(not isinstance(r.get('seats'), dict) or not r['seats'] or any(type(p) is not str for p in r['seats'])
               or any(type(r.get(k)) is not str or not r[k] for k in ('election', 'reference_version', 'date'))
               for r in (preliminary, official)):
            return None
        if (preliminary['status'] != 'preliminary' or official['status'] != 'official'
                or preliminary['election'] != official['election']
                or preliminary['reference_version'] != official['reference_version']
                or set(preliminary['seats']) != set(official['seats'])
                or datetime.fromisoformat(preliminary['date']) >= datetime.fromisoformat(official['date'])):
            return None
        if any(type(n) is not int or not 0 <= n <= 999999999 for r in (preliminary, official) for n in r['seats'].values()):
            return None
        result = dict(label='Change since preliminary result', preliminary_date=preliminary['date'], official_date=official['date'],
                      changes={p: official['seats'][p] - n for p, n in preliminary['seats'].items()})
        evidence = official.get('specials')
        if (isinstance(evidence, dict) and isinstance(evidence.get('source'), str) and evidence['source'].startswith('https://')
                and isinstance(evidence.get('votes'), dict) and set(evidence['votes']) == set(official['seats'])
                and all(type(v) is int and 0 <= v <= 999999999 for v in evidence['votes'].values())):
            result['specials'] = evidence
        return result
    except (KeyError, TypeError, ValueError):
        return None
