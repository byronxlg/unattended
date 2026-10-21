"""Historical scorecard contract, verified offline against pinned captures."""
from copy import deepcopy
from fractions import Fraction
import gzip
import json
import shutil

import pytest

from product.nz_election.pipeline import snapshots as s
from product.nz_election.pipeline.pollster_scorecard import load_pollster_record, DAYS


@pytest.fixture
def snapshot(tmp_path):
    data = json.loads((s.SNAPSHOTS / 'pollster-record.json').read_text())
    shutil.copytree(s.SNAPSHOTS / 'pollster-record-sources', tmp_path / 'pollster-record-sources')
    return data, tmp_path / 'pollster-record.json'


def load(snapshot):
    data, path = snapshot
    path.write_text(json.dumps(data))
    return load_pollster_record(path)


def rational(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def test_scorecard_final_eligible_poll(snapshot):
    rows = load(snapshot)
    assert len(rows) == 19
    expected = {
        2017: {'roy-morgan': '2017-09-10', 'reid-research': '2017-09-20',
               'verian': '2017-09-19', 'bauer': '2017-09-05', 'ssi': '2017-09-06',
               'umr': '2017-08-16'},
        2020: {'roy-morgan': '2020-09-30', 'reid-research': '2020-10-15',
               'verian': '2020-10-14', 'yougov': '2019-11-11', 'umr': '2020-09-02'},
        2023: {'verian': '2023-10-10', 'reid-research': '2023-10-10',
               'roy-morgan': '2023-10-08', 'essential': '2023-10-08',
               'curia': '2023-10-04', 'talbot-mills': '2023-09-28',
               'freshwater': '2023-08-30', 'horizon': '2023-05-17'},
    }
    assert {(r['year'], r['pollster_id']): r['fieldwork_end'] for r in rows} == {
        (year, p): end for year, ps in expected.items() for p, end in ps.items()}
    newer = deepcopy(snapshot[0]['candidates'][0])
    newer.update(id='later-survey', fieldwork_end='2017-09-21')
    snapshot[0]['candidates'].append(newer)
    with pytest.raises(ValueError, match='^scorecard_final_poll$'):
        load(snapshot)


def test_scorecard_excludes_post_election_information(snapshot):
    data, _ = snapshot
    rows = load(snapshot)
    # Later retrospective tables add precision and omit Loyal; freeze the prior observations.
    cb = next(r for r in rows if r['year'] == 2017 and r['pollster_id'] == 'verian')
    assert cb['poll_shares']['tpm'] == '1'
    cb = next(r for r in rows if r['year'] == 2020 and r['pollster_id'] == 'verian')
    assert cb['poll_shares']['nzf'] == '3'
    assert next(r for r in rows if r['year'] == 2023 and r['pollster_id'] == 'verian')[
        'poll_shares']['loyal'] == '1.2'
    assert any(c['year'] == 2020 and c['pollster_id'] == 'umr'
               and c['fieldwork_label'] == '13 Oct 2020' and 'excluded_reason' in c
               for c in data['candidates'])
    for source in data['sources']:
        assert source['revision_at'][:10] < DAYS[source['year']]
        raw = json.loads(gzip.decompress((s.SNAPSHOTS / source['capture']).read_bytes()))
        revision = next(iter(raw['query']['pages'].values()))['revisions'][0]
        assert str(revision['revid']) == source['revision_id']
        assert revision['timestamp'] == source['revision_at']
    data['records'][0]['published_by'] = '2017-09-22T12:00:00Z'
    with pytest.raises(ValueError, match='^scorecard_publication$'):
        load(snapshot)


def test_scorecard_party_errors_and_coverage(snapshot):
    data, _ = snapshot
    rows = load(snapshot)
    officials = {r['year']: r for r in data['official_results']}
    assert [r['valid_party_votes'] for r in data['official_results']] == [
        '2591896', '2886420', '2851211']
    for r in rows:
        official = officials[r['year']]
        counts = {p['party_id']: int(p['votes']) for p in official['parties']}
        assert sum(counts.values()) == int(official['valid_party_votes'])
        errors = [Fraction(r['poll_shares'][p]) - Fraction(100 * counts[p], sum(counts.values()))
                  for p in r['compared_parties']]
        assert [rational(r['party_errors'][p]) for p in r['compared_parties']] == errors
        assert rational(r['mean_absolute_error']) == sum(map(abs, errors)) / len(errors)
        assert set(r['not_reported_parties']) == set(counts) - set(r['poll_shares'])
    morgan = rows[0]
    # A published zero is compared; a blank is not imputed as zero.
    assert morgan['poll_shares']['united-future'] == '0'
    assert 'united-future' in morgan['compared_parties']
    assert 'mana' in morgan['not_reported_parties']
    assert rational(morgan['party_errors']['nat']) < 0
    assert rational(morgan['party_errors']['lab']) > 0


def test_scorecard_absent_comparable_input(snapshot):
    snapshot[0]['records'][0]['poll_shares'] = {}
    with pytest.raises(ValueError, match='^scorecard_absent_comparable_input$'):
        load(snapshot)


BAD = ['', None, [], {}, True, 1.5, 10**100, 'NaN', '\u200b', '1e99999']


@pytest.mark.parametrize('value', BAD)
@pytest.mark.parametrize('field,code', [
    ('source_url', 'source'), ('retrieved_at', 'retrieved_at'),
    ('fieldwork_end', 'fieldwork'), ('published_by', 'publication'),
    ('mean_absolute_error', 'mean'), ('year', 'record'), ('pollster_id', 'record'),
    ('compared_parties', 'coverage'), ('not_reported_parties', 'coverage'),
    ('party_errors', 'error'), ('official_shares', 'official'), ('licence', 'licence'),
])
def test_scorecard_named_error_malformed_record(snapshot, field, code, value):
    snapshot[0]['records'][0][field] = value
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


@pytest.mark.parametrize('value', BAD + ['100.1', '-1', '0.1234567890123'])
def test_scorecard_decimal_named_error(snapshot, value):
    snapshot[0]['records'][0]['poll_shares']['nat'] = value
    with pytest.raises(ValueError, match='^scorecard_decimal$'):
        load(snapshot)


@pytest.mark.parametrize('field,code', [('fieldwork_end', 'fieldwork'),
                                        ('published_by', 'publication')])
def test_scorecard_cutoff_named_error(snapshot, field, code):
    snapshot[0]['records'][0][field] = ('2017-09-23' if field == 'fieldwork_end'
                                      else '2017-09-22T12:00:00Z')
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


def test_scorecard_duplicate_named_error(snapshot):
    snapshot[0]['records'].append(deepcopy(snapshot[0]['records'][0]))
    with pytest.raises(ValueError, match='^scorecard_duplicate$'):
        load(snapshot)


@pytest.mark.parametrize('field,code', [('party_errors', 'error'),
                                        ('mean_absolute_error', 'mean'),
                                        ('official_shares', 'official')])
def test_scorecard_arithmetic_named_error(snapshot, field, code):
    value = snapshot[0]['records'][0][field]
    if field != 'mean_absolute_error':
        value = value['nat']
    value['numerator'] = str(int(value['numerator']) + 1)
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


@pytest.mark.parametrize('url', [
    'https://en.wikipedia.org/wiki/Poll', 'https://en.wikipedia.org/w/index.php?oldid=NaN',
    'https://en.wikipedia.org.evil.test/w/index.php?oldid=123',
    'https://en.wikipedia.org:444/w/index.php?oldid=123',
    'https://user@en.wikipedia.org/w/index.php?oldid=123',
    'https://example.com/?oldid=123',
])
def test_scorecard_source_named_error(snapshot, url):
    snapshot[0]['records'][0]['source_url'] = url
    with pytest.raises(ValueError, match='^scorecard_source$'):
        load(snapshot)


@pytest.mark.parametrize('field', ['source_url', 'retrieved_at'])
def test_scorecard_required_provenance_named_error(snapshot, field):
    del snapshot[0]['records'][0][field]
    code = 'source' if field == 'source_url' else field
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


def test_scorecard_official_denominator_named_error(snapshot):
    # Total votes including informal votes is not the valid party-vote denominator.
    snapshot[0]['official_results'][0]['valid_party_votes'] = '2602689'
    with pytest.raises(ValueError, match='^scorecard_official$'):
        load(snapshot)


def test_scorecard_coverage_named_error(snapshot):
    snapshot[0]['records'][0]['not_reported_parties'].pop()
    with pytest.raises(ValueError, match='^scorecard_coverage$'):
        load(snapshot)


@pytest.mark.parametrize('mutation,code', [
    ('schema', 'schema'), ('source_revision', 'revision'), ('digest', 'capture'),
    ('candidate', 'candidate'), ('skip', 'skip'), ('record', 'record'),
])
def test_scorecard_envelope_named_errors(snapshot, mutation, code):
    data, _ = snapshot
    if mutation == 'schema':
        data['schema'] = None
    elif mutation == 'source_revision':
        data['sources'][0]['revision_id'] = '123'
    elif mutation == 'digest':
        data['sources'][0]['sha256'] = '0' * 64
    elif mutation == 'candidate':
        data['candidates'].append(deepcopy(data['candidates'][0]))
    elif mutation == 'skip':
        data['skipped'].pop()
    else:
        data['records'][0] = None
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


def test_scorecard_unreadable_named_error(tmp_path):
    path = tmp_path / 'broken.json'
    path.write_text('{')
    with pytest.raises(ValueError, match='^scorecard_schema$'):
        load_pollster_record(path)


@pytest.mark.parametrize('value', BAD + ['0', '-1', '1.5'])
@pytest.mark.parametrize('field,code', [('party_errors', 'error'),
                                        ('mean_absolute_error', 'mean')])
def test_scorecard_ratio_denominator_named_error(snapshot, value, field, code):
    target = snapshot[0]['records'][0][field]
    if field == 'party_errors':
        target = target['nat']
    target['denominator'] = value
    with pytest.raises(ValueError, match='^scorecard_' + code + '$'):
        load(snapshot)


def test_scorecard_truncated_capture_named_error(snapshot):
    _, path = snapshot
    (path.parent / 'pollster-record-sources/wikipedia-2017.json.gz').write_bytes(b'\x1f\x8b')
    with pytest.raises(ValueError, match='^scorecard_capture$'):
        load(snapshot)
