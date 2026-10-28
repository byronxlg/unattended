"""Report scheduled workflow coverage for complete Pacific/Auckland calendar days."""
import argparse
from datetime import datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import shlex
import textwrap
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))
from product.nz_election.pipeline.deployment_guard import START, END
from product.nz_election.pipeline.night_live import CLOSE
from product.nz_election.pipeline.sunsets import HOURLY_CLOSE, DAILY_CLOSE, SOCIAL_CLOSE

POLICY = (
    'Cron is evaluated in UTC and reported by NZ calendar day; inactive days require no runs. '
    'Declared publication, night-operation and collection sunset guards bound the active window. '
    'Hourly: gaps between consecutive successful runs are measured across midnight and must be at most 3 hours. '
    'Use the last success before each day and first success after it within the window; '
    'use window start/end only when no such success exists. '
    'Every failure must be followed by a success within 2 hours, including across midnight. '
    'Daily: the last run of the day must conclude success; a successful rerun reports recovery. '
    'Counts are reported, not required. Times and ordering use run creation timestamps.'
)
NZ = ZoneInfo('Pacific/Auckland')


def scheduled_workflows(root):
    workflows = []
    for path in sorted((root / '.github/workflows').glob('*')):
        if path.suffix not in {'.yml', '.yaml'}:
            continue
        source = path.read_text()
        # These repository workflows use a block-style on.schedule mapping.
        if re.search(r'^  schedule:\s*\n\s+- cron:', source, re.M):
            name = re.search(r'^name:\s*(.+)$', source, re.M)
            if not name:
                raise ValueError(f'missing workflow name: {path.name}')
            workflows.append((path.name, name[1].strip().strip('\"\'')))
    if not workflows:
        raise ValueError('no scheduled workflows discovered')
    return workflows


def cron_field(field, low, high, names=()):
    for index, name in enumerate(names):
        field = re.sub(name, str(low + index), field, flags=re.I)
    values = set()
    for part in field.split(','):
        match = re.fullmatch(r'(\*|[0-9]+(?:-[0-9]+)?)(?:/([0-9]+))?', part)
        if not match:
            raise ValueError(f'unsupported cron field: {field}')
        base, step = match.groups()
        step = int(step or 1)
        if step < 1:
            raise ValueError(f'invalid cron step: {field}')
        if base == '*':
            first, last = low, high
        elif '-' in base:
            first, last = map(int, base.split('-'))
        else:
            first = int(base)
            last = high if match[2] else first
        if not low <= first <= last <= high:
            raise ValueError(f'invalid cron range: {field}')
        values.update(range(first, last + 1, step))
    return values


def workflow_schedule(source):
    schedules = []
    for cron in re.findall(r"^\s+- cron:\s*['\"]([^'\"]+)['\"]", source, re.M):
        fields = cron.split()
        if len(fields) != 5:
            raise ValueError(f'invalid cron: {cron}')
        minute, hour, day, month, weekday = fields
        schedules.append((cron_field(minute, 0, 59), cron_field(hour, 0, 23),
                          cron_field(day, 1, 31),
                          cron_field(month, 1, 12, ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                                                   'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')),
                          {d % 7 for d in cron_field(weekday, 0, 7,
                                                    ('SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'))},
                          day.startswith('*'), weekday.startswith('*')))
    if not schedules:
        raise ValueError('no supported cron schedules')
    return schedules


def matches_date(schedule, day):
    _, _, days, months, weekdays, any_day, any_weekday = schedule
    dom = day.day in days
    dow = (day.weekday() + 1) % 7 in weekdays
    return day.month in months and ((dom and dow) if any_day or any_weekday else (dom or dow))


def scheduled_times(schedules, start, end):
    # GitHub cron uses UTC; a single NZ date can contain two UTC dates.
    stamps = set()
    day = start.date()
    while day <= end.date():
        for schedule in schedules:
            if not matches_date(schedule, day):
                continue
            minutes, hours = schedule[:2]
            for hour in hours:
                for minute in minutes:
                    stamp = datetime.combine(day, time(hour, minute), timezone.utc)
                    if start <= stamp < end:
                        stamps.add(stamp)
        day += timedelta(days=1)
    return sorted(stamps)


def python_invocation(words):
    if words[:2] == ['uv', 'run']:
        words = words[2:]
    elif not words or words[0] not in {'python', 'python3'}:
        return None
    if words and words[0] in {'python', 'python3'}:
        words = words[1:]
    if words and re.fullmatch(r'(?:\./)?product/nz_election/pipeline/[a-z_]+\.py', words[0]):
        return words
    return None


def shell_commands(source):
    """Accept only a whole step of simple commands, never a shell fragment.

    The supported grammar is newline-separated literal echo, known set options,
    and direct Python/uv script invocations, with quotes, comments and line
    continuations. Operators, expansion, nesting and other command forms reject
    the entire step, including invocations preceding the unsupported syntax.
    """
    # Reject before splitting or comment removal can hide unsupported bytes.
    if any(char not in '\t\n' and not ' ' <= char <= '~' for char in source):
        raise ValueError('unsupported shell character')
    commands = [[]]
    quote = None
    in_word = False
    index = 0
    while index < len(source):
        char = source[index]
        if char == '\\' and quote != "'" and index + 1 < len(source):
            following = source[index + 1]
            if following != '\n':
                commands[-1].extend((char, following))
                in_word = True
            index += 2
            continue
        if quote:
            if quote == '"' and char in '$`':
                raise ValueError('unsupported shell expansion')
            commands[-1].append(char)
            if char == quote:
                quote = None
        elif char in {'"', "'"}:
            commands[-1].append(char)
            quote = char
            in_word = True
        elif char == '#' and not in_word:
            # A comment consumes its text, not the command-separating newline.
            while index < len(source) and source[index] != '\n':
                index += 1
            continue
        elif char == '\n':
            commands.append([])
            in_word = False
        elif char in '$`;|&()<>{}*?[]~':
            # Reject before quote removal or command splitting can hide syntax.
            # We never need to infer nesting depth: only depth zero is accepted.
            raise ValueError('unsupported shell syntax')
        else:
            commands[-1].append(char)
            in_word = char not in ' \t;&|()<>'
        index += 1
    tokenized = []
    for command in commands:
        lexer = shlex.shlex(''.join(command), posix=True, punctuation_chars=';&|()<>')
        lexer.whitespace = ' \t\n'
        lexer.whitespace_split = True
        lexer.commenters = ''
        words = list(lexer)
        if not words:
            continue
        if (words[0] != 'echo' and words not in (['set', '-e'], ['set', '-eu'], ['set', '-euo', 'pipefail'])
                and python_invocation(words) is None):
            raise ValueError('unsupported shell command')
        tokenized.append(words)
    return tokenized


def workflow_commands(source):
    """Read the repository's block-style step run scalars without executing YAML."""
    lines = source.split('\n')
    steps_indent = None
    step_key_indent = None
    in_jobs = False
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            in_jobs = line == 'jobs:'
        if steps_indent is not None and indent <= steps_indent:
            steps_indent = None
        if in_jobs and line.strip() == 'steps:':
            steps_indent = indent
            step_key_indent = None
        match = re.match(r'^( *)(- )?([\w-]+):[ \t]*(.*)$', line)
        if not match:
            continue
        space, dash, key, value = match.groups()
        key_indent = len(space) + (2 if dash else 0)
        if steps_indent is not None and dash and step_key_indent is None:
            step_key_indent = key_indent
        if re.fullmatch(r'[|>][-+0-9]*(?:\s+#.*)?', value):
            body = []
            while index < len(lines):
                candidate = lines[index]
                if candidate.strip() and len(candidate) - len(candidate.lstrip()) <= key_indent:
                    break
                body.append(candidate)
                index += 1
            if match[4].startswith('>'):
                # Folding depends on blank lines and indentation. Raw text is
                # not execution evidence; consume the scalar without guessing.
                continue
            value = textwrap.dedent('\n'.join(body))
        elif value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                continue
        elif value.startswith("'"):
            if not value.endswith("'"):
                continue
            value = value[1:-1].replace("''", "'")
        if key != 'run' or steps_indent is None or key_indent != step_key_indent:
            continue
        try:
            commands = shell_commands(value)
        except ValueError:
            continue
        for words in commands:
            invocation = python_invocation(words)
            if invocation is not None:
                yield invocation


def collection_sunset(commands):
    deadlines = {'hourly': HOURLY_CLOSE, 'daily': DAILY_CLOSE, 'social': SOCIAL_CLOSE}
    # Overrides and unknown arguments are not evidence of the shared deadline.
    return min((deadlines[words[1]] for words in commands
                if words[0].removeprefix('./') == 'product/nz_election/pipeline/sunsets.py'
                and len(words) == 2 and words[1] in deadlines), default=None)


def active_intervals(source, start, end):
    commands = list(workflow_commands(source))
    scripts = {words[0].removeprefix('./') for words in commands}
    sunset = collection_sunset(commands)
    if sunset is not None:
        end = min(end, sunset)
    if 'product/nz_election/pipeline/night_live.py' in scripts:
        start, end = max(start, END), min(end, CLOSE)
    intervals = [(start, end)] if start < end else []
    if ('product/nz_election/pipeline/deployment_guard.py' in scripts or
            any(words[0].removeprefix('./') == 'product/nz_election/pipeline/social.py' and
                '--check-freeze' in words[1:] for words in commands)):
        intervals = [(left, right) for a, b in intervals
                     for left, right in ((a, min(b, START)), (max(a, END), b)) if left < right]
    return intervals


def date_intervals(schedules, day):
    """Partition one UTC date into its scheduled cadence windows."""
    matching = [schedule for schedule in schedules if matches_date(schedule, day)]
    if not matching:
        return []
    hours = sorted(set().union(*(schedule[1] for schedule in matching)))
    midnight = datetime.combine(day, time.min, timezone.utc)
    if max(b - a for a, b in zip(hours, hours[1:] + [hours[0] + 24])) <= 3:
        return [(midnight, midnight + timedelta(days=1), True)]
    groups = []
    for hour in hours:
        if groups and hour - groups[-1][-1] <= 3:
            groups[-1].append(hour)
        else:
            groups.append([hour])
    if all(len(group) == 1 for group in groups):
        return [(midnight, midnight + timedelta(days=1), False)]
    # Include the whole first and last scheduled hour, not just the interval
    # after the last observed run. Long unscheduled breaks split the policy.
    return [(midnight + timedelta(hours=group[0]), midnight + timedelta(hours=group[-1] + 1),
             len(group) > 1) for group in groups]


def expected_intervals(source, schedules, start, end):
    intervals = []
    for a, b in active_intervals(source, start, end):
        parts = []
        day = a.date()
        while day <= b.date():
            for left, right, hourly in date_intervals(schedules, day):
                left, right = max(a, left), min(b, right)
                if left < right:
                    parts.append((left, right, hourly))
            day += timedelta(days=1)
        if not any(hourly for _, _, hourly in parts):
            # Daily coverage and manual recovery remain NZ-calendar-day checks.
            if scheduled_times(schedules, a, b):
                intervals.append((a, b, False))
            continue
        for left, right, hourly in parts:
            if not hourly and not scheduled_times(schedules, left, right):
                continue
            if intervals and intervals[-1][1:] == (left, hourly):
                intervals[-1] = (intervals[-1][0], right, hourly)
            else:
                intervals.append((left, right, hourly))
    return intervals


def day_result(runs, start, end, hourly, later_successes=(), *, gap_start=None, gap_end=None):
    runs = sorted(runs, key=lambda r: r[0])
    successes = [stamp for stamp, run in runs
                 if run['status'] == 'completed' and run['conclusion'] == 'success']
    failures = [stamp for stamp, run in runs
                if run['status'] == 'completed' and run['conclusion'] != 'success']
    recovered = sum(any(stamp < success and (not hourly or success - stamp <= timedelta(hours=2))
                        for success in [*successes, *later_successes]) for stamp in failures)
    reasons = []
    if hourly:
        boundaries = [gap_start if gap_start is not None else start, *successes,
                      gap_end if gap_end is not None else end]
        gap = max(b - a for a, b in zip(boundaries, boundaries[1:]))
        if gap > timedelta(hours=3):
            reasons.append(f'success gap {gap.total_seconds() / 3600:g} hours exceeds 3 hours')
        elif not runs:
            reasons.append('no runs')
        if recovered != len(failures):
            reasons.append(f'{len(failures) - recovered} failures without success within 2 hours')
    elif not runs:
        reasons.append('no runs')
    else:
        # Equal creation timestamps must not let API ordering hide a failed latest run.
        latest = [run for stamp, run in runs if stamp == runs[-1][0]]
        if any(run['status'] != 'completed' or run['conclusion'] != 'success' for run in latest):
            reasons.append('last run did not conclude success')
    return len(successes), len(failures), recovered, reasons


def check_history(days, *, runner=subprocess.run, now=None, root=ROOT):
    today = (now or datetime.now(timezone.utc)).astimezone(NZ).date()
    dates = [today - timedelta(days=n) for n in range(days, 0, -1)]
    ok = True
    for filename, name in scheduled_workflows(root):
        source = (root / '.github/workflows' / filename).read_text()
        schedules = workflow_schedule(source)
        sunset = collection_sunset(workflow_commands(source))
        daily_runs = []
        for day in dates:
            start = datetime.combine(day, time.min, NZ).astimezone(timezone.utc)
            end = datetime.combine(day + timedelta(days=1), time.min, NZ).astimezone(timezone.utc)
            intervals = expected_intervals(source, schedules, start, end)
            if not intervals:
                print(f'PASS {name} {day}: not scheduled (cron or active-window guard)')
            for start, end, hourly in intervals:
                query_end = end + timedelta(hours=2) if hourly else end
                # A manual recovery may follow the last cron fire. Keep the
                # two-hour recovery policy while respecting execution guards.
                active = active_intervals(source, end, query_end)
                if hourly:
                    query_end = active[0][1] if active and active[0][0] == end else end
                # Query each day and fail closed at the cap rather than accepting truncated evidence.
                result = runner(['gh', 'run', 'list', '--workflow', filename, '--branch', 'main',
                                 '--created', f'{start.isoformat()}..{query_end.isoformat()}', '--limit', '1000',
                                 '--json', 'createdAt,event,status,conclusion'], cwd=root, text=True,
                                capture_output=True)
                if result.returncode:
                    raise ValueError(f'{name} {day}: gh exit {result.returncode}')
                runs = json.loads(result.stdout)
                if not isinstance(runs, list) or len(runs) >= 1000:
                    raise ValueError(f'{name} {day}: invalid or truncated history')
                selected = []
                later_successes = []
                for run in runs:
                    stamp = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
                    if stamp.tzinfo is None:
                        raise ValueError('run timestamp lacks timezone')
                    if run['event'] in {'schedule', 'workflow_dispatch'}:
                        if start <= stamp < end:
                            selected.append((stamp, run))
                        elif (hourly and end <= stamp <= query_end
                              and (sunset is None or stamp < sunset)
                              and run['status'] == 'completed' and run['conclusion'] == 'success'):
                            later_successes.append(stamp)
                daily_runs.append((day, start, end, selected, later_successes, hourly))
        # Collect the whole window before reporting so midnight cannot split a real gap.
        window_successes = sorted(stamp for _, _, _, selected, _, _ in daily_runs
                                  for stamp, run in selected
                                  if run['status'] == 'completed' and run['conclusion'] == 'success')
        for index, (day, start, end, selected, later_successes, hourly) in enumerate(daily_runs):
            first = last = index
            while first > 0 and daily_runs[first - 1][2] == daily_runs[first][1] and daily_runs[first - 1][5] == hourly:
                first -= 1
            while last + 1 < len(daily_runs) and daily_runs[last][2] == daily_runs[last + 1][1] and daily_runs[last + 1][5] == hourly:
                last += 1
            window_start, window_end = daily_runs[first][1], daily_runs[last][2]
            gap_start = max((stamp for stamp in window_successes if window_start <= stamp < start),
                            default=window_start)
            gap_end = min((stamp for stamp in window_successes if end <= stamp < window_end),
                          default=window_end)
            successes, failures, recovered, reasons = day_result(
                selected, start, end, hourly, later_successes,
                gap_start=gap_start, gap_end=gap_end)
            cron = any(r['event'] == 'schedule' for _, r in selected)
            note = '' if cron else ('; cron did not fire, workflow_dispatch covered it' if successes else '; cron did not fire')
            counts = f'{len(selected)} runs, {successes} successes, {failures} failures, {recovered} recovered'
            reason = '; ' + '; '.join(reasons) if reasons else ''
            print(f'{"FAIL" if reasons else "PASS"} {name} {day}: {counts}{note}{reason}')
            ok = ok and not reasons
    return ok


def main(argv=None, *, runner=subprocess.run, now=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__ + " " + POLICY)
    parser.add_argument('--days', type=int, default=3)
    args = parser.parse_args(argv)
    if not 1 <= args.days <= 366:
        parser.error('--days must be between 1 and 366')
    try:
        ok = check_history(args.days, runner=runner, now=now, root=root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f'FAIL workflow history: {exc}')
        return 1
    print('PASS workflow history' if ok else 'FAIL workflow history: daily policy not met')
    return int(not ok)


if __name__ == '__main__':
    raise SystemExit(main())
