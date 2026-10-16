# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Local git test transport for owned poll publication. No branch bootstrap or network."""
from pathlib import Path
import shutil
import subprocess
import tempfile
from . import export

DATA = Path('product/nz_election/data')
OWNED = {s + ext for s in ('polls', 'averages', 'seats') for ext in ('.json', '.csv')}


def git(root, *args, check=True):
    return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                          text=True, capture_output=True, check=check)


def status_of(envs):
    return next((s for s in envs['status']['data'] if s['dataset'] == 'polls'), None)


def publish(bundle, repository, *, before_push=None, attempts=3):
    bundle, repository = Path(bundle).resolve(), Path(repository).resolve()
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError('INVALID_RETRY_LIMIT')
    incoming = export.validate_bundle(bundle)
    if not repository.is_dir() or git(repository, 'rev-parse', '--is-bare-repository').stdout.strip() != 'true':
        raise ValueError('LOCAL_BARE_REPOSITORY_REQUIRED')
    proposed = status_of(incoming)
    with tempfile.TemporaryDirectory(prefix='nz-publish-') as tmp:
        checkout = Path(tmp)
        git(checkout, 'init', '-q')
        git(checkout, 'config', 'user.name', 'Offline publication test')
        git(checkout, 'config', 'user.email', 'offline@example.invalid')
        for attempt in range(attempts):
            git(checkout, 'fetch', str(repository), 'refs/heads/data')
            git(checkout, 'checkout', '-B', 'data', 'FETCH_HEAD')
            # No file from the fetched tree is executable or accepted as configuration.
            listing = git(checkout, 'ls-tree', '-r', 'HEAD').stdout.splitlines()
            for line in listing:
                mode, _, rest = line.split(' ', 2)
                _, name = rest.split('\t', 1)
                if mode != '100644' or not name.startswith(str(DATA) + '/') or Path(name).name not in export.ALLOWED:
                    raise ValueError('UNSAFE_DATA_TREE')
            target = checkout / DATA
            current = export.validate_bundle(target)
            previous = status_of(current)
            if previous and ((previous['last_success_at'] or '') > (proposed['last_success_at'] or '')
                             or previous['last_attempt_at'] > proposed['last_attempt_at']):
                return dict(outcome='older-run-retained', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            for name in OWNED | {'LICENCES.md'}:
                if (bundle / name).exists():
                    shutil.copyfile(bundle / name, target / name)
            statuses = [s for s in current['status']['data'] if s['dataset'] != 'polls'] + [proposed]
            metadata = incoming['status']
            export.pair(target, 'status', export.envelope(statuses, [], metadata['run_url'], metadata['code_sha']))
            export.inventory(target, metadata['run_url'], metadata['code_sha'], proposed['last_attempt_at'])
            export.validate_bundle(target)
            git(checkout, 'add', '--', *[str(DATA / n) for n in sorted(export.ALLOWED) if (target / n).exists()])
            if git(checkout, 'diff', '--cached', '--quiet', check=False).returncode == 0:
                return dict(outcome='unchanged', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            git(checkout, 'commit', '-qm', 'Publish validated offline poll bundle')
            if before_push:
                before_push(attempt)
            pushed = git(checkout, 'push', str(repository), 'HEAD:refs/heads/data', check=False)
            if pushed.returncode == 0:
                return dict(outcome='published', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            if 'non-fast-forward' not in pushed.stderr and 'fetch first' not in pushed.stderr and 'failed to update ref' not in pushed.stderr:
                raise RuntimeError('PUBLICATION_FAILED: ' + pushed.stderr)
        raise RuntimeError('PUBLICATION_RETRIES_EXHAUSTED')
