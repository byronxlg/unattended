"""Reader abbreviations in the shared legacy and social seat strip."""
import json
from pathlib import Path
import subprocess

import pytest

from product.nz_election.pipeline.build import explorer, strip
from product.nz_election.pipeline.content_checks import Tree


def test_strip_uses_top_reader_abbreviation():
    counts = dict(nat=43, lab=35, grn=15, act=9, nzf=7, tpm=4, opp=7)
    html = strip(dict(seats=counts, entitlements=counts,
                      assumed_house=120, assumed_majority=61, overhang=0))
    assert '<span>TOP</span>' in html
    assert 'OPP' not in html
    for party in ('NAT', 'LAB', 'GRN', 'ACT', 'NZF', 'TPM'):
        assert f'<span>{party}</span>' in html


@pytest.mark.parametrize('overhang', [0, 3])
def test_seven_party_client_server_abbreviation_parity(overhang):
    counts = dict(nat=43, lab=35, grn=15, act=9, nzf=7, tpm=4, opp=7)
    average = dict(id='average', shares=counts, denominator=120, coherent=True,
                   missing=[], poll_ids=['poll'],
                   descriptive={p: {'poll_ids': ['poll']} for p in counts})
    seats = dict(average_id='average', capacity_checked=False,
                 assumptions=dict(non_list_winners=[], base_seats=120, electorate_wins={}))
    envs = dict(averages={'data': [average]},
                seats=dict(data=seats, input_hashes={'averages.json': 'a' * 64}),
                manifest={'data': [{'path': 'seats.json', 'sha256': 'b' * 64}]})
    rows = [n.attrs for n in Tree(explorer(envs)).nodes if 'data-party-row' in n.attrs]
    labels = {r['data-party-row']: dict(name=r['data-name'], colour=r['data-colour'],
                                       abbreviation=r.get('data-abbreviation')) for r in rows}
    result = dict(seats=dict(counts, nat=43 + overhang), entitlements=counts,
                  assumed_house=120 + overhang, assumed_majority=(120 + overhang) // 2 + 1,
                  overhang=overhang)
    module = Path(__file__).resolve().parents[1] / 'web/coalitions.mjs'
    script = ('import {stripHTML} from ' + json.dumps(module.as_uri()) + ';'
              "let raw=''; for await (const chunk of process.stdin) raw+=chunk;"
              'const x=JSON.parse(raw); process.stdout.write(stripHTML(x.result,x.labels));')
    actual = subprocess.run(['node', '--input-type=module', '-e', script],
                            input=json.dumps(dict(result=result, labels=labels)),
                            text=True, capture_output=True, check=True).stdout
    assert '<span>TOP</span>' in actual
    assert 'OPP' not in actual
    assert actual == strip(result)
    assert labels['opp']['abbreviation'] == 'TOP'
