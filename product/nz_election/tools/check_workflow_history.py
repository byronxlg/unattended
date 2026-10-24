"""Report scheduled workflow coverage for complete Pacific/Auckland calendar days."""
import argparse
from datetime import datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
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


def check_history(days, *, runner=subprocess.run, now=None, root=ROOT):
    today = (now or datetime.now(timezone.utc)).astimezone(NZ).date()
    dates = [today - timedelta(days=n) for n in range(days, 0, -1)]
    ok = True
    for filename, name in scheduled_workflows(root):
        for day in dates:
            start = datetime.combine(day, time.min, NZ).astimezone(timezone.utc)
            end = datetime.combine(day + timedelta(days=1), time.min, NZ).astimezone(timezone.utc)
            # Query each day and fail closed at the cap rather than accepting truncated evidence.
            result = runner(['gh', 'run', 'list', '--workflow', filename, '--branch', 'main',
                             '--created', f'{start.isoformat()}..{end.isoformat()}', '--limit', '1000',
                             '--json', 'createdAt,event,status,conclusion'], cwd=root, text=True,
                            capture_output=True)
            if result.returncode:
                raise ValueError(f'{name} {day}: gh exit {result.returncode}')
            runs = json.loads(result.stdout)
            if not isinstance(runs, list) or len(runs) >= 1000:
                raise ValueError(f'{name} {day}: invalid or truncated history')
            selected = []
            for run in runs:
                stamp = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
                if stamp.tzinfo is None:
                    raise ValueError('run timestamp lacks timezone')
                if start <= stamp < end and run['event'] in {'schedule', 'workflow_dispatch'}:
                    selected.append(run)
            successes = sum(r['status'] == 'completed' and r['conclusion'] == 'success' for r in selected)
            failures = sum(r['status'] == 'completed' and r['conclusion'] != 'success' for r in selected)
            cron = any(r['event'] == 'schedule' for r in selected)
            note = '' if cron else ('; cron did not fire, workflow_dispatch covered it' if successes else '; cron did not fire')
            print(f'{"PASS" if successes else "FAIL"} {name} {day}: {successes} successes, {failures} failures{note}')
            ok = ok and bool(successes)
    return ok


def main(argv=None, *, runner=subprocess.run, now=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=3)
    args = parser.parse_args(argv)
    if not 1 <= args.days <= 366:
        parser.error('--days must be between 1 and 366')
    try:
        ok = check_history(args.days, runner=runner, now=now, root=root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f'FAIL workflow history: {exc}')
        return 1
    print('PASS workflow history' if ok else 'FAIL workflow history: missing daily success')
    return int(not ok)


if __name__ == '__main__':
    raise SystemExit(main())
