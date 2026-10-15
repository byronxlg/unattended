"""Supervisor capture API emitting archives only to a supplied byte stream."""
import hashlib
import io
import json
import os
import platform
import plistlib
import re
import tarfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .files import LocalFiles
from .launchctl_parse import redact_environment
from .models import Error, Manifest, Snapshot
from .registry import join_plists, load_registry
from .reports import serialize
from .snapshot import command_key


def capture_snapshot(directory, domain, mode, *, files=None, commands=None, clock=None, macos_label=None):
    if mode not in ('observer', 'audit') or directory is None or not re.fullmatch(r'gui/\d+', domain):
        raise ValueError('capture requires observer mode, runbook directory and gui domain')
    from .collect import LiveCommands
    if files is None and commands is None and domain != f'gui/{os.getuid()}':
        raise ValueError('capture requires current-user domain')
    files = files if files is not None else LocalFiles()
    commands = commands if commands is not None else LiveCommands()
    stamp = clock() if clock else datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    runbooks, plists = {}, {}

    class RecordingFiles:
        def discover(self, path):
            self.discovery = files.discover(path)
            return self.discovery

        def read_regular(self, path, limit):
            obs = files.read_regular(path, limit)
            target = runbooks if path in (self.discovery.data or ()) else plists
            if target is plists and obs.data is not None:
                try:
                    obj = plistlib.loads(obs.data)
                except Exception:
                    # Unparseable bytes cannot be safely redacted.
                    obs = replace(obs, data=None, error=Error('invalid_plist', 'malformed plist; bytes withheld'))
                else:
                    if isinstance(obj, dict) and 'EnvironmentVariables' in obj:
                        env = obj['EnvironmentVariables']
                        if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
                            obs = replace(obs, data=None, error=Error('invalid_plist', 'invalid environment'))
                        else:
                            obj['EnvironmentVariables'] = {key: '' for key in env}
                            obs = replace(obs, data=plistlib.dumps(obj))
            target[path] = obs
            return obs

    recorder = RecordingFiles()
    registry = join_plists(load_registry(Path(directory), int(domain.split('/')[1]), recorder), recorder)
    observations = {}
    if not registry.errors:
        argv_list = [('/bin/launchctl', 'print', domain)]
        argv_list.extend(('/bin/launchctl', 'print', f'{domain}/{job.identity.label}') for job in registry.jobs)
        argv_list.append(('/bin/launchctl', 'print-disabled', domain))
        for argv in argv_list:
            obs = commands.run(argv)
            if obs.data is not None:
                obs = replace(obs, data=replace(obs.data, stdout=redact_environment(obs.data.stdout),
                                                stderr=redact_environment(obs.data.stderr)))
            observations[command_key(argv, stamp)] = obs
    indexes = {'discovery': serialize(recorder.discovery)}
    manifest = Manifest(1, stamp, domain, macos_label if macos_label is not None else platform.mac_ver()[0], indexes,
                        {'kind': 'real' if files.__class__ is LocalFiles else 'synthetic', 'mode': mode,
                         'environment': 'keys only; values removed'})
    return Snapshot(manifest, runbooks, plists, observations, {}, {}, {'reviewed': False})


def emit_archive(snapshot, stream):
    members, indexes = {}, {'discovery': snapshot.manifest.indexes['discovery']}
    for group in ('runbooks', 'plists'):
        indexes[group] = {}
        for index, (logical, obs) in enumerate(sorted(getattr(snapshot, group).items())):
            name = f'{group}/{index}' if obs.data is not None else None
            if name is not None:
                members[name] = obs.data
            indexes[group][logical] = {'member': name, 'observation': serialize(replace(obs, data=None))}
    indexes['commands'] = {}
    for index, (key, obs) in enumerate(sorted(snapshot.commands.items())):
        name = f'commands/{index}.json'
        indexes['commands'][key] = name
        members[name] = json.dumps(serialize(obs)).encode()
    for group in ('stats', 'receipts', 'expected'):
        name = 'receipts/index.json' if group == 'receipts' else f'{group}.json'
        indexes[group] = name
        members[name] = json.dumps(getattr(snapshot, group)).encode()
    def reference(name):
        content = members[name]
        return {'name': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
                'origin': snapshot.manifest.provenance['kind'],
                'source': snapshot.manifest.provenance.get('source', 'capture ' + snapshot.manifest.capture_clock)}
    for group in ('runbooks', 'plists'):
        for entry in indexes[group].values():
            if entry['member'] is not None:
                entry['member'] = reference(entry['member'])
    indexes['commands'] = {key: reference(name) for key, name in indexes['commands'].items()}
    for group in ('stats', 'receipts', 'expected'):
        indexes[group] = reference(indexes[group])
    members['manifest.json'] = json.dumps(serialize(replace(snapshot.manifest, indexes=indexes))).encode()
    with tarfile.open(fileobj=stream, mode='w|') as archive:
        for name, content in sorted(members.items()):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(content), 0o600, 0
            archive.addfile(info, io.BytesIO(content))
