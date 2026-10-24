"""Report scheduled workflow coverage for complete Pacific/Auckland calendar days."""
import argparse
from datetime import datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
POLICY = (
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


def hourly_workflow(root, filename):
    source = (root / '.github/workflows' / filename).read_text()
    crons = re.findall(r"^\s+- cron:\s*['\"]([^'\"]+)['\"]", source, re.M)
    return any(len(cron.split()) == 5 and cron.split()[1] == '*' for cron in crons)


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
        hourly = hourly_workflow(root, filename)
        daily_runs = []
        for day in dates:
            start = datetime.combine(day, time.min, NZ).astimezone(timezone.utc)
            end = datetime.combine(day + timedelta(days=1), time.min, NZ).astimezone(timezone.utc)
            query_end = end + timedelta(hours=2) if hourly else end
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
        for day, start, end, selected, later_successes in daily_runs:
            gap_start = max((stamp for stamp in window_successes if stamp < start),
                            default=daily_runs[0][1])
            gap_end = min((stamp for stamp in window_successes if stamp >= end),
                          default=daily_runs[-1][2])
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
