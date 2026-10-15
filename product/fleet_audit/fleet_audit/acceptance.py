"""Offline assertions using only explicitly indexed fixture files."""
import argparse
import json
import os
import sys
from pathlib import Path

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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline registry acceptance")
    parser.add_argument("stage", choices=["registry"])
    parser.add_argument("--offline", action="store_true", required=True)
    parser.parse_args(argv)
    global _OFFLINE
    _OFFLINE = True
    try:
        prove_registry()
    finally:
        _OFFLINE = False
    print("OK registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
