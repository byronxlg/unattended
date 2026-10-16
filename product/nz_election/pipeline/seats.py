"""Theoretical current seats without invented candidate capacity."""
from .allocator import entitlement
from .fixtures import golden

NAMES = {'nat': 'National Party', 'lab': 'Labour Party', 'grn': 'Green Party',
         'act': 'ACT New Zealand', 'nzf': 'New Zealand First Party', 'tpm': 'Te Pāti Māori'}


def assumptions():
    official = golden()
    wins = {p: official['input']['electorateWins'][next(k for k, v in official['partyNames'].items() if v == name)]
            for p, name in NAMES.items()}
    return dict(electorate_wins=wins, non_list_winners=[], unassigned_electorates=1, base_seats=120,
                basis='2023 electorate seats assumed; 2026 has different boundaries',
                capacity_policy='List capacity not checked', source_ref=[dict(source_id='E:ec-2023/winners.csv', row='2023 electorate winners')])


def project(average):
    scenario = assumptions()
    result = dict(id='seats-' + average['date'], source_ref=average['source_ref'] + scenario['source_ref'],
                  observed_at=average['date'], average_id=average['id'], available=False,
                  reason='Incomplete party coverage; seats withheld.', assumptions=scenario,
                  entitlements=None, list_members=None, seats=None, overhang=None, vacancies=None,
                  occupied_house=None, majority=None, assumed_house=None, assumed_majority=None,
                  capacity_checked=False, quotients=[], unresolved_ties=[])
    if not average['coherent']:
        return result
    votes = average['shares']
    wins = scenario['electorate_wins']
    if not set(wins) <= votes.keys() or average['denominator'] <= 0:
        result['reason'] = 'Missing vote coverage for the electorate assumptions; seats withheld.'
        return result
    eligible = [p for p in votes if p != 'others' and (100 * votes[p] >= 5 * average['denominator'] or wins.get(p, 0))]
    allocated = entitlement(votes, eligible)
    result.update(entitlements=allocated['entitlements'], quotients=allocated['quotients'],
                  unresolved_ties=allocated['unresolvedTies'])
    if allocated['unresolvedTies']:
        result['reason'] = 'An allocation tie needs a recorded lot result.'
        return result
    ent = allocated['entitlements']
    seats = {p: max(v, wins.get(p, 0)) for p, v in ent.items() if p != 'others'}
    overhang = sum(max(0, wins.get(p, 0) - ent.get(p, 0)) for p in wins)
    result.update(available=True, reason=None, seats=seats, overhang=overhang,
                  assumed_house=120 + overhang, assumed_majority=(120 + overhang) // 2 + 1)
    return result
