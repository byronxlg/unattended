"""Workflow contracts and real git publication, entirely offline."""
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from product.nz_election.pipeline import export
from product.nz_election.pipeline.publish import DATA, git, publish
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.tests.test_pipeline import fail, make_bundle, repository

ROOT = Path(__file__).resolve().parents[3]


def workflow(name):
    return yaml.safe_load((ROOT / '.github/workflows' / name).read_text())


def test_hourly_contract():
    doc = workflow('nz-election-hourly.yml')
    triggers = doc[True]
    assert doc['name'] == 'NZ election hourly'
    assert triggers == {'schedule': [{'cron': '17 * * * *'}], 'workflow_dispatch': None}
    assert doc['permissions'] == {}
    refresh_job, publication = doc['jobs']['refresh'], doc['jobs']['publish']
    assert refresh_job['permissions'] == {'contents': 'read'}
    assert refresh_job['if'] == "github.ref == 'refs/heads/main'"
    assert publication['permissions'] == {'contents': 'write'}
    assert publication['needs'] == 'refresh'
    assert publication['if'] == "needs.refresh.outputs.validated == 'true'"
    assert publication['concurrency'] == {'group': 'nz-election-data-publication', 'cancel-in-progress': False}
    assert refresh_job['outputs']['validated'] == '${{ steps.refresh.outputs.validated }}'
    steps = refresh_job['steps']
    refresh_step = next(s for s in steps if s.get('id') == 'refresh')
    assert refresh_step['continue-on-error'] is True
    assert '--fixtures' not in refresh_step['run']
    upload = next(s for s in steps if s.get('uses') == 'actions/upload-artifact@v4')
    assert upload['if'] == "steps.refresh.outputs.validated == 'true'"
    assert upload['with']['if-no-files-found'] == 'error'
    assert upload['with']['path'] == '_nz-election-data/product/nz_election/data/'
    download = next(s for s in publication['steps'] if s.get('uses') == 'actions/download-artifact@v4')
    assert download['with']['name'] == upload['with']['name']
    assert publication['steps'][-1]['run'] == 'uv run product/nz_election/pipeline/publish.py --bundle _nz-election-bundle'
    assert publication['steps'][-1]['env'] == {'GITHUB_TOKEN': '${{ github.token }}'}
    for job in (refresh_job, publication):
        assert job['steps'][0]['with']['ref'] == '${{ github.sha }}'
        assert job['steps'][0]['with']['persist-credentials'] is False
    snapshot = next(s for s in steps if s.get('with', {}).get('path') == '_nz-election-data')
    assert snapshot['with']['ref'] == '${{ steps.data.outputs.sha }}'
    assert snapshot['with']['persist-credentials'] is False
    resolver = next(s for s in steps if s.get('id') == 'data')['run']
    assert 'set -euo pipefail' in resolver and 'git ls-remote origin refs/heads/data' in resolver
    assert not any('secrets.' in str(s) for s in steps + publication['steps'])


def test_orphan_bootstrap(tmp_path):
    remote = tmp_path / 'empty.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    bundle = make_bundle(tmp_path)
    result = publish(bundle, remote)
    assert result['outcome'] == 'published' and result['attempts'] == 1
    assert git(remote, 'rev-list', '--parents', '-n', '1', 'data').stdout.split() == [result['sha']]
    names = git(remote, 'ls-tree', '-r', '--name-only', 'data').stdout.splitlines()
    assert set(names) == {str(DATA / n) for n in {'polls.json', 'polls.csv', 'averages.json', 'averages.csv', 'seats.json', 'seats.csv', 'status.json', 'status.csv', 'manifest.json', 'manifest.csv', 'LICENCES.md'}}
    assert publish(bundle, remote)['outcome'] == 'unchanged'
    # Bootstrap conflicts must rebase the owned bundle onto the winning orphan commit.
    racing = tmp_path / 'racing.git'
    racing.mkdir()
    git(racing, 'init', '--bare', '-q')
    newer = make_bundle(tmp_path, 2)
    result = publish(newer, racing, before_push=lambda attempt: publish(bundle, racing) if attempt == 0 else None)
    assert result['attempts'] == 2
    assert git(racing, 'rev-list', '--count', 'data').stdout.strip() == '2'
    import shutil
    for index, name in enumerate(('rogue.json', '../escape.json', 'nested/status.json')):
        invalid = tmp_path / ('bad-' + str(index))
        shutil.copytree(bundle, invalid)
        manifest = json.loads((invalid / 'manifest.json').read_text())
        manifest['data'][0]['path'] = name
        export.pair(invalid, 'manifest', manifest)
        with pytest.raises(ValueError, match='INVENTORY'):
            publish(invalid, remote)
    invalid = tmp_path / 'symlink'
    shutil.copytree(bundle, invalid)
    (invalid / 'polls.json').unlink()
    (invalid / 'polls.json').symlink_to(bundle / 'polls.json')
    with pytest.raises(ValueError, match='UNSAFE'):
        publish(invalid, remote)
    before = git(remote, 'rev-parse', 'data').stdout
    (bundle / 'unexpected').mkdir()
    with pytest.raises(ValueError):
        publish(bundle, remote)
    assert git(remote, 'rev-parse', 'data').stdout == before


def test_pages_triggers_and_pinned_checkouts(tmp_path):
    doc = workflow('pages.yml')
    triggers = doc[True]
    assert triggers['push'] == {'branches': ['main']}
    assert triggers['workflow_run'] == {'workflows': ['NZ election hourly', 'NZ election daily'], 'types': ['completed'], 'branches': ['main']}
    assert set(triggers['workflow_dispatch']['inputs']) == {'code_sha', 'data_sha'}
    assert all(v['required'] is False for v in triggers['workflow_dispatch']['inputs'].values())
    assert doc['concurrency'] == {'group': 'pages', 'cancel-in-progress': False}
    build = doc['jobs']['build']
    assert "github.event.workflow_run.head_branch == 'main'" in build['if']
    assert 'github.event.workflow_run.head_repository.full_name == github.repository' in build['if']
    assert 'conclusion' not in build['if']
    assert build['permissions'] == {'contents': 'read'}
    assert doc['jobs']['deploy']['permissions'] == {'pages': 'write', 'id-token': 'write'}
    steps = build['steps']
    assert steps[0]['with']['fetch-depth'] == 0
    assert steps[0]['with']['ref'] == '${{ github.sha }}'
    validate = next(s for s in steps if s.get('name') == 'Validate rollback inputs')
    rollback = next(s for s in steps if s.get('with', {}).get('ref') == '${{ inputs.code_sha }}')
    assert steps.index(validate) < steps.index(rollback)
    for value in ('', 'a' * 40, 'A' * 40, '0' * 39, 'a' * 41, '$(exit 0)', 'a' * 40 + '\n', 'null'):
        result = subprocess.run(['bash', '-c', validate['run']], env={'CODE_SHA': value, 'DATA_SHA': ''}, capture_output=True)
        assert (result.returncode == 0) == (value in ('', 'a' * 40))
    data = next(s for s in steps if s.get('with', {}).get('path') == '_nz-election-data')
    assert data['with']['ref'] == '${{ steps.data.outputs.sha }}'
    assert data['with']['persist-credentials'] is False
    assert data['if'] == "steps.data.outputs.sha != ''"
    resolver = next(s for s in steps if s.get('id') == 'data')['run']
    assert 'set -euo pipefail' in resolver and 'git ls-remote origin refs/heads/data' in resolver
    import os
    fake_git = tmp_path / 'git'
    fake_git.write_text('#!/bin/sh\nprintf "%s" "$REF_RESULT"\nexit "$REF_EXIT"\n')
    fake_git.chmod(0o755)
    output = tmp_path / 'outputs'
    for remote_output, exit_code in (('', '0'), ('a' * 40 + '\trefs/heads/data', '0'), ('', '1')):
        output.write_text('')
        result = subprocess.run(['bash', '-c', resolver], capture_output=True, env=dict(
            os.environ, PATH=str(tmp_path) + ':' + os.environ['PATH'], DATA_SHA='',
            GITHUB_OUTPUT=str(output), REF_RESULT=remote_output, REF_EXIT=exit_code))
        assert (result.returncode == 0) == (exit_code == '0')
        assert output.read_text() == (('sha=' + remote_output.split('\t')[0] + '\n') if exit_code == '0' else '')
    commands = [s.get('run', '') for s in steps]
    product = 'uv run product/nz_election/pipeline/build.py --data _nz-election-data/product/nz_election/data --out site/nz-election'
    assert commands.index('bin/metrics') < commands.index(product) < commands.index('bin/blog build')
    assert any('uv run product/nz_election/pipeline/verify.py all --data _nz-election-data/product/nz_election/data --site site' in c for c in commands)
    record = next(s['run'] for s in steps if s.get('name') == 'Record actual checkouts')
    assert 'NZ_CODE_SHA=$(git rev-parse HEAD)' in record
    assert 'NZ_DATA_SHA=$(git -C _nz-election-data rev-parse HEAD)' in record
    for command in commands:
        for line in command.splitlines():
            if '_nz-election-data' in line:
                assert '--data _nz-election-data/product/nz_election/data' in line or 'git -C _nz-election-data rev-parse HEAD' in line
    stamp = next(s['run'] for s in steps if s.get('name') == 'Record build manifest')
    assert "export.pair(root, 'build-manifest', manifest)" in stamp
    assert "data_sha=os.environ.get('NZ_DATA_SHA') or None" in stamp
    assert "manifest.update(code_sha=os.environ['NZ_CODE_SHA'], run_url=run)" in stamp
    assert steps[-1]['uses'] == 'actions/upload-pages-artifact@v3'
    import sys
    root = tmp_path / 'site/nz-election'
    root.mkdir(parents=True)
    stamp_time = '2026-10-17T01:00:00Z'
    manifest = export.envelope(dict(id='build', source_ref=[], observed_at=stamp_time,
        built_at=stamp_time, code_sha='old', data_sha=None, build_run_url='old', data_available=False), [], 'old', 'old')
    export.pair(root, 'build-manifest', manifest)
    code = '\n'.join(stamp.splitlines()[1:-1])
    subprocess.run([sys.executable, '-c', code], cwd=tmp_path, check=True, env=dict(
        os.environ, PYTHONPATH=str(ROOT), NZ_CODE_SHA='a' * 40, NZ_DATA_SHA='b' * 40,
        GITHUB_SERVER_URL='https://github.com', GITHUB_REPOSITORY='byronxlg/unattended', GITHUB_RUN_ID='123'))
    recorded = json.loads((root / 'build-manifest.json').read_text())
    export.validate_envelope(recorded, 'build-manifest')
    assert recorded['code_sha'] == recorded['data']['code_sha'] == 'a' * 40
    assert recorded['data']['data_sha'] == 'b' * 40
    assert recorded['data']['data_available'] is False
    assert (root / 'build-manifest.csv').read_bytes() == export.csv_bytes(recorded)


def test_status_published_after_handled_failure(tmp_path):
    for first in (True, False):
        root = tmp_path / str(first)
        root.mkdir()
        bundle = root / 'bundle'
        if first:
            remote = root / 'empty.git'
            remote.mkdir()
            git(remote, 'init', '--bare', '-q')
            before = {}
        else:
            refresh(bundle, now='2026-10-17T01:00:00Z')
            remote = repository(root, bundle)
            before = {n: (bundle / n).read_bytes() for n in export.ALLOWED if n.startswith(('polls.', 'averages.', 'seats.'))}
        status = refresh(bundle, now='2026-10-17T02:00:00Z', parse=fail)
        publish(bundle, remote)
        published = json.loads(git(remote, 'show', 'data:' + str(DATA / 'status.json')).stdout)['data'][0]
        assert published == status
        assert published['state'] == ('unavailable' if first else 'stale')
        assert published['error_code'] == 'parse_drift'
        for name, raw in before.items():
            assert git(remote, 'show', 'data:' + str(DATA / name)).stdout.encode() == raw
