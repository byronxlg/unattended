"""Published poll vectors can produce overhang in more than one party."""
import pytest

from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.build import config, default_scenario
from product.nz_election.pipeline.seats import project


@pytest.mark.parametrize('votes,expected,bloc_totals,overhangs', [
    # origin/data 922492d7d8b39f62ee455af1ecffda5107326a91, published 26 October.
    (dict(act=662, grn=1044, lab=1997, nat=1990, nzf=724, opp=431, others=94, tpm=90),
     dict(act=11, grn=18, lab=35, nat=43, nzf=13, opp=7, tpm=6), (67, 59, 7), dict(nat=9, tpm=4)),
    # origin/data 0ae9bb49b6dd13b7eda4144456c6b1c9e3ff1660, published 27 October.
    (dict(act=786, grn=1192, lab=2270, nat=2279, nzf=824, opp=494, others=96, tpm=91),
     dict(act=12, grn=18, lab=34, nat=43, nzf=13, opp=7, tpm=6), (68, 58, 7), dict(nat=8, tpm=5)),
])
def test_published_seat_sum_overhang_majority_and_blocs(votes, expected, bloc_totals, overhangs):
    # Scaling the captured vector preserves exact quotients and qualification.
    average = trend([dict(id='captured-vector', revision='1', fieldwork_end='2026-10-27',
                          shares=votes, scale=100)], ['2026-10-27'])[0]
    projected = project(average)
    home = default_scenario(dict(averages=dict(data=[average]), seats=dict(data=projected)))
    wins = projected['assumptions']['electorate_wins']
    groups = config('seat-groups')
    government = set(groups['government']['parties'])
    opposition = set(groups['opposition']['parties'])
    assert government.isdisjoint(opposition)
    for result in (projected, home):
        assert result['seats'] == expected
        ent = result['entitlements']
        assert sum(ent.values()) == 120 and ent['others'] == 0
        assert {p: max(0, wins.get(p, 0) - ent[p]) for p in ('nat', 'tpm')} == overhangs
        assert result['overhang'] == sum(max(0, wins.get(p, 0) - ent[p]) for p in ent) == 13
        assert sum(result['seats'].values()) == result['assumed_house'] == 120 + result['overhang']
        assert result['assumed_majority'] == result['assumed_house'] // 2 + 1 == 67
        totals = tuple(sum(n for p, n in result['seats'].items() if p in members)
                       for members in (government, opposition, set(expected) - government - opposition))
        assert totals == bloc_totals and sum(totals) == result['assumed_house']

    # Synthetic ample lists compare the full allocator without asserting real capacity.
    allocated = allocate(dict(
        partyVotes=votes, electorateWins={p: wins.get(p, 0) for p in votes},
        lists={p: [f'{p}-{i}' for i in range(120)] for p in votes if p != 'others'},
        electorateWinners={p: [f'{p}-{i}' for i in range(wins.get(p, 0))] for p in votes},
        nonListWinners=[]))
    assert allocated['entitlements'] == projected['entitlements']
    assert allocated['seats'] == dict(expected, others=0)
    assert allocated['vacancies'] == 0
    assert allocated['occupiedHouse'] == 120 + allocated['overhang'] == home['assumed_house']
