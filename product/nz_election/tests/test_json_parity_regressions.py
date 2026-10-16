"""One allocator decision per JSON document, including number spelling and ID order."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import parse_polls


def parity(document):
    node = shutil.which('node')
    assert node, 'NODE_REQUIRED_FOR_PARITY'
    try:
        expected = {'result': allocate(json.loads(document))}
    except ValueError as error:
        expected = {'error': str(error)}
    runner = Path(__file__).with_name('allocator_runner.mjs')
    process = subprocess.run([node, str(runner)], input='[' + document + ']',
                             text=True, capture_output=True, check=True)
    assert json.loads(process.stdout) == [expected]
    return expected


@pytest.mark.parametrize('field,token,accepted', [
    ('baseSeats', '1.0', True),
    ('baseSeats', '1e0', True),
    ('partyVotes', '100.0', True),
    ('partyVotes', '1e2', True),
    ('electorateWins', '0.0', True),
    ('electorateWins', '-0.0', True),
    ('electorateWins', '1.0', True),
    *[(field, token, False)
      for field in ('baseSeats', 'partyVotes', 'electorateWins')
      for token in ('true', '1.5', '1e400', '-1.0', '9007199254740992.0')],
])
def test_numeric_json_tokens(field, token, accepted):
    data = dict(partyVotes={'A': 100}, electorateWins={'A': 0}, lists={'A': ['c']},
                electorateWinners={'A': []}, nonListWinners=[], baseSeats=1)
    if field == 'electorateWins' and token == '1.0':
        data['electorateWinners']['A'] = ['c']
    if field == 'baseSeats':
        data[field] = 'NUMBER_TOKEN'
    else:
        data[field]['A'] = 'NUMBER_TOKEN'
    document = json.dumps(data).replace('"NUMBER_TOKEN"', token)
    result = parity(document)
    if accepted:
        assert result['result']['seats'] == {'A': 1}
        assert result['result']['occupiedHouse'] == 1
    else:
        assert result == {'error': 'INVALID_INPUT'}


@pytest.mark.parametrize('base', [1, 2])
def test_code_point_party_order(base):
    parties = ['\U00010000', '\ue000']
    data = dict(partyVotes={p: 50 for p in parties}, electorateWins={p: 0 for p in parties},
                lists={p: [p + 'candidate'] for p in parties},
                electorateWinners={p: [] for p in parties}, nonListWinners=[], baseSeats=base)
    result = parity(json.dumps(data))['result']
    if base == 1:
        assert result['unresolvedTies'][0]['candidates'] == ['\ue000', '\U00010000']
    else:
        assert [q['party_id'] for q in result['quotients']] == ['\ue000', '\U00010000']


def test_uppercase_sort_attribute(mapping):
    labels = ('Date', 'Polling organisation', 'Sample size', 'NAT', 'LAB', 'GRN',
              'ACT', 'NZF', 'TPM', 'OPP', 'Others', 'Lead')
    text = '==Party vote==\n=== Table of polls ===\n{|\n' + '\n'.join('! ' + s for s in labels)
    text += ('\n|-\n| DATA-SORT-VALUE="2026-10-12" | 8–12 Oct 2026\n'
             '| Roy Morgan\n| 1000 || 30 || 30 || 10 || 10 || 10 || 3 || 5 || 2 || Tie\n|}')
    result = parse_polls(text, 'test', mapping, {})
    assert result.polls[0]['fieldwork_end'] == '2026-10-12'
    with pytest.raises(ParseDrift, match='invalid_dates'):
        parse_polls(text.replace('"2026-10-12"', '"2026-10-11"'), 'test', mapping, {})
