"""Bounded file access; adapters keep logical paths separate from storage."""
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from .models import Error, Observation

LIMIT = 1024 * 1024


def observed(data, command, error=None):
    return Observation("attempted", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                       tuple(command), None, error, data)


def read_regular(path: str, limit: int = LIMIT) -> Observation[bytes]:
    try:
        # Nonblocking open prevents a FIFO from hanging before the descriptor check.
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            meta = os.fstat(fd)
            if not stat.S_ISREG(meta.st_mode):
                return observed(None, ("read_regular", path), Error("nonregular", "not a regular file"))
            if meta.st_size > limit:
                return observed(None, ("read_regular", path), Error("too_large", f"file exceeds {limit} bytes"))
            data = bytearray()
            while len(data) <= limit:
                chunk = os.read(fd, min(65536, limit + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            if len(data) > limit:
                return observed(None, ("read_regular", path), Error("too_large", f"file exceeds {limit} bytes"))
            return observed(bytes(data), ("read_regular", path))
        finally:
            os.close(fd)
    except OSError as exc:
        return observed(None, ("read_regular", path), Error("missing" if isinstance(exc, FileNotFoundError)
                                                         else "unreadable", str(exc)))


class FileSource(Protocol):
    def read_regular(self, path: str, limit: int = LIMIT) -> Observation[bytes]: ...
    def discover(self, directory: Path) -> Observation[tuple[str, ...]]: ...


class LocalFiles:
    read_regular = staticmethod(read_regular)

    def discover(self, directory: Path) -> Observation[tuple[str, ...]]:
        paths = []
        try:
            if directory.is_symlink() or not directory.is_dir():
                raise OSError("expected directory, not directory symlink")
            def fail(exc):
                raise exc
            for root, dirs, names in os.walk(directory, followlinks=False, onerror=fail):
                dirs[:] = sorted(d for d in dirs if not Path(root, d).is_symlink())
                for name in sorted(names):
                    if name.endswith(".md"):
                        paths.append(str(Path(root, name)))
                        if len(paths) > 1000:
                            raise OSError("discovery exceeds 1000 files")
            return observed(tuple(sorted(paths)), ("discover", str(directory)))
        except OSError as exc:
            return observed(None, ("discover", str(directory)), Error("discovery", str(exc)))
