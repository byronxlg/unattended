"""Exercise the Actions script with disposable git remotes, never network."""
import json
from pathlib import Path

import pytest
from product.nz_election.pipeline import export, fixtures, night_live, publish, result_import
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.test_result_states import capture
from product.nz_election.tests.test_workflows import workflow

NOW = '2026-11-28T00:00:00Z'


def register(root, raw, name='reviewed'):
    path = 'result-import/' + name + '.json'
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(raw))
    entry = dict(path=path, sha256=export.digest(target.read_bytes()), capture_kind='human-reviewed-real', reviewer='Offline test')
    (root / 'manifest.json').write_text(json.dumps(dict(entries=[entry])))
    return path


@pytest.fixture
def repo(tmp_path):
    remote = tmp_path / 'remote.git'
    remote.mkdir()
    publish.git(remote, 'init', '--bare', '-q')
    data = tmp_path / 'data'
    raw = capture('preliminary')
    daily_refresh(data, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'])
    sha = publish.publish(data, remote, family='night', now=lambda: NOW)['sha']
    root = tmp_path / 'captures'
    path = register(root, raw)
    return remote, sha, root, path


def execute(repo, **kwargs):
    remote, sha, root, path = repo
    return result_import.run(kwargs.pop('state', 'settled'), path, kwargs.pop('data_sha', sha),
                             repository=remote, root=root, now=kwargs.pop('now', lambda: NOW),
                             run_url='offline-verification', **kwargs)


def test_rehearsal_imports_pin_and_rollback(repo, tmp_path):
    remote, original, root, path = repo
    deployments = []
    settled = execute(repo, deploy=deployments.append)
    assert settled['checks'] == ['PASS night', 'PASS waterfall']
    assert settled['capture_sha256'] == export.digest((root / path).read_bytes())
    register(root, capture('official'))
    official = execute(repo, state='official', data_sha=settled['published_data_sha'])
    assert official['checks'] == ['PASS night', 'PASS waterfall']
    checkout = tmp_path / 'pinned'
    checkout.mkdir()
    result_import.pin(remote, original, checkout)
    assert publish.git(checkout, 'rev-parse', 'HEAD').stdout.strip() == original
    assert 'result_state' not in export.validate_bundle(checkout / publish.DATA)['night/live/current']['data'][0]
    restored = execute(repo, rollback=True)
    assert restored['published_data_sha'] != official['published_data_sha']
    for suffix in ('json', 'csv'):
        name = str(publish.DATA / ('night/live/current.' + suffix))
        assert publish.git(remote, 'show', 'data:' + name).stdout == publish.git(remote, 'show', original + ':' + name).stdout
    assert deployments == [settled['published_data_sha']]


@pytest.mark.parametrize('bad', [None, '', [], 1, 1.5, 10**100, 'x\x00', 'a'*40, 'A'*40])
def test_invalid_sha(repo, tmp_path, bad):
    checkout = tmp_path / 'pin'
    checkout.mkdir()
    with pytest.raises(ValueError, match='^NIGHT_DATA_SHA$'):
        result_import.pin(repo[0], bad, checkout)


@pytest.mark.parametrize('fault,code', [('missing', 'MISSING_CAPTURE'), ('synthetic', 'NIGHT_CAPTURE_NOT_REAL'),
    ('freeze', 'PUBLICATION_FROZEN'), ('verify', 'NIGHT_VERIFY_FAILED'), ('hash', 'CAPTURE_HASH_MISMATCH')])
def test_refusals_leave_remote_unchanged(repo, fault, code):
    remote, sha, root, path = repo
    kwargs = {}
    if fault == 'missing':
        (root / 'manifest.json').write_text('{"entries": []}')
    elif fault == 'synthetic':
        doc = json.loads((root / 'manifest.json').read_text())
        doc['entries'][0]['notes'] = 'Synthetic fixture'
        (root / 'manifest.json').write_text(json.dumps(doc))
    elif fault == 'freeze':
        kwargs['now'] = lambda: '2026-11-07T00:00:00Z'
    elif fault == 'verify':
        kwargs['verifier'] = lambda data: ['FAIL night']
    else:
        (root / path).write_text('{}')
    with pytest.raises(ValueError, match=code):
        execute(repo, **kwargs)
    assert publish.git(remote, 'rev-parse', 'data').stdout.strip() == sha


@pytest.mark.parametrize('fault,code', [('source', 'NIGHT_STATE'), ('date', 'NIGHT_STATE'), ('reference', 'NIGHT_LIVE')])
def test_official_refusals(repo, fault, code):
    settled = execute(repo)
    raw = capture('official')
    if fault == 'source':
        raw['acquisition_source'] = {'kind': 'official', 'url': 'https://invalid.example/'}
    elif fault == 'date':
        raw['retrieved_at'] = '2026-11-25T10:35:00Z'
    else:
        raw['raw']['parties.xml'] = raw['raw']['parties.xml'].replace('<short_name>', '<short_name>Changed ', 1)
    register(repo[2], raw)
    with pytest.raises(ValueError, match=code):
        execute(repo, state='official', data_sha=settled['published_data_sha'])
    assert publish.git(repo[0], 'rev-parse', 'data').stdout.strip() == settled['published_data_sha']


def test_committed_synthetic_rejected():
    for name in ('2026-11-07-preliminary-final', '2026-11-27-official'):
        with pytest.raises(ValueError, match='NIGHT_CAPTURE_NOT_REAL'):
            result_import.capture_bytes('result-states/' + name + '.json', fixtures.ROOT)


def test_workflow_contract():
    doc = workflow('nz-election-result-import.yml')
    assert set(doc[True]) == {'workflow_dispatch'}
    assert set(doc[True]['workflow_dispatch']['inputs']) == {'state', 'capture', 'data_sha', 'rollback'}
    assert doc['concurrency'] == {'group': 'nz-election-data-publication', 'cancel-in-progress': False}
    job = doc['jobs']['import']
    assert job['if'] == "github.ref == 'refs/heads/main'"
    assert job['steps'][0]['with'] == {'ref': '${{ github.sha }}', 'persist-credentials': False}
    assert 'result_import.py' in job['steps'][-1]['run']
    source = Path(result_import.__file__).read_text()
    assert "family='night'" in source and "'pages.yml', '--ref', 'main'" in source


def test_rollback_lease_conflict(repo):
    result = execute(repo)
    with pytest.raises(ValueError, match='NIGHT_ROLLBACK_CONFLICT'):
        with __import__('tempfile').TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            result_import.pin(repo[0], repo[1], checkout)
            publish.publish(checkout / publish.DATA, repo[0], family='night', night_rollback=repo[1], now=lambda: NOW)
    assert publish.git(repo[0], 'rev-parse', 'data').stdout.strip() == result['published_data_sha']


@pytest.mark.parametrize('returncode,stdout', [(1, 'PASS night\n'), (0, 'SKIP night\n')])
def test_verify_requires_exit_zero_and_pass(tmp_path, monkeypatch, returncode, stdout):
    import subprocess
    monkeypatch.setattr(result_import.subprocess, 'run', lambda *a, **kw: subprocess.CompletedProcess(a, returncode, stdout, ''))
    with pytest.raises(ValueError, match='^NIGHT_VERIFY_FAILED$'):
        result_import.verify(tmp_path)


def test_unreachable_existing_commit(repo, tmp_path):
    remote, sha, _, _ = repo
    tree = publish.git(remote, 'rev-parse', sha + '^{tree}').stdout.strip()
    publish.git(remote, 'config', 'user.name', 'Test')
    publish.git(remote, 'config', 'user.email', 'test@example.com')
    other = publish.git(remote, 'commit-tree', tree, '-m', 'Unrelated history').stdout.strip()
    publish.git(remote, 'update-ref', 'refs/heads/other', other)
    checkout = tmp_path / 'unreachable'
    checkout.mkdir()
    with pytest.raises(ValueError, match='^NIGHT_DATA_SHA$'):
        result_import.pin(remote, other, checkout)


def test_relocated_known_synthetic_is_rejected(tmp_path):
    path = register(tmp_path, capture('official'))
    manifest = json.loads((tmp_path / 'manifest.json').read_text())
    manifest['entries'].append(dict(manifest['entries'][0], path='result-states/original.json', notes='Synthetic capture'))
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='^NIGHT_CAPTURE_NOT_REAL$'):
        result_import.capture_bytes(path, tmp_path)


@pytest.mark.parametrize('bad', [None, '', [], 1, 1.5, 10**100, 'capture\x00'])
def test_malformed_capture_contract(tmp_path, bad):
    path = register(tmp_path, bad)
    with pytest.raises(ValueError, match='^NIGHT_CAPTURE_NOT_REAL$'):
        result_import.capture_bytes(path, tmp_path)
    with pytest.raises(ValueError, match='^MISSING_CAPTURE'):
        result_import.capture_bytes(bad, tmp_path)


def test_cli_job_clock_and_producing_url(monkeypatch):
    monkeypatch.setenv('GITHUB_TOKEN', 'offline-test-token')
    monkeypatch.setenv('GITHUB_SERVER_URL', 'https://github.com')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'test/repo')
    monkeypatch.setenv('GITHUB_RUN_ID', '123')
    monkeypatch.setattr('sys.argv', ['result_import.py', '--state', 'settled', '--data-sha', 'a'*40])
    called = []
    def run(*args, **kwargs):
        assert export.timestamp(kwargs['now']())
        assert kwargs['run_url'] == 'https://github.com/test/repo/actions/runs/123'
        called.append(args)
    monkeypatch.setattr(result_import, 'run', run)
    # Keep authentication configuration scoped to this test process.
    for key in ('GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0'):
        monkeypatch.setenv(key, '')
    result_import.main()
    assert len(called) == 1


@pytest.mark.parametrize('race', [False, True], ids=['newer-head', 'lease-retry'])
def test_stale_pinned_capture_cannot_report_or_deploy(repo, tmp_path, monkeypatch, race):
    remote, pinned, _, _ = repo
    raw = capture('preliminary')
    raw['retrieved_at'] = '2026-11-07T10:36:00Z'
    newer = tmp_path / 'newer'
    daily_refresh(newer, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'])
    original_publish = publish.publish
    heads = []
    def advance():
        heads.append(original_publish(newer, remote, family='night', now=lambda: NOW)['sha'])
    if race:
        def racing_publish(*args, **kwargs):
            return original_publish(*args, **kwargs, before_push=lambda attempt: advance() if attempt == 0 else None)
        monkeypatch.setattr(publish, 'publish', racing_publish)
    else:
        advance()
    summary = tmp_path / 'summary'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    deployments = []
    with pytest.raises(ValueError, match='^NIGHT_IMPORT_CONFLICT$'):
        execute(repo, deploy=deployments.append)
    assert not deployments
    assert not summary.exists()
    assert len(heads) == 1 and heads[0] != pinned
    assert publish.git(remote, 'rev-parse', 'data').stdout.strip() == heads[0]
    current = json.loads(publish.git(remote, 'show', 'data:' + str(publish.DATA / 'night/live/current.json')).stdout)
    assert current['data'][0]['retrieved_at'] == raw['retrieved_at']
    assert 'result_state' not in current['data'][0]


@pytest.fixture
def preparation_bundle(tmp_path):
    # Disposable simulated acquisition, never registered or published outside this test.
    raw = capture('preliminary')
    raw['raw'] = {k: v.replace('23:30:00', '23:31:00') for k, v in raw['raw'].items()}
    data = tmp_path / 'preparation-data'
    daily_refresh(data, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'])
    return data, raw


def test_prepare_cli_round_trip(preparation_bundle, tmp_path):
    import subprocess
    from product.nz_election.pipeline import settlement_capture
    data, original = preparation_bundle
    remote = tmp_path / 'prepared.git'
    remote.mkdir()
    publish.git(remote, 'init', '--bare', '-q')
    pinned_sha = publish.publish(data, remote, family='night', now=lambda: NOW)['sha']
    pinned = tmp_path / 'pinned-preparation'
    pinned.mkdir()
    result_import.pin(remote, pinned_sha, pinned)
    data = pinned / publish.DATA
    baseline = export.validate_bundle(data)['night/live/current']
    before = {p.relative_to(data): p.read_bytes() for p in data.rglob('*') if p.is_file()}
    root = tmp_path / 'review'
    (root / 'result-import').mkdir(parents=True)
    out = root / 'result-import/prepared.json'
    result = subprocess.run(['python3', '-B', settlement_capture.__file__, '--data', str(data), '--out', str(out)],
                            capture_output=True, text=True, check=True)
    metadata = json.loads(result.stdout)
    assert metadata == dict(path=str(out), sha256=export.digest(out.read_bytes()), bytes=out.stat().st_size,
                            retrieved_at=original['retrieved_at'], source=original['acquisition_source'])
    assert json.loads(out.read_bytes()) == {k: original[k] for k in ('raw', 'retrieved_at', 'acquisition_source')}
    second = tmp_path / 'second.json'
    settlement_capture.prepare(data, second)
    assert second.read_bytes() == out.read_bytes()
    assert before == {p.relative_to(data): p.read_bytes() for p in data.rglob('*') if p.is_file()}
    entry = dict(metadata, path='result-import/prepared.json', capture_kind='human-reviewed-real', reviewer='Offline test')
    (root / 'manifest.json').write_text(json.dumps(dict(entries=[entry])))
    report = result_import.run('settled', entry['path'], pinned_sha, repository=remote, now=lambda: NOW,
                               root=root, run_url='offline-verification')
    final = tmp_path / 'final-preparation'
    final.mkdir()
    result_import.pin(remote, report['published_data_sha'], final)
    settled = export.validate_bundle(final / publish.DATA)['night/live/current']
    assert settled['data'][0]['preliminary_package'] == baseline
    plain = {k: v for k, v in settled['data'][0].items() if k not in {'preliminary_package', 'result_state'}}
    plain['mode'] = night_live.MODE
    assert plain == baseline['data'][0]
    assert settled['source'] == baseline['source']
    assert settled['input_hashes'] == baseline['input_hashes']
    for check in ('night', 'waterfall'):
        verified = subprocess.run(['python3', '-B', 'product/nz_election/pipeline/verify.py', check,
                                   '--data', str(final / publish.DATA)], capture_output=True, text=True, check=True)
        assert 'PASS ' + check in verified.stdout.splitlines()
        print(verified.stdout, end='')


@pytest.mark.parametrize('label', ['synthetic', 'Recorded demo', 'replay', 'rehearsal'])
def test_prepare_rejects_labels(preparation_bundle, tmp_path, label):
    from product.nz_election.pipeline import settlement_capture
    data, raw = preparation_bundle
    daily_refresh(data, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'],
                  run_url='https://example.test/' + label.replace(' ', '-'))
    out = tmp_path / 'refused.json'
    with pytest.raises(ValueError, match='NIGHT_CAPTURE_NOT_REAL'):
        settlement_capture.prepare(data, out)
    assert not out.exists()


def test_prepare_rejects_known_synthetic(repo, tmp_path):
    from product.nz_election.pipeline import settlement_capture
    pinned = tmp_path / 'synthetic-pin'
    pinned.mkdir()
    result_import.pin(repo[0], repo[1], pinned)
    out = tmp_path / 'refused.json'
    with pytest.raises(ValueError, match='NIGHT_CAPTURE_NOT_REAL'):
        settlement_capture.prepare(pinned / publish.DATA, out)
    assert not out.exists()


@pytest.mark.parametrize('fault', ['mismatch', 'partial', 'absent', 'settled', 'demo'])
def test_prepare_rejects_bad_snapshot(preparation_bundle, tmp_path, monkeypatch, fault):
    from product.nz_election.pipeline import settlement_capture
    data, _ = preparation_bundle
    envs = export.validate_bundle(data)
    row = envs['night/live/current']['data'][0]
    if fault == 'mismatch':
        row['valid_party_votes'] += 1
    elif fault == 'partial':
        del row['raw_xml']['e71/e71.xml']
    elif fault == 'absent':
        del envs['night/live/current']
    elif fault == 'settled':
        row['result_state'] = 'settled'
    else:
        row['acquisition_source']['kind'] = 'demo'
    # Exercise extraction's own guards independently of bundle validation.
    monkeypatch.setattr(export, 'validate_bundle', lambda path: envs)
    out = tmp_path / 'refused.json'
    with pytest.raises(ValueError):
        settlement_capture.prepare(data, out)
    assert not out.exists()


def test_prepared_capture_mismatched_import_rejected(preparation_bundle, tmp_path):
    from product.nz_election.pipeline import settlement_capture
    data, _ = preparation_bundle
    remote = tmp_path / 'mismatch.git'
    remote.mkdir()
    publish.git(remote, 'init', '--bare', '-q')
    sha = publish.publish(data, remote, family='night', now=lambda: NOW)['sha']
    out = tmp_path / 'draft.json'
    settlement_capture.prepare(data, out)
    captured = json.loads(out.read_bytes())
    captured['retrieved_at'] = '2026-11-07T10:36:00Z'
    root = tmp_path / 'mismatch-captures'
    path = register(root, captured)
    with pytest.raises(ValueError, match='^NIGHT_BASELINE$'):
        execute((remote, sha, root, path))
    assert publish.git(remote, 'rev-parse', 'data').stdout.strip() == sha


def test_prepare_output_is_exclusive(preparation_bundle, tmp_path):
    from product.nz_election.pipeline import settlement_capture
    data, _ = preparation_bundle
    out = tmp_path / 'existing.json'
    out.write_bytes(b'keep')
    with pytest.raises(FileExistsError):
        settlement_capture.prepare(data, out)
    link = tmp_path / 'link.json'
    link.symlink_to(out)
    with pytest.raises(FileExistsError):
        settlement_capture.prepare(data, link)
    assert out.read_bytes() == b'keep'
    with pytest.raises(ValueError, match='UNSAFE_CAPTURE_PATH'):
        settlement_capture.prepare(data, data / 'capture.json')
    assert not (data / 'capture.json').exists()


def test_prepare_validates_manifest_before_extraction(preparation_bundle, tmp_path):
    from product.nz_election.pipeline import settlement_capture
    data, _ = preparation_bundle
    (data / 'night/live/current.json').write_text('{}')
    out = tmp_path / 'refused.json'
    with pytest.raises(ValueError):
        settlement_capture.prepare(data, out)
    assert not out.exists()
