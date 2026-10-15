"""Frozen evidence and fake process boundaries; no child processes are run."""
import json
from dataclasses import replace

import pytest

from fleet_audit.acceptance import FIXTURES, FixtureFiles
from fleet_audit.collect import collect_jobs, run_bounded
from fleet_audit.launchctl_parse import parse_domain, parse_service
from fleet_audit.models import Absent, CommandData, Identity, Known, Observation, Unknown
from fleet_audit.overrides import effective_disabled, parse_overrides
from fleet_audit.registry import join_plists, load_registry

ROOT = FIXTURES / 'observer'


def frozen(name):
    return json.loads((ROOT / (name + '.json')).read_text())


def command(name):
    obj = frozen(name)
    record = obj['record']
    if name.startswith('audit-'):
        record = record['collection']
    elif isinstance(record.get('command'), dict):
        record = record['command']
    argv = tuple(record['command'])
    stamp = obj['provenance']['captured_at']
    return Observation('attempted', stamp, argv, record['returncode'], None,
                       CommandData(argv, record['stdout'], record['stderr'], False, False, None))


def jobs():
    files = FixtureFiles()
    return join_plists(load_registry(FIXTURES / 'registry-valid', 501, files), files).jobs


class Commands:
    def __init__(self, inventory='snapshot-inventory'):
        self.inventory = inventory
        self.calls = []

    def run(self, argv):
        self.calls.append(argv)
        if argv[1] == 'print-disabled':
            return command('print-disabled')
        if argv[2] == 'gui/501':
            return command(self.inventory)
        return command(argv[2].split('/')[-1])


def test_empty_inventory_exit_one_retains_every_job():
    from fleet_audit.snapshot import load_snapshot, replay
    report = replay(load_snapshot(FIXTURES / 'host'), 'observer')
    assert len(report['jobs']) == len(jobs())
    assert all(j['verdict']['name'] == 'cannot_determine' and 'rc=1' in j['verdict']['reason'] for j in report['jobs'])
    source = Commands('snapshot-launchctl_list')
    original = jobs()
    fleet = collect_jobs(original * 2, 'gui/501', source)
    assert len(fleet.jobs) == 2
    assert all(j.verdict.name == 'cannot_determine' and j.verdict.rule_id == 1 and 'rc=1' in j.verdict.reason for j in fleet.jobs)
    assert [call[1] for call in source.calls] == ['print', 'print', 'print', 'print-disabled']


def test_empty_inventory_without_jobs_reports_coverage_issue():
    fleet = collect_jobs((), 'gui/501', Commands('snapshot-launchctl_list'))
    assert not fleet.jobs and not fleet.coverage.complete
    assert 'rc=1' in fleet.coverage.issues[0]


def service(name):
    obs = command(name)
    return parse_service(obs, Identity('local', 'gui/501', obs.data.argv[-1].split('/')[-1]))


def test_real_service_fields_and_capture_separation():
    original = service('com.unattended.tick')
    audit = service('audit-com.unattended.tick')
    assert original.data.runs == Known(28) and audit.data.runs == Known(29)
    assert original.observed_at != audit.observed_at
    assert original.data.argv == Known(('/bin/bash', '/Users/byron/repos/unattended/bin/tick'))
    assert original.data.schedule.interval_seconds == Known(600)
    assert original.data.schedule.run_at_load == Known(True)
    assert service('org.nixos.skhd').data.last_exit_code == Known(78)
    assert service('org.nixos.skhd').data.last_exit_text == Known('EX_CONFIG')
    assert service('com.koekeishiya.yabai').data.loaded == Known(False)
    assert len(service('snapshot-com.apple.talagent').data.schedule.calendar.value) == 2
    assert isinstance(service('com.pdw.docker-restart').data.schedule.calendar, Known)
    assert service('snapshot-com.apple.appleseed.seedusaged.postinstall').data.loaded == Known(True)
    assert isinstance(service('snapshot-com.apple.networkserviceproxy').data.loaded, Unknown)
    assert len(list(ROOT.glob('audit-*.json'))) == 12
    for path in ROOT.glob('audit-*.json'):
        obj = json.loads(path.read_text())
        assert obj['provenance']['kind'] == 'real' and '18c8e8c' in obj['provenance']['source']
        if obj['record']['collection'] is not None:
            parsed = service(path.stem)
            assert parsed.data.structural_valid
    assert service('audit-org.nixos.yabai').data.last_exit_code == Known(78)
    inventory = parse_domain(command('snapshot-inventory'), 'gui/501')
    assert inventory.data.complete and len(inventory.data.labels) == 454


def variant(name, base='com.unattended.tick'):
    obs = command(base)
    recipe = frozen(name)['recipe']
    text = obs.data.stdout
    if 'replace' in recipe:
        assert recipe['replace'][0] in text
        text = text.replace(*recipe['replace'])
    if recipe.get('remove_last_line'):
        text = '\n'.join(text.splitlines()[:-1])
    return replace(obs, return_code=recipe.get('returncode', obs.return_code),
                   data=replace(obs.data, stdout=recipe.get('stdout', text), stderr=recipe.get('stderr', obs.data.stderr)))


@pytest.mark.parametrize('name', ['blank-success', 'wrong-domain', 'wrong-label', 'unrelated-113',
                                  'truncated-service', 'duplicate-state', 'invalid-pid'])
def test_structural_and_identity_failures_are_unknown(name):
    result = parse_service(variant(name), Identity('local', 'gui/501', 'com.unattended.tick'))
    assert isinstance(result.data.loaded, Unknown) and not result.data.structural_valid
    obs = command('com.unattended.tick')
    obs = replace(obs, data=replace(obs.data, stdout=obs.data.stdout.replace('\tstate = not running\n', '')))
    result = parse_service(obs, Identity('local', 'gui/501', 'com.unattended.tick'))
    assert isinstance(result.data.state, Unknown)
    assert result.data.loaded == Known(True)


def test_missing_pid_and_exit_are_not_zero():
    result = parse_service(variant('never-exited'), Identity('local', 'gui/501', 'com.unattended.tick'))
    assert isinstance(result.data.pid, Absent)
    assert isinstance(result.data.last_exit_code, Unknown)
    result = parse_service(variant('truncated-service'), result.data.identity)
    assert isinstance(result.data.pid, Unknown)


def test_real_override_map_and_precedence():
    override = parse_overrides(command('print-disabled'))
    entries = dict(override.data.entries)
    assert override.data.complete and len(entries) == 15
    assert sum(value for label, value in entries.items() if label.startswith('com.apple.')) == 5
    plist = dict(jobs()[0].observations)['plist']
    plist = replace(plist, data=replace(plist.data, disabled=Known(True), present_keys=plist.data.present_keys + ('Disabled',)))
    assert effective_disabled('org.nixos.skhd', plist, override).value == Known(False)
    assert effective_disabled('org.nixos.skhd', plist, override).origin == 'override'
    assert effective_disabled('absent', plist, override).value == Known(True)
    assert effective_disabled('absent', plist, override).entry == 'absent'
    for name in ('override-denied', 'override-incomplete'):
        failed = parse_overrides(variant(name, 'print-disabled'))
        assert not failed.data.complete
        assert isinstance(effective_disabled('org.nixos.skhd', plist, failed).value, Unknown)
    assert parse_overrides(variant('override-absent', 'print-disabled')).data.complete


def test_subprocess_bounds_and_reaping(monkeypatch):
    import fleet_audit.collect as module
    class Stream:
        def __init__(self, fd): self.fd, self.closed = fd, False
        def fileno(self): return self.fd
        def close(self): self.closed = True
    class Process:
        def __init__(self):
            self.stdout, self.stderr = Stream(10), Stream(11)
            self.killed, self.waited, self.finished = False, 0, False
        def kill(self): self.killed, self.finished = True, True
        def wait(self, timeout=None):
            self.waited += 1
            self.finished = True
            return -9 if self.killed else 0
        def poll(self): return 0 if self.finished else None
    class Selector:
        def __init__(self): self.items = {}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def register(self, stream, event, index):
            from types import SimpleNamespace
            self.items[stream.fd] = SimpleNamespace(fileobj=stream, data=index)
        def unregister(self, stream): del self.items[stream.fd]
        def get_map(self): return self.items
        def select(self, timeout): return [(item, 1) for item in list(self.items.values())]
    monkeypatch.setattr(module.selectors, 'DefaultSelector', Selector)
    monkeypatch.setattr(module.os, 'set_blocking', lambda *a: None)
    argv = ('/bin/launchctl', 'print', 'gui/501')
    for scenario in ('combined-output-limit', 'timeout', 'normal', 'spawn'):
        proc = Process()
        chunks = {10: [b'abcd', b''], 11: [b'efghi', b'']}
        monkeypatch.setattr(module.os, 'read', lambda fd, size: chunks[fd].pop(0)[:size])
        ticks = iter([0, 11, 12, 13, 14]) if scenario == 'timeout' else iter(range(20))
        monkeypatch.setattr(module.time, 'monotonic', lambda: next(ticks))
        def spawn(args, **kw):
            assert args == argv and kw['shell'] is False
            assert kw['stdout'] == kw['stderr'] == module.subprocess.PIPE
            if scenario == 'spawn': raise OSError('denied')
            return proc
        monkeypatch.setattr(module.subprocess, 'Popen', spawn)
        result = run_bounded(argv, max_bytes=8 if scenario == 'combined-output-limit' else 100)
        if scenario != 'spawn':
            assert proc.waited and proc.stdout.closed and proc.stderr.closed
        if scenario in ('timeout', 'combined-output-limit'):
            assert proc.killed and result.error is not None
        if scenario == 'timeout': assert result.data.timed_out and result.return_code is None
        if scenario == 'combined-output-limit': assert result.data.truncated and len(result.data.stdout + result.data.stderr) <= 8
        if scenario == 'spawn': assert result.return_code is None and result.error is not None
        if scenario == 'normal': assert result.error is None and result.return_code == 0
    for invalid in (('/bin/sh', '-c', 'true'), ('/bin/launchctl', 'list'), ('/bin/launchctl', 'print', 'system')):
        with pytest.raises(ValueError): run_bounded(invalid)


def test_arguments_preserve_empty_spaces_and_delimiters():
    obs = command('com.unattended.tick')
    text = obs.data.stdout.replace('\t\t/bin/bash\n', '\t\t/bin/bash\n\t\t\n\t\ttwo words\n\t\t}\n\t\tx = y\n')
    result = parse_service(replace(obs, data=replace(obs.data, stdout=text)), Identity('local', 'gui/501', 'com.unattended.tick'))
    assert result.data.argv.value[:5] == ('/bin/bash', '', 'two words', '}', 'x = y')


def test_rule_one_only_and_guarded_observer_acceptance():
    import sys
    import fleet_audit.acceptance as acceptance
    from fleet_audit.verdicts import RULES
    assert tuple(rule.id for rule in RULES) == (1,)
    assert collect_jobs(jobs(), 'gui/501', Commands()).jobs[0].verdict is None
    acceptance.main(['observer', '--offline'])
    acceptance._OFFLINE = True
    try:
        with pytest.raises(AssertionError, match='process'):
            sys.audit('subprocess.Popen', 'fake', (), None, None)
        with pytest.raises(AssertionError, match='non-fixture'):
            open('/not-a-fixture')
    finally:
        acceptance._OFFLINE = False
