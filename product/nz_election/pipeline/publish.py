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
from product.nz_election.pipeline.deployment_guard import require_publication_allowed

DATA = Path('product/nz_election/data')
OWNED = {s + ext for s in ('polls', 'averages', 'seats') for ext in ('.json', '.csv')}


def git(root, *args, check=True):
    return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                          text=True, capture_output=True, check=check)


def status_of(envs, family='polls'):
    return next((s for s in envs['status']['data'] if s['dataset'] == family), None)


def success_order(envs, family='polls'):
    if family != 'polls':
        env = envs.get('electorates' if family == 'geography' else 'social/daily' if family == 'social' else 'night/index' if family == 'night' else 'advance-voting' if family == 'advance' else family, {})
        return (env.get('fetched_at') or '', env.get('generated_at', ''))
    if 'polls' not in envs:
        return ('', '')
    return (envs['polls'].get('fetched_at') or '', envs['averages']['generated_at'])


def publish(bundle, repository, *, before_push=None, attempts=3, family='hourly', claim=None, now=None):
    require_publication_allowed(now() if now else None)
    if claim is not None and family != 'social':
        raise ValueError('INVALID_FAMILY')
    if family not in {'hourly', 'daily', 'social', 'night'}:
        raise ValueError('INVALID_FAMILY')
    datasets = ['polls'] if family == 'hourly' else ['social'] if family == 'social' else ['night'] if family == 'night' else [f for f in export.FAMILIES if f not in {'polls', 'social'}]
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
    datasets = [f for f in datasets if status_of(incoming, f) is not None]
    if not datasets:
        raise ValueError('MISSING_FAMILY_STATUS')
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
                    if mode != '100644' or not name.startswith(str(DATA) + '/') or not export.allowed_path(name[len(str(DATA)) + 1:]):
                        raise ValueError('UNSAFE_DATA_TREE')
                git(checkout, 'checkout', '-B', 'data', 'FETCH_HEAD')
            else:
                git(checkout, 'checkout', '--orphan', 'bootstrap-' + str(attempt))
                git(checkout, 'rm', '-rf', '--ignore-unmatch', '.')
            target = checkout / DATA
            current = export.validate_bundle(target) if fetched_sha else {'status': {'data': []}}
            if family == 'night' and 'night/live/current' in current and 'night/live/current' in incoming:
                if current['night/live/current']['data'][0]['raw_xml'] == incoming['night/live/current']['data'][0]['raw_xml']:
                    return dict(outcome='unchanged', attempts=attempt + 1, sha=fetched_sha)
            target.mkdir(parents=True, exist_ok=True)
            statuses = current['status']['data'][:]
            all_older = True
            for dataset in datasets:
                proposed = status_of(incoming, dataset)
                stem = 'electorates' if dataset == 'geography' else 'social/daily' if dataset == 'social' else 'night/index' if dataset == 'night' else 'advance-voting' if dataset == 'advance' else dataset
                owned = {s + ext for s in export.FAMILIES[dataset] for ext in ('.json', '.csv')}
                if dataset == 'night':
                    owned = {s + ext for s in incoming if s.startswith('night/') for ext in ('.json', '.csv')}
                previous = status_of(current, dataset)
                if dataset == 'social':
                    # Ledger accounting must survive stale aggregates and lease retries.
                    old_rows = {r['id']: r for r in current.get('social/credits', {}).get('data', [])}
                    incoming_rows = incoming.get('social/credits', {}).get('data', [])
                    # Receipts identify accepted actual reports without refunding the
                    # conservative charge. Only the leased remote can supply receipts.
                    receipt_prefix = 'social-report/'
                    receipts = {k: v for k, v in current.get('social/credits', {}).get('input_hashes', {}).items()
                                if k.startswith(receipt_prefix)}
                    if claim and claim not in old_rows:
                        raise ValueError('SOCIAL_RESERVATION_CONSUMED')
                    for row in incoming_rows:
                        old = old_rows.get(row['id'])
                        if claim == row['id']:
                            if not old or old['closed'] or old['requests'] or old['spent'] or old != row:
                                raise ValueError('SOCIAL_RESERVATION_CONSUMED')
                            # Charge the entire allowance before exposing collection authority.
                            # Lost runners remain fully accounted for, even without a report.
                            old_rows[row['id']] = dict(old, closed=True, spent=old['reserved'])
                            continue
                        if old and any(old[k] != row[k] for k in ('day', 'cap', 'allocation', 'reserved')):
                            raise ValueError('SOCIAL_LEDGER_CONFLICT')
                        if old == row:
                            continue
                        receipt_key = receipt_prefix + row['id']
                        report_hash = export.digest(export.canonical(row).encode())
                        if receipt_key in receipts:
                            if not old or receipts[receipt_key] != report_hash:
                                raise ValueError('SOCIAL_LEDGER_CONFLICT')
                            continue
                        if old and old['closed']:
                            consumed = old['requests'] == 0 and old['spent'] == old['reserved'] and old['allocation'] > 0
                            if not consumed or not row['closed']:
                                raise ValueError('SOCIAL_LEDGER_CONFLICT')
                            # The final report can add request counts but cannot refund unknown spend.
                            old_rows[row['id']] = dict(row, spent=old['spent'])
                            receipts[receipt_key] = report_hash
                        elif old and (old['spent'] or old['requests']):
                            raise ValueError('SOCIAL_LEDGER_CONFLICT')
                        else:
                            # Distinct run IDs append distinct spending records; never merge via max.
                            old_rows[row['id']] = row
                    metadata = incoming['social/credits']
                    hashes = {k: v for k, v in metadata.get('input_hashes', {}).items()
                              if not k.startswith(receipt_prefix)}
                    hashes.update(receipts)
                    merged_ledger = dict(metadata, data=list(old_rows.values()))
                    if 'input_hashes' in metadata or receipts:
                        merged_ledger['input_hashes'] = hashes
                    from product.nz_election.pipeline.social import validate_ledger
                    validate_ledger(merged_ledger['data'])
                    export.pair(target, 'social/credits', merged_ledger)
                    owned -= {'social/credits.json', 'social/credits.csv'}
                # Validation guarantees canonical UTC strings, so lexical order is instant order.
                # Acquisition wins first; unchanged captures use successful average-generation
                # time. Exact ties retain repository bytes, independently of attempt chronology.
                keep_data = previous and success_order(current, dataset) >= success_order(incoming, dataset)
                if dataset != 'polls' and stem in current and stem in incoming:
                    old_vector = {s['id']: s['fetched_at'] for s in current[stem]['source']}
                    new_vector = {s['id']: s['fetched_at'] for s in incoming[stem]['source']}
                    if not old_vector.keys() <= new_vector.keys() or any(new_vector[k] < old_vector[k] for k in old_vector):
                        keep_data = True
                    elif new_vector.keys() > old_vector.keys() or any(new_vector[k] > old_vector[k] for k in old_vector):
                        keep_data = False
                keep_status = previous and previous['last_attempt_at'] > proposed['last_attempt_at']
                all_older = all_older and bool(keep_status and keep_data)
                if not keep_data:
                    if dataset == 'night' and 'night/index' in incoming and (target / 'night').exists():
                        shutil.rmtree(target / 'night')
                    for name in owned:
                        if (bundle / name).exists():
                            (target / name).parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(bundle / name, target / name)
                # Attempt chronology and successful acquisition chronology are independent.
                merged = dict(previous if keep_status else proposed)
                last_good = previous if keep_data else proposed
                merged.update(last_success_at=last_good['last_success_at'], last_good_run_url=last_good['last_good_run_url'])
                if merged['error_code'] is not None or (dataset == 'advance' and merged['state'] == 'unavailable'):
                    merged['state'] = 'stale' if merged['last_success_at'] else 'unavailable'
                statuses = [s for s in statuses if s['dataset'] != dataset] + [merged]
                metadata = current['status'] if keep_status else incoming['status']
            if all_older and family != 'social':
                return dict(outcome='older-run-retained', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            export.pair(target, 'status', export.envelope(statuses, [], metadata['run_url'], metadata['code_sha']))
            export.merged_licences(target)
            export.inventory(target, metadata['run_url'], metadata['code_sha'], max(r['last_attempt_at'] for r in statuses))
            export.validate_bundle(target)
            git(checkout, 'add', '-A', '--', str(DATA))
            if git(checkout, 'diff', '--cached', '--quiet', check=False).returncode == 0:
                return dict(outcome='unchanged', attempts=attempt + 1, sha=git(checkout, 'rev-parse', 'HEAD').stdout.strip())
            git(checkout, 'commit', '-qm', 'Publish validated poll bundle')
            if before_push:
                before_push(attempt)
            if family == 'social':
                from product.nz_election.pipeline.social import frozen
                from product.nz_election.pipeline.refresh import utc_now
                if frozen(utc_now()):
                    return dict(outcome='frozen', attempts=attempt + 1, sha=fetched_sha)
            require_publication_allowed(now() if now else None)
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
    parser.add_argument('--claim')
    parser.add_argument('--family', choices=['hourly', 'daily', 'social', 'night'], default='hourly')
    args = parser.parse_args()
    # Validate the artifact before any git operation or credential use.
    incoming = export.validate_bundle(args.bundle)
    if args.family == 'social':
        from product.nz_election.pipeline.social import frozen
        from product.nz_election.pipeline.refresh import utc_now
        if frozen(utc_now()):
            print('Social publication frozen.')
            return
    token = os.environ['GITHUB_TOKEN']
    authorization = base64.b64encode(('x-access-token:' + token).encode()).decode()
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                      GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + authorization)
    result = publish(args.bundle, 'https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '.git', family=args.family, claim=args.claim)
    if args.claim and result['outcome'] == 'published' and os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('claimed=true\n')
    report = dict(result, status=status_of(incoming, 'polls' if args.family == 'hourly' else 'social' if args.family == 'social' else 'geography'))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write('## Data publication\n\n```json\n' + json.dumps(report, indent=2) + '\n```\n')
    print(json.dumps(result))
    if any(r['error_code'] is not None for r in incoming['status']['data']
           if r['dataset'] in (['polls'] if args.family == 'hourly' else ['social'] if args.family == 'social' else [f for f in export.FAMILIES if f not in {'polls', 'social'}])):
        raise SystemExit('FAIL refresh: handled failure status published')


if __name__ == '__main__':
    main()
