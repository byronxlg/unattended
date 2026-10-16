"""Regression coverage for PR 9's four confirmed review findings."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import parse_polls

HEADER = '==Party vote==\n=== Table of polls ===\n{|\n' + '\n'.join(
    '! ' + label for label in ('Date', 'Polling organisation', 'Sample size',
                               'NAT', 'LAB', 'GRN', 'ACT', 'NZF', 'TPM', 'OPP', 'Others', 'Lead')) + '\n'


def row(day=12, citation=''):
    return (f'|-\n| data-sort-value="2026-10-{day}" | 8–{day} Oct 2026\n'
            f'| Roy Morgan{citation}\n| 1000 || 30 || 30 || 10 || 10 || 10 || 3 || 5 || 2 || Tie\n')


def parse(body, mapping):
    return parse_polls(HEADER + body + '|}', 'test', mapping, {}).polls


@pytest.mark.parametrize('quote', ["'", '"', ''])
def test_share_rowspan_all_quoting(mapping, quote):
    body = row().replace('|| 3 ||', f'|| rowspan={quote}2{quote} | 3 ||')
    with pytest.raises(ParseDrift, match='unexplained_merge'):
        parse(body, mapping)


@pytest.mark.parametrize('quote', ["'", '"', ''])
def test_sort_date_all_quoting(mapping, quote):
    body = row().replace('"2026-10-12"', f'{quote}2026-10-11{quote}')
    with pytest.raises(ParseDrift, match='invalid_dates'):
        parse(body, mapping)


@pytest.mark.parametrize('inline', ['', '<ref>https://example.org/inline</ref>'])
def test_forward_named_reference_isolation(mapping, inline):
    body = row(12, '<ref name="x"/>') + row(13, inline) + row(14, '<ref name="x">https://example.org/x</ref>')
    polls = parse(body, mapping)
    assert polls[0]['reference_urls'] == ['https://example.org/x']
    assert '8–13 Oct' not in polls[0]['reference_text']
    assert '8–14 Oct' not in polls[0]['reference_text']
    assert polls[1]['reference_urls'] == (['https://example.org/inline'] if inline else [])
    assert polls[2]['reference_urls'] == ['https://example.org/x']


def valid(party='A'):
    return dict(partyVotes={party: 100}, electorateWins={party: 0},
                lists={party: ['c']}, electorateWinners={party: []},
                nonListWinners=[], baseSeats=1)


def js_results(inputs):
    node = shutil.which('node')
    assert node, 'NODE_REQUIRED_FOR_PARITY'
    runner = Path(__file__).with_name('allocator_runner.mjs')
    result = subprocess.run([node, str(runner)], input=json.dumps(inputs), text=True,
                            capture_output=True, check=True)
    return json.loads(result.stdout)


def malformed():
    yield {}
    data = valid(); data['lists']['A'] = [{}]; yield data
    data = valid(); data['baseSeats'] = None; yield data
    yield None
    yield []
    for key in valid():
        data = valid(); data[key] = None; yield data
    for key in ('partyVotes', 'electorateWins', 'lists', 'electorateWinners', 'nonListWinners'):
        data = valid(); del data[key]; yield data
    for lot in (None, [], {'order': [{}]}, {'reference': 5}, {'order': 'A'}):
        data = valid(); data['tieOrder'] = lot; yield data
    data = valid(); data['electorateWinners']['A'] = [{}]; yield data
    data = valid(); data['nonListWinners'] = [{}]; yield data


@pytest.mark.parametrize('data', list(malformed()))
def test_malformed_inputs_exact_error_parity(data):
    with pytest.raises(ValueError, match='^INVALID_INPUT$'):
        allocate(data)
    assert js_results([data]) == [{'error': 'INVALID_INPUT'}]


@pytest.mark.parametrize('party', ['__proto__', 'constructor', 'toString'])
def test_special_party_ids_parity(party):
    data = valid(party)
    expected = allocate(data)
    assert expected['seats'] == {party: 1}
    assert js_results([data]) == [{'result': expected}]


def test_absent_base_defaults_in_both_languages():
    data = valid(); del data['baseSeats']
    assert js_results([data]) == [{'result': allocate(data)}]


@pytest.mark.parametrize('party', ['__proto__', 'constructor', 'toString'])
def test_missing_list_does_not_use_object_prototype(party):
    data = valid(party)
    data['lists'] = {}
    with pytest.raises(ValueError, match='^INVALID_INPUT$'):
        allocate(data)
    assert js_results([data]) == [{'error': 'INVALID_INPUT'}]
