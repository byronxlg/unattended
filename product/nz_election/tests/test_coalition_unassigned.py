"""Unavailable allocations retain the current electorate count in both runtimes."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest
from coalition_unassigned_cases import unassigned_inputs
from product.nz_election.pipeline import coalitions, export


@pytest.mark.parametrize('no_eligible', [False, True])
def test_unassigned_count_tracks_unavailable_allocation(no_eligible):
    average, seats = unassigned_inputs(no_eligible)
    data = coalitions.inputs(average, seats, 'a' * 64)
    requests, results = [], []
    for wins in ('0', '1', '0'):
        state = deepcopy(data['initial'])
        state['counts']['b'] = wins
        result = coalitions.scenario(data, state)
        assert result['unassigned_electorates'] == 71 - int(wins)
        assert (result['seats'] is None) == (no_eligible or wins == '1')
        if wins == '1':
            assert result['unresolved_ties']
        requests.append(dict(average=average, seats=seats, fingerprint='a' * 64, state=state))
        results.append(dict(result=result))
    runner = Path(__file__).with_name('coalitions_runner.mjs')
    actual = subprocess.run(['node', str(runner)], input=json.dumps(requests), text=True,
                            capture_output=True, check=True).stdout
    assert actual == export.canonical(results)
