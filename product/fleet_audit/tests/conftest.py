"""Fail closed on process creation or access to the host's Library."""
import os
import sys
from pathlib import Path

import pytest

from fleet_audit.acceptance import FIXTURES

_GUARD = False


def guard(event, args):
    if not _GUARD:
        return
    if event.startswith("subprocess.") or event in ("os.system", "os.posix_spawn", "os.fork", "os.exec"):
        raise AssertionError("live process use forbidden")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = os.path.abspath(os.fsdecode(args[0]))
        if path == "/Users/byron/Library" or path.startswith("/Users/byron/Library/"):
            raise AssertionError("live Library access forbidden")


sys.addaudithook(guard)


@pytest.fixture(autouse=True)
def forbid_live():
    global _GUARD
    _GUARD = True
    try:
        yield
    finally:
        _GUARD = False


@pytest.fixture
def materialized(tmp_path):
    for name in ("registry-valid", "registry-schema-errors"):
        directory = tmp_path / name
        directory.mkdir()
        for source in (FIXTURES / name).glob("*.md"):
            (directory / source.name).write_text(source.read_text().replace("/fleet-fixtures/", str(tmp_path) + "/"))
    for source in FIXTURES.glob("*.plist"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    return tmp_path
