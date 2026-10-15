"""Scan contracts, transport isolation and public reports."""
import builtins
import json
import plistlib
from dataclasses import replace
from pathlib import Path

import pytest

from fleet_audit import acceptance, cli
from fleet_audit.acceptance import FIXTURES, STAMP
from fleet_audit.capture import capture_snapshot
from fleet_audit.models import Error, Observation
from fleet_audit.reports import exit_code, render_json, render_text
from fleet_audit.scan import scan_fleet, scan_plists
from fleet_audit.snapshot import SnapshotCommands, SnapshotFiles, load_snapshot, replay
from test_snapshot import materialize

ROOT = FIXTURES / 'fleet'


def snapshot(name='real-twelve'):
    return load_snapshot(ROOT / name)


def report(name='real-twelve'):
    return replay(snapshot(name), 'scan')


def test_scan_twelve_rows_and_both_nix_failures():
    snap = snapshot()
    class Commands(SnapshotCommands):
        def run(self, argv):
            assert 'keystone' not in argv[-1]
            return super().run(argv)
    files = SnapshotFiles(snap)
    fleet = scan_fleet(scan_plists('/ignored', files, 'gui/501'), files, Commands(snap))
    assert len(fleet.jobs) == 12
    rows = report()['jobs']
    assert sum(j['identity']['label'] is None for j in rows) == 2
    for job in rows:
        assert job['registry'] is None and job['project'] is None
        if job['identity']['label'] in ('org.nixos.skhd', 'org.nixos.yabai'):
            assert job['verdict'] == 'failing' and '78 EX_CONFIG' in job['reason']
        if job['identity']['label'] is None:
            assert job['observations']['service']['status'] == 'not_applicable'
    assert report()['exit_code'] == 1
    assert rows[-1]['observations']['service']['observed_at'] is None


def test_scan_label_filter_and_unreadable_filename_fallback():
    contents = {'ordinary.plist': {'Label': 'com.apple.hidden'}, 'com.apple.keep.plist': {'Label': 'third.party'},
                'com.apple.no-label.plist': {}, 'com.apple.denied.plist': None,
                'com.appleish.plist': None, 'no-label.plist': {}, 'bad-label.plist': {'Label': 'bad label'}}
    class Files:
        def discover_plists(self, directory):
            return Observation('attempted', STAMP, (), None, None, tuple('/scan/'+n for n in contents))
        def read_regular(self, path, limit):
            value = contents[Path(path).name]
            return Observation('attempted', STAMP, (), None, Error('unreadable', 'denied') if value is None else None,
                               plistlib.dumps(value) if value is not None else None)
    fleet = scan_plists('/scan', Files(), 'gui/501')
    assert [Path(j.plist_path).name for j in fleet.jobs] == ['bad-label.plist', 'com.apple.keep.plist', 'com.appleish.plist', 'no-label.plist']
    assert [j.identity.label for j in fleet.jobs] == [None, 'third.party', None, None]


def test_scan_no_freshness_and_deduplicated_stats():
    snap = snapshot()
    class Files(SnapshotFiles):
        calls = []
        def stat_output(self, path):
            self.calls.append(path)
            return super().stat_output(path)
        def read_tail(self, *args): raise AssertionError('scan read a receipt')
        def read_regular(self, path, limit):
            assert path in snap.plists
            return super().read_regular(path, limit)
    files = Files(snap)
    fleet = scan_fleet(scan_plists('/scan', files, 'gui/501'), files, SnapshotCommands(snap))
    assert len(files.calls) == len(set(files.calls)) == len(snap.stats)
    tick = next(j for j in fleet.jobs if j.identity.label == 'com.unattended.tick')
    assert tick.verdict.reason == 'no freshness contract declared'
    assert all(j.verdict.name not in ('late', 'healthy_idle') for j in fleet.jobs)


def test_scan_running_old_ollama_log():
    job = next(j for j in report()['jobs'] if j['identity']['label'] == 'homebrew.mxcl.ollama')
    assert job['verdict'] == 'running' and job['reason'].endswith('useful work not established')
    log = job['observations']['output:0']['data']
    assert log['age_seconds'] > 7 * 86400 and log['size'] is None


def test_scan_disabled_loaded_disabled_and_absent():
    for name, verdict, code in [('scan-disabled', 'disabled', 2), ('scan-loaded-disabled', 'loaded_disabled', 1),
                               ('scan-service-absent', 'cannot_determine', 2)]:
        result = report(name)
        assert (result['jobs'][0]['verdict'], result['exit_code']) == (verdict, code)
    assert report('scan-service-absent')['jobs'][0]['reason'] == 'plist on disk, service absent; not declared'
    assert 'expected_enabled=unknown' in report('scan-disabled')['jobs'][0]['reason']


def test_reports_schema_stability_and_provenance():
    result = report('report-unattempted')
    assert set(result) == {'schema_version','command','domain','observed_at','jobs','issues','summary','exit_code'}
    assert json.loads(render_json(result)) == result
    job = result['jobs'][0]
    assert job['observations']['service']['data']['argv']['value'] == ['/bin/echo', '', 'two words']
    assert job['observations']['receipt'] == {'status':'not_applicable','observed_at':None,'source_command':[],
                                             'return_code':None,'error':None,'data':None}
    assert job['observations']['service']['observed_at'].endswith('Z')
    assert all(ref in job['observations'] for ref in job['evidence_refs'])
    assert result['summary'] == {'jobs':1,'verdicts':{'cannot_determine':1},'drift_findings':0,
                                  'uncertainties':1,'invalid_input_errors':0}
    snap = snapshot()
    assert render_json(replay(replace(snap, plists=dict(reversed(list(snap.plists.items())))), 'scan')) == render_json(report())
    escaped = report('report-escaping')
    escaped['jobs'][0]['reason'] += '\n\t"back\\control\x00'
    text = render_text(escaped)
    assert len(text.splitlines()) == 2
    assert '\\n\\t\\"back\\\\control\\u0000' in text
    assert text.startswith('scan//scan/quote\\"slash\\\\.plist gui/501/no_label cannot_determine:')


def test_reports_never_emit_environment_values(tmp_path):
    snap = snapshot('report-environment-redaction')
    secret = 'sentinel-private-value'
    class Files(SnapshotFiles):
        def read_regular(self, path, limit):
            obs = super().read_regular(path, limit)
            value = plistlib.loads(obs.data)
            value['EnvironmentVariables'] = {'SYNTHETIC_KEY': secret}
            return replace(obs, data=plistlib.dumps(value))
    captured = capture_snapshot('/scan','gui/501','scan',files=Files(snap),commands=SnapshotCommands(snap),
                                clock=lambda: STAMP,macos_label='synthetic')
    archive = materialize(captured, tmp_path)
    result = replay(load_snapshot(tmp_path), 'scan')
    assert secret.encode() not in archive
    assert secret not in render_text(result) + render_json(result)
    assert result['jobs'][0]['observations']['plist']['data']['environment_keys']['value'] == ['SYNTHETIC_KEY']
    assert captured.expected == {'reviewed':False}
    assert not captured.runbooks and not captured.receipts


def test_cli_help_domains_and_validation_before_collection(monkeypatch, capsys, tmp_path):
    from fleet_audit.collect import LiveCommands
    def trap(*args): raise AssertionError('live collection')
    monkeypatch.setattr(LiveCommands, 'run', trap)
    with pytest.raises(SystemExit) as exc: cli.main(['--help'])
    assert exc.value.code == 0 and 'scan' in capsys.readouterr().out
    for args in (['--unknown'], ['scan','--unknown'], ['scan','/not-a-runbook']):
        with pytest.raises(SystemExit) as exc: cli.main(args)
        assert exc.value.code == 3
    assert cli.main(['scan','--domain','system']) == 3
    assert cli.main(['scan','--fixture',str(ROOT/'scan-disabled'),'--domain','gui/999']) == 3
    assert cli.main(['scan','--fixture',str(tmp_path)]) == 3
    assert cli.main(['audit',str(tmp_path)]) == 3
    assert cli.main(['scan','--fixture',str(ROOT/'scan-loaded-disabled'),'--json']) == 1
    assert cli.main(['declared',str(tmp_path),'--json']) == 3


def test_empty_or_mixed_fleet_exit_precedence():
    assert report('scan-empty-coverage')['exit_code'] == 2
    mixed = report('report-mixed-exits')
    assert mixed['exit_code'] == 1
    mixed['issues'] = [{'exit_code':3,'message':'invalid input'}]
    assert exit_code(mixed) == 3
    uncertain = report('scan-disabled')
    uncertain['issues'] = [{'exit_code':1,'message':'definite finding'}]
    assert exit_code(uncertain) == 1
    healthy = replay(load_snapshot(FIXTURES/'verdicts/completed-no-result'),'audit')
    assert exit_code(healthy) == 0
    healthy['issues'] = ['incomplete coverage']
    assert exit_code(healthy) == 2
    healthy['summary']['invalid_input_errors'] = 1
    assert exit_code(healthy) == 3


def test_scan_snapshot_missing_entries_and_offline_guard(tmp_path, monkeypatch):
    snap = snapshot()
    def trap(*args, **kwargs): raise AssertionError('live access')
    from fleet_audit import files, collect, capture
    class NoClock:
        now = staticmethod(trap)
    for module in (files, collect, capture): monkeypatch.setattr(module, 'datetime', NoClock)
    monkeypatch.setattr(collect.LiveCommands, 'run', trap)
    monkeypatch.setattr(collect.time, 'time', trap)
    monkeypatch.setattr(collect.time, 'monotonic', trap)
    monkeypatch.setattr(builtins, 'open', trap)
    monkeypatch.setattr(Path, 'open', trap)
    monkeypatch.setattr(files.os, 'open', trap)
    assert replay(snap, 'scan')['exit_code'] == 1
    with pytest.raises(ValueError, match='missing command'): replay(replace(snap,commands={}), 'scan')
    with pytest.raises(ValueError, match='missing stat'): replay(replace(snap,stats={}), 'scan')


def test_fleet_acceptance_offline_and_review_required(monkeypatch):
    acceptance.main(['fleet','--offline'])
    load = acceptance.load_snapshot
    monkeypatch.setattr(acceptance,'load_snapshot',lambda path: replace(load(path),expected={'reviewed':False}))
    with pytest.raises(AssertionError, match='unreviewed'): acceptance.main(['fleet','--offline'])
    assert not acceptance._OFFLINE


def test_scan_discovery_is_bounded_and_nonrecursive(tmp_path):
    from fleet_audit.files import LocalFiles
    files = LocalFiles()
    (tmp_path / 'nested').mkdir()
    (tmp_path / 'nested' / 'hidden.plist').write_bytes(b'')
    (tmp_path / 'b.plist').write_bytes(b'')
    (tmp_path / 'a.plist').write_bytes(b'')
    assert files.discover_plists(tmp_path).data == (str(tmp_path/'a.plist'), str(tmp_path/'b.plist'))
    for i in range(999):
        (tmp_path / f'{i}.plist').write_bytes(b'')
    obs = files.discover_plists(tmp_path)
    assert obs.data is None and obs.error.message == 'discovery exceeds 1000 files'
    assert files.discover_plists(tmp_path/'missing').error is not None


def test_audit_observation_references_and_utc_receipt():
    from fleet_audit.receipts import normalize_tick
    result = replay(load_snapshot(FIXTURES/'verdicts/completed-no-result'), 'audit')
    job = result['jobs'][0]
    for ref in job['evidence_refs']:
        assert ref in job['observations']
    for comparison in job['comparisons']:
        assert all(ref in job['observations'] for ref in comparison['evidence_refs'])
    registry = job['observations']['registry']
    assert registry['data'] == job['registry'] and registry['status'] == 'attempted'
    receipt = normalize_tick({'ts':'2026-10-16T13:00:00+13:00',
                              'supervisor':{'ran':False,'rc':None,'error':None}})
    assert receipt.ts == '2026-10-16T00:00:00Z'
    assert receipt.last_object['ts'] == receipt.ts


def test_scan_plist_field_errors_are_uncertain():
    from fleet_audit.reports import build_report
    snap = snapshot()
    path = '/Users/byron/Library/LaunchAgents/homebrew.mxcl.ollama.plist'
    class Files(SnapshotFiles):
        def discover_plists(self, directory):
            return replace(super().discover_plists(directory), data=(path,))
        def read_regular(self, path, limit):
            obs = super().read_regular(path, limit)
            value = plistlib.loads(obs.data)
            value['StandardOutPath'] = 42
            return replace(obs, data=plistlib.dumps(value))
    files = Files(snap)
    fleet = scan_fleet(scan_plists('/scan', files, 'gui/501'), files, SnapshotCommands(snap))
    result = build_report('scan', fleet)
    job = result['jobs'][0]
    assert job['verdict'] == 'running'
    assert 'plist: StandardOutPath: invalid value' in job['uncertainties']
    assert result['summary']['uncertainties'] == 1
    assert result['exit_code'] == 2


def test_receipt_timestamp_overflow_is_invalid():
    from fleet_audit.receipts import normalize_tick
    value = {'ts': '0001-01-01T00:00:00+01:00',
             'supervisor': {'ran': False, 'rc': None, 'error': None}}
    receipt = normalize_tick(value)
    assert receipt.ts is None
    assert receipt.parsing_errors == ('invalid receipt ts',)
    assert receipt == normalize_tick(value | {'ts': 'invalid'})


def test_scan_unsupported_plist_values_are_uncertain():
    from fleet_audit.reports import build_report
    snap = snapshot()
    path = '/Users/byron/Library/LaunchAgents/homebrew.mxcl.ollama.plist'
    class Files(SnapshotFiles):
        def discover_plists(self, directory):
            return replace(super().discover_plists(directory), data=(path,))
        def read_regular(self, path, limit):
            obs = super().read_regular(path, limit)
            value = plistlib.loads(obs.data)
            value['KeepAlive'] = {'SuccessfulExit': False}
            return replace(obs, data=plistlib.dumps(value))
    files = Files(snap)
    fleet = scan_fleet(scan_plists('/scan', files, 'gui/501'), files, SnapshotCommands(snap))
    result = build_report('scan', fleet)
    uncertainty = 'plist: KeepAlive: KeepAlive mappings are unsupported'
    assert result['jobs'][0]['verdict'] == 'running'
    assert result['jobs'][0]['uncertainties'] == [uncertainty]
    assert 'uncertainty: ' + uncertainty in render_text(result)
    assert result['summary']['uncertainties'] == 1
    assert result['exit_code'] == 2


def test_output_mtime_out_of_range_is_uncertain(monkeypatch):
    import os
    import stat
    from fleet_audit.files import stat_output
    for mtime in (253402300800, 1e20):
        info = os.stat_result((stat.S_IFREG | 0o600, 1, 1, 1, 501, 20, 42, 0, mtime, 0))
        with monkeypatch.context() as scoped:
            scoped.setattr('fleet_audit.files.os.stat', lambda path: info)
            observation = stat_output('/synthetic/output.log')
        assert observation.error.code == 'stat'
        assert observation.data.stat_error == observation.error
        assert observation.data.exists is None
        assert observation.data.mtime is None
        assert observation.data.age_seconds is None


def test_output_mtime_out_of_range_round_trips_snapshot(monkeypatch):
    import os
    import stat
    from fleet_audit.files import stat_output
    from fleet_audit.reports import serialize
    from fleet_audit.snapshot import output_observation
    path = '/synthetic/output.log'
    for mtime in (253402300800, 1e20):
        info = os.stat_result((stat.S_IFREG | 0o600, 1, 1, 1, 501, 20, 42, 0, mtime, 0))
        with monkeypatch.context() as scoped:
            scoped.setattr('fleet_audit.files.os.stat', lambda path: info)
            observation = stat_output(path)
        assert output_observation(serialize(observation), path) == observation
