"""Offline assertions using only explicitly indexed fixture files."""
import argparse
import json
import os
import sys
from pathlib import Path

from .collect import collect_jobs
from .snapshot import load_snapshot, replay
from .launchctl_parse import parse_service
from .overrides import parse_overrides
from .models import CommandData, Identity, Known, Unknown

from .files import LIMIT, read_regular
from .models import Observation
from .registry import join_plists, load_registry
from .reports import build_report, render_json, render_text

FIXTURES = Path(__file__).absolute().parent.parent / "fixtures"
STAMP = "2026-10-16T00:00:00Z"
_OFFLINE = False


def offline_guard(event, args):
    if not _OFFLINE:
        return
    if event.startswith("subprocess.") or event in ("os.system", "os.posix_spawn", "os.fork", "os.exec"):
        raise AssertionError("offline acceptance forbids process creation")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.path.abspath(os.fsdecode(args[0])))
        if not path.is_relative_to(FIXTURES):
            raise AssertionError(f"offline acceptance forbids non-fixture access: {path}")


sys.addaudithook(offline_guard)


class FixtureFiles:
    def __init__(self, scenario="registry-valid"):
        self.paths = {str(p): p for p in sorted((FIXTURES / scenario).glob("*.md"))}
        self.plists = {"/fleet-fixtures/" + p.name: p for p in FIXTURES.glob("*.plist")}
        self.reads = []

    def discover(self, directory):
        return Observation("attempted", STAMP, ("fixture discovery", str(directory)), None, None, tuple(self.paths))

    def read_regular(self, path, limit=LIMIT):
        self.reads.append(path)
        indexed = self.paths | self.plists
        if path not in indexed:
            raise AssertionError(f"unindexed fixture read: {path}")
        result = read_regular(str(indexed[path]), limit)
        return Observation("attempted", STAMP, ("fixture read", path), None, result.error, result.data)


def prove_registry():
    files = FixtureFiles()
    result = join_plists(load_registry(FIXTURES / "registry-valid", 501, files), files)
    assert not result.errors, result.errors
    assert len(result.jobs) == 1
    report = build_report(result, "gui/501")
    assert report["exit_code"] == 0
    assert "com.unattended.tick declared:" in render_text(report)
    assert json.loads(render_json(report))["jobs"][0]["observations"]["service"]["status"] == "not_requested"
    for name, suffix in (("registry-schema-errors", "unknown field"),
                         ("registry-duplicate-project", "duplicate project example"),
                         ("registry-duplicate-job", "duplicate job id tick"),
                         ("registry-duplicate-identity", "duplicate identity local/gui/501/com.unattended.tick"),
                         ("registry-label-mismatch", "plist Label com.unattended.tick differs from different.label"),
                         ("registry-path-errors", "expected absolute normalized path")):
        files = FixtureFiles(name)
        result = join_plists(load_registry(FIXTURES / name, 501, files), files)
        assert any(e.message.endswith(suffix) for e in result.errors), (name, result.errors)
        assert build_report(result, "gui/501")["exit_code"] == 3
    for name in ("com.google.keystone.agent", "com.google.keystone.xpcservice"):
        files = FixtureFiles()
        path = next(iter(files.paths))
        content = files.read_regular(path).data.replace(b"com.unattended.tick.plist", (name + ".plist").encode())
        from .registry import parse_frontmatter
        result = join_plists(parse_frontmatter(path, content, 501), files)
        assert result.errors[0].message.endswith("plist Label missing")



def prove_observer():
    snapshot = load_snapshot(FIXTURES / 'host')
    assert snapshot.expected.get('reviewed') is True, 'unreviewed expected placeholder'
    report = replay(snapshot, 'observer')
    assert report['exit_code'] == 2 and len(report['jobs']) == snapshot.expected['job_count']
    for job in report['jobs']:
        assert job['verdict']['name'] == 'cannot_determine'
        assert job['verdict']['rule_id'] == snapshot.expected['rule_id']
        assert snapshot.expected['reason_contains'] in job['verdict']['reason']
    from .snapshot import SnapshotCommands
    fleet = collect_jobs((), 'gui/501', SnapshotCommands(snapshot))
    assert not fleet.jobs and 'rc=1' in fleet.coverage.issues[0]

    def command(name):
        obj = json.loads((FIXTURES / 'observer' / (name + '.json')).read_text())
        record = obj['record']
        if name.startswith('audit-'):
            record = record['collection']
        elif isinstance(record.get('command'), dict):
            record = record['command']
        argv = tuple(record['command'])
        stamp = obj['provenance']['captured_at']
        stamp = stamp.replace('+00:00', 'Z') if 'T' in stamp else None
        return Observation('attempted', stamp, argv, record['returncode'], None,
                           CommandData(argv, record['stdout'], record['stderr'], False, False, None))

    tick = Identity('local', 'gui/501', 'com.unattended.tick')
    assert parse_service(command('com.unattended.tick'), tick).data.runs == Known(28)
    assert parse_service(command('audit-com.unattended.tick'), tick).data.runs == Known(29)
    skhd = parse_service(command('org.nixos.skhd'), Identity('local', 'gui/501', 'org.nixos.skhd'))
    assert skhd.data.last_exit_code == Known(78) and skhd.data.last_exit_text == Known('EX_CONFIG')
    absent = parse_service(command('com.koekeishiya.yabai'), Identity('local', 'gui/501', 'com.koekeishiya.yabai'))
    assert absent.data.loaded == Known(False)
    apple = 'com.apple.networkserviceproxy'
    assert isinstance(parse_service(command('snapshot-' + apple), Identity('local', 'gui/501', apple)).data.loaded, Unknown)
    overrides = parse_overrides(command('print-disabled'))
    assert overrides.data.complete and len(overrides.data.entries) == 15
    assert sum(disabled for label, disabled in overrides.data.entries if label.startswith('com.apple.')) == 5

def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline registry acceptance")
    parser.add_argument("stage", choices=["registry", "observer"])
    parser.add_argument("--offline", action="store_true", required=True)
    args = parser.parse_args(argv)
    global _OFFLINE
    _OFFLINE = True
    try:
        (prove_registry if args.stage == "registry" else prove_observer)()
    finally:
        _OFFLINE = False
    print("OK " + args.stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
