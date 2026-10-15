"""Decision table precedence and observation-relative freshness."""
from dataclasses import replace

import pytest

from fleet_audit.acceptance import FIXTURES
from fleet_audit.collect import collect_jobs
from fleet_audit.models import Absent, Coverage, Error, Known, Unknown, Unsupported
from fleet_audit.reports import audit_fleet, build_report, exit_code
from fleet_audit.snapshot import SnapshotCommands, SnapshotFiles, load_snapshot, registry_from, replay
from fleet_audit.registry import join_plists
from fleet_audit.verdicts import RULES, evaluate

ROOT = FIXTURES / 'verdicts'


def scenario(name='completed-no-result'):
    return load_snapshot(ROOT / name)


def fleet(name='completed-no-result'):
    snap = scenario(name)
    files = SnapshotFiles(snap)
    jobs = join_plists(registry_from(snap), files).jobs
    return audit_fleet(collect_jobs(jobs, snap.manifest.domain, SnapshotCommands(snap)), files)


def check_age(age, verdict):
    report = replay(scenario('age-boundaries-' + str(age)), 'audit')
    assert report['jobs'][0]['verdict'] == verdict


def test_age_minus_one(): check_age(-1, 'cannot_determine')
def test_age_at_m(): check_age(1200, 'healthy_idle')
def test_age_at_m_plus_one(): check_age(1201, 'cannot_determine')
def test_age_at_m_plus_g(): check_age(3000, 'cannot_determine')
def test_age_at_m_plus_g_plus_one(): check_age(3001, 'late')


def changed_service(job, **fields):
    observations = dict(job.observations)
    obs = observations['service']
    observations['service'] = replace(obs, data=replace(obs.data, **fields))
    return replace(job, observations=tuple(observations.items()))


def test_fourteen_rule_order_and_first_match():
    assert tuple(rule.id for rule in RULES) == tuple(range(1, 15))
    won = set()
    for path in ROOT.iterdir():
        if not (path / 'manifest.json').exists(): continue
        snap = load_snapshot(path)
        report = replay(snap, 'audit')
        job = report['jobs'][0]
        assert (job['rule_id'], job['verdict'], report['exit_code']) == (snap.expected['rule_id'], snap.expected['verdict'], snap.expected['exit_code'])
        won.add(job['rule_id'])
    f = fleet(); job = f.jobs[0]
    assert evaluate(job, replace(f.coverage, complete=False, issues=('global failure',))).rule_id == 1
    assert evaluate(replace(job, disabled=Unknown('unknown')), f.coverage).rule_id == 2
    assert evaluate(changed_service(job, last_exit_code=Known(7)), f.coverage).rule_id == 7
    won.update((1, 2, 7))
    assert won == set(range(1, 15))
    running = fleet('running-old-exit').jobs[0]
    assert evaluate(replace(running, disabled=replace(running.disabled, value=Known(True))), f.coverage).rule_id == 3


@pytest.mark.parametrize('unknown', [Unknown('missing'), Unsupported('raw', 'unsupported')])
def test_unknown_never_matches_predicate(unknown):
    with pytest.raises(TypeError): bool(unknown)
    with pytest.raises(TypeError): bool(Known(False))
    with pytest.raises(TypeError): bool(Absent('absent'))
    f = fleet(); job = f.jobs[0]
    for field in ('state', 'pid', 'last_exit_code'):
        assert evaluate(changed_service(job, **{field: unknown}), f.coverage).name == 'cannot_determine'
    assert evaluate(replace(job, loaded=unknown), f.coverage).rule_id == 1
    assert evaluate(replace(job, disabled=unknown), f.coverage).rule_id == 2
    spawn = changed_service(job, state=Known('spawn scheduled'), last_exit_code=unknown)
    observations = dict(spawn.observations)
    for name in ('service', 'plist'):
        obs = observations[name]
        observations[name] = replace(obs, data=replace(obs.data, schedule=replace(obs.data.schedule, keep_alive=unknown)))
    assert evaluate(replace(spawn, observations=tuple(observations.items())), f.coverage).name == 'cannot_determine'


@pytest.mark.parametrize('source', ['global', 'service', 'override', 'parse', 'file'])
def test_collection_error_never_healthy_idle(source):
    f = fleet(); job = f.jobs[0]; coverage = f.coverage
    if source == 'global':
        coverage = replace(coverage, complete=False, issues=('failed inventory',))
    else:
        name = {'parse': 'plist', 'file': 'output'}.get(source, source)
        observations = dict(job.observations)
        observations[name] = replace(observations[name], error=Error('failure', 'failed'))
        job = replace(job, observations=tuple(observations.items()))
    assert evaluate(job, coverage).name == 'cannot_determine'


def test_receipt_timestamp_not_log_or_mtime():
    f = fleet('stale-failed-receipt'); job = f.jobs[0]
    assert dict(job.observations)['output'].data.age_seconds == 0
    assert job.verdict.name == 'late'
    f = fleet(); job = f.jobs[0]
    observations = dict(job.observations)
    obs = observations['output']
    observations['output'] = replace(obs, data=replace(obs.data, age_seconds=999999))
    assert evaluate(replace(job, observations=tuple(observations.items())), f.coverage).name == 'healthy_idle'
    del observations['receipt']
    assert evaluate(replace(job, observations=tuple(observations.items())), f.coverage).name == 'cannot_determine'


def test_audit_exit_precedence():
    healthy = replay(scenario(), 'audit')
    assert healthy['exit_code'] == 0
    uncertain = replay(scenario('running-ancillary-error'), 'audit')
    failing = replay(scenario('failed-nonzero-rc'), 'audit')
    mixed = healthy | {'jobs': healthy['jobs'] + uncertain['jobs'] + failing['jobs']}
    assert exit_code(mixed) == 1
    assert exit_code(mixed | {'summary': {'invalid_input_errors': 1}}) == 3
    for name, expected in [('expected-disabled', 0), ('unexpected-disabled', 1), ('running-ancillary-error', 2)]:
        assert replay(scenario(name), 'audit')['exit_code'] == expected
    f = fleet()
    assert build_report('audit', replace(f, jobs=(), coverage=Coverage(False, ('empty inventory',), ())))['exit_code'] == 2
    assert build_report('audit', replace(f, coverage=replace(f.coverage, complete=False, issues=('incomplete',))))['exit_code'] == 2


def test_declaration_budgets_and_no_contract():
    f = fleet('age-boundaries-1200'); job = f.jobs[0]
    contract = replace(job.registry.output, max_age_seconds=10)
    job = replace(job, registry=replace(job.registry, output=contract, grace_seconds=20))
    assert evaluate(job, f.coverage).name == 'late'
    assert evaluate(replace(job, registry=replace(job.registry, output=None)), f.coverage).rule_id == 10


def test_running_invalid_receipt_retains_uncertainty():
    snap = scenario('running-old-exit')
    bad = scenario('invalid-producer-fields')
    report = replay(replace(snap, receipts=bad.receipts), 'audit')
    assert report['jobs'][0]['verdict'] == 'running'
    assert report['exit_code'] == 2
