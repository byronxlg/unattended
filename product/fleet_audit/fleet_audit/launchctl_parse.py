"""Conservative structural parsing of version-specific diagnostic text."""
import re
from dataclasses import replace

from .models import Absent, DomainData, Error, Known, Schedule, ServiceData, Unknown, Unsupported
from .registry import calendar_error, freeze_calendar, valid_label, valid_path


def redact_environment(text):
    lines, environment_indent = [], None
    for raw in text.splitlines():
        line = raw.lstrip()
        indent = len(raw) - len(line)
        if environment_indent is not None:
            if line == '}' and indent == environment_indent:
                environment_indent = None
                lines.append(raw)
            elif '=>' in line:
                lines.append(raw.split('=>', 1)[0] + '=> [redacted]')
            # Unsupported or partial environment lines are discarded, never exported.
            continue
        if re.fullmatch(r'(?:inherited |default )?environment = \{', line):
            environment_indent = indent
        lines.append(raw)
    return '\n'.join(lines) + ('\n' if text.endswith('\n') else '')


def tree(text):
    root, stack = [], []
    current = root
    for raw in text.splitlines():
        if not raw.strip() and not (stack and stack[-1][3] == 'arguments' and raw.startswith('\t' * (stack[-1][1] + 1))):
            continue
        line = raw.lstrip('\t ')
        indent = len(raw) - len(line)
        if stack and line == stack[-1][2] and indent == stack[-1][1]:
            current = stack.pop()[0]
            continue
        if stack and indent <= stack[-1][1]:
            raise ValueError('malformed nesting')
        if stack and stack[-1][3] == 'arguments':
            current.append((None, raw[stack[-1][1] + 1:] if raw.startswith('\t') else line))
            continue
        if line in ('}', ']'):
            raise ValueError('unmatched closing delimiter')
        match = re.fullmatch(r'(.+?)\s+(?:=>|=)\s+(.*)', line)
        if match:
            key, value = match.groups()
            key = key.strip('"')
            if value in ('{', '['):
                child = []
                current.append((key, child))
                stack.append((current, indent, '}' if value == '{' else ']', key))
                current = child
            else:
                current.append((key, value))
        elif line == '{':
            child = []
            current.append((None, child))
            stack.append((current, indent, '}', ''))
            current = child
        else:
            current.append((None, line))
    if stack:
        raise ValueError('unclosed block')
    return root


def one(block, key):
    values = [v for k, v in block if k == key]
    if len(values) > 1:
        raise ValueError('duplicate ' + key)
    return values[0] if values else None


def command_error(command):
    if command.error is not None:
        return command.error
    if command.data is None or command.status != 'attempted':
        return Error('collection', 'command unavailable')
    if command.data.timed_out or command.data.truncated:
        return Error('collection', 'partial command output')
    if command.return_code != 0:
        return Error('collection', 'command failed')
    return None


def parse_domain(command, domain):
    error = command_error(command)
    labels = []
    if error is None:
        try:
            root = tree(command.data.stdout)
            if len(root) != 1 or root[0][0] != domain or not isinstance(root[0][1], list):
                raise ValueError('wrong domain root')
            services = one(root[0][1], 'services')
            if not isinstance(services, list):
                raise ValueError('missing services block')
            for key, row in services:
                match = re.fullmatch(r'\s*\d+\s+(?:-|-?\d+|\([a-z]+\))\s+(\S+)', row) if key is None and isinstance(row, str) else None
                if not match or not valid_label(match[1]) or match[1] in labels:
                    raise ValueError('unsupported inventory row')
                labels.append(match[1])
            if not labels:
                raise ValueError('empty inventory')
        except ValueError as exc:
            error = Error('domain_parse', str(exc))
    return replace(command, data=DomainData(domain, tuple(sorted(labels)), error is None,
                                           (error.message,) if error else ()), error=error)


def parse_service(command, identity):
    unknown = Unknown('not reported')
    schedule = Schedule(unknown, unknown, unknown, unknown, unknown)
    values = {name: unknown for name in ('state', 'pid', 'runs', 'last_exit_code', 'last_exit_text',
                                        'program', 'argv', 'working_directory', 'plist_path', 'properties')}
    loaded, valid = Unknown('untrusted service response'), False
    error = command_error(command)
    data = command.data
    diagnostic = (f'Bad request.\nCould not find service "{identity.label}" '
                  f'in domain for user gui: {identity.domain.removeprefix("gui/")}\n')
    if (data is not None and command.error is None and command.return_code == 113
            and not data.timed_out and not data.truncated and data.stdout == ''
            and data.stderr == diagnostic and data.argv and data.argv[-1] == f'{identity.domain}/{identity.label}'):
        loaded, valid, error = Known(False), True, None
    elif error is None:
        try:
            root = tree(data.stdout)
            if len(root) != 1 or root[0][0] != f'{identity.domain}/{identity.label}' or not isinstance(root[0][1], list):
                raise ValueError('wrong service root')
            block = root[0][1]
            reported_domain = one(block, 'domain')
            if reported_domain is not None and (not isinstance(reported_domain, str) or not re.fullmatch(re.escape(identity.domain) + r' \[\d+\]', reported_domain)):
                raise ValueError('wrong reported domain')
            for name, key in [('state', 'state'), ('program', 'program'),
                              ('working_directory', 'working directory'), ('plist_path', 'path')]:
                value = one(block, key)
                if value is not None:
                    if not isinstance(value, str) or not value or (name != 'state' and not valid_path(value)):
                        raise ValueError('invalid ' + key)
                    values[name] = Known(value)
            for name in ('pid', 'runs'):
                value = one(block, name)
                if value is None:
                    values[name] = Absent('no reported pid') if name == 'pid' else unknown
                elif not isinstance(value, str) or not re.fullmatch(r'\d+', value) or (name == 'pid' and int(value) == 0):
                    raise ValueError('invalid ' + name)
                else:
                    values[name] = Known(int(value))
            value = one(block, 'last exit code')
            if value is not None and value != '(never exited)':
                match = re.fullmatch(r'(-?\d+)(?::\s*(.*))?', value) if isinstance(value, str) else None
                if not match:
                    raise ValueError('invalid last exit code')
                values['last_exit_code'] = Known(int(match[1]))
                values['last_exit_text'] = Known(match[2]) if match[2] is not None else Absent('no exit text')
            args = one(block, 'arguments')
            if args is not None:
                if not isinstance(args, list) or any(k is not None or not isinstance(v, str) for k, v in args):
                    raise ValueError('invalid arguments')
                values['argv'] = Known(tuple(v for _, v in args))
            interval = one(block, 'run interval')
            if interval is not None:
                match = re.fullmatch(r'([1-9]\d*) seconds', interval) if isinstance(interval, str) else None
                schedule = replace(schedule, interval_seconds=Known(int(match[1])) if match else Unsupported(interval, 'unsupported interval'))
            calendars = []
            triggers = one(block, 'event triggers')
            if isinstance(triggers, list):
                for _, trigger in triggers:
                    if isinstance(trigger, list) and one(trigger, 'stream') == 'com.apple.launchd.calendarinterval':
                        descriptor = one(trigger, 'descriptor')
                        try:
                            calendar = {k: int(v) for k, v in descriptor}
                            if len(calendar) != len(descriptor) or calendar_error(calendar):
                                raise ValueError('invalid calendar')
                            calendars.append(calendar)
                        except (TypeError, ValueError):
                            calendars = None
                            break
                if calendars:
                    schedule = replace(schedule, calendar=Known(freeze_calendar(calendars)))
                elif calendars is None:
                    schedule = replace(schedule, calendar=Unsupported(triggers, 'unsupported calendar'))
            properties = one(block, 'properties')
            if isinstance(properties, str):
                tokens = tuple(properties.split(' | '))
                values['properties'] = Known(tokens)
                schedule = replace(schedule, keep_alive=Known(True) if 'keepalive' in tokens else unknown,
                                   run_at_load=Known(True) if 'runatload' in tokens else unknown)
            loaded, valid = Known(True), True
        except ValueError as exc:
            error = Error('service_parse', str(exc))
            values = {name: Unknown(str(exc)) for name in values}
    service = ServiceData(identity, loaded, **values, schedule=schedule,
                          missing_fields=tuple(k for k, v in values.items() if isinstance(v, (Unknown, Absent))),
                          warnings=(error.message,) if error else (), structural_valid=valid)
    return replace(command, data=service, error=error)
