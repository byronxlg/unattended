"""Report scheduled workflow coverage for complete Pacific/Auckland calendar days."""
import argparse
from datetime import datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))
from product.nz_election.pipeline.deployment_guard import START, END
from product.nz_election.pipeline.night_live import CLOSE

POLICY = (
    'Cron is evaluated in UTC and reported by NZ calendar day; inactive days require no runs. '
    'Declared publication and night-operation guards bound the active window. '
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


def scheduled_times(schedules, start, end):
    # GitHub cron uses UTC; a single NZ date can contain two UTC dates.
    stamps = set()
    day = start.date()
    while day <= end.date():
        for minutes, hours, days, months, weekdays, any_day, any_weekday in schedules:
            dom = day.day in days
            dow = (day.weekday() + 1) % 7 in weekdays
            matches_day = (dom and dow) if any_day or any_weekday else (dom or dow)
            if day.month not in months or not matches_day:
                continue
            for hour in hours:
                for minute in minutes:
                    stamp = datetime.combine(day, time(hour, minute), timezone.utc)
                    if start <= stamp < end:
                        stamps.add(stamp)
        day += timedelta(days=1)
    return sorted(stamps)


def active_intervals(source, start, end):
    # Reuse the guards of the entry points declared in these workflows, not dates
    # copied into the history policy. Never execute shell from workflow YAML.
    if 'product/nz_election/pipeline/night_live.py' in source:
        start, end = max(start, END), min(end, CLOSE)
    intervals = [(start, end)] if start < end else []
    if ('product/nz_election/pipeline/deployment_guard.py' in source or
            re.search(r'product/nz_election/pipeline/social.py[^\n]*--check-freeze', source)):
        intervals = [(left, right) for a, b in intervals
                     for left, right in ((a, min(b, START)), (max(a, END), b)) if left < right]
    return intervals


def hourly_workflow(root, filename):
    source = (root / '.github/workflows' / filename).read_text()
    return hourly_schedule(workflow_schedule(source))


def hourly_schedule(schedules):
    hours = sorted(set().union(*(schedule[1] for schedule in schedules)))
    return max(b - a for a, b in zip(hours, hours[1:] + [hours[0] + 24])) <= 3


def expected_intervals(source, schedules, start, end, hourly):
    intervals = []
    for a, b in active_intervals(source, start, end):
        if not hourly:
            if scheduled_times(schedules, a, b):
                intervals.append((a, b))
            continue
        # A dated hourly cron can start halfway through an NZ day. Midnight
        # gaps count only within consecutive UTC dates on which it is active.
        cursor = a
        while cursor < b:
            boundary = min(b, datetime.combine(cursor.date() + timedelta(days=1), time.min, timezone.utc))
            if scheduled_times(schedules, cursor, boundary):
                if intervals and intervals[-1][1] == cursor:
                    intervals[-1] = (intervals[-1][0], boundary)
                else:
                    intervals.append((cursor, boundary))
            cursor = boundary
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
        hourly = hourly_schedule(schedules)
        daily_runs = []
        for day in dates:
            start = datetime.combine(day, time.min, NZ).astimezone(timezone.utc)
            end = datetime.combine(day + timedelta(days=1), time.min, NZ).astimezone(timezone.utc)
            intervals = expected_intervals(source, schedules, start, end, hourly)
            if not intervals:
                print(f'PASS {name} {day}: not scheduled (cron or active-window guard)')
            for start, end in intervals:
                query_end = end + timedelta(hours=2) if hourly else end
                active = expected_intervals(source, schedules, end, query_end, hourly)
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
                        elif hourly and end <= stamp <= query_end and run['status'] == 'completed' and run['conclusion'] == 'success':
                            later_successes.append(stamp)
                daily_runs.append((day, start, end, selected, later_successes))
        # Collect the whole window before reporting so midnight cannot split a real gap.
        window_successes = sorted(stamp for _, _, _, selected, _ in daily_runs
                                  for stamp, run in selected
                                  if run['status'] == 'completed' and run['conclusion'] == 'success')
        for index, (day, start, end, selected, later_successes) in enumerate(daily_runs):
            first = last = index
            while first > 0 and daily_runs[first - 1][2] == daily_runs[first][1]:
                first -= 1
            while last + 1 < len(daily_runs) and daily_runs[last][2] == daily_runs[last + 1][1]:
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
