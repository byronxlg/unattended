"""EC spine, explicit identity review, safe parsing and family retention."""
from copy import deepcopy
import json
import pytest
from product.nz_election.pipeline import candidates as c, export
from product.nz_election.pipeline.fixtures import captures
from product.nz_election.pipeline.refresh import config


def test_required_candidate_captures():
    raw = captures(paths={c.SHEET, c.PDF})
    assert len(c.spreadsheet(raw[c.SHEET])) == 469
    assert raw[c.PDF].startswith(b'%PDF')


def test_candidates_revision_capture():
    path = 'wikipedia/candidates-2026.api.json'
    raw = captures(paths={path, c.WIKI})
    page = json.loads(raw[path])['query']['pages'][0]
    revision = page['revisions'][0]
    assert revision['revid'] == 1380178146
    assert revision['slots']['main']['content'] == raw[c.WIKI].decode()


def test_wikidata_capture_and_mapping(tmp_path):
    raw = json.loads(captures(paths={c.WD})[c.WD])
    assert all(r['statement']['value'].startswith('http://www.wikidata.org/entity/statement/') for r in raw['results']['bindings'])
    assert config('candidate-mappings')['mappings'] == []
    assert c.propose(tmp_path / 'proposal.json') == 0
    with pytest.raises(ValueError, match='OUTSIDE_CONFIG'):
        c.propose(c.PRODUCT / 'config/proposal.json')


def test_official_spine_and_explicit_joins():
    payload, _, _ = c.load()
    rows = payload['candidates']
    official = c.spreadsheet(captures(paths={c.SHEET})[c.SHEET])
    by_id = {r['id']: r for r in rows}
    for ec in official:
        row = by_id['ec-row-' + str(ec['row'])]
        assert (row['name'], row['party_id']) == (ec['Name'], ec['Party'])
        assert row['electorate_id'] == config('electorate-aliases')[c.nfc(ec['Electorate'])]
        assert row['wikidata_id'] is row['wikipedia_url'] is row['person_id'] is row['list_rank'] is None
    list_ids = {i for p in payload['party-lists'] for i in p['candidate_ids']}
    assert set(by_id) == {'ec-row-' + str(r['row']) for r in official} | list_ids
    assert len(list_ids) == 443
    assert all(by_id[i]['electorate_id'] is None for i in list_ids)
    assert len({r['electorate_id'] for r in rows if r['electorate_id']}) == 71


@pytest.mark.parametrize('field', ['name', 'party_id', 'list_rank'])
def test_conflicts_preserved(field):
    row = deepcopy(c.load()[0]['candidates'][0])
    original = row[field]
    official_sources = deepcopy(row['field_sources'][field])
    agreement = dict(value=original, source_id=c.WIKI, locator='section/box:1')
    claim = dict(value=2 if field == 'list_rank' else 'Different official value', source_id=c.WD, locator='statement:2')
    mapping = dict(candidate_id=row['id'], electorate_id=row['electorate_id'], party_id=row['party_id'],
                   reviewer='test reviewer', evidence='synthetic reviewed identifiers', claims={field: [claim]})
    conflicts = c.apply_mappings([row], [dict(mapping, claims={field: [agreement]}), mapping])
    assert row[field] == original and row['join_status'] == 'Unresolved'
    expected = ([original] if original is not None else []) + [original, claim['value']]
    assert [r['value'] for r in conflicts[0]['claims']] == expected
    assert all(r['source_id'] and r['locator'] for r in conflicts[0]['claims'])
    assert row['field_sources'][field][:len(official_sources)] == official_sources
    assert agreement in row['field_sources']['reviewed_claims'][field]
    assert claim in row['field_sources']['reviewed_claims'][field]
    if field in {'name', 'party_id'}:
        assert row['field_sources'][field] == official_sources
    from product.nz_election.pipeline.electorate_pages import detail, candidate_records
    electorate = next(r for r in config('electorates') if r['id'] == row['electorate_id'])
    env = dict(data=[row], source=c.load()[1], run_url='offline-verification')
    html = detail(electorate, {'candidates': env, 'candidate-review': {'data': conflicts}})
    assert 'Unresolved' in html and claim['locator'] not in html and agreement['locator'] not in html
    records = candidate_records({'candidates': env, 'candidate-review': {'data': conflicts}})
    assert 'Unresolved' in records and claim['locator'] in records and agreement['locator'] in records


def test_list_capacity_requires_complete_review():
    payload, _, _ = c.load()
    assert all(not row['complete'] for row in payload['party-lists'])
    assert 'identity' in config('ec-party-lists-2026').get('review', {}).get('status', 'identity unchecked')
    from product.nz_election.pipeline.seats import project
    from product.nz_election.pipeline.average import trend
    assert not project(trend([], ['2026-10-17'])[0])['capacity_checked']


@pytest.mark.parametrize('raw', [b'', None, '', 1, 1.5, 10**100, b'<html>Incapsula</html>', b'PK\x03\x04', 'Ｍāori'])
def test_malformed_sheet(raw):
    with pytest.raises(ValueError, match='^INVALID_CANDIDATE_SHEET$'):
        c.spreadsheet(raw)


def test_daily_independent_retention(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    path = tmp_path / 'data'
    daily_refresh(path, now='2026-10-18T00:00:00Z')
    before = {p.name: p.read_bytes() for p in path.iterdir() if p.stem in export.FAMILIES['candidates']}
    def fail():
        raise ValueError('parse_drift')
    from product.nz_election.pipeline import baseline
    daily_refresh(path, now='2026-10-19T00:00:00Z', loaders={'candidates': fail, 'baseline-2023': baseline.load})
    envs = export.validate_bundle(path)
    assert all((path / n).read_bytes() == b for n, b in before.items())
    assert envs['baseline-2023']['generated_at'] == '2026-10-19T00:00:00Z'
    assert next(r for r in envs['status']['data'] if r['dataset'] == 'candidates')['state'] == 'stale'


def test_agreeing_claims_keep_official_provenance():
    row = deepcopy(c.load()[0]['candidates'][0])
    original = deepcopy(row['field_sources'])
    claims = {field: [dict(value=row[field], source_id=c.WIKI, locator='section/box:1')]
              for field in ('name', 'party_id')}
    mapping = dict(candidate_id=row['id'], electorate_id=row['electorate_id'], party_id=row['party_id'],
                   reviewer='test reviewer', evidence='synthetic reviewed identifiers', claims=claims)
    assert c.apply_mappings([row], [mapping]) == []
    for field in claims:
        assert row['field_sources'][field] == original[field]
        assert claims[field][0] in row['field_sources']['reviewed_claims'][field]
    assert row['join_status'] == 'Reviewed'
