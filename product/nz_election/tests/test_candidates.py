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


def test_conflicts_preserved():
    row = deepcopy(c.load()[0]['candidates'][0])
    claim = dict(value='Different official name', source_id=c.WIKI, locator='section/box:1')
    mapping = dict(candidate_id=row['id'], electorate_id=row['electorate_id'], party_id=row['party_id'],
                   reviewer='test reviewer', evidence='synthetic reviewed identifiers', claims={'name': [claim]})
    conflicts = c.apply_mappings([row], [mapping])
    assert row['name'] == 'CHANG, Johan' and row['join_status'] == 'Unresolved'
    assert [r['value'] for r in conflicts[0]['claims']] == ['CHANG, Johan', claim['value']]
    assert all(r['source_id'] and r['locator'] for r in conflicts[0]['claims'])


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
