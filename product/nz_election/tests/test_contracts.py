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
    assert len(captures()) == 11


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
