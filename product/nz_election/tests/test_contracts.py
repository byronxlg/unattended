"""Published bytes retain provenance and lossless nested collections."""
import csv
import io
import json
import pytest
from product.nz_election.pipeline import export
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.fixtures import captures, golden


@pytest.fixture
def bundle(tmp_path):
    path = tmp_path / 'data'
    refresh(path, now='2026-10-17T01:00:00Z')
    return path


def test_capture_manifest():
    raw = captures()
    assert len(raw) == 144
    assert {p for p in raw if p.startswith('result-states/')} == {
        'result-states/2026-11-07-preliminary-final.json', 'result-states/2026-11-27-official.json'}


def test_envelopes_and_provenance(bundle):
    envs = export.validate_bundle(bundle)
    assert envs['polls']['fetched_at'] != envs['averages']['generated_at']
    assert envs['seats']['data']['capacity_checked'] is False
    assert envs['seats']['data']['occupied_house'] is None
    for env in envs.values():
        for row in export.rows(env):
            assert {'id', 'source_ref', 'observed_at'} <= row.keys()
    bad = dict(envs['polls'], schema_version=2)
    with pytest.raises(ValueError, match='ENVELOPE'):
        export.validate_envelope(bad, 'polls')


def test_csv_round_trip(bundle):
    for stem, env in export.validate_bundle(bundle).items():
        records = list(csv.DictReader(io.StringIO((bundle / (stem + '.csv')).read_text())))
        assert len(records) == len(export.rows(env))
        for record, payload in zip(records, export.rows(env)):
            for key, value in payload.items():
                if key + '_json' in record:
                    assert json.loads(record[key + '_json']) == value
                else:
                    assert record[key] == export.scalar(value)


def test_manifest_hashes_and_licences(bundle):
    envs = export.validate_bundle(bundle)
    for entry in envs['manifest']['data']:
        if not entry['path'].startswith('manifest.'):
            assert entry['sha256'] == export.digest((bundle / entry['path']).read_bytes())
    assert 'CC BY-SA 4.0' in (bundle / 'LICENCES.md').read_text()
    assert 'No open licence stated' in (bundle / 'LICENCES.md').read_text()
    (bundle / 'polls.csv').write_text('corrupt')
    with pytest.raises(ValueError, match='CSV_MISMATCH'):
        export.validate_bundle(bundle)


def test_official_candidate_identity_joins():
    official = golden()
    assert sum(official['input']['partyVotes'].values()) == 2851211
    assert sum(official['expectedSeats'].values()) == 122
    assert len(official['quotients']) == 120


def test_geography_family_and_coordinate_exception(bundle):
    from copy import deepcopy
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in export.FAMILIES['polls']}
    daily_refresh(bundle, now='2026-10-18T01:00:00Z')
    envs = export.validate_bundle(bundle)
    assert all((bundle / name).read_bytes() == raw for name, raw in before.items())
    for stem in export.FAMILIES['geography']:
        assert envs[stem]['input_hashes'] and envs[stem]['generated_at']
        assert envs[stem]['data']
    boundary = deepcopy(envs['general-2025'])
    boundary['features'][0]['properties']['bad'] = 1.5
    with pytest.raises(ValueError, match='INEXACT_NUMBER'):
        export.validate_envelope(boundary, 'general-2025')
    boundary = deepcopy(envs['general-2025'])
    boundary['features'][0]['geometry']['coordinates'][0][0][1][0] = 181
    with pytest.raises(ValueError, match='COORDINATE'):
        export.validate_envelope(boundary, 'general-2025')
    for stem in export.GEO:
        records = list(csv.DictReader(io.StringIO((bundle / (stem + '.csv')).read_text())))
        assert [json.loads(r['geometry_json']) for r in records] == [next(f['geometry'] for f in envs[stem]['features'] if f['id'] == r['id']) for r in records]
    assert 'Stats NZ' in (bundle / 'LICENCES.md').read_text()


def test_daily_failure_retains_family_and_hourly_independent(bundle):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(bundle, now='2026-10-18T01:00:00Z')
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in export.FAMILIES['geography']}
    def fail():
        raise ValueError('MISSING_CAPTURE')
    status = daily_refresh(bundle, now='2026-10-18T02:00:00Z', load=fail)
    assert status['state'] == 'stale'
    refresh(bundle, now='2026-10-18T03:00:00Z')
    assert all((bundle / name).read_bytes() == raw for name, raw in before.items())
    assert 'Stats NZ' in (bundle / 'LICENCES.md').read_text()
    first = daily_refresh(bundle.parent / 'first-daily', now='2026-10-18T01:00:00Z', load=fail)
    assert first['state'] == 'unavailable' and first['last_success_at'] is None


def test_hourly_daily_race_preserves_union(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.publish import publish, git, DATA
    hourly, daily, remote = [tmp_path / s for s in ('hourly', 'daily', 'remote.git')]
    refresh(hourly, now='2026-10-18T01:00:00Z')
    daily_refresh(daily, now='2026-10-18T01:00:00Z', historical_advance=True)
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    barrier = threading.Barrier(2)
    def run(family):
        return publish(hourly if family == 'hourly' else daily, remote, family=family,
                       before_push=lambda n: barrier.wait(timeout=20) if n == 0 else None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, ['hourly', 'daily']))
    assert sorted(r['attempts'] for r in results) == [1, 2]
    from product.nz_election.pipeline.social import refresh_social, fixture_send
    social = tmp_path / 'social'
    assert refresh_social(social, '2026-10-17', now='2026-10-18T01:00:00Z',
                          fixture=True, send=fixture_send(), sleep=lambda _: None) == 'ok'
    publish(social, remote, family='social')
    checkout = tmp_path / 'checkout'
    git(tmp_path, 'clone', '-q', '--branch', 'data', str(remote), str(checkout))
    envs = export.validate_bundle(checkout / DATA)
    assert set.union(*export.FAMILIES.values()) <= envs.keys()
    from product.nz_election.pipeline import night
    assert night.validate(checkout / DATA) == night.validate(daily)
    for path in night.validate(daily):
        assert (daily / path).read_bytes() == (checkout / DATA / path).read_bytes()
    assert {r['dataset'] for r in envs['status']['data']} == set(export.FAMILIES)
    assert 'Stats NZ' in (checkout / DATA / 'LICENCES.md').read_text()
    for source in (hourly, daily, social):
        for p in source.rglob('*'):
            relative = p.relative_to(source)
            if p.is_file() and relative.with_suffix('').as_posix() in set.union(*export.FAMILIES.values()):
                assert p.read_bytes() == (checkout / DATA / relative).read_bytes()


def test_family_scoped_capture_failure(tmp_path):
    from shutil import copytree
    from product.nz_election.pipeline.fixtures import ROOT
    copytree(ROOT, tmp_path / 'fixtures')
    (tmp_path / 'fixtures/stats-nz/general-2025.geojson').unlink()
    assert captures(tmp_path / 'fixtures', paths={'wikipedia/polls-2026.wikitext'})
    with pytest.raises(ValueError, match='MISSING_CAPTURE'):
        captures(tmp_path / 'fixtures', paths={'stats-nz/general-2025.geojson'})


def test_daily_mixed_source_regression_rejected(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.publish import publish, git, DATA
    original, incoming, remote = [tmp_path / s for s in ('original', 'incoming', 'remote.git')]
    daily_refresh(original, now='2026-10-18T01:00:00Z')
    daily_refresh(incoming, now='2026-10-19T01:00:00Z')
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    publish(original, remote, family='daily')
    for stem in export.FAMILIES['geography']:
        env = json.loads((incoming / (stem + '.json')).read_text())
        env['source'][0]['fetched_at'] = '2026-10-15T01:00:00Z'
        env['source'][1]['fetched_at'] = '2026-10-19T01:00:00Z'
        env['fetched_at'] = '2026-10-19T01:00:00Z'
        export.pair(incoming, stem, env)
    export.inventory(incoming, 'offline-verification', 'test', '2026-10-19T01:00:00Z')
    publish(incoming, remote, family='daily')
    for stem in export.FAMILIES['geography']:
        actual = git(remote, 'show', 'data:' + str(DATA / (stem + '.json'))).stdout
        assert actual == (original / (stem + '.json')).read_text()
    env = json.loads((incoming / 'electorates.json').read_text())
    env['generated_at'] = '2026-10-20T01:00:00Z'
    export.pair(incoming, 'electorates', env)
    export.inventory(incoming, 'offline-verification', 'test', '2026-10-20T01:00:00Z')
    with pytest.raises(ValueError, match='MIXED_GEOGRAPHY_GENERATION'):
        export.validate_bundle(incoming)


def test_last_good_geography_survives_config_correction(tmp_path, monkeypatch):
    from shutil import copytree
    from product.nz_election.pipeline import geography, refresh as hourly
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.publish import publish, git, DATA
    bundle, remote = tmp_path / 'data', tmp_path / 'remote.git'
    refresh(bundle, now='2026-10-18T01:00:00Z')
    daily_refresh(bundle, now='2026-10-18T01:00:00Z')
    before = {p.name: p.read_bytes() for p in bundle.iterdir() if p.stem in export.FAMILIES['geography']}
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    publish(bundle, remote)
    publish(bundle, remote, family='daily')
    current = tmp_path / 'current-product'
    copytree(geography.PRODUCT / 'config', current / 'config')
    registry_path = current / 'config/electorates.json'
    correspondence_path = current / 'config/electorate-correspondence.json'
    registry = json.loads(registry_path.read_text())
    correspondence = json.loads(correspondence_path.read_text())
    registry[0]['boundary_note'] = 'Reviewed correction to the boundary note.'
    next(r for r in correspondence['entries'] if r['new_id'] == registry[0]['stats_id'])['note'] = registry[0]['boundary_note']
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    correspondence_path.write_text(json.dumps(correspondence, ensure_ascii=False, indent=2) + '\n')
    monkeypatch.setattr(hourly, 'PRODUCT', current)
    monkeypatch.setattr(geography, 'PRODUCT', current)
    assert export.validate_bundle(bundle)['electorates']['data'][0]['boundary_note'] != registry[0]['boundary_note']
    refresh(bundle, now='2026-10-19T01:00:00Z')
    assert all((bundle / name).read_bytes() == raw for name, raw in before.items())
    assert publish(bundle, remote)['outcome'] == 'published'
    for name, raw in before.items():
        assert git(remote, 'show', 'data:' + str(DATA / name)).stdout.encode() == raw
    assert daily_refresh(bundle, now='2026-10-19T02:00:00Z')['state'] == 'fresh'
    envs = export.validate_bundle(bundle)
    assert envs['electorates']['data'] == registry
    for stem in export.FAMILIES['geography']:
        for path in (registry_path, correspondence_path):
            assert envs[stem]['input_hashes']['config/' + path.name] == export.digest(path.read_bytes())


def test_geography_snapshot_hash_mismatch_rejected(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(tmp_path / 'data', now='2026-10-18T01:00:00Z')
    root = tmp_path / 'data'
    registry = json.loads((root / 'electorates.json').read_text())
    registry['data'][0]['boundary_note'] = 'Unrecorded byte change'
    export.pair(root, 'electorates', registry)
    with pytest.raises(ValueError, match='DATA_HASH_MISMATCH'):
        export.validate_bundle(root)


def test_geography_producer_checks_current_registry(tmp_path, monkeypatch):
    from copy import deepcopy
    from product.nz_election.pipeline import daily_refresh as daily
    from product.nz_election.pipeline.refresh import config
    def corrected(name):
        result = deepcopy(config(name))
        if name == 'electorates':
            result[0]['boundary_note'] = 'Unreviewed change without matching correspondence'
        return result
    monkeypatch.setattr(daily, 'config', corrected)
    status = daily.daily_refresh(tmp_path / 'data', now='2026-10-18T01:00:00Z')
    assert status['state'] == 'unavailable'
    assert status['error_code'] == 'REGISTRY_MISMATCH'
    assert not (tmp_path / 'data/electorates.json').exists()


def test_geography_registry_bound_after_inventory_regeneration(tmp_path):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    daily_refresh(tmp_path / 'data', now='2026-10-18T01:00:00Z')
    root = tmp_path / 'data'
    envs = export.validate_bundle(root)
    expected = export.digest(export.canonical(envs['electorates']['data']).encode('utf-8'))
    assert all(envs[s]['input_hashes']['electorates.data'] == expected for s in export.FAMILIES['geography'])
    registry = envs['electorates']
    registry['data'][0]['boundary_note'] = 'Unrecorded note despite regenerated inventory'
    export.pair(root, 'electorates', registry)
    export.inventory(root, registry['run_url'], registry['code_sha'], '2026-10-18T02:00:00Z')
    with pytest.raises(ValueError, match='GEOGRAPHY_REGISTRY_HASH_MISMATCH'):
        export.validate_bundle(root)


@pytest.mark.parametrize('bad', ['', None, [], {}, 1.5, 10**100, 'ſ-invalid-hash'])
def test_geography_registry_binding_rejects_malformed_hash(tmp_path, bad):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    root = tmp_path / 'data'
    daily_refresh(root, now='2026-10-18T01:00:00Z')
    for stem in export.FAMILIES['geography']:
        env = json.loads((root / (stem + '.json')).read_text())
        env['input_hashes']['electorates.data'] = bad
        # Write raw siblings to probe validation without the producer's exact-number gate.
        (root / (stem + '.json')).write_text(export.canonical(env) + '\n')
        (root / (stem + '.csv')).write_bytes(export.csv_bytes(env))
    if isinstance(bad, float):
        with pytest.raises(ValueError, match='INEXACT_NUMBER'):
            export.validate_bundle(root)
    else:
        export.inventory(root, 'offline-verification', 'test', '2026-10-18T02:00:00Z')
        with pytest.raises(ValueError, match='GEOGRAPHY_REGISTRY_HASH_MISMATCH'):
            export.validate_bundle(root)


@pytest.mark.parametrize('change', ['add', 'drop', 'add-regressed'])
def test_baseline_source_set_advancement(tmp_path, change):
    from copy import deepcopy
    from shutil import copytree
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.pipeline.publish import publish, git, DATA
    original, incoming, remote = [tmp_path / s for s in ('original', 'incoming', 'remote.git')]
    daily_refresh(original, now='2026-10-18T01:00:00Z')
    copytree(original, incoming)
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    publish(original, remote, family='daily')
    env = json.loads((incoming / 'baseline-2023.json').read_text())
    env['generated_at'] = '2026-10-19T01:00:00Z'
    source = deepcopy(next(s for s in env['source'] if s['id'].endswith('place-1.csv')))
    source['id'] = 'ec-2023/candidate-votes-by-voting-place-21.csv'
    source['url'] = source['url'].replace('place-1.csv', 'place-21.csv')
    if change == 'add':
        source['id'] = 'ec-2023/candidate-votes-by-voting-place-99.csv'
        source['url'] = source['url'].replace('place-21.csv', 'place-99.csv')
        assert source['id'] not in {s['id'] for s in env['source']}
    if change == 'drop':
        env['source'] = [s for s in env['source'] if s['id'] != 'ec-2023-xml/electorates.xml']
    else:
        env['source'].append(source)
        if change == 'add-regressed':
            env['source'][0]['fetched_at'] = '2020-01-01T00:00:00Z'
    env['fetched_at'] = max(s['fetched_at'] for s in env['source'])
    export.pair(incoming, 'baseline-2023', env)
    export.inventory(incoming, 'offline-verification', 'test', '2026-10-19T01:00:00Z')
    publish(incoming, remote, family='daily')
    for suffix in ('.json', '.csv'):
        name = 'baseline-2023' + suffix
        actual = git(remote, 'show', 'data:' + str(DATA / name)).stdout
        assert actual == ((incoming if change == 'add' else original) / name).read_text()
