"""Three-way comparisons, exact values and conservative loaded policy evidence."""
import builtins
import json
import plistlib
from dataclasses import replace
from pathlib import Path

import pytest

from fleet_audit.acceptance import FIXTURES
from fleet_audit.drift import compare_job, normalize_calendar
from fleet_audit.launchctl_parse import parse_service
from fleet_audit.models import Absent, Error, Known, Unknown, Unsupported
from fleet_audit.plists import parse_plist
from fleet_audit.reports import render_text
from fleet_audit.snapshot import load_snapshot, replay
from fleet_audit.verdicts import evaluate
from test_observer import command, service
from test_verdicts import fleet

PAIRS = ('registry-to-disk', 'registry-to-loaded', 'disk-to-loaded')
FIELDS = [('program', '/one', '/two', 'wrong_program'),
          ('arguments', ('/one', '', 'two words'), ('/one', 'two', 'words'), 'wrong_arguments'),
          ('working_directory', '/one', '/two', 'wrong_working_directory'),
          ('interval_seconds', 600, 601, 'wrong_schedule'),
          ('calendar', ((('Hour', 3),),), ((('Hour', 4),),), 'wrong_schedule'),
          ('keep_alive', True, False, 'wrong_schedule'),
          ('run_at_load', True, False, 'wrong_schedule')]


def with_field(job, source, field, value):
    schedule = field in ('interval_seconds', 'calendar', 'keep_alive', 'run_at_load')
    if source == 'registry':
        declaration = job.registry
        if schedule:
            declaration = replace(declaration, expected_schedule=replace(declaration.expected_schedule, **{field: value}))
        else:
            declaration = replace(declaration, **{'expected_' + field: value if field == 'working_directory' else value.value})
        return replace(job, registry=declaration)
    observations = dict(job.observations)
    obs = observations[source]
    data = obs.data
    if schedule:
        data = replace(data, schedule=replace(data.schedule, **{field: value}))
    else:
        data = replace(data, **{'argv' if field == 'arguments' and source == 'service' else field: value})
    observations[source] = replace(obs, data=data)
    return replace(job, observations=tuple(observations.items()))


@pytest.mark.parametrize('field,left,right,kind', FIELDS)
@pytest.mark.parametrize('pair', PAIRS)
def test_three_pairs_per_declared_field(field, left, right, kind, pair):
    job = fleet().jobs[0]
    sources = {'registry': 'registry', 'disk': 'plist', 'loaded': 'service'}
    for source in sources.values():
        job = with_field(job, source, field, Known(left))
    left_source, right_source = pair.split('-to-')
    job = with_field(job, sources[right_source], field, Known(right))
    comparisons, findings = compare_job(job)
    name = 'schedule.' + field if kind == 'wrong_schedule' else field
    comparison = next(c for c in comparisons if c.field == name and c.pair == pair)
    assert comparison.status == 'different'
    finding = next(f for f in findings if f.field == name and f.pair == pair)
    assert finding.kind == kind
    assert finding.reason == f'{name}: {left_source}={left} differs from {right_source}={right}'
    assert finding.evidence_refs == comparison.evidence_refs == (sources[left_source], sources[right_source])
    assert len([c for c in comparisons if c.field == name]) == 3


@pytest.mark.parametrize('value', [Unknown('missing'), Absent('missing'), Unsupported({'raw': True}, 'unsupported')])
def test_unknown_is_incomplete_not_drift(value):
    job = with_field(fleet().jobs[0], 'service', 'program', value)
    comparisons, findings = compare_job(job)
    assert [c.status for c in comparisons if c.field == 'program'] == ['equal', 'unknown', 'unknown']
    assert not findings
    assert {c.field for c in comparisons} == {'program', 'arguments'}
    absent, findings = compare_job(replace(job, loaded=Known(False)))
    assert all(c.status == 'not_applicable' for c in absent if c.pair.endswith('loaded'))
    assert not findings
    job = replace(job, comparisons=comparisons)
    assert evaluate(job, fleet().coverage).rule_id == 9


def test_program_fallback_and_exact_argv():
    values = {'Label': 'example', 'ProgramArguments': ['/literal path/bin', '', 'two words', '$HOME', '~/bin']}
    parsed = parse_plist('/example.plist', plistlib.dumps(values))
    assert parsed.program == Known('/literal path/bin')
    assert parsed.arguments == Known(tuple(values['ProgramArguments']))
    assert parse_plist('/example.plist', plistlib.dumps(values | {'Program': '/different'})).program == Known('/different')
    assert isinstance(parse_plist('/example.plist', plistlib.dumps({'Program': '/only'})).arguments, Absent)
    job = fleet().jobs[0]
    for source in ('registry', 'plist', 'service'):
        job = with_field(job, source, 'arguments', parsed.arguments)
    assert not compare_job(job)[1]
    for changed in (('/different', *values['ProgramArguments'][1:]), tuple(reversed(values['ProgramArguments'])),
                    ('/literal', 'path/bin', '', 'two', 'words', '$HOME', '~/bin')):
        assert len(compare_job(with_field(job, 'service', 'arguments', Known(changed)))[1]) == 2
    report = replay(load_snapshot(FIXTURES / 'drift/argv-boundaries'), 'audit')
    assert report['exit_code'] == 0 and not report['jobs'][0]['drift']
    assert report['jobs'][0]['observations']['service']['data']['argv']['value'] == ['/alias', '', 'two words', '$LITERAL', '~/literal']


def test_calendar_canonicalization():
    alternatives = [{'Weekday': 7, 'Hour': 3}, {'Minute': 10}, {'Hour': 3, 'Weekday': 0}]
    assert normalize_calendar(alternatives) == normalize_calendar([{'Minute': 10}, {'Hour': 3, 'Weekday': 0}])
    assert normalize_calendar({'Hour': 3}) != normalize_calendar({'Hour': 3, 'Minute': 0})
    for invalid in ({}, [], {'Hour': True}, {'Hour': 24}, {'Other': 0}, ((('Hour', 3), ('Hour', 3)),)):
        assert isinstance(normalize_calendar(invalid), Unsupported)
    for name in ('calendar-equivalent', 'interval-and-calendar'):
        report = replay(load_snapshot(FIXTURES / 'drift' / name), 'audit')
        assert report['exit_code'] == 0
    evidence = report['jobs'][0]['observations']['service']['data']['schedule']
    assert evidence['interval_seconds']['value'] == 600 and len(evidence['calendar']['value']) == 2
    for name in ('com.pdw.docker-restart', 'snapshot-com.apple.talagent'):
        calendar = service(name).data.schedule.calendar
        assert isinstance(normalize_calendar(calendar.value), Known)
    assert len(service('snapshot-com.apple.talagent').data.schedule.calendar.value) == 2


def test_policy_presence_and_disk_defaults():
    disk = parse_plist('/example.plist', plistlib.dumps({'Label': 'example'}))
    assert disk.schedule.keep_alive == disk.schedule.run_at_load == Known(False)
    assert 'KeepAlive' not in disk.present_keys and 'RunAtLoad' not in disk.present_keys
    unsupported = parse_plist('/example.plist', plistlib.dumps({'KeepAlive': {'SuccessfulExit': False}}))
    assert unsupported.schedule.keep_alive == Unsupported((('SuccessfulExit', False),), 'KeepAlive mappings are unsupported')
    assert service('com.unattended.tick').data.schedule.run_at_load == Known(True)
    assert service('org.nixos.skhd').data.schedule.keep_alive == Known(True)
    assert isinstance(service('com.unattended.tick').data.schedule.keep_alive, Unknown)
    for name in ('policy-positive-tokens', 'policy-missing', 'policy-unsupported'):
        report = replay(load_snapshot(FIXTURES / 'drift' / name), 'audit')
        assert not report['jobs'][0]['drift']
        assert report['exit_code'] == (0 if name == 'policy-positive-tokens' else 2)
    schedule = report['jobs'][0]['observations']['service']['data']['schedule']
    assert schedule['keep_alive']['status'] == schedule['run_at_load']['status'] == 'unsupported'
    assert schedule['keep_alive']['raw'] == [['SuccessfulExit', 'false']]


def test_loaded_policy_never_inferred_from_disk():
    f = fleet('keepalive-no-exit')
    job = f.jobs[0]
    for source in ('registry', 'plist'):
        job = with_field(job, source, 'keep_alive', Known(True))
    job = with_field(job, 'service', 'keep_alive', Unknown('not reported'))
    comparisons, findings = compare_job(job)
    assert [c.status for c in comparisons if c.field == 'schedule.keep_alive'] == ['equal', 'unknown', 'unknown']
    assert not findings
    assert evaluate(replace(job, comparisons=comparisons), f.coverage).rule_id == 8


def test_drift_retained_with_running_and_exit_one():
    report = replay(load_snapshot(FIXTURES / 'drift/running-drift'), 'audit')
    job = report['jobs'][0]
    assert job['verdict'] == 'running' and job['rule_id'] == 6
    assert report['exit_code'] == 1 and len(job['drift']) == report['summary']['drift_findings'] == 2
    assert 'drift: program: registry=/bin/bash differs from loaded=/other' in render_text(report)
    assert json.loads(json.dumps(report)) == report


def test_unsupported_loaded_forms_retain_raw():
    obs = command('com.unattended.tick')
    for extra, field in [('\tRunAtLoad = maybe\n', 'run_at_load'),
                         ('\tevent triggers = {\n\t\tunknown = opaque\n\t}\n', 'calendar')]:
        changed = replace(obs, data=replace(obs.data, stdout=obs.data.stdout[:-2] + extra + '}\n'))
        parsed = parse_service(changed, fleet().jobs[0].identity)
        assert parsed.error is None
        value = getattr(parsed.data.schedule, field)
        assert isinstance(value, Unsupported) and value.raw


def test_failed_observation_cannot_supply_known_comparison():
    job = fleet().jobs[0]
    observations = dict(job.observations)
    observations['service'] = replace(observations['service'], error=Error('failure', 'untrusted'))
    comparisons, findings = compare_job(replace(job, observations=tuple(observations.items())))
    assert all(c.status == 'unknown' for c in comparisons if c.pair.endswith('loaded'))
    assert not findings


def test_drift_acceptance_offline_and_review_required(monkeypatch):
    import fleet_audit.acceptance as acceptance
    acceptance.main(['drift', '--offline'])
    load = acceptance.load_snapshot
    monkeypatch.setattr(acceptance, 'load_snapshot', lambda path: replace(load(path), expected={'reviewed': False}))
    with pytest.raises(AssertionError, match='unreviewed'):
        acceptance.main(['drift', '--offline'])
    assert not acceptance._OFFLINE


def test_drift_replay_never_reads_original_paths_commands_or_clock(monkeypatch):
    snapshot = load_snapshot(FIXTURES / 'drift/calendar-equivalent')
    def trap(*args, **kwargs): raise AssertionError('live access')
    class NoClock:
        now = staticmethod(trap)
    import fleet_audit.files as files
    import fleet_audit.collect as collect
    import fleet_audit.capture as capture
    for module in (files, collect, capture):
        monkeypatch.setattr(module, 'datetime', NoClock)
    monkeypatch.setattr(collect.LiveCommands, 'run', trap)
    monkeypatch.setattr(collect.time, 'time', trap)
    monkeypatch.setattr(collect.time, 'monotonic', trap)
    monkeypatch.setattr(files.os, 'open', trap)
    monkeypatch.setattr(builtins, 'open', trap)
    monkeypatch.setattr(Path, 'open', trap)
    assert replay(snapshot, 'audit')['exit_code'] == 0
