"""Snapshot transport, validation and replay isolation."""
import builtins
import io
import json
import tarfile
from dataclasses import replace
from pathlib import Path

import pytest

from fleet_audit.acceptance import FIXTURES, FixtureFiles, STAMP
from fleet_audit.capture import capture_snapshot, emit_archive
from fleet_audit.models import Observation
from fleet_audit.snapshot import load_snapshot, replay
from test_observer import Commands, command


def captured(inventory='snapshot-inventory', files=None):
    class CanonicalCommands(Commands):
        def run(self, argv):
            obs = super().run(argv)
            if self.inventory == 'snapshot-launchctl_list' and argv[2] == 'gui/501' and argv[1] == 'print':
                return obs
            return replace(obs, source_command=argv, data=replace(obs.data, argv=argv))
    return capture_snapshot(str(FIXTURES/'registry-valid'), 'gui/501', 'observer',
                            files=files or FixtureFiles(), commands=CanonicalCommands(inventory),
                            clock=lambda: STAMP, macos_label='synthetic composition of macOS 26.5 evidence')


def materialize(snapshot, directory):
    stream = io.BytesIO()
    emit_archive(snapshot, stream)
    stream.seek(0)
    with tarfile.open(fileobj=stream) as archive:
        archive.extractall(directory, filter='data')
    return stream.getvalue()


def test_snapshot_validation_and_failure_evidence(tmp_path):
    materialize(captured('snapshot-launchctl_list'), tmp_path)
    snapshot = load_snapshot(tmp_path)
    report = replay(snapshot, 'observer')
    assert len(report['jobs']) == 1 and report['exit_code'] == 2
    assert 'rc=1' in report['jobs'][0]['verdict']['reason']
    manifest = json.loads((tmp_path/'manifest.json').read_text())
    for recipe in ('snapshot-missing-entry', 'snapshot-path-escape'):
        assert json.loads((FIXTURES/'observer'/f'{recipe}.json').read_text())['provenance']['kind'] == 'synthetic'
    path = tmp_path/'manifest.json'
    original = path.read_bytes()
    first = next(iter(manifest['indexes']['commands']))
    del manifest['indexes']['commands'][first]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='missing command'): load_snapshot(tmp_path)
    path.write_bytes(original)
    manifest = json.loads(original)
    entry = next(iter(manifest['indexes']['commands'].values()))
    original_name = entry['name']
    entry['name'] = '../escape'
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='escape'): load_snapshot(tmp_path)
    entry['name'] = original_name
    path.write_text(json.dumps(manifest))
    member = tmp_path / original_name
    data = member.read_bytes()
    member.unlink()
    with pytest.raises(ValueError, match='missing'): load_snapshot(tmp_path)
    member.symlink_to(tmp_path/'manifest.json')
    with pytest.raises(ValueError, match='symlink'): load_snapshot(tmp_path)
    member.unlink()
    member.write_bytes(data + b' ')
    with pytest.raises(ValueError, match='integrity'): load_snapshot(tmp_path)
    member.write_bytes(data)
    assert load_snapshot(tmp_path).manifest.format_version == 1


def test_replay_forbids_live_commands_paths_and_clock(tmp_path, monkeypatch):
    import fleet_audit.collect as collect
    import fleet_audit.files as files
    import fleet_audit.capture as capture
    materialize(captured('snapshot-launchctl_list'), tmp_path)
    snapshot = load_snapshot(tmp_path)
    def trap(*args, **kwargs): raise AssertionError('replay attempted live access')
    class Clock:
        now = staticmethod(trap)
    monkeypatch.setattr(files, 'datetime', Clock)
    monkeypatch.setattr(collect, 'datetime', Clock)
    monkeypatch.setattr(capture, 'datetime', Clock)
    monkeypatch.setattr(collect.time, 'time', trap)
    monkeypatch.setattr(collect.time, 'monotonic', trap)
    monkeypatch.setattr(collect.LiveCommands, 'run', trap)
    monkeypatch.setattr(files.LocalFiles, 'read_regular', trap)
    monkeypatch.setattr(files.LocalFiles, 'discover', trap)
    monkeypatch.setattr(builtins, 'open', trap)
    monkeypatch.setattr(Path, 'open', trap)
    monkeypatch.setattr(files.os, 'open', trap)
    report = replay(snapshot, 'observer')
    assert report['jobs'][0]['verdict']['rule_id'] == 1
    assert report['exit_code'] == 2


def test_capture_roundtrip_and_environment_redaction(tmp_path, monkeypatch):
    import plistlib
    class EnvironmentFiles(FixtureFiles):
        def read_regular(self, path, limit=1048576):
            obs = super().read_regular(path, limit)
            if path.endswith('.plist'):
                obj = plistlib.loads(obs.data)
                obj['EnvironmentVariables'] = {'SYNTHETIC_KEY': 'secret-marker-do-not-export'}
                obs = replace(obs, data=plistlib.dumps(obj))
            return obs
    snapshot = captured(files=EnvironmentFiles())
    original_open = builtins.open
    def no_write(path, mode='r', *args, **kwargs):
        assert not any(flag in mode for flag in 'wa+')
        return original_open(path, mode, *args, **kwargs)
    with monkeypatch.context() as scoped:
        scoped.setattr(builtins, 'open', no_write)
        stream = io.BytesIO()
        emit_archive(snapshot, stream)
    data = materialize(snapshot, tmp_path)
    assert b'secret-marker-do-not-export' not in data and b'SYNTHETIC_KEY' in data
    assert b'/var/run/com.apple.launchd.' not in data
    restored = load_snapshot(tmp_path)
    assert replay(restored, 'observer') == replay(snapshot, 'observer')
    assert restored.expected == {'reviewed': False}
    plist = next(iter(restored.plists.values())).data
    assert plistlib.loads(plist)['EnvironmentVariables'] == {'SYNTHETIC_KEY': ''}


@pytest.mark.parametrize('failure', ['timeout', 'truncated', 'spawn', 'missing_plist'])
def test_recorded_failures_are_valid_snapshot_evidence(tmp_path, failure):
    from fleet_audit.models import Error
    snapshot = captured()
    if failure == 'missing_plist':
        path, obs = next(iter(snapshot.plists.items()))
        snapshot = replace(snapshot, plists={path: replace(obs, data=None, error=Error('missing', 'ENOENT'))})
    else:
        key, obs = next(iter(snapshot.commands.items()))
        if failure == 'spawn':
            obs = replace(obs, return_code=None, error=Error('command_io', 'PermissionError'), data=None)
        else:
            obs = replace(obs, return_code=None if failure == 'timeout' else -9,
                          error=Error(failure, 'recorded failure'),
                          data=replace(obs.data, timed_out=failure == 'timeout', truncated=failure == 'truncated'))
        snapshot = replace(snapshot, commands=snapshot.commands | {key: obs})
    materialize(snapshot, tmp_path)
    report = replay(load_snapshot(tmp_path), 'observer')
    assert report['exit_code'] == (3 if failure == 'missing_plist' else 2)
    assert len(report['jobs']) == 1
    if failure != 'missing_plist': assert report['jobs'][0]['verdict']['rule_id'] == 1


@pytest.mark.parametrize('field,value', [('format_version', True), ('domain', 501),
                                        ('capture_clock', '2026-10-16'), ('indexes', {})])
def test_malformed_manifests_are_invalid_input(tmp_path, field, value):
    materialize(captured(), tmp_path)
    path = tmp_path/'manifest.json'
    obj = json.loads(path.read_text())
    obj[field] = value
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError): load_snapshot(tmp_path)
