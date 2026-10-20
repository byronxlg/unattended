"""Window boundaries, coverage and exact arithmetic independent of captured percentages."""
from decimal import Decimal
from product.nz_election.pipeline.average import select_window, deduplicate, check_vector, mean_vector, trend, threshold_watch, display


def poll(identity='a', end='2026-10-17', revision='1', **shares):
    return dict(id=identity, fieldwork_end=end, revision=revision,
                shares={k: None if v is None else Decimal(v) for k, v in shares.items()})


def test_inclusive_window():
    rows = [poll(str(n), end=d) for n, d in enumerate(['2026-09-17', '2026-09-18', '2026-10-17', '2026-10-18'])]
    assert [p['id'] for p in select_window(rows, '2026-10-17')] == ['1', '2']


def test_corrected_poll_deduplication():
    rows = [poll(revision='11', nat='32'), poll(revision='2', nat='31'), poll('b', nat='30')]
    assert len(deduplicate(rows)) == 2
    assert deduplicate(rows)[0]['shares']['nat'] == 32


def test_coherent_vector():
    rows = [poll(nat='51', others='49'), poll('b', nat='52', others='48')]
    assert check_vector(rows)[2] == []
    assert mean_vector(rows)['coherent']
    review = {'exclusions': {'a': {'revision': '1', 'reason': 'synthetic coverage review', 'review_ref': 'test'}}}
    included, exclusions, missing = check_vector(rows, review=review)
    assert len(included) == len(exclusions) == 1 and not missing


def test_missing_is_not_zero():
    rows = [poll(nat='51', others='49'), poll('b', nat='52', opp='3', others='45')]
    result = trend(rows, ['2026-10-17'])[0]
    assert not result['coherent'] and result['shares'] is None
    assert result['missing'] == [{'poll_id': 'a', 'party_id': 'opp'}]
    assert result['descriptive']['opp']['poll_ids'] == ['b']
    assert not trend([poll(nat='50')], ['2026-10-17'])[0]['coherent']


def test_exact_integer_mean():
    result = mean_vector([poll(nat='33.25', others='66.7'), poll('b', nat='33.35', others='66.7')])
    assert result['shares'] == {'nat': 6660, 'others': 13340}
    assert result['scale'] == 200 and result['denominator'] == 20000
    assert mean_vector([poll(nat='33.3', others='66.6')])['denominator'] == 999


def test_trend_dates_and_rounding():
    result = trend([poll(nat='2.25', others='97.75')], ['2026-10-16', '2026-10-17'])
    assert result[0]['shares'] is None
    assert result[1]['window_start'] == '2026-09-18'
    assert display(225, 100) == '2.3%'
    assert display(None, 0) == ''


def test_threshold_membership():
    rows = [poll(nat='90', opp='2', tpm='7', others='1'), poll('b', nat='92', opp='1', tpm=None, others='7')]
    avg = trend(rows, ['2026-10-17'])[0]
    watch = threshold_watch(rows, avg, {'electorate_wins': {'tpm': 6}})
    assert {p['party_id'] for p in watch} == {'opp', 'tpm'}
    tpm = next(p for p in watch if p['party_id'] == 'tpm')
    assert tpm['electorate_qualifies'] and tpm['missing_poll_ids'] == ['b']


def test_theoretical_primitive_python_js_parity():
    import json
    from pathlib import Path
    import shutil
    import subprocess
    from product.nz_election.pipeline.allocator import entitlement
    node = shutil.which('node')
    assert node, 'NODE_REQUIRED_FOR_PARITY'
    module = (Path(__file__).resolve().parents[1] / 'web/allocator.mjs').as_uri()
    cases = [({'nat': 35, 'lab': 34, 'grn': 11, 'act': 9, 'nzf': 6, 'others': 5}, ['nat', 'lab', 'grn', 'act', 'nzf'], 120),
             ({'a': 1, 'b': 1}, ['a', 'b'], 1)]
    for votes, eligible, count in cases:
        source = f"import {{entitlement}} from {json.dumps(module)}; const v={json.dumps(votes)}; console.log(JSON.stringify(entitlement(Object.fromEntries(Object.entries(v).map(([p,n])=>[p,BigInt(n)])),{json.dumps(eligible)},BigInt({count}))));"
        actual = json.loads(subprocess.check_output([node, '--input-type=module', '-e', source], text=True))
        assert actual == entitlement(votes, eligible, count)
