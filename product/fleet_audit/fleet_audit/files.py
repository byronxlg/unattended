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
    def discover_plists(self, directory: Path) -> Observation[tuple[str, ...]]: ...
    def stat_output(self, path: str) -> Observation: ...
    def read_tail(self, path: str, limit: int = 65536) -> Observation: ...


class LocalFiles:
    read_regular = staticmethod(read_regular)

    def discover_plists(self, directory):
        try:
            directory = Path(directory)
            if directory.is_symlink() or not directory.is_dir():
                raise OSError('expected LaunchAgents directory')
            paths = []
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.name.endswith('.plist'):
                        paths.append(entry.path)
                        if len(paths) > 1000:
                            raise OSError('discovery exceeds 1000 files')
            return observed(tuple(sorted(paths)), ('discover_plists', str(directory)))
        except OSError as exc:
            return observed(None, ('discover_plists', str(directory)), Error('discovery', str(exc)))

    def stat_output(self, path):
        return stat_output(path)

    def read_tail(self, path, limit=65536):
        return tail_regular(path, limit)

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


def metadata(info):
    from .models import FileMetadata
    return FileMetadata(info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
                        info.st_ctime_ns, stat.S_ISREG(info.st_mode))


def stat_output(path):
    from .models import OutputData
    try:
        info = os.stat(path)
        if not stat.S_ISREG(info.st_mode):
            raise OSError('not a regular file')
        stamp = datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat().replace('+00:00', 'Z')
        return observed(OutputData(path, True, info.st_size, stamp, None, None), ('stat', path))
    except OSError as exc:
        error = Error('missing' if isinstance(exc, FileNotFoundError) else 'stat', str(exc))
        return observed(OutputData(path, False if isinstance(exc, FileNotFoundError) else None,
                                   None, None, None, error), ('stat', path), error)


def tail_regular(path, limit=65536):
    from .models import TailData
    if type(limit) is not int or not 0 < limit <= 65536:
        raise ValueError('invalid tail limit')
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            before = metadata(os.fstat(fd))
            if not before.regular:
                return observed(None, ('read_tail', path), Error('nonregular', 'not a regular file'))
            offset = max(0, before.size - limit)
            os.lseek(fd, offset, os.SEEK_SET)
            retained = bytearray()
            while len(retained) < min(limit, before.size):
                chunk = os.read(fd, min(limit, before.size) - len(retained))
                if not chunk:
                    break
                retained.extend(chunk)
            after = metadata(os.fstat(fd))
            path_after = metadata(os.stat(path))
            changed = before != after or after != path_after or len(retained) != before.size - offset
            data = TailData(path, before, after, path_after, offset, len(retained), offset == 0,
                            bytes(retained), changed)
            return observed(data, ('read_tail', path), Error('changed', 'receipt changed during read') if changed else None)
        finally:
            os.close(fd)
    except OSError as exc:
        return observed(None, ('read_tail', path), Error('tail_io', str(exc)))
