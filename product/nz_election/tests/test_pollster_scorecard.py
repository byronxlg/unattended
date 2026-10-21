"""Historical scorecard contract, verified offline against pinned captures."""
from copy import deepcopy
from fractions import Fraction
import gzip
import json
import re
from collections import Counter
import shutil

import pytest

from product.nz_election.pipeline import snapshots as s
from product.nz_election.pipeline.poll_parser import tables, split_markup, cell, clean
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
    assert len(rows) == 20
    expected = {
        2017: {'roy-morgan': '2017-09-10', 'reid-research': '2017-09-20',
               'verian': '2017-09-19', 'bauer': '2017-09-05', 'ssi': '2017-09-06',
               'umr': '2017-08-16', 'herald-digipoll': '2015-12-14'},
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


# Source labels, independently enumerated from all national tables. Unknown labels
# must fail this audit rather than disappear through the transcription's filter.
CAPTURE_POLLSTERS = {
    'Roy Morgan Research': 'roy-morgan', 'Roy Morgan': 'roy-morgan',
    '3 News Reid Research': 'reid-research', 'Newshub Reid Research': 'reid-research',
    'Newshub–Reid Research': 'reid-research', 'Business NZ–Reid Research': 'reid-research',
    'One News Colmar Brunton': 'verian', '1 News–Colmar Brunton': 'verian',
    '1 News–Kantar Public': 'verian', '1 News–Verian': 'verian',
    'Listener: Bauer Media Insights': 'bauer', 'Newsroom-SSI': 'ssi',
    'Herald-DigiPoll': 'herald-digipoll', 'UMR Research': 'umr', 'Curia': 'curia',
    'Stuff–YouGov': 'yougov', 'Guardian Essential': 'essential',
    'Horizon Research': 'horizon', 'Talbot Mills': 'talbot-mills',
    'Labour–Talbot Mills': 'talbot-mills', 'The Post–Freshwater Strategy': 'freshwater',
    "Taxpayers' Union-Curia": 'curia', "Taxpayers' Union–Curia": 'curia',
}


def assert_capture_pollster_completeness(data):
    outcomes = Counter((r['year'], r['pollster_id'])
                       for r in data['records'] + data['skipped'])
    assert all(count == 1 for count in outcomes.values())
    observed = set()
    for source in data['sources']:
        raw = json.loads(gzip.decompress((s.SNAPSHOTS / source['capture']).read_bytes()))
        text = next(iter(raw['query']['pages'].values()))['revisions'][0]['slots']['main']['*']
        national_tables = 0
        for section, _, body in tables(text):
            if not (section[0].startswith('Party vote') and section[-1] in {
                    'Individual polls', 'UMR and Curia polls', 'Nationwide polling'}):
                continue
            national_tables += 1
            for row in split_markup(body, '\n|-')[1:]:
                cells = []
                for chunk in split_markup(row, '\n'):
                    if chunk.startswith('|') and not chunk.startswith('|+'):
                        cells.extend(split_markup(chunk[1:], '||'))
                # Event rows span columns; header rows start with !, not |.
                if len(cells) < 6:
                    continue
                label = clean(cell(cells[0 if source['year'] == 2017 else 1])[1])
                if re.fullmatch(r'20[0-9]{2} election result', label):
                    continue
                assert label in CAPTURE_POLLSTERS, f'Unaccounted source pollster: {label}'
                key = source['year'], CAPTURE_POLLSTERS[label]
                observed.add(key)
                assert outcomes[key] == 1, f'Expected exactly one score or exclusion: {key}'
        assert national_tables == (1 if source['year'] == 2023 else 2)
    assert {pid for _, pid in observed} == {pid for _, pid in outcomes}
    return observed


def test_scorecard_pinned_capture_pollster_completeness(snapshot):
    observed = assert_capture_pollster_completeness(snapshot[0])
    assert (2017, 'herald-digipoll') in observed
    assert len(observed) == 21  # 20 scores and Curia's ineligible 2020 national rows.


@pytest.mark.parametrize('pollster', sorted(set(CAPTURE_POLLSTERS.values())))
def test_scorecard_completeness_detects_omitted_pollster(snapshot, pollster):
    data, _ = snapshot
    # Removing the entire identity used to fool the self-referential ledger check.
    for key in ('records', 'skipped', 'candidates'):
        data[key] = [r for r in data[key] if r['pollster_id'] != pollster]
    with pytest.raises(AssertionError, match='Expected exactly one score or exclusion'):
        assert_capture_pollster_completeness(data)


def test_scorecard_herald_digipoll_has_no_age_exemption(snapshot):
    rows = load(snapshot)
    herald = next(r for r in rows if r['pollster_id'] == 'herald-digipoll')
    assert herald['fieldwork_label'] == '4–14 Dec 2015'
    assert herald['poll_shares'] == {
        'nat': '51.3', 'lab': '31.1', 'grn': '8.2', 'nzf': '5.7',
        'tpm': '2.1', 'act': '0.8', 'united-future': '0.3'}
    assert rational(herald['mean_absolute_error']) == Fraction(28389754, 11339545)
    assert next(r for r in rows if r['pollster_id'] == 'yougov')['fieldwork_end'] == '2019-11-11'


@pytest.mark.parametrize('changes', [
    {'fieldwork_end': '2020-09-29'},
    {'fieldwork_end': '2020-08-31'},
    {'fieldwork_end': '2019-09-30'},
    {'fieldwork_precision': 'day'},
    {'fieldwork_end': '2020-09-29', 'fieldwork_precision': 'day'},
    {'fieldwork_label': 'Sep 0000'},
    {'fieldwork_label': 'Bogus 2020'},
    {'fieldwork_label': 'Sep 20'},
    {'fieldwork_label': '9–29 Sep 2020'},
])
def test_scorecard_month_end_bound_rejects_source_mismatch(snapshot, changes):
    # Mutate both copies so consistency/final-selection checks cannot mask the gap.
    for row in snapshot[0]['records'] + snapshot[0]['candidates']:
        if (row['year'], row['pollster_id'], row['fieldwork_label']) == (
                2020, 'roy-morgan', 'Sep 2020'):
            row.update(changes)
    with pytest.raises(ValueError, match='^scorecard_fieldwork$'):
        load(snapshot)
