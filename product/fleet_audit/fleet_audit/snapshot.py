"""Indexed replay with no host-path or live-clock fallback."""
import hashlib
import json
import math
import os
import re
import stat
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from .models import CommandData, Error, Manifest, Observation, Snapshot
from .registry import join_plists, load_registry, valid_path
from .reports import build_report, serialize

MAX_MEMBER = 8 * 1024 * 1024
MAX_ARCHIVE = 32 * 1024 * 1024


def json_object(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)



def valid_time(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', value):
        return False
    try:
        return datetime.fromisoformat(value).utcoffset().total_seconds() == 0
    except ValueError:
        return False

def observation(obj, data):
    if not isinstance(obj, dict) or set(obj) != {'status', 'observed_at', 'source_command', 'return_code', 'error', 'data'}:
        raise ValueError('invalid observation')
    if obj['status'] not in ('attempted', 'not_requested', 'not_applicable'):
        raise ValueError('invalid observation status')
    if obj['observed_at'] is not None and not valid_time(obj['observed_at']):
        raise ValueError('invalid observation time')
    if not isinstance(obj['source_command'], list) or not all(isinstance(v, str) for v in obj['source_command']):
        raise ValueError('invalid source argv')
    if obj['return_code'] is not None and type(obj['return_code']) is not int:
        raise ValueError('invalid return code')
    if obj['status'] != 'attempted' and (data is not None or any(obj[k] is not None for k in ('observed_at', 'return_code', 'error', 'data'))):
        raise ValueError('unattempted observation contains evidence')
    error = obj['error']
    if error is not None and (not isinstance(error, dict) or set(error) != {'code', 'message'}
                              or not all(isinstance(v, str) for v in error.values())):
        raise ValueError('invalid recorded error')
    return Observation(obj['status'], obj['observed_at'], tuple(obj['source_command']), obj['return_code'],
                       Error(**error) if error else None, data)


def command_observation(obj):
    if not isinstance(obj, dict):
        raise ValueError('invalid command envelope')
    data = obj.get('data')
    if data is not None:
        if (not isinstance(data, dict) or set(data) != {'argv', 'stdout', 'stderr', 'timed_out', 'truncated', 'duration_seconds'}
                or not isinstance(data['argv'], list) or not all(isinstance(v, str) for v in data['argv'])
                or not all(isinstance(data[k], str) for k in ('stdout', 'stderr'))
                or not all(type(data[k]) is bool for k in ('timed_out', 'truncated'))
                or (data['duration_seconds'] is not None and (type(data['duration_seconds']) not in (int, float) or not math.isfinite(data['duration_seconds']) or data['duration_seconds'] < 0))
                or sum(len(data[k].encode()) for k in ('stdout', 'stderr')) > 4194304):
            raise ValueError('invalid command data')
        data = CommandData(**(data | {'argv': tuple(data['argv'])}))
    result = observation(obj, data)
    if data is not None and data.argv != result.source_command:
        raise ValueError('command argv mismatch')
    return result


def load_snapshot(directory):
    directory = Path(directory).absolute()
    total = 0
    if directory.is_symlink():
        raise ValueError('snapshot symlink')

    def member(reference):
        nonlocal total
        if isinstance(reference, dict):
            if set(reference) != {'name', 'bytes', 'sha256', 'origin', 'source'}:
                raise ValueError('invalid member reference')
            name = reference['name']
        else:
            name = reference
        if not isinstance(name, str) or not name or any(ord(c) < 32 for c in name) or name.startswith('/') or any(p in ('', '.', '..') for p in name.split('/')):
            raise ValueError('snapshot path escape')
        current = directory
        for part in name.split('/'):
            current = current / part
            if current.is_symlink():
                raise ValueError('snapshot symlink')
        try:
            fd = os.open(current, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_MEMBER:
                    raise ValueError('invalid snapshot member size or type')
                chunks = bytearray()
                while len(chunks) <= MAX_MEMBER:
                    chunk = os.read(fd, min(65536, MAX_MEMBER + 1 - len(chunks)))
                    if not chunk:
                        break
                    chunks.extend(chunk)
                total += len(chunks)
                if len(chunks) > MAX_MEMBER or total > MAX_ARCHIVE:
                    raise ValueError('snapshot size limit')
                content = bytes(chunks)
                if isinstance(reference, dict):
                    if (type(reference['bytes']) is not int or len(content) != reference['bytes']
                            or hashlib.sha256(content).hexdigest() != reference['sha256']
                            or reference['origin'] not in ('real', 'synthetic') or not isinstance(reference['source'], str)):
                        raise ValueError('member integrity or provenance mismatch')
                elif name != 'manifest.json':
                    raise ValueError('missing member integrity')
                return content
            finally:
                os.close(fd)
        except OSError as exc:
            raise ValueError('missing or unreadable snapshot member: ' + name) from exc

    raw = json_object(member('manifest.json'))
    if not isinstance(raw, dict) or set(raw) != {'format_version', 'capture_clock', 'domain', 'macos_label', 'indexes', 'provenance'}:
        raise ValueError('invalid manifest')
    if type(raw['format_version']) is not int or raw['format_version'] != 1 or not isinstance(raw['domain'], str) or not re.fullmatch(r'gui/\d+', raw['domain']):
        raise ValueError('unsupported snapshot version or domain')
    if not valid_time(raw['capture_clock']) or not isinstance(raw['macos_label'], str) or not isinstance(raw['provenance'], dict):
        raise ValueError('invalid manifest metadata')
    indexes = raw['indexes']
    if not isinstance(indexes, dict) or set(indexes) != {'runbooks', 'plists', 'commands', 'stats', 'receipts', 'expected', 'discovery'}:
        raise ValueError('missing snapshot index')
    groups = {}
    for group in ('runbooks', 'plists'):
        groups[group] = {}
        if not isinstance(indexes[group], dict):
            raise ValueError('invalid file index')
        for logical, entry in indexes[group].items():
            if not valid_path(logical) or not isinstance(entry, dict) or set(entry) != {'member', 'observation'}:
                raise ValueError('invalid logical file entry')
            obs = observation(entry['observation'], member(entry['member']) if entry['member'] is not None else None)
            if obs.data is None and obs.error is None:
                raise ValueError('missing file evidence')
            if obs.data is not None and len(obs.data) > 1048576:
                raise ValueError('file evidence too large')
            groups[group][logical] = obs
    commands = {}
    if not isinstance(indexes['commands'], dict):
        raise ValueError('invalid command index')
    for key, name in indexes['commands'].items():
        obs = command_observation(json_object(member(name)))
        expected_key = command_key(obs.source_command, raw['capture_clock'])
        # The plan requires replaying the real blank inventory from spike 18c8e8c, which used list.
        legacy = (obs.source_command in (('launchctl', 'list'), ('/bin/launchctl', 'list'))
                  and obs.return_code == 1 and obs.data is not None
                  and obs.data.stdout == obs.data.stderr == ''
                  and key == command_key(('/bin/launchctl', 'print', raw['domain']), raw['capture_clock']))
        if key != expected_key and not legacy:
            raise ValueError('command index mismatch')
        commands[key] = obs
    discovery = observation(indexes['discovery'], indexes['discovery']['data'])
    if discovery.data is not None and (not isinstance(discovery.data, list) or not all(isinstance(v, str) for v in discovery.data) or len(discovery.data) > 1000 or len(discovery.data) != len(set(discovery.data))
                                      or set(discovery.data) != set(groups['runbooks'])):
        raise ValueError('missing runbook entry')
    snapshot = Snapshot(Manifest(**raw), groups['runbooks'], groups['plists'], commands,
                        json_object(member(indexes['stats'])), json_object(member(indexes['receipts'])),
                        json_object(member(indexes['expected'])))
    validate_entries(snapshot)
    return snapshot


def command_key(argv, capture_identity):
    return json.dumps([capture_identity, list(argv)], separators=(',', ':'))


class SnapshotFiles:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def discover(self, directory):
        obj = self.snapshot.manifest.indexes['discovery']
        return observation(obj, tuple(obj['data']) if obj['data'] is not None else None)

    def read_regular(self, path, limit=1048576):
        entries = self.snapshot.runbooks | self.snapshot.plists
        if path not in entries:
            raise ValueError('missing file index: ' + path)
        obs = entries[path]
        if obs.data is not None and len(obs.data) > limit:
            return replace(obs, data=None, error=Error('too_large', 'recorded file exceeds read limit'))
        return obs


class SnapshotCommands:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def run(self, argv):
        key = command_key(argv, self.snapshot.manifest.capture_clock)
        if key not in self.snapshot.commands:
            raise ValueError('missing command index: ' + key)
        return self.snapshot.commands[key]


def registry_from(snapshot):
    files = SnapshotFiles(snapshot)
    uid = int(snapshot.manifest.domain.split('/')[1])
    return load_registry(Path('/snapshot-runbooks'), uid, files)


def validate_entries(snapshot):
    registry = registry_from(snapshot)
    if registry.errors:
        return
    for job in registry.jobs:
        if job.plist_path not in snapshot.plists:
            raise ValueError('missing plist entry')
    joined = join_plists(registry, SnapshotFiles(snapshot))
    if not joined.errors:
        required = [('/bin/launchctl', 'print', snapshot.manifest.domain),
                    ('/bin/launchctl', 'print-disabled', snapshot.manifest.domain)]
        required.extend(('/bin/launchctl', 'print', f'{job.identity.domain}/{job.identity.label}') for job in registry.jobs)
        for argv in required:
            SnapshotCommands(snapshot).run(argv)


def replay(snapshot, command):
    if command != 'observer':
        raise ValueError('only observer replay is implemented')
    validate_entries(snapshot)
    registry = join_plists(registry_from(snapshot), SnapshotFiles(snapshot))
    if registry.errors:
        return build_report(registry, snapshot.manifest.domain) | {'command': command}
    from .collect import collect_jobs
    fleet = collect_jobs(registry.jobs, snapshot.manifest.domain, SnapshotCommands(snapshot))
    jobs = [serialize(job) for job in fleet.jobs]
    return {'schema_version': 1, 'command': command, 'domain': fleet.domain, 'observed_at': fleet.observed_at,
            'jobs': jobs, 'issues': list(fleet.coverage.issues),
            'summary': {'jobs': len(jobs), 'verdicts': {'cannot_determine': sum(j.verdict is not None for j in fleet.jobs)}},
            'exit_code': 2}
