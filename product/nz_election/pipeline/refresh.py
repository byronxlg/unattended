# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Refresh a validated bundle from checked captures or bounded live acquisition."""
import argparse
from datetime import date, datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export
from product.nz_election.pipeline.average import METHOD, trend
from product.nz_election.pipeline.fixtures import ROOT, captures
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import parse_polls, compare_revisions
from product.nz_election.pipeline.seats import project
from product.nz_election.pipeline.storage import replace_directory

PRODUCT = Path(__file__).resolve().parents[1]


def config(name):
    return json.loads((PRODUCT / 'config' / (name + '.json')).read_text())


def code_sha():
    return os.environ.get('GITHUB_SHA') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()


def utc_now():
    return export.timestamp(datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'))


def source_entries():
    from product.nz_election.pipeline.fixtures import GOLDEN_PATHS
    entries = json.loads((ROOT / 'manifest.json').read_text())['entries']
    wiki = next(e for e in entries if e['path'] == 'wikipedia/polls-2026.wikitext')
    source = config('sources')['wikipedia']
    p = dict(id='P', url=source['url'], revision=source['revision'], licence=source['licence'],
             fetched_at=wiki['captured_at'], history_url=source['history_url'])
    e = [dict(id='E:' + row['path'], url=row['url'], revision=row['revision'], licence=row['licence'],
              fetched_at=row['captured_at'], history_url=None) for row in entries if row['path'] in GOLDEN_PATHS]
    return [p], e


def normalize(poll, history=False):
    from product.nz_election.pipeline.average import scaled_vector
    shares, unit = scaled_vector(poll)
    ref = poll['source_ref']
    if isinstance(ref, str):
        ref = [dict(source_id='P', revision=poll['revision'], row=ref)]
    result = dict(revision=poll['revision'], source_ref=ref, fieldwork_start=poll['fieldwork_start'],
                  fieldwork_end=poll['fieldwork_end'], shares=shares,
                  scale=unit, reference_urls=poll['reference_urls'])
    if not history:
        result.update(id=poll['id'], observed_at=poll['fieldwork_end'], pollster=poll['pollster'], sample=poll['sample'],
                      history=[normalize(h, True) for h in poll.get('history', [])])
    return result


def previous_parser_rows(rows):
    from product.nz_election.pipeline.average import values
    return [dict({k: v for k, v in p.items() if k != 'scale'}, shares=values(p)) for p in rows]


def licences(source=None):
    source = source or config('sources')['wikipedia']
    return f'''# Dataset licences

Polls, averages, theoretical seats and their CSV siblings: CC BY-SA 4.0.
Source: Wikipedia contributors. CC BY-SA 4.0. Parsed and averaged by this project.
Revision: {source['url']}
Contributor history: {source['history_url']}
Licence: https://creativecommons.org/licenses/by-sa/4.0/

Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.
EC captures validate the 2023 calculation and supply the explicitly labelled electorate assumption.
The poll licence does not relicense EC material.

Method: Electoral Act 1993, sections 191-193. Legislation has no copyright.
Validation data: Electoral Commission.

CSV contract: provenance columns repeat on each row. Nested values use canonical JSON
in *_json columns. Empty scalar cells mean null; booleans are true/false. Counts mean
payload records. Manifest hashes and sizes exclude self-reference.
Poll totals are the sum of each row's shares divided by its scale, including Others;
no input is forced to total 100. Fixture runs are offline verification, not live polling.
'''


def refresh(out, *, now=None, end_date=None, parse=parse_polls, run_url='offline-verification', sha=None, acquire=None):
    out = Path(out).absolute()
    if out.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    now = export.timestamp(utc_now() if now is None else now, 'refresh.now')
    sha = sha or code_sha()
    with (out.parent / ('.' + out.name + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = export.validate_bundle(out) if out.exists() else {}
        with tempfile.TemporaryDirectory(prefix='.refresh-', dir=out.parent) as tmp:
            stage = Path(tmp) / 'bundle'
            if out.exists():
                shutil.copytree(out, stage)
            else:
                stage.mkdir()
            good = old.get('status', {}).get('data', [])
            prior = next((s for s in good if s['dataset'] == 'polls'), {})
            error = None
            try:
                from product.nz_election.pipeline.fixtures import GOLDEN_PATHS
                raw = captures(paths=GOLDEN_PATHS | {'wikipedia/polls-2026.api.json', 'wikipedia/polls-2026.wikitext'})
                sources, ec = source_entries()
                wikitext = raw['wikipedia/polls-2026.wikitext'].decode()
                if acquire is not None:
                    acquired = acquire()
                    sources[0].update(revision=acquired['revision'], fetched_at=acquired['fetched_at'],
                                      url='https://en.wikipedia.org/w/index.php?oldid=' + acquired['revision'])
                    wikitext = acquired['wikitext']
                parsed = parse(wikitext, sources[0]['revision'],
                               config('party-map'), config('poll-identities'))
                compared = compare_revisions(previous_parser_rows(old.get('polls', {}).get('data', [])),
                                             parsed, config('poll-review'))
                polls = [normalize(p) for p in compared.polls]
                start = min(date.fromisoformat(p['fieldwork_end']) for p in polls)
                from zoneinfo import ZoneInfo
                end = date.fromisoformat(end_date) if end_date else datetime.fromisoformat(now.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland')).date()
                days = [start + timedelta(days=n) for n in range((end - start).days + 1)]
                if not days:
                    raise ValueError('INVALID_WINDOW')
                averages = trend(polls, days, config('party-map'), config('poll-review'))
                config_hashes = {'config/' + name + '.json': export.digest((PRODUCT / 'config' / (name + '.json')).read_bytes())
                                 for name in ('party-map', 'poll-identities', 'poll-review')}
                ec_hashes = {'fixtures/' + name: export.digest(value) for name, value in raw.items() if name.startswith('ec-')}
                export.pair(stage, 'polls', export.envelope(polls, sources, run_url, sha))
                export.pair(stage, 'averages', export.envelope(averages, sources, run_url, sha,
                            inputs={'polls.json': export.digest((stage / 'polls.json').read_bytes()), **config_hashes}, method=METHOD, generated=now))
                export.pair(stage, 'seats', export.envelope(project(averages[-1]), sources + ec, run_url, sha,
                            inputs={'averages.json': export.digest((stage / 'averages.json').read_bytes()), **ec_hashes}, method=METHOD, generated=now))
                state, success, good_run = 'fresh', sources[0]['fetched_at'], run_url
                message = ('Wikipedia revision ' + sources[0]['revision'] + ' acquired and validated.'
                           if acquire is not None else 'Offline verification from immutable captures. Not live data.')
            except ValueError as exc:
                # Restore the entire family, including files written before validation failed.
                shutil.rmtree(stage)
                if out.exists():
                    shutil.copytree(out, stage)
                else:
                    stage.mkdir()
                error = getattr(exc, 'code', 'validation_error')
                state = 'stale' if 'polls' in old else 'unavailable'
                success, good_run = prior.get('last_success_at'), prior.get('last_good_run_url')
                message = 'Refresh failed; retained last-good data.' if success else 'No data yet. A validated refresh is needed.'
                if isinstance(exc, ParseDrift):
                    message += ' ' + json.dumps(dict(reason=exc.reason, locator=exc.public_locator), ensure_ascii=True)
            status = dict(id='status-polls', source_ref=[], observed_at=now, dataset='polls', state=state,
                          last_attempt_at=now, last_success_at=success, last_good_run_url=good_run,
                          error_code=error, message=message)
            statuses = [s for s in good if s['dataset'] != 'polls'] + [status]
            export.pair(stage, 'status', export.envelope(statuses, [], run_url, sha))
            if error is None:
                (stage / 'LICENCES.md').write_text(licences(sources[0]))
            elif not (stage / 'LICENCES.md').exists():
                (stage / 'LICENCES.md').write_text(licences())
            if (stage / 'electorates.json').exists():
                export.merged_licences(stage)
            export.inventory(stage, run_url, sha, now)
            export.validate_bundle(stage)
            replace_directory(stage, out)
            return status


def main(*, now=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    from product.nz_election.pipeline.sunsets import skip, require_collection, SunsetReached, ended
    if not args.fixtures and skip('hourly', now() if now else None):
        return
    attempted_revision = None
    if args.fixtures:
        status = refresh(args.out)
    else:
        from product.nz_election.pipeline.deployment_guard import require_publication_allowed
        require_publication_allowed()
        from product.nz_election.pipeline.fetch import acquire
        run_url = os.environ['GITHUB_SERVER_URL'] + '/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']
        def live():
            nonlocal attempted_revision
            require_collection('hourly', now() if now else None)
            result = acquire()
            attempted_revision = result['revision']
            return result
        try:
            status = refresh(args.out, acquire=live, run_url=run_url, sha=os.environ['GITHUB_SHA'])
        except SunsetReached as exc:
            ended(exc.kind)
            return
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('validated=true\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write('## Poll refresh\n\n```json\n' + json.dumps(dict(status, attempted_revision=attempted_revision), indent=2) + '\n```\n')
    if status['state'] != 'fresh':
        detail = ' ' + status['message'] if status['error_code'] == 'parse_drift' else ''
        raise SystemExit('FAIL refresh: ' + status['error_code'] + detail)
    if args.fixtures:
        print('Offline verification: immutable captures, not live data')
    print('PASS refresh: polls bundle')


if __name__ == '__main__':
    main()
