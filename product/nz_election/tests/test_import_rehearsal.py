"""Run the Actions entry point against an isolated target without network access."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from product.nz_election.pipeline import export, publish, result_import
from product.nz_election.tests.test_workflows import workflow


def test_import_rehearsal_entry_point(tmp_path):
    remote = tmp_path / 'target.git'
    remote.mkdir()
    publish.git(remote, 'init', '--bare', '-q')
    out = tmp_path / 'artifact'
    result = subprocess.run([sys.executable, 'product/nz_election/pipeline/import_rehearsal.py',
                             '--remote', str(remote), '--out', str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((out / 'report.json').read_text())
    assert report['label'].startswith('Synthetic')
    assert publish.git(remote, 'for-each-ref', '--format=%(refname)').stdout.splitlines() == ['refs/heads/rehearsal-data']
    original = report['original_data_sha']
    for step, record, state in zip(('settled', 'official', 'rollback'), report['steps'], ('settled', 'official', 'preliminary'), strict=True):
        sha = record['published_data_sha']
        assert record['pass_line'] == f'PASS {step} served_sha={sha} result_state={state}'
        assert record['pass_line'] in result.stdout.splitlines()
        assert record['checks'] == ['PASS night', 'PASS waterfall']
        served = out / step / 'served'
        manifest = json.loads((served / 'build-manifest.json').read_text())
        assert manifest['data']['data_sha'] == sha
        assert manifest['code_sha'] == report['code_sha']
        envs = export.validate_bundle(served / 'data')
        assert envs['night/live/current']['data'][0].get('result_state', 'preliminary') == state
        for path in (served / 'data/night').rglob('*'):
            if path.is_file():
                name = str(publish.DATA / path.relative_to(served / 'data'))
                assert path.read_text() == publish.git(remote, 'show', sha + ':' + name).stdout
                if step == 'rollback':
                    assert path.read_text() == publish.git(remote, 'show', original + ':' + name).stdout
    assert 'PASS isolated target: data ref absent; no Pages dispatch' in result.stdout
    for entry in json.loads((out / 'captures/manifest.json').read_text())['entries']:
        assert entry['capture_kind'] == 'synthetic'
        with pytest.raises(ValueError, match='^NIGHT_CAPTURE_NOT_REAL$'):
            result_import.capture_bytes(entry['path'], out / 'captures')


def test_import_job_has_only_checkout_network_access():
    doc = workflow('nz-election-night-rehearsal.yml')
    assert set(doc[True]) == {'workflow_dispatch'}
    assert doc['jobs']['rehearse']['if'] == 'inputs.import_only != true'
    job = doc['jobs']['import-rehearsal']
    assert job['if'] == 'inputs.import_only == true'
    assert job['permissions'] == {'contents': 'read'}
    assert job['steps'] == [
        {'uses': 'actions/checkout@v4', 'with': {'ref': '${{ github.sha }}', 'persist-credentials': False}},
        {'name': 'Rehearse synthetic settlement, official import and rollback locally',
         'run': 'python3 product/nz_election/pipeline/import_rehearsal.py'},
    ]


def test_rehearsal_refuses_existing_target(tmp_path):
    remote = tmp_path / 'target.git'
    remote.mkdir()
    publish.git(remote, 'init', '--bare', '-q')
    from product.nz_election.pipeline.import_rehearsal import rehearse
    # An existing ref is sufficient to refuse before preparing or publishing any data.
    publish.git(remote, 'symbolic-ref', 'refs/heads/data', 'refs/heads/main')
    # Symbolic unborn refs are not enumerated, so use an actual commit from this checkout.
    publish.git(remote, 'fetch', str(Path.cwd()), 'HEAD:refs/heads/main')
    before = publish.git(remote, 'show-ref').stdout
    with pytest.raises(ValueError, match='^EMPTY_REHEARSAL_REPOSITORY_REQUIRED$'):
        rehearse(tmp_path / 'artifact', remote)
    assert publish.git(remote, 'show-ref').stdout == before
    assert not (tmp_path / 'artifact').exists()
