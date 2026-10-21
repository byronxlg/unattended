"""Night packaging is closed-world and independent of the current registry."""
import json
from pathlib import Path
import pytest
from product.nz_election.pipeline import night, export
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.night_smoke import check


@pytest.fixture
def family(tmp_path):
    night.prepare(tmp_path, night.load(), 'offline-verification', 'test', '2026-10-21T00:00:00Z')
    return tmp_path


@pytest.mark.parametrize('damage', ['extra', 'missing', 'hash', 'traversal', 'duplicate', 'version', 'symlink'])
def test_night_index_closed_world(family, damage):
    path = family / 'night/index.json'
    env = json.loads(path.read_text())
    seq = env['data'][0]
    target = family / seq['snapshot_paths'][0]
    if damage == 'extra':
        (family / 'night/extra.json').write_text('{}')
    elif damage == 'missing':
        target.unlink()
    elif damage == 'hash':
        target.write_text('{}')
    elif damage == 'traversal':
        seq['snapshot_paths'][0] = '../secret.json'
    elif damage == 'duplicate':
        seq['snapshot_paths'].append(seq['snapshot_paths'][0])
    elif damage == 'version':
        seq['reference_version'] = 'wrong'
    else:
        target.unlink()
        target.symlink_to(path)
    path.write_text(json.dumps(env))
    with pytest.raises(ValueError, match='NIGHT_'):
        night.validate(family)


def test_final_snapshot_has_no_fake_timeline(family):
    index = json.loads((family / 'night/index.json').read_text())['data']
    for seq in index:
        if seq['mode'] == 'Final snapshot':
            assert len(seq['snapshot_paths']) == 1
            row = json.loads((family / seq['snapshot_paths'][0]).read_text())['data'][0]
            assert 'elapsed_seconds' not in row
            assert 'electorate_results' not in row


def test_illustrative_replay_label_persists(family):
    check(family)
    rows = [json.loads(p.read_text())['data'][0] for p in sorted((family / 'night/illustrative-2023').glob('*.json'))]
    assert [r['elapsed_seconds'] for r in rows] == [0, 300, 600]
    assert all(r['mode'] == night.LABEL and 'source_updated_local' not in r for r in rows)
    assert 'reported_house' not in rows[0] and 'statistics' not in rows[0]


def test_night_family_replacement_and_retention(tmp_path):
    root = tmp_path / 'data'
    daily_refresh(root, loaders={'night': night.load}, now='2026-10-21T00:00:00Z')
    before = {p.relative_to(root): p.read_bytes() for p in (root / 'night').rglob('*') if p.is_file()}
    def fail():
        raise ValueError('XML_COUNT')
    daily_refresh(root, loaders={'night': fail}, now='2026-10-21T00:01:00Z')
    assert all((root / p).read_bytes() == raw for p, raw in before.items())
    assert next(s for s in export.validate_bundle(root)['status']['data'] if s['dataset'] == 'night')['state'] == 'stale'
    def shorter():
        payloads, sources, hashes = night.load()
        payloads['night/index'] = [s for s in payloads['night/index'] if s['id'] != 'mediademo']
        payloads = {k: v for k, v in payloads.items() if not k.startswith('night/mediademo/') and k != 'night/references/mediademo'}
        return payloads, sources, hashes
    daily_refresh(root, loaders={'night': shorter}, now='2026-10-21T00:02:00Z')
    assert not (root / 'night/mediademo').exists()
    export.validate_bundle(root)


def test_night_publication_replaces_nested_files(tmp_path):
    from product.nz_election.pipeline.publish import publish, git, DATA
    root, remote = tmp_path / 'data', tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    daily_refresh(root, loaders={'night': night.load}, now='2026-10-21T00:00:00Z')
    publish(root, remote, family='daily')
    assert json.loads(git(remote, 'show', 'data:' + str(DATA / 'night/index.json')).stdout)['data']
    def shorter():
        payloads, sources, hashes = night.load()
        row = next(s for s in payloads['night/index'] if s['id'] == 'illustrative-2023')
        obsolete = row['snapshot_paths'].pop(1)
        del payloads[obsolete[:-5]]
        return payloads, sources, hashes
    daily_refresh(root, loaders={'night': shorter}, now='2026-10-21T00:02:00Z')
    publish(root, remote, family='daily')
    listing = git(remote, 'ls-tree', '-r', '--name-only', 'data').stdout
    assert 'night/illustrative-2023/step-1' not in listing
    assert 'night/illustrative-2023/step-2.json' in listing


def test_recorded_demo_and_deterministic_derivation():
    payloads, sources, hashes = night.load()
    assert (payloads, sources, hashes) == night.load()
    seq = next(s for s in payloads['night/index'] if s['id'] == 'mediademo')
    rows = [payloads[p[:-5]][0] for p in seq['snapshot_paths']]
    assert [r['valid_party_votes'] for r in rows] == [2189321, 2195788]
    assert all(r['mode'] == 'Recorded demo' and 'elapsed_seconds' not in r for r in rows)
    end = payloads['night/illustrative-2023/step-2'][0]
    for step, numerator in [(0, 1), (1, 5)]:
        row = payloads['night/illustrative-2023/step-' + str(step)][0]
        assert row['party_results'] == {p: {'votes': r['votes'] * numerator // 10} for p, r in end['party_results'].items()}


def test_prepare_rejects_paths_before_writing(tmp_path):
    payloads, sources, hashes = night.load()
    payloads['../outside'] = []
    with pytest.raises(ValueError, match='^NIGHT_PATH$'):
        night.prepare(tmp_path, (payloads, sources, hashes), 'offline-verification', 'test', '2026-10-21T00:00:00Z')
    assert not list(tmp_path.iterdir())
