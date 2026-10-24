"""Run the milestone checks without allowing partial verification to pass."""
import argparse
import ast
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
NETWORK_EVALS = {'pages-home-bytes-live': 'fetches the remote data branch'}


def verifier_families(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'checks' for t in node.targets):
            if isinstance(node.value, ast.Dict):
                names = [ast.literal_eval(k) for k in node.value.keys]
                if {'night', 'waterfall', 'campaign'} <= set(names):
                    return names
    raise ValueError('cannot discover verifier families')


def verification_error(output, families):
    lines = output.splitlines()
    if not lines or lines[-1] != 'PASS all' or lines.count('PASS all') != 1:
        return 'missing final PASS all'
    passed = [re.fullmatch(r'PASS ([\w-]+)(?:: .*)?', line) for line in lines[:-1]]
    names = [m[1] for m in passed if m]
    missing = [name for name in families if names.count(name) != 1]
    if missing:
        return 'missing or duplicate family lines: ' + ', '.join(missing)
    if any(line.startswith(('FAIL', 'SKIP')) for line in lines):
        return 'verifier reported FAIL or SKIP'
    return None


def result_error(output):
    for line in output.splitlines():
        if re.match(r'^\s*(?:SKIP|FAIL)\b', line):
            return 'reported ' + line.strip()
    return None


def main(argv=None, *, runner=subprocess.run, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--site', required=True, type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--history', action='store_true', help='required for PASS; otherwise a clean run is PARTIAL (exit 1)')
    args = parser.parse_args(argv)
    first = None

    def fail(step, reason):
        nonlocal first
        first = first or step
        print(f'FAIL {step}: {reason}', flush=True)

    def run(step, command, validate=None):
        print(f'RUN {step}', flush=True)
        try:
            result = runner(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = result.stdout or ''
            print(output, end='' if output.endswith('\n') else '\n', flush=True)
            error = f'exit {result.returncode}' if result.returncode else result_error(output) or (validate(output) if validate else None)
            if error:
                fail(step, error)
            else:
                print(f'PASS {step}', flush=True)
        except (OSError, ValueError) as exc:
            fail(step, str(exc))

    directories = sorted(p for p in (root / 'evals').glob('*') if p.is_dir())
    for directory in directories:
        if not (directory / 'check.sh').is_file():
            fail('eval ' + directory.name, 'missing check.sh')
    evals = [p / 'check.sh' for p in directories if (p / 'check.sh').is_file()]
    if not evals:
        fail('eval discovery', 'no check.sh files')
    for check in evals:
        step = 'eval ' + check.parent.name
        if args.offline and check.parent.name in NETWORK_EVALS:
            print(f'SKIP {step}: --offline; {NETWORK_EVALS[check.parent.name]}', flush=True)
            first = first or step + ' (SKIP)'
        else:
            run(step, ['bash', str(check)])
    verifier = root / 'product/nz_election/pipeline/verify.py'
    try:
        families = verifier_families(verifier)
    except (OSError, ValueError, SyntaxError) as exc:
        fail('verify all', str(exc))
    else:
        run('verify all', ['uv', 'run', str(verifier), 'all', '--data', str(args.data.resolve()),
                           '--site', str(args.site.resolve())], lambda out: verification_error(out, families))
    tests = root / 'product/nz_election/tests'
    run('freeze tests', ['uv', 'run', '--with', 'pytest', 'pytest', '-q',
                        *[str(tests / name) for name in ('test_social.py', 'test_social_fix_round1.py', 'test_night_operation.py')]])
    if args.history:
        if args.offline:
            print('SKIP workflow history: --offline; requires GitHub API', flush=True)
            first = first or 'workflow history (SKIP)'
        else:
            run('workflow history', ['uv', 'run', str(root / 'product/nz_election/tools/check_workflow_history.py'), '--days', '3'])
    outcome = 'PASS harden' if args.history else 'PARTIAL harden (history not checked)'
    print('FAIL harden: ' + first if first else outcome, flush=True)
    return int(first is not None or not args.history)


if __name__ == '__main__':
    raise SystemExit(main())
