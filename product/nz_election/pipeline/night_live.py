# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Serial Actions acquisition; a complete validated cycle is the transaction unit."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, fetch, night, xml_parser
from product.nz_election.pipeline.deployment_guard import END, require_publication_allowed

MODE = 'Live preliminary results'
REHEARSAL = 'Recorded demo'
REFERENCES = ('electorates.xml', 'parties.xml', 'candidates.xml')
FLOOR = 300
CLOSE = END.replace(day=8)


def stamp(now):
    return now().astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def require_open(now):
    instant = now()
    require_publication_allowed(stamp(lambda: instant))
    if instant >= CLOSE:
        raise ValueError('NIGHT_CLOSED')
    if instant < END:
        raise ValueError('NIGHT_NOT_OPEN')


def parsed(raw, *, rehearsal=False):
    if type(raw) is not dict or any(type(k) is not str or type(v) is not str for k, v in raw.items()) or not set(REFERENCES) <= raw.keys():
        raise ValueError('NIGHT_PARTIAL')
    refs = xml_parser.references(*(raw[n].encode() for n in ('parties.xml', 'electorates.xml', 'candidates.xml')))
    if not rehearsal and set(refs['electorates']) != {str(n) for n in range(1, 72)}:
        raise ValueError('NIGHT_REGISTRY')
    if not rehearsal:
        from product.nz_election.pipeline import fixtures
        anchor = fixtures.captures(paths={'ec-2026-media-xml/electorates.xml'})
        expected = xml_parser.records(xml_parser.document(anchor['ec-2026-media-xml/electorates.xml'], 'electorates'),
                                      'electorate', 'e_no', ['electorate_name'])
        if refs['electorates'] != expected:
            raise ValueError('NIGHT_REGISTRY')
    paths = [f'e{int(n):02}/e{int(n):02}.xml' for n in sorted(refs['electorates'], key=int)]
    if set(raw) != set(REFERENCES) | {'election.xml'} | set(paths):
        raise ValueError('NIGHT_PARTIAL')
    row = xml_parser.election(raw['election.xml'].encode(), refs)
    row['leaders'] = {}
    for ident, path in zip(sorted(refs['electorates'], key=int), paths):
        detail = xml_parser.detail(raw[path].encode(), refs)
        if detail['electorate_id'] != ident:
            raise ValueError('NIGHT_REFERENCE')
        detail['source_ref'] = ['actions-xml/' + path]
        row['leaders'][ident] = detail
    return refs, row


def cycle(*, acquire, now, rehearsal=False, monotonic=time.monotonic):
    deadline = monotonic() + 1200
    transport = acquire
    def acquire(name):
        if monotonic() >= deadline:
            raise ValueError('NIGHT_CYCLE_TIMEOUT')
        return transport(name)
    if not rehearsal:
        require_open(now)
    raw = {}
    for name in REFERENCES:
        raw[name] = acquire(name).decode('utf-8')
    refs = xml_parser.references(*(raw[n].encode() for n in ('parties.xml', 'electorates.xml', 'candidates.xml')))
    raw['election.xml'] = acquire('election.xml').decode('utf-8')
    for ident in sorted(refs['electorates'], key=int):
        name = f'e{int(ident):02}/e{int(ident):02}.xml'
        raw[name] = acquire(name).decode('utf-8')
    # A reference rotation during results acquisition invalidates the entire pending cycle.
    for name in REFERENCES:
        if acquire(name).decode('utf-8') != raw[name]:
            raise ValueError('NIGHT_REFERENCE_CHANGED')
    refs, row = parsed(raw, rehearsal=rehearsal)
    return dict(raw=raw, retrieved_at=stamp(now), reference_version=refs['reference_version'], result=row)


def loaded(captured, *, rehearsal=False):
    payloads, sources, hashes = night.load()
    root = fetch.NIGHT_ROOTS[1 if rehearsal else 0]
    refs, result = parsed(captured['raw'], rehearsal=rehearsal)
    for path, text in captured['raw'].items():
        ident = 'actions-xml/' + path
        digest = export.digest(text.encode())
        sources.append(dict(id=ident, url=root + path, revision=digest, licence='Copyright Electoral Commission; no open licence stated.',
                            fetched_at=captured['retrieved_at'], history_url=None))
        hashes[ident] = digest
    mode = REHEARSAL if rehearsal else MODE
    row = dict(result, id='night/live/current', source_ref=['actions-xml/election.xml'], mode=mode,
               packaging_label='Packaged by the site', retrieved_at=captured['retrieved_at'], raw_xml=captured['raw'], rehearsal=rehearsal)
    payloads['night/live/current'] = [row]
    payloads['night/references/live'] = [dict(refs, id='live', source_ref=['actions-xml/' + n for n in REFERENCES])]
    payloads['night/index'].append(dict(id='live', sequence_id='live', source_ref=row['source_ref'], mode=mode,
        reference_path='night/references/live.json', reference_version=refs['reference_version'], snapshot_paths=['night/live/current.json']))
    return payloads, sources, hashes


def validate_row(row, env, reference):
    if row.get('packaging_label') != 'Packaged by the site' or type(row.get('rehearsal')) is not bool:
        raise ValueError('NIGHT_LIVE')
    refs, result = parsed(row['raw_xml'], rehearsal=row['rehearsal'])
    if set(row) != set(result) | {'id', 'source_ref', 'mode', 'retrieved_at', 'raw_xml', 'rehearsal', 'packaging_label'}:
        raise ValueError('NIGHT_LIVE')
    if any(row.get(k) != v for k, v in result.items()) or any(reference.get(k) != v for k, v in refs.items()):
        raise ValueError('NIGHT_LIVE')
    export.timestamp(row['retrieved_at'])
    sources = {s['id']: s for s in env['source']}
    root = fetch.NIGHT_ROOTS[1 if row['rehearsal'] else 0]
    for path, text in row['raw_xml'].items():
        ident = 'actions-xml/' + path
        if (env['input_hashes'].get(ident) != export.digest(text.encode()) or sources[ident]['url'] != root + path
                or sources[ident]['fetched_at'] != row['retrieved_at'] or sources[ident]['revision'] != export.digest(text.encode())):
            raise ValueError('NIGHT_LIVE')
    if not row['rehearsal']:
        require_open(lambda: datetime.fromisoformat(row['retrieved_at'].replace('Z', '+00:00')))


class Deployment:
    """The data ref and served build manifest survive runner loss; memory only avoids repeat reads."""
    def __init__(self, now):
        self.now = now
        self.confirmed_sha = None

    def recover(self):
        require_open(self.now)
        refs = json.loads(subprocess.check_output(['gh', 'api',
            'repos/' + os.environ['GITHUB_REPOSITORY'] + '/git/matching-refs/heads/data'], timeout=60))
        head = next((r['object']['sha'] for r in refs if r['ref'] == 'refs/heads/data'), None)
        return self.ensure(head) if head else False

    def ensure(self, sha):
        require_open(self.now)
        if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('NIGHT_DATA_SHA')
        if sha == self.confirmed_sha:
            return False
        if fetch.deployed_data_sha() == sha:
            self.confirmed_sha = sha
            return False
        key = 'night-' + os.environ['GITHUB_RUN_ID'] + '-' + str(time.monotonic_ns())
        subprocess.run(['gh', 'workflow', 'run', 'pages.yml', '--ref', 'main',
                        '-f', 'data_sha=' + sha, '-f', 'night_cycle=' + key], check=True, timeout=120)
        wait_until = time.monotonic() + 600
        while True:
            if time.monotonic() >= wait_until:
                raise OSError('PAGES_WAIT_TIMEOUT')
            runs = json.loads(subprocess.check_output(['gh', 'run', 'list', '--workflow', 'pages.yml', '--limit', '100',
                              '--json', 'status,conclusion,displayTitle'], timeout=60))
            run = next((r for r in runs if r['displayTitle'] == key), None)
            if run and run['status'] == 'completed':
                if run['conclusion'] != 'success':
                    raise OSError('PAGES_DEPLOYMENT_FAILED')
                self.confirmed_sha = sha
                return True
            time.sleep(30)


class Runner:
    def __init__(self, *, acquire, now, monotonic, sleep, commit, rehearsal=False, log=print, recover=None):
        self.acquire, self.now, self.monotonic, self.sleep, self.commit = acquire, now, monotonic, sleep, commit
        self.rehearsal = rehearsal
        self.log = log
        self.recover = recover
        self.next_cycle = 0
        self.last_good = None
        self.digest = None

    def tick(self):
        self.sleep(max(0, self.next_cycle - self.monotonic()))
        self.next_cycle = self.monotonic() + FLOOR
        try:
            # A recovery consumes this cycle's slot, so it cannot double the deployment rate.
            if self.recover and self.recover():
                return 'recovered'
            captured = cycle(acquire=self.acquire, now=self.now, rehearsal=self.rehearsal)
            digest = export.digest(export.canonical(captured['raw']).encode())
            changed = digest != self.digest
            if changed or not self.rehearsal:
                if not self.rehearsal:
                    require_open(self.now)
                self.commit(captured)
            self.last_good, self.digest = captured, digest
            return 'changed' if changed else 'unchanged'
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            self.log('Retained last good cycle: ' + str(exc), flush=True)
            return 'retained'


def main(*, now=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rehearsal', action='store_true')
    parser.add_argument('--out', type=Path, default=Path('artifacts/night-rehearsal'))
    args = parser.parse_args()
    now = now or (lambda: datetime.now(timezone.utc))
    scheduled = os.environ.get('GITHUB_EVENT_NAME') == 'schedule'
    if scheduled:
        args.rehearsal = False
    if not args.rehearsal:
        try:
            require_open(now)
        except ValueError:
            if scheduled:
                return 0
            raise
    root = fetch.NIGHT_ROOTS[1 if args.rehearsal else 0]
    run_url = os.environ['GITHUB_SERVER_URL'] + '/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']
    deployment = Deployment(now) if not args.rehearsal else None
    def commit(captured):
        from product.nz_election.pipeline.daily_refresh import daily_refresh
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / 'data'
            daily_refresh(bundle, loaders={'night': lambda: loaded(captured, rehearsal=args.rehearsal)}, now=captured['retrieved_at'],
                          sha=os.environ['GITHUB_SHA'], run_url=run_url)
            envs = export.validate_bundle(bundle)
            if 'night/live/current' not in envs:
                raise ValueError('NIGHT_CYCLE_INVALID')
            if args.rehearsal:
                import shutil
                args.out.mkdir(parents=True, exist_ok=True)
                shutil.copytree(bundle, args.out / captured['retrieved_at'].replace(':', ''), dirs_exist_ok=True)
                return
            result = subprocess.run([sys.executable, 'product/nz_election/pipeline/publish.py', '--family', 'night', '--bundle', str(bundle)], check=True, capture_output=True, text=True, timeout=120)
            publication = json.loads(result.stdout)
            deployment.ensure(publication['sha'])
    runner = Runner(acquire=lambda path: fetch.night_xml(root, path), now=now, monotonic=time.monotonic,
                    sleep=time.sleep, commit=commit, rehearsal=args.rehearsal,
                    recover=deployment.recover if deployment else None)
    deadline = time.monotonic() + (600 if args.rehearsal else 300 * 60)
    while time.monotonic() < deadline:
        if not args.rehearsal and now() >= CLOSE:
            return 0
        print(runner.tick(), flush=True)
    if not args.rehearsal:
        if now() >= CLOSE:
            return 0
        require_open(now)
        subprocess.run(['gh', 'workflow', 'run', 'nz-election-night-live.yml', '--ref', 'main'], check=True, timeout=120)


def verify_contract():
    """Offline executable transport contract, also used by the night verifier."""
    from product.nz_election.tests.night_live_cases import Clock, captures
    clock, raw, commits, calls = Clock(), captures(), [], []
    def acquire(path):
        calls.append(path)
        return raw[path]
    runner = Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic, sleep=clock.sleep, commit=commits.append, log=lambda *a, **k: None)
    assert runner.tick() == 'changed'
    assert calls[:4] == list(REFERENCES) + ['election.xml']
    assert len(commits[0]['result']['leaders']) == 71
    assert runner.tick() == 'unchanged' and clock.seconds == FLOOR
    raw['e71/e71.xml'] = b'<broken>'
    assert runner.tick() == 'retained' and len(commits) == 2
    require_open(clock.now)


if __name__ == '__main__':
    main()
