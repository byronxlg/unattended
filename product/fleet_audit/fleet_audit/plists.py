"""Typed plist fields, preserving presence without retaining environment values."""
import plistlib
from dataclasses import replace
from xml.parsers.expat import ExpatError

from .files import LIMIT
from .models import Absent, Error, Known, PlistData, Schedule, Unknown, Unsupported


def frozen(value):
    if isinstance(value, dict):
        return tuple((k, frozen(v)) for k, v in sorted(value.items()))
    if isinstance(value, list):
        return tuple(frozen(v) for v in value)
    return value


def parse_plist(path: str, content: bytes) -> PlistData:
    from .registry import calendar_error, controls, freeze_calendar, positive, valid_label, valid_path

    obj = plistlib.loads(content)
    if not isinstance(obj, dict):
        raise ValueError("expected mapping")
    errors = []

    def field(key, predicate, transform=lambda v: v, default=None):
        if key not in obj:
            return Absent("key absent") if default is None else Known(default)
        if not predicate(obj[key]):
            errors.append(Error("plist_field", f"{key}: invalid value"))
            return Unknown("invalid value")
        return Known(transform(obj[key]))

    arguments = field("ProgramArguments", lambda v: isinstance(v, list) and bool(v)
                      and all(isinstance(a, str) and not controls(a) for a in v), tuple)
    program = field("Program", valid_path)
    if "Program" not in obj and isinstance(arguments, Known):
        program = Known(arguments.value[0])
    if isinstance(obj.get("KeepAlive"), dict):
        keep_alive = Unsupported(frozen(obj["KeepAlive"]), "KeepAlive mappings are unsupported")
    else:
        keep_alive = field("KeepAlive", lambda v: type(v) is bool, default=False)
    environment = field("EnvironmentVariables", lambda v: isinstance(v, dict)
                        and all(isinstance(k, str) and isinstance(val, str) for k, val in v.items()),
                        lambda v: tuple(sorted(v)))
    return PlistData(path, tuple(sorted(obj)), field("Label", valid_label), program, arguments,
                     field("WorkingDirectory", valid_path),
                     Schedule(field("StartInterval", positive),
                              field("StartCalendarInterval", lambda v: calendar_error(v) is None, freeze_calendar),
                              Absent("not a plist field"), keep_alive,
                              field("RunAtLoad", lambda v: type(v) is bool, default=False)),
                     field("Disabled", lambda v: type(v) is bool, default=False),
                     field("StandardOutPath", valid_path), field("StandardErrorPath", valid_path),
                     environment, tuple(errors))


def observe_plist(path, files):
    content = files.read_regular(path, LIMIT)
    if content.error is not None:
        return replace(content, source_command=("plistlib.load", path))
    try:
        data = parse_plist(path, content.data)
        return replace(content, data=data, source_command=("plistlib.load", path))
    except (ValueError, TypeError, OverflowError, ExpatError, plistlib.InvalidFileException) as exc:
        # Parser diagnostics can quote input; retain the class, never raw plist values.
        return replace(content, data=None, source_command=("plistlib.load", path),
                       error=Error("invalid_plist", f"{type(exc).__name__}: malformed plist"))
