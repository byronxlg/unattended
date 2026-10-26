# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Artifact-only publication rehearsal using the night runner and leased publisher."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import build, night_live, publish
from product.nz_election.tests.night_live_cases import Clock, captures


class ArtifactDeployment(night_live.Deployment):
    def __init__(self, now, remote, out, code_sha, run_url, *, fail=False):
        super().__init__(now)
        self.remote, self.out = remote, out
        self.code_sha, self.run_url, self.fail = code_sha, run_url, fail

    def guard(self):
        # This adapter has no remote writer or Pages dispatch capability.
        pass

    def head(self):
        result = publish.git(self.remote, 'rev-parse', '--verify', 'refs/heads/rehearsal-data', check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def served(self):
        path = self.out / 'served/build-manifest.json'
        return json.loads(path.read_text())['data']['data_sha'] if path.exists() else None

    def deploy(self, sha):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp) / 'checkout'
            publish.git(self.remote, 'clone', '--no-checkout', str(self.remote), str(checkout))
            publish.git(checkout, 'checkout', '--detach', sha)
            actual = publish.git(checkout, 'rev-parse', 'HEAD').stdout.strip()
            pending = self.out / 'pending'
            # Keep the renderer's freeze guard intact with an explicit simulated post-close build clock.
            build.build(checkout / publish.DATA, pending, built=night_live.stamp(lambda: night_live.END),
                        sha=self.code_sha, data_sha=actual, run_url=self.run_url)
            attempts = self.out / 'deployment-attempts.json'
            history = json.loads(attempts.read_text()) if attempts.exists() else []
            history.append(dict(data_sha=actual, outcome='injected-failure' if self.fail else 'promoted'))
            attempts.write_text(json.dumps(history, indent=2) + '\n')
            if self.fail:
                assert self.served() is None, 'Failed first deployment exposed a site'
                raise OSError('PAGES_DEPLOYMENT_FAILED: injected artifact promotion failure')
            served = self.out / 'served'
            pending.rename(served)


def rehearse(out, *, code_sha, run_url, remote=None):
    # Git commands change directory, so the workflow's relative artifact path must be anchored first.
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    remote = remote.resolve() if remote is not None else out / 'repository.git'
    if not remote.exists():
        remote.mkdir()
        publish.git(remote, 'init', '--bare', '-q')
    def production_ref():
        return publish.git(remote, 'rev-parse', '--verify', 'refs/heads/data', check=False).stdout.strip()
    before = production_ref()
    clock = Clock()
    # Deliberately inside the production freeze: only this local target is exempt.
    clock.origin = datetime(2026, 11, 7, 5, tzinfo=timezone.utc)
    raw = captures(demo=True)
    events = []
    deployment = ArtifactDeployment(clock.now, remote, out, code_sha, run_url, fail=True)
    def acquire(path):
        if not events:
            assert deployment.head() is None and production_ref() == before
            events.append('first-feed-failure')
            raise OSError('injected first-feed failure')
        return raw[path]
    def publication(bundle):
        result = publish.publish(bundle, remote, family='night', rehearsal=True, now=lambda: night_live.stamp(clock.now))
        events.append('published')
        return result
    def commit(captured):
        night_live.publish_cycle(captured, rehearsal=True, publication=publication, deployment=deployment,
                                 code_sha=code_sha, run_url=run_url)
    def recover():
        # A fresh adapter proves recovery uses durable refs/manifest, not process memory.
        return ArtifactDeployment(clock.now, remote, out, code_sha, run_url).recover()
    runner = night_live.Runner(acquire=acquire, now=clock.now, monotonic=clock.monotonic,
                              sleep=clock.sleep, commit=commit, rehearsal=True, recover=recover)
    outcomes = night_live.run_until(runner, 600, successor=lambda: events.append('ready-to-chain'))
    assert outcomes == ['retained', 'retained', 'recovered'], outcomes
    assert events == ['first-feed-failure', 'published', 'ready-to-chain'], events
    assert before == production_ref(), 'Production ref changed'
    attempts = json.loads((out / 'deployment-attempts.json').read_text())
    assert [a['outcome'] for a in attempts] == ['injected-failure', 'promoted']
    assert all(a['data_sha'] == deployment.head() for a in attempts)
    manifest = json.loads((out / 'served/build-manifest.json').read_text())
    assert manifest['code_sha'] == code_sha
    assert manifest['data']['data_sha'] == deployment.head()
    report = dict(label='Offline verification, recorded demo with synthetic missing details',
                  outcomes=outcomes, events=events, deployment_attempts=attempts, code_sha=code_sha, data_sha=deployment.head(),
                  production_ref_before=before, production_ref_after=production_ref(),
                  simulated_seconds=clock.seconds)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    # The artifact carries only reviewable site bytes and evidence, never executable git metadata.
    if remote == out / 'repository.git':
        shutil.rmtree(remote)
    return report


def successor(out, code_sha):
    report = json.loads((out / 'report.json').read_text())
    manifest = json.loads((out / 'served/build-manifest.json').read_text())
    assert manifest['code_sha'] == report['code_sha'] == code_sha
    assert manifest['data']['data_sha'] == report['data_sha']
    clock = Clock()
    clock.origin = night_live.CLOSE
    def forbidden(*args):
        raise AssertionError('bounded stop performed work')
    runner = night_live.Runner(acquire=forbidden, now=clock.now, monotonic=clock.monotonic,
                              sleep=forbidden, commit=forbidden, rehearsal=True, recover=forbidden)
    assert night_live.run_until(runner, 600, successor=forbidden) == []
    assert night_live.chain(clock.now, rehearsal_generation=1) is False
    print('PASS successor: pinned code/data manifest and bounded stop')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('artifacts/night-publication'))
    parser.add_argument('--generation', type=int, choices=(0, 1), default=0)
    parser.add_argument('--chain', action='store_true')
    args = parser.parse_args()
    code_sha = os.environ.get('REHEARSAL_CODE_SHA') or os.environ['GITHUB_SHA']
    actual = publish.git(Path.cwd(), 'rev-parse', 'HEAD').stdout.strip()
    assert actual == code_sha
    if args.chain:
        night_live.chain(lambda: datetime.now(timezone.utc), rehearsal_generation=args.generation)
    elif args.generation == 1:
        successor(args.out, code_sha)
    else:
        run_url = os.environ['GITHUB_SERVER_URL'] + '/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']
        print(json.dumps(rehearse(args.out, code_sha=actual, run_url=run_url), indent=2))
        print('PASS publication rehearsal')


if __name__ == '__main__':
    main()
