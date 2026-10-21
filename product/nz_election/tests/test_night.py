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


@pytest.mark.parametrize('sequence_id', ['mediademo', 'illustrative-2023'])
def test_prepare_rejects_relabelled_simulation(tmp_path, sequence_id):
    loaded = night.load()
    payloads = loaded[0]
    seq = next(s for s in payloads['night/index'] if s['id'] == sequence_id)
    if sequence_id == 'mediademo':
        removed = seq['snapshot_paths'].pop()
        del payloads[removed[:-5]]
    seq['mode'] = 'Final snapshot'
    for path in seq['snapshot_paths']:
        payloads[path[:-5]][0]['mode'] = 'Final snapshot'
    with pytest.raises(ValueError, match='^NIGHT_MODE$'):
        night.prepare(tmp_path, loaded, 'offline-verification', 'test', '2026-10-21T00:00:00Z')


def test_validate_rejects_relabelled_demo_even_with_matching_hashes(family):
    index_path = family / 'night/index.json'
    index = json.loads(index_path.read_text())
    seq = next(s for s in index['data'] if s['id'] == 'mediademo')
    removed = seq['snapshot_paths'].pop()
    for name in (removed, removed[:-5] + '.csv'):
        (family / name).unlink()
        del seq['files'][name]
    seq['mode'] = 'Final snapshot'
    path = family / seq['snapshot_paths'][0]
    env = json.loads(path.read_text())
    env['data'][0]['mode'] = 'Final snapshot'
    path.write_text(export.canonical(env) + '\n')
    path.with_suffix('.csv').write_bytes(export.csv_bytes(env))
    for name in (seq['snapshot_paths'][0], seq['snapshot_paths'][0][:-5] + '.csv'):
        seq['files'][name] = export.digest((family / name).read_bytes())
    index_path.write_text(export.canonical(index) + '\n')
    index_path.with_suffix('.csv').write_bytes(export.csv_bytes(index))
    with pytest.raises(ValueError, match='^NIGHT_MODE$'):
        night.validate(family)


@pytest.mark.parametrize('supplied', [False, True])
def test_verify_night_fixture_or_supplied_artifact(tmp_path, monkeypatch, capsys, supplied):
    from product.nz_election.pipeline import verify
    args = ['verify', 'night']
    tmp_path = tmp_path / 'data'
    if supplied:
        daily_refresh(tmp_path, loaders={'night': night.load})
        args += ['--data', str(tmp_path)]
        def no_fixture_build(*args, **kwargs):
            pytest.fail('supplied artifact must not be replaced by a fixture build')
        monkeypatch.setattr('product.nz_election.pipeline.daily_refresh.daily_refresh', no_fixture_build)
    monkeypatch.setattr('sys.argv', args)
    from product.nz_election.tests import night_smoke
    checked = []
    original = night_smoke.check
    def smoke(root):
        checked.append(root)
        return original(root)
    monkeypatch.setattr(night_smoke, 'check', smoke)
    verify.main()
    assert len(checked) == 1
    if supplied:
        assert checked == [tmp_path]
    assert capsys.readouterr().out == 'PASS night\n'


def test_verify_night_missing_supplied_family(tmp_path, monkeypatch, capsys):
    from product.nz_election.pipeline import verify
    from product.nz_election.pipeline.refresh import refresh
    tmp_path = tmp_path / 'data'
    refresh(tmp_path)
    monkeypatch.setattr('sys.argv', ['verify', 'night', '--data', str(tmp_path)])
    with pytest.raises(ValueError, match='^MISSING_NIGHT_FAMILY$'):
        verify.main()
    assert 'PASS night' not in capsys.readouterr().out


@pytest.mark.parametrize('mode', ['', None, [], {}, True, 1.5, 10**100, 'Ｒecorded demo', night.LABEL])
def test_demo_mode_rejects_malformed_or_incompatible_labels(mode):
    payloads, _, _ = night.load()
    seq = next(s for s in payloads['night/index'] if s['id'] == 'mediademo')
    row = payloads[seq['snapshot_paths'][0][:-5]][0]
    row['mode'] = mode
    with pytest.raises(ValueError, match='^NIGHT_MODE$'):
        night.validate_row(row, seq['snapshot_paths'][0][:-5])


def write_unchecked_night(root, loaded):
    """Serialize self-consistent bytes without invoking the validator under test."""
    from copy import deepcopy
    payloads, sources, hashes = deepcopy(loaded)
    for stem in sorted(payloads, key=lambda s: s == 'night/index'):
        if stem == 'night/index':
            for seq in payloads[stem]:
                seq['files'] = {name: export.digest((root / name).read_bytes())
                                for path in [seq['reference_path']] + seq['snapshot_paths']
                                for name in (path, path[:-5] + '.csv')}
        env = export.envelope(payloads[stem], sources, 'offline-verification', 'test',
                              inputs=hashes, method='night-v1', generated='2026-10-21T00:00:00Z')
        path = root / (stem + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(export.canonical(env) + '\n')
        path.with_suffix('.csv').write_bytes(export.csv_bytes(env))


@pytest.mark.parametrize('entrypoint', ['prepare', 'validate'])
def test_stripped_replay_cannot_impersonate_archive(tmp_path, entrypoint):
    payloads, sources, hashes = night.load()
    seq = next(s for s in payloads['night/index'] if s['id'] == 'illustrative-2023')
    final = next(s for s in payloads['night/index'] if s['id'] == '2023')
    row = payloads[seq['snapshot_paths'][0][:-5]][0]
    assert row['valid_party_votes'] == 285114
    del row['derivation']
    del row['elapsed_seconds']
    row['source_updated_local'] = payloads[final['snapshot_paths'][0][:-5]][0]['source_updated_local']
    row['mode'] = seq['mode'] = 'Final snapshot'
    seq['snapshot_paths'] = seq['snapshot_paths'][:1]
    payloads = {'night/index': [seq], seq['reference_path'][:-5]: payloads[seq['reference_path'][:-5]],
                seq['snapshot_paths'][0][:-5]: [row]}
    loaded = payloads, sources, hashes
    if entrypoint == 'validate':
        write_unchecked_night(tmp_path, loaded)
    with pytest.raises(ValueError, match='^NIGHT_CAPTURE_MISMATCH$'):
        if entrypoint == 'prepare':
            night.prepare(tmp_path, loaded, 'offline-verification', 'test', '2026-10-21T00:00:00Z')
        else:
            night.validate(tmp_path)


@pytest.mark.parametrize('bad_hash', ['', None, {}, [], True, 1.5, 10**100, '異', '0' * 64])
def test_final_capture_hash_is_verified(tmp_path, bad_hash):
    loaded = night.load()
    loaded[2]['ec-2023-xml/election.xml'] = bad_hash
    write_unchecked_night(tmp_path, loaded)
    with pytest.raises(ValueError, match='^(NIGHT_CAPTURE_MISMATCH|INEXACT_NUMBER)$'):
        night.validate(tmp_path)


def test_verify_empty_directory_reports_named_failure(tmp_path):
    import subprocess
    import sys
    result = subprocess.run([sys.executable, '-m', 'product.nz_election.pipeline.verify',
                             'night', '--data', str(tmp_path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert result.stdout + result.stderr == 'FAIL night: MISSING_NIGHT_FAMILY\n'
