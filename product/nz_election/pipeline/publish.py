# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Publish validated owned data with a leased push and bounded conflict retries."""
import argparse
import base64
import json
import os
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export

DATA = Path('product/nz_election/data')
OWNED = {s + ext for s in ('polls', 'averages', 'seats') for ext in ('.json', '.csv')}


def git(root, *args, check=True):
    return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                          text=True, capture_output=True, check=check)


def status_of(envs):
    return next((s for s in envs['status']['data'] if s['dataset'] == 'polls'), None)


def success_order(envs):
    if 'polls' not in envs:
        return ('', '')
    return (envs['polls']['fetched_at'], envs['averages']['generated_at'])


def publish(bundle, repository, *, before_push=None, attempts=3):
    bundle = Path(bundle).absolute()
    incoming = export.validate_bundle(bundle)
    remote = str(repository)
    if not remote.startswith('https://github.com/'):
        repository = Path(repository).resolve()
        if not repository.is_dir() or git(repository, 'rev-parse', '--is-bare-repository').stdout.strip() != 'true':
            raise ValueError('LOCAL_BARE_REPOSITORY_REQUIRED')
        remote = str(repository)
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError('INVALID_RETRY_LIMIT')
    proposed = status_of(incoming)
    with tempfile.TemporaryDirectory(prefix='nz-publish-') as tmp:
        checkout = Path(tmp)
        git(checkout, 'init', '-q')
        git(checkout, 'config', 'user.name', 'NZ election publication')
        git(checkout, 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        for attempt in range(attempts):
            refs = git(checkout, 'ls-remote', remote, 'refs/heads/data').stdout.split()
            fetched_sha = refs[0] if refs else ''
            if fetched_sha:
                git(checkout, 'fetch', remote, fetched_sha)
                # Inspect the tree before checkout, so data never installs git configuration.
                listing = git(checkout, 'ls-tree', '-r', 'FETCH_HEAD').stdout.splitlines()
                for line in listing:
                    mode, _, rest = line.split(' ', 2)
                    _, name = rest.split('\t', 1)
                    if mode != '100644' or name not in {str(DATA / n) for n in export.ALLOWED}:
                        raise ValueError('UNSAFE_DATA_TREE')
                git(checkout, 'checkout', '-B', 'data', 'FETCH_HEAD')
            else:
                git(checkout, 'checkout', '--orphan', 'bootstrap-' + str(attempt))
                git(checkout, 'rm', '-rf', '--ignore-unmatch', '.')
            target = checkout / DATA
            current = export.validate_bundle(target) if fetched_sha else {'status': {'data': []}}
            target.mkdir(parents=True, exist_ok=True)
            previous = status_of(current)
            # Validation guarantees canonical UTC strings, so lexical order is instant order.
            # Acquisition wins first; unchanged captures use successful average-generation
            # time. Exact ties retain repository bytes, independently of attempt chronology.
            keep_data = previous and success_order(current) >= success_order(incoming)
            keep_status = previous and previous['last_attempt_at'] > proposed['last_attempt_at']
            if keep_status and keep_data:
                return dict(outcome='older-run-retained', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            if not keep_data:
                for name in OWNED | {'LICENCES.md'}:
                    if (bundle / name).exists():
                        shutil.copyfile(bundle / name, target / name)
            # Attempt chronology and successful acquisition chronology are independent.
            merged = dict(previous if keep_status else proposed)
            last_good = previous if keep_data else proposed
            merged.update(last_success_at=last_good['last_success_at'], last_good_run_url=last_good['last_good_run_url'])
            if merged['error_code'] is not None:
                merged['state'] = 'stale' if merged['last_success_at'] else 'unavailable'
            statuses = [s for s in current['status']['data'] if s['dataset'] != 'polls'] + [merged]
            metadata = current['status'] if keep_status else incoming['status']
            export.pair(target, 'status', export.envelope(statuses, [], metadata['run_url'], metadata['code_sha']))
            export.inventory(target, metadata['run_url'], metadata['code_sha'], merged['last_attempt_at'])
            export.validate_bundle(target)
            git(checkout, 'add', '--', *[str(DATA / n) for n in sorted(export.ALLOWED) if (target / n).exists()])
            if git(checkout, 'diff', '--cached', '--quiet', check=False).returncode == 0:
                return dict(outcome='unchanged', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            git(checkout, 'commit', '-qm', 'Publish validated poll bundle')
            if before_push:
                before_push(attempt)
            pushed = git(checkout, 'push', '--porcelain', f'--force-with-lease=refs/heads/data:{fetched_sha}',
                         remote, 'HEAD:refs/heads/data', check=False)
            if pushed.returncode == 0:
                return dict(outcome='published', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            # Compare the leased ref itself, not platform-specific rejection prose.
            remote_ref = git(checkout, 'ls-remote', remote, 'refs/heads/data').stdout.split()
            if not remote_ref or remote_ref[0] == fetched_sha:
                raise RuntimeError('PUBLICATION_FAILED: ' + pushed.stderr)
        raise RuntimeError('PUBLICATION_RETRIES_EXHAUSTED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()
    # Validate the artifact before any git operation or credential use.
    incoming = export.validate_bundle(args.bundle)
    token = os.environ['GITHUB_TOKEN']
    authorization = base64.b64encode(('x-access-token:' + token).encode()).decode()
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                      GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + authorization)
    result = publish(args.bundle, 'https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '.git')
    report = dict(result, status=status_of(incoming))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write('## Data publication\n\n```json\n' + json.dumps(report, indent=2) + '\n```\n')
    print(json.dumps(result))
    if status_of(incoming)['error_code'] is not None:
        raise SystemExit('FAIL refresh: handled failure status published')


if __name__ == '__main__':
    main()
