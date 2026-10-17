"""Original totals, honest missing observations and all current detail routes."""
import json
import pytest
from product.nz_election.pipeline import baseline, enrolment, electorate_polls, export
from product.nz_election.pipeline.fixtures import captures
from product.nz_election.pipeline.refresh import config


def test_required_baseline_captures():
    captures(paths={baseline.PARTY} | {f'ec-2023/candidate-votes-by-voting-place-{n}.csv' for n in range(1, 73)})


def test_original_names_and_successor_comparisons():
    from product.nz_election.pipeline.electorate_pages import detail
    rows, _, _ = baseline.load()
    row = next(r for r in config('electorates') if r['slug'] == 'wellington-north')
    html = detail(row, {})
    assert row['boundary_note'] in html
    assert 'not been moved or added together' in html
    env = dict(data=rows['baseline-2023'], source=[], run_url='offline-verification')
    html = detail(row, {'baseline-2023': env})
    for old in rows['baseline-2023']:
        if old['old_electorate_id'] in row['baseline_ids']:
            assert old['old_name'] + ' (2023)' in html
    assert 'Comparison unresolved' in detail(dict(row, baseline_ids=[], mapping_status='unresolved'), {})


def test_no_total_double_count():
    rows = baseline.load()[0]['baseline-2023']
    central = next(r for r in rows if r['old_electorate_id'] == 1)
    assert sum(v['votes'] for v in central['candidate_votes']) == 34447
    assert sum(v['votes'] for v in central['party_votes']) == 35378
    assert len(rows) == 72
    assert sum(sum(v['votes'] for v in r['party_votes']) for r in rows) == 2851211


def test_port_waikato_not_fabricated():
    row = next(r for r in baseline.load()[0]['baseline-2023'] if r['old_electorate_id'] == 39)
    assert row['candidate_votes'] is None
    assert 'deferred' in row['field_sources']['candidate_status']
    assert sum(r['votes'] for r in row['party_votes']) > 0


def test_enrolment_capture_has_observation_date():
    for kind in ('general', 'maori'):
        path = f'ec-2026/wayback-enrolment-{kind}.html'
        assert enrolment.observation(captures(paths={path})[path]) == ('2024-09-30' if kind == 'general' else '2024-08-31')
        shell = f'ec-2026/enrolment-{kind}.html'
        assert enrolment.observation(captures(paths={shell})[shell]) is None
    rows = enrolment.load()[0]['enrolment']
    assert len(rows) == 71
    assert all(r['as_of'] == r['observed_at'] and r['as_of'] in {'2024-08-31', '2024-09-30'} and r['enrolled'] is r['eligible'] is None for r in rows)
    assert all('national' in r['roll_basis'].lower() for r in rows)


def test_local_poll_measures_separate():
    rows = electorate_polls.load()[0]['electorate-polls']
    assert len(rows) == 27
    assert {r['measure'] for r in rows} == {'candidate_vote', 'party_vote'}
    assert all(r['boundary_basis'] and r['source_ref'] and r['reference_urls'] for r in rows)
    unknown = [r for r in rows if r['fieldwork_end'] is None]
    assert len(unknown) == 1 and unknown[0]['boundary_basis']['fieldwork_label'] == 'Sep 2026'
    assert any(v['approximate'] for r in rows for v in r['shares'].values())
    assert {r['boundary_basis']['source_name'] for r in rows if r['electorate_id'] is None} == {'Kāpiti', 'Mount Albert'}


def test_local_unknown_table_fails():
    path = electorate_polls.PATH
    raw = captures(paths={path})[path].decode()
    from product.nz_election.pipeline.models import ParseDrift
    with pytest.raises(ParseDrift):
        electorate_polls.parse(raw.replace('Electorate vote', 'Mystery vote'), '2026-10-17T00:00:00Z')
    assert electorate_polls.parse('No local tables in this source.', '2026-10-17T00:00:00Z') == []


def test_local_poll_regions_have_distinct_names():
    from copy import deepcopy
    from html.parser import HTMLParser
    from product.nz_election.pipeline.electorate_pages import detail

    class Tables(HTMLParser):
        def __init__(self):
            super().__init__()
            self.regions, self.sources = [], []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if attrs.get('role') == 'region':
                self.regions.append(attrs['aria-label'])
            if tag == 'table':
                self.sources.append(attrs.get('aria-describedby'))

    poll = next(p for p in electorate_polls.load()[0]['electorate-polls'] if p['electorate_id'])
    row = next(r for r in config('electorates') if r['id'] == poll['electorate_id'])
    other = deepcopy(poll)
    other['id'] += '-second-report'
    other['poll_id'] = other['id']
    env = dict(data=[poll, other], source=[], run_url='offline-verification')
    for measure in ('party_vote', 'candidate_vote'):
        other['measure'] = measure
        parsed = Tables()
        parsed.feed(detail(row, {'electorate-polls': env}))
        assert len(parsed.regions) == len(set(parsed.regions)) == 2
        assert all(poll['pollster'] in name and poll['boundary_basis']['fieldwork_label'] in name
                   for name in parsed.regions)
        assert parsed.sources == ['source-electorate-polls', 'source-electorate-polls']


def test_71_pages_and_missing_data(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.electorate_pages import detail
    path, site = tmp_path / 'data', tmp_path / 'output'
    daily_refresh(path)
    build(path, site)
    assert len(list((site / 'electorates').glob('*/index.html'))) == 71
    expected = [r['path'] for r in config('routes')] + ['electorates/' + r['slug'] + '/' for r in config('electorates')]
    assert len(expected) == len(set(expected))
    assert {p.relative_to(site).as_posix() for p in site.rglob('index.html')} == {p + 'index.html' for p in expected}
    from copy import deepcopy
    envs = export.validate_bundle(path)
    central = next(r for r in config('electorates') if r['slug'] == 'auckland-central')
    assert 'No candidate baseline' not in detail(central, envs)
    missing = deepcopy(envs)
    old = next(r for r in missing['baseline-2023']['data'] if r['old_electorate_id'] == 1)
    old['candidate_votes'] = None
    old['field_sources']['candidate_status'] = 'Missing candidate capture.'
    html = detail(central, missing)
    assert 'No candidate baseline. Missing candidate capture.' in html
    assert '<summary>No 2023 candidate results for this electorate</summary>' in html
    assert 'Auckland Central (2023)' in html and 'party votes' in html
    row = next(r for r in config('electorates') if r['slug'] == 'te-tai-tonga')
    html = detail(row, {})
    assert 'Official candidates not available' in html and 'Map not available' in html
    assert 'no dated electorate enrolment observation' in html


def test_new_csv_and_dates(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(tmp_path / 'data')
    envs = export.validate_bundle(tmp_path / 'data')
    for stem in export.NEW_FIELDS:
        assert (tmp_path / 'data' / (stem + '.csv')).read_bytes() == export.csv_bytes(envs[stem])
    env = json.loads(json.dumps(envs['enrolment']))
    env['source'][0]['fetched_at'] = '2024-08-31'
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        export.validate_envelope(env, 'enrolment')


def test_sheet_zip_limits():
    import io
    import zipfile
    from product.nz_election.pipeline.candidates import spreadsheet
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('xl/workbook.xml', b' ' * 2_000_001)
    with pytest.raises(ValueError, match='INVALID_CANDIDATE_SHEET'):
        spreadsheet(buffer.getvalue())


def test_new_numeric_contracts():
    from copy import deepcopy
    payloads, sources, hashes = enrolment.load()
    env = export.envelope(payloads['enrolment'], sources, 'offline-verification', 'test', inputs=hashes,
                          method='enrolment-v1', generated='2026-10-17T00:00:00Z')
    for value in ['', '0', False, 1.5, -1, [], {}]:
        bad = deepcopy(env)
        bad['data'][0]['enrolled'] = value
        with pytest.raises(ValueError):
            export.validate_envelope(bad, 'enrolment')
    bad = deepcopy(env)
    bad['data'][0]['as_of'] = None
    with pytest.raises(ValueError, match='INVALID_ENROLMENT_OBSERVATION'):
        export.validate_envelope(bad, 'enrolment')


def test_family_failure_before_first_success(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline import candidates
    def fail():
        raise ValueError('MISSING_CAPTURE: enrolment')
    path = tmp_path / 'data'
    daily_refresh(path, loaders={'enrolment': fail, 'candidates': candidates.load})
    envs = export.validate_bundle(path)
    assert 'enrolment' not in envs and 'candidates' in envs
    status = next(r for r in envs['status']['data'] if r['dataset'] == 'enrolment')
    assert status['state'] == 'unavailable' and status['last_success_at'] is None


def test_verifier_accepts_present_mangere(tmp_path, monkeypatch):
    from copy import deepcopy
    from product.nz_election.pipeline.verify import verify_electorates
    original_load = baseline.load
    def present():
        payload, sources, hashes = original_load()
        rows = payload['baseline-2023']
        mangere = next(r for r in rows if r['old_electorate_id'] == 21)
        # Synthetic presence isolates the verifier from the outstanding capture gate.
        mangere['candidate_votes'] = deepcopy(next(r for r in rows if r['old_electorate_id'] == 1)['candidate_votes'])
        mangere['field_sources']['candidate_status'] = None
        return payload, sources, hashes
    monkeypatch.setattr(baseline, 'load', present)
    verify_electorates({}, tmp_path)
