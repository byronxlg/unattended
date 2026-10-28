# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Actions-only result import orchestration; offline tests inject repository and clock."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, fixtures, night_live, publish, result_states
from product.nz_election.pipeline.deployment_guard import require_publication_allowed
from product.nz_election.pipeline.refresh import utc_now


def capture_bytes(path, root):
    if not isinstance(path, str) or not path:
        raise ValueError('MISSING_CAPTURE')
    raw = fixtures.captures(root, paths={path})[path]
    entries = json.loads((root / 'manifest.json').read_text())['entries']
    entry = next(e for e in entries if e['path'] == path)
    synthetic = re.compile(r'synthetic|rehearsal|offline fixture', re.I)
    if any(e['sha256'] == export.digest(raw) and synthetic.search(json.dumps(e)) for e in entries):
        raise ValueError('NIGHT_CAPTURE_NOT_REAL')
    if (not re.fullmatch(r'result-import/[a-zA-Z0-9_-]+\.json', path)
            or entry.get('capture_kind') != 'human-reviewed-real'
            or not entry.get('reviewer')
            or synthetic.search(json.dumps(entry))):
        raise ValueError('NIGHT_CAPTURE_NOT_REAL')
    try:
        captured = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError('NIGHT_CAPTURE_NOT_REAL') from None
    if (not isinstance(captured, dict) or not isinstance(captured.get('raw'), dict)
            or not isinstance(captured.get('retrieved_at'), str)
            or captured.get('rehearsal') or captured.get('synthetic')):
        raise ValueError('NIGHT_CAPTURE_NOT_REAL')
    return captured, export.digest(raw)


def pin(repository, sha, checkout, *, ref='refs/heads/data'):
    if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('NIGHT_DATA_SHA')
    publish.git(checkout, 'init', '-q')
    publish.git(checkout, 'fetch', str(repository), ref)
    head = publish.git(checkout, 'rev-parse', 'FETCH_HEAD').stdout.strip()
    if publish.git(checkout, 'merge-base', '--is-ancestor', sha, head, check=False).returncode:
        raise ValueError('NIGHT_DATA_SHA')
    for line in publish.git(checkout, 'ls-tree', '-r', sha).stdout.splitlines():
        mode, _, rest = line.split(' ', 2)
        _, name = rest.split('\t', 1)
        if mode != '100644' or not name.startswith(str(publish.DATA) + '/') or not export.allowed_path(name[len(str(publish.DATA)) + 1:]):
            raise ValueError('UNSAFE_DATA_TREE')
    publish.git(checkout, 'checkout', '--detach', sha)
    return head


def verify(data):
    lines = []
    for check in ('night', 'waterfall'):
        result = subprocess.run([sys.executable, 'product/nz_election/pipeline/verify.py', check, '--data', str(data)],
                                capture_output=True, text=True)
        print(result.stdout, end='')
        if result.returncode or 'PASS ' + check not in result.stdout.splitlines():
            print(result.stderr, end='')
            raise ValueError('NIGHT_VERIFY_FAILED')
        lines.append('PASS ' + check)
    return lines


def run(state, capture, data_sha, *, repository, now, run_url, rollback=False,
        root=fixtures.ROOT, verifier=verify, deploy=None,
        capture_reader=capture_bytes, pin_data=pin, publisher=None):
    # Local rehearsal adapters are programmatic only; the Actions CLI keeps production defaults.
    publisher = publisher or publish.publish
    require_publication_allowed(now())
    if not isinstance(state, str) or state not in result_states.MODES:
        raise ValueError('NIGHT_STATE')
    captured, digest = capture_reader(capture, root) if not rollback else (None, None)
    with tempfile.TemporaryDirectory(prefix='nz-result-import-') as tmp:
        checkout = Path(tmp) / 'checkout'
        checkout.mkdir()
        head = pin_data(repository, data_sha, checkout)
        data = checkout / publish.DATA
        envs = export.validate_bundle(data)
        if rollback:
            if 'night/live/current' not in envs or envs['night/live/current']['data'][0].get('rehearsal'):
                raise ValueError('NIGHT_BASELINE')
            out = data
        else:
            if state == 'settled':
                reviewed = night_live.loaded(captured)[0]['night/live/current'][0]
                if reviewed != envs.get('night/live/current', {}).get('data', [None])[0]:
                    raise ValueError('NIGHT_BASELINE')
            out = Path(tmp) / 'output'
            result_states.prepare(data, out, state, now=now(), run_url=run_url, captured=captured)
        lines = verifier(out)
        if lines != ['PASS night', 'PASS waterfall']:
            raise ValueError('NIGHT_VERIFY_FAILED')
        result = publisher(out, repository, family='night', now=now,
                                 night_rollback=head if rollback else None, require_night_match=True)
        report = dict(input_data_sha=data_sha, capture=capture if not rollback else None,
                      capture_sha256=digest, published_data_sha=result['sha'], rollback=rollback, checks=lines)
        text = json.dumps(report, indent=2)
        print(text)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
                summary.write('```json\n' + text + '\n```\n')
        if deploy:
            deploy(result['sha'])
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True)
    parser.add_argument('--capture', default='')
    parser.add_argument('--data-sha', required=True)
    parser.add_argument('--rollback', action='store_true')
    args = parser.parse_args()
    authorization = base64.b64encode(('x-access-token:' + os.environ['GITHUB_TOKEN']).encode()).decode()
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                      GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + authorization)
    run_url = os.environ['GITHUB_SERVER_URL'] + '/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']
    def deploy(sha):
        require_publication_allowed()
        subprocess.run(['gh', 'workflow', 'run', 'pages.yml', '--ref', 'main', '-f', 'data_sha=' + sha,
                        '-f', 'night_cycle=result-import-' + os.environ['GITHUB_RUN_ID']], check=True, timeout=120)
    try:
        run(args.state, args.capture, args.data_sha, repository='https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '.git',
            now=utc_now, run_url=run_url, rollback=args.rollback, deploy=deploy)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == '__main__':
    main()
