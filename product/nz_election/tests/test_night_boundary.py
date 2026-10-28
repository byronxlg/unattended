"""Executed boundary scenarios and isolation, without upstream or production access."""
from datetime import timedelta
from pathlib import Path
import socket
import subprocess

import pytest
from product.nz_election.pipeline import night_boundary as drill
from product.nz_election.tests.test_workflows import workflow


@pytest.mark.parametrize('scenario', drill.scenarios())
def test_boundary_scenario(scenario):
    drill.run_scenario(scenario)


@pytest.mark.parametrize('kind', drill.SUNSETS)
@pytest.mark.parametrize('seconds', [-1, 1])
def test_sunset_one_second_mutation_detected(monkeypatch, kind, seconds):
    constant = kind.upper() + '_CLOSE'
    monkeypatch.setattr(drill.sunsets, constant, drill.SUNSETS[kind] + timedelta(seconds=seconds))
    position = 'before' if seconds == -1 else 'at'
    with pytest.raises(AssertionError, match='SUNSET_ALLOWED'):
        drill.run_scenario(f'sunset-{kind}-schedule-{position}')


@pytest.mark.parametrize('seconds', [-1, 1])
def test_startup_one_second_mutation_detected(monkeypatch, seconds):
    monkeypatch.setattr(drill.night_live, 'END', drill.OPEN + timedelta(seconds=seconds))
    monkeypatch.setattr(drill.deployment_guard, 'END', drill.OPEN + timedelta(seconds=seconds))
    with pytest.raises((AssertionError, ValueError)):
        drill.run_scenario('startup')


@pytest.mark.parametrize('seconds', [-1, 1])
def test_stop_one_second_mutation_detected(monkeypatch, seconds):
    monkeypatch.setattr(drill.night_live, 'CLOSE', drill.STOP + timedelta(seconds=seconds))
    with pytest.raises(AssertionError):
        drill.run_scenario('inflight-acquisition')
    with pytest.raises(AssertionError):
        drill.run_scenario('watchdog-cutoff')


@pytest.mark.parametrize('rollback', [False, True])
def test_removed_publisher_freeze_detected(monkeypatch, rollback):
    monkeypatch.setattr(drill.publish, 'require_publication_allowed', lambda *a: None)
    scenario = 'queued-' + ('rollback' if rollback else 'publish') + '-at-freeze'
    with pytest.raises(AssertionError, match='GUARD_REMOVED'):
        drill.run_scenario(scenario)


def test_isolation_denies_network_commands_and_outside_git(tmp_path):
    with drill.isolated(tmp_path):
        with pytest.raises(AssertionError, match='ISOLATION_VIOLATION'):
            socket.socket()
        with pytest.raises(AssertionError, match='COMMAND_DENIED'):
            subprocess.run(['gh', 'workflow', 'run', 'pages.yml'])
        with pytest.raises(AssertionError, match='NONLOCAL_GIT'):
            drill.publish.git(Path.cwd(), 'status')


def test_failure_line_and_nonzero_exit(monkeypatch, capsys):
    monkeypatch.setattr(drill, 'scenarios', lambda: {'broken': None, 'next': None})
    def run(name):
        if name == 'broken':
            raise AssertionError('GUARD_REMOVED')
    monkeypatch.setattr(drill, 'run_scenario', run)
    assert drill.main() == 1
    assert capsys.readouterr().out == 'FAIL broken GUARD_REMOVED\nPASS next\n'


def test_boundary_dispatch_is_exclusive_and_read_only():
    doc = workflow('nz-election-night-rehearsal.yml')
    assert doc['permissions'] == {}
    assert doc[True]['workflow_dispatch']['inputs']['boundary_only'] == {
        'description': 'Run only the isolated offline time boundary drill', 'type': 'boolean', 'default': False}
    jobs = doc['jobs']
    assert jobs['rehearse']['if'] == 'inputs.import_only != true'
    assert jobs['import-rehearsal']['if'] == 'inputs.import_only == true'
    assert jobs['rehearse']['needs'] == jobs['import-rehearsal']['needs'] == 'non-boundary'
    assert jobs['non-boundary'] == {
        'if': 'inputs.boundary_only != true', 'runs-on': 'ubuntu-latest',
        'timeout-minutes': 1, 'permissions': {}, 'steps': [{'run': 'true'}]}
    boundary = jobs['boundary-rehearsal']
    assert boundary['if'] == 'inputs.boundary_only == true'
    assert boundary['permissions'] == {'contents': 'read'}
    assert boundary['steps'] == [
        {'uses': 'actions/checkout@v4', 'with': {'ref': '${{ github.sha }}', 'persist-credentials': False}},
        {'name': 'Exercise isolated election time boundaries',
         'run': 'python3 product/nz_election/pipeline/night_boundary.py'}]
    assert 'env' not in boundary
