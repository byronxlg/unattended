# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Synthetic offline verification of the import chain on a disposable bare target."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import build, export, fixtures, night_live, publish, result_import, settlement_capture
from product.nz_election.pipeline.daily_refresh import daily_refresh

LABEL = 'Synthetic offline fixture rehearsal, never real election results'
# Scenario input to the existing offline APIs, not a change to any production clock or guard.
SCENARIO = '2026-11-28T00:00:00Z'
REF = 'refs/heads/rehearsal-data'


def fixture(state):
    name = 'result-states/2026-11-' + ('07-preliminary-final' if state == 'settled' else '27-official') + '.json'
    return json.loads(fixtures.captures(paths={name})[name])


def synthetic_provenance(env, row):
    if env['run_url'] != LABEL or row['raw_xml'] != fixture('settled')['raw']:
        raise ValueError('REHEARSAL_SYNTHETIC_REQUIRED')


def register(root, path):
    raw = (root / path).read_bytes()
    captured = json.loads(raw)
    manifest = root / 'manifest.json'
    entries = json.loads(manifest.read_text())['entries'] if manifest.exists() else []
    entries.append(dict(path=path, sha256=export.digest(raw), bytes=len(raw),
                        retrieved_at=captured['retrieved_at'], source=captured['acquisition_source'],
                        capture_kind='synthetic', notes=LABEL))
    manifest.write_text(json.dumps(dict(entries=entries), indent=2) + '\n')
    # Registration must remain unusable by the production importer.
    try:
        result_import.capture_bytes(path, root)
    except ValueError as exc:
        if str(exc) != 'NIGHT_CAPTURE_NOT_REAL':
            raise
    else:
        raise AssertionError('Synthetic capture accepted as real')


def synthetic_capture(path, root):
    raw = fixtures.captures(root, paths={path})[path]
    entry = next(e for e in json.loads((root / 'manifest.json').read_text())['entries'] if e['path'] == path)
    if entry['capture_kind'] != 'synthetic' or entry['notes'] != LABEL:
        raise ValueError('REHEARSAL_SYNTHETIC_REQUIRED')
    captured = json.loads(raw)
    if captured not in (fixture('settled'), fixture('official')):
        raise ValueError('REHEARSAL_SYNTHETIC_REQUIRED')
    return captured, export.digest(raw)


def pin(repository, sha, checkout):
    return result_import.pin(repository, sha, checkout, ref=REF)


def publication(bundle, repository, **kwargs):
    return publish.publish(bundle, repository, rehearsal=True, **kwargs)


def night_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in (root / 'night').rglob('*') if p.is_file()}


def rehearse(out, remote):
    out, remote = out.resolve(), remote.resolve()
    if not remote.is_dir() or publish.git(remote, 'rev-parse', '--is-bare-repository').stdout.strip() != 'true':
        raise ValueError('LOCAL_BARE_REPOSITORY_REQUIRED')
    if publish.git(remote, 'for-each-ref', '--format=%(refname)').stdout.strip():
        raise ValueError('EMPTY_REHEARSAL_REPOSITORY_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    code_sha = publish.git(Path.cwd(), 'rev-parse', 'HEAD').stdout.strip()
    (out / 'README.txt').write_text(LABEL + '\nScenario input: ' + SCENARIO + '\n')
    reports = []
    with tempfile.TemporaryDirectory(prefix='nz-import-rehearsal-') as tmp:
        work = Path(tmp)
        bundle = work / 'bundle'
        raw = fixture('settled')
        daily_refresh(bundle, loaders={'night': lambda: night_live.loaded(raw)},
                      now=raw['retrieved_at'], sha=code_sha, run_url=LABEL)
        original = publication(bundle, remote, family='night')['sha']
        checkout = work / 'original'
        checkout.mkdir()
        pin(remote, original, checkout)
        baseline = night_bytes(checkout / publish.DATA)
        root = out / 'captures'
        root.mkdir()
        settled_path = 'synthetic-settled.json'
        metadata = settlement_capture.prepare(checkout / publish.DATA, root / settled_path,
                                               provenance_check=synthetic_provenance)
        assert metadata['sha256'] == export.digest((root / settled_path).read_bytes())
        register(root, settled_path)
        official_path = 'synthetic-official.json'
        (root / official_path).write_text(json.dumps(fixture('official')) + '\n')
        register(root, official_path)
        print('PASS synthetic capture preparation and registration pinned_sha=' + original)
        previous = original
        for step in ('settled', 'official', 'rollback'):
            rollback = step == 'rollback'
            report = result_import.run('settled' if rollback else step,
                settled_path if step == 'settled' else official_path,
                original if rollback else previous, repository=remote, now=lambda: SCENARIO,
                run_url=LABEL, rollback=rollback, root=root, capture_reader=synthetic_capture,
                pin_data=pin, publisher=publication)
            sha = report['published_data_sha']
            served_checkout = work / step
            served_checkout.mkdir()
            assert pin(remote, sha, served_checkout) == sha
            assert publish.git(served_checkout, 'rev-parse', 'HEAD').stdout.strip() == sha
            data = served_checkout / publish.DATA
            served = out / step / 'served'
            build.build(data, served, built=SCENARIO, sha=code_sha, data_sha=sha, run_url=LABEL)
            # Read the promoted publication target, not the importer staging directory.
            manifest = json.loads((served / 'build-manifest.json').read_text())
            envs = export.validate_bundle(served / 'data')
            row = envs['night/live/current']['data'][0]
            state = row.get('result_state', 'preliminary')
            assert manifest['code_sha'] == code_sha
            assert manifest['data']['data_sha'] == sha
            assert night_bytes(served / 'data') == night_bytes(data)
            assert state == ('preliminary' if rollback else step)
            if rollback:
                assert night_bytes(served / 'data') == baseline
            else:
                assert row['preliminary_package'] == export.validate_bundle(checkout / publish.DATA)['night/live/current']
            line = f'PASS {step} served_sha={sha} result_state={state}'
            print(line)
            reports.append(dict(report, served_sha=sha, result_state=state, pass_line=line))
            previous = sha
    assert publish.git(remote, 'for-each-ref', '--format=%(refname)').stdout.splitlines() == [REF]
    print('PASS isolated target: data ref absent; no Pages dispatch')
    report = dict(label=LABEL, scenario_input=SCENARIO, code_sha=code_sha, original_data_sha=original, steps=reports)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('artifacts/import-rehearsal'))
    parser.add_argument('--remote', type=Path, help='Empty local bare Git repository; never a remote URL')
    args = parser.parse_args()
    if args.remote:
        rehearse(args.out, args.remote)
    else:
        with tempfile.TemporaryDirectory(prefix='nz-import-target-') as tmp:
            remote = Path(tmp)
            publish.git(remote, 'init', '--bare', '-q')
            rehearse(args.out, remote)


if __name__ == '__main__':
    main()
