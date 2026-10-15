"""Audit transport, validation, CLI, and frozen-only acceptance."""
import builtins
from dataclasses import replace
from pathlib import Path

import pytest

from fleet_audit.acceptance import FIXTURES
from fleet_audit.capture import capture_snapshot
from fleet_audit.cli import main
from fleet_audit.snapshot import SnapshotCommands, SnapshotFiles, load_snapshot, replay
from test_snapshot import materialize
from test_verdicts import scenario


def test_receipt_capture_replay_roundtrip_and_no_live_access(tmp_path, monkeypatch):
    snap = scenario()
    captured = capture_snapshot('/ignored', 'gui/501', 'audit', files=SnapshotFiles(snap),
                                commands=SnapshotCommands(snap), clock=lambda: snap.manifest.capture_clock,
                                macos_label='synthetic')
    assert captured.receipts and captured.stats and captured.expected == {'reviewed': False}
    materialize(captured, tmp_path)
    restored = load_snapshot(tmp_path)
    def trap(*args, **kwargs): raise AssertionError('unexpected live access')
    class NoClock:
        now = staticmethod(trap)
    import fleet_audit.files as files
    import fleet_audit.collect as collect
    import fleet_audit.capture as capture
    monkeypatch.setattr(files, 'datetime', NoClock)
    monkeypatch.setattr(collect, 'datetime', NoClock)
    monkeypatch.setattr(capture, 'datetime', NoClock)
    monkeypatch.setattr(collect.time, 'time', trap)
    monkeypatch.setattr(collect.time, 'monotonic', trap)
    monkeypatch.setattr(collect.LiveCommands, 'run', trap)
    monkeypatch.setattr(files.os, 'open', trap)
    monkeypatch.setattr(builtins, 'open', trap)
    monkeypatch.setattr(Path, 'open', trap)
    assert replay(restored, 'audit') == replay(captured, 'audit')
    assert replay(restored, 'audit')['exit_code'] == 0


def test_verdict_acceptance_guard_and_reviewed_requirement(monkeypatch):
    import fleet_audit.acceptance as acceptance
    acceptance.main(['verdicts', '--offline'])
    load = acceptance.load_snapshot
    monkeypatch.setattr(acceptance, 'load_snapshot', lambda path: replace(load(path), expected={'reviewed': False}))
    with pytest.raises(AssertionError, match='unreviewed'):
        acceptance.main(['verdicts', '--offline'])
    assert not acceptance._OFFLINE


def test_audit_cli_offline_and_invalid_input(capsys, monkeypatch):
    root = FIXTURES / 'verdicts'
    assert main(['audit', '/never-read', '--fixture', str(root / 'completed-no-result'), '--json']) == 0
    assert 'healthy_idle' in capsys.readouterr().out
    assert main(['audit', '/never-read', '--fixture', str(root / 'grace-window')]) == 2
    assert 'within grace' in capsys.readouterr().out
    assert main(['audit', '/never-read', '--fixture', str(root / 'unexpected-disabled')]) == 1
    assert main(['audit', '/never-read', '--fixture', str(root / 'completed-no-result'), '--domain', 'gui/502']) == 3
    import fleet_audit.collect as collect
    def trap(*args, **kwargs): raise AssertionError('live command before validation')
    monkeypatch.setattr(collect.LiveCommands, 'run', trap)
    assert main(['audit', '/missing-runbook-directory']) == 3
    with pytest.raises(SystemExit) as exc:
        main(['audit', '/ignored', '--unknown'])
    assert exc.value.code == 3


@pytest.mark.parametrize('group', ['stats', 'receipts'])
def test_audit_missing_evidence_is_invalid_input(group):
    snap = scenario()
    with pytest.raises(ValueError, match='missing .* index'):
        replay(replace(snap, **{group: {}}), 'audit')


@pytest.mark.parametrize('mutation', ['encoding', 'oversize', 'metadata', 'path', 'type'])
def test_receipt_envelope_validation(tmp_path, mutation):
    snap = scenario()
    path = next(iter(snap.receipts))
    entry = snap.receipts[path]
    data = dict(entry['data'])
    if mutation == 'encoding': data['tail_bytes'] = {'base64': '!'}
    if mutation == 'oversize': data['bytes_read'] = 65537
    if mutation == 'metadata': data['before'] = {'regular': True}
    if mutation == 'path': data['path'] = '/different'
    if mutation == 'type': data['changed'] = 1
    snap = replace(snap, receipts={path: entry | {'data': data}})
    materialize(snap, tmp_path)
    with pytest.raises(ValueError): load_snapshot(tmp_path)


def test_receipt_embedded_paths_never_become_inputs():
    from fleet_audit.receipts import normalize_tick
    receipt = normalize_tick({'ts': '2026-10-16T00:00:00Z', 'path': '/never-open',
                              'supervisor': {'ran': False, 'rc': None, 'error': None, 'result': '/also-never-open'},
                              'environment': {'HOME': '/never-use'}})
    assert set(receipt.last_object) == {'ts', 'supervisor'}
    assert receipt.outcome == 'completed'
