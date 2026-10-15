"""Complete override maps take precedence over disk defaults."""
from dataclasses import replace

from .launchctl_parse import command_error, tree
from .models import DisabledState, Error, Known, OverrideData, Unknown
from .registry import valid_label


def parse_overrides(command):
    error, entries = command_error(command), {}
    if error is None:
        try:
            root = tree(command.data.stdout)
            if len(root) != 1 or root[0][0] != 'disabled services' or not isinstance(root[0][1], list):
                raise ValueError('expected complete disabled services block')
            for label, value in root[0][1]:
                if not valid_label(label) or label in entries or value not in ('enabled', 'disabled'):
                    raise ValueError('invalid or duplicate override')
                entries[label] = value == 'disabled'
        except ValueError as exc:
            error = Error('override_parse', str(exc))
    return replace(command, data=OverrideData(tuple(sorted(entries.items())), error is None,
                                              (error.message,) if error else ()), error=error)


def effective_disabled(label, plist, overrides):
    if overrides.error is not None or overrides.data is None or not overrides.data.complete:
        return DisabledState(Unknown('override map unavailable'), 'unknown', 'unknown', ('override',))
    entries = dict(overrides.data.entries)
    if label in entries:
        value = entries[label]
        return DisabledState(Known(value), 'override', 'disabled' if value else 'enabled', ('override',))
    if plist is not None and plist.error is None and plist.data is not None and not plist.data.field_errors:
        return DisabledState(plist.data.disabled, 'plist' if 'Disabled' in plist.data.present_keys else 'plist default',
                             'absent', ('override', 'plist'))
    return DisabledState(Unknown('valid plist unavailable'), 'unknown', 'absent', ('override', 'plist'))
