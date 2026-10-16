"""Official acceptance plus independently specified synthetic edge cases."""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import pytest
from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.fixtures import captures, require_equal, ROOT


def case(votes=None, wins=None, base=20, capacities=None, nonlist=None):
    votes = votes or {'A': 90, 'B': 10}
    wins = wins or {}
    capacities = capacities or {}
    return dict(partyVotes=votes, electorateWins={p: wins.get(p, 0) for p in votes},
                lists={p: [f'{p}{i}' for i in range(capacities.get(p, base))] for p in votes},
                electorateWinners={p: [f'{p}{i}' for i in range(wins.get(p, 0))] for p in votes},
                nonListWinners=nonlist or [], baseSeats=base)


def test_2023_official_result(official, tmp_path):
    result = allocate(official['input'])
    assert result['seats'] == official['expectedSeats']
    assert result['listMembers'] == official['expectedListMembers']
    assert result['occupiedHouse'] == 122
    assert result['overhang'] == 2 and result['vacancies'] == 0
    assert [result['entitlements'][p] for p in ('16', '13', '10', '5', '17', '14')] == [48, 34, 15, 11, 8, 4]
    assert sum(official['input']['partyVotes'].values()) == 2851211
    assert len(result['listMembers']['16']) == 5
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest))
    first = manifest['entries'][0]['path']
    with pytest.raises(ValueError, match=f'MISSING_CAPTURE: {first}'):
        captures(tmp_path)
    target = tmp_path / first
    target.parent.mkdir(parents=True)
    target.write_bytes(b'corrupt')
    with pytest.raises(ValueError, match=f'CAPTURE_HASH_MISMATCH: {first}'):
        captures(tmp_path)
    with pytest.raises(ValueError, match='FIXTURE_2023_MISMATCH: house: 123 != 122'):
        require_equal(123, 122, 'house')


def test_all_120_quotients(official):
    qs = allocate(official['input'])['quotients']
    assert len(qs) == len(official['quotients']) == 120
    for actual, expected in zip(qs, official['quotients']):
        assert (actual['rank'], actual['party_id'], actual['divisor']) == (expected['rank'], expected['party_id'], expected['divisor'])
        exact = Fraction(int(actual['numerator']), int(actual['divisor']))
        assert abs(exact - Fraction(Decimal(expected['display']))) <= Fraction(1, 2000)
    assert (qs[-1]['numerator'], qs[-1]['divisor']) == ('330907', '29')
    ent = allocate(official['input'])['entitlements']
    losing = max((Fraction(official['input']['partyVotes'][p], 2*n+1), p, 2*n+1)
                 for p,n in ent.items() if n)
    assert losing == (Fraction(1085851, 97), '16', 97)


def test_exactly_five_percent():
    assert allocate(case({'A': 95, 'B': 5}))['entitlements']['B'] == 1


def test_below_five_with_electorate():
    assert allocate(case({'A': 96, 'B': 4}, {'B': 1}))['entitlements']['B'] == 1


def test_below_five_without_electorate():
    assert allocate(case({'A': 96, 'B': 4}))['entitlements']['B'] == 0


def test_excluded_votes_in_denominator():
    data = case({'A': 46, 'B': 4, 'Others': 50})
    del data['lists']['Others']
    assert allocate(data)['entitlements'] == {'A': 20, 'B': 0, 'Others': 0}


def test_independent_and_unlisted_winners():
    result = allocate(case(nonlist=['independent', 'unlisted']))
    assert sum(result['entitlements'].values()) == 18
    assert result['occupiedHouse'] == 20


def test_multiple_overhang_parties():
    result = allocate(case({'A': 98, 'B': 1, 'C': 1}, {'B': 2, 'C': 2}))
    assert result['overhang'] == 4 and result['occupiedHouse'] == 24
    assert result['seats']['B'] == result['seats']['C'] == 2


def test_exhausted_lists():
    result = allocate(case(capacities={'A': 2}))
    assert result['vacancies'] == 16 and result['occupiedHouse'] == 4
    assert result['seats'] == {'A': 2, 'B': 2}


def test_electorate_winners_skipped():
    result = allocate(case(wins={'A': 2}))
    assert result['listMembers']['A'] == [f'A{i}' for i in range(2, 18)]


def test_cutoff_ties():
    data = case({'A': 50, 'B': 50}, base=1)
    result = allocate(data)
    assert result['occupiedHouse'] is None and result['entitlements'] is None
    assert result['unresolvedTies'][0]['places_remaining'] == 1
    data['tieOrder'] = {'order': ['B', 'A'], 'reference': 'synthetic recorded lot'}
    assert allocate(data)['seats'] == {'A': 0, 'B': 1}
    data['tieOrder'].pop('reference')
    assert allocate(data)['occupiedHouse'] is None


def invalid_cases():
    cases = []
    for value in (True, -1, 1.5, '1.0', '01'):
        data = case(); data['partyVotes']['A'] = value; cases.append(data)
    data = case({'A': 0, 'B': 0}); cases.append(data)
    data = case(); data['baseSeats'] = 0; cases.append(data)
    data = case(); data['lists']['A'] = ['A0', 'A0']; cases.append(data)
    data = case(); data['electorateWins']['A'] = 1; cases.append(data)
    data = case(); data['nonListWinners'] = ['A0']; cases.append(data)
    data = case(); data['electorateWinners']['B'] = ['A0']; data['electorateWins']['B'] = 1; cases.append(data)
    data = case(); data['nonListWinners'] = [str(i) for i in range(21)]; cases.append(data)
    return cases


def test_zero_votes_and_invalid_inputs():
    assert allocate(case({'A': 100, 'B': 0}))['seats']['B'] == 0
    for data in invalid_cases():
        with pytest.raises(ValueError, match='INVALID_INPUT'):
            allocate(data)


def test_scaled_equivalent_inputs():
    data = case()
    expected = allocate(data)
    data['partyVotes'] = {p: str(v * 10**30) for p,v in data['partyVotes'].items()}
    actual = allocate(data)
    assert actual['seats'] == expected['seats']
    assert actual['entitlements'] == expected['entitlements']


def test_python_js_parity(official):
    node = shutil.which('node')
    assert node, 'NODE_REQUIRED_FOR_PARITY'
    inputs = [official['input'], case(), case({'16': 50, '5': 50}, base=1), case({'A': 50, 'B': 50}, base=1),
              case({'A': 98, 'B': 1, 'C': 1}, {'B': 2, 'C': 2}),
              case(capacities={'A': 2}), case(nonlist=['i', 'u']),
              case({'A': str(95 * 10**30), 'B': str(5 * 10**30)}), *invalid_cases()]
    lot = case({'A': 50, 'B': 50}, base=1)
    lot['tieOrder'] = {'order': ['B', 'A'], 'reference': 'synthetic lot'}
    inputs.append(lot)
    expected = []
    for data in inputs:
        try:
            expected.append({'result': allocate(deepcopy(data))})
        except ValueError as error:
            expected.append({'error': str(error)})
    process = subprocess.run([node, str(Path(__file__).with_name('allocator_runner.mjs'))],
                             input=json.dumps(inputs), text=True, capture_output=True, check=True)
    assert json.loads(process.stdout) == expected
