"""Regression cases from the 1271c0e review; synthetic transports only."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.tests.test_social import aggregate, classifier, fixture, post, response, run_row, DAY, NOW
from product.nz_election.tests.design_checks import provenance


def test_validator_rejects_identifiers_in_permitted_model_field():
    row = aggregate()
    row['model_versions'] = ['jev-fictional-post-id-123456789']
    with pytest.raises(ValueError, match='INVALID_SOCIAL_MODEL'):
        export.validate_envelope(export.envelope([row], [], 'offline-verification', 'fixture'), 'social/daily')


def test_unknown_upstream_model_is_sanitized(tmp_path, capsys):
    body = response()
    body['model'] = 'jev-fictional-post-id-123456789'
    rows, excluded = social.classify([post()], key='fiction', send=classifier(body))
    assert rows == []
    assert excluded == dict(duplicate=0, unsupported=0, irrelevant=0, classification=1)
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=None attempt=1 check=model\n'
    upstream = social.fixture_send()
    def send(method, *args):
        return classifier(body)(method, *args) if method == 'POST' else upstream(method, *args)
    assert social.refresh_social(tmp_path / 'data', DAY, now=NOW, send=send, sleep=lambda _: None) == 'SOCIAL_UPSTREAM_FAILED'
    for path in (tmp_path / 'data').rglob('*'):
        if path.is_file():
            assert b'jev-fictional-post-id' not in path.read_bytes()


def test_freeze_cli_preserves_page_and_blocks_delayed_deployment(tmp_path):
    out = tmp_path / 'output'
    build(tmp_path / 'absent', out, built='2026-11-06T10:00:00Z')
    before = (out / 'social/poc/index.html').read_bytes()
    # A build must not replace the already served pre-freeze state.
    with pytest.raises(ValueError, match='PUBLICATION_FROZEN'):
        build(tmp_path / 'absent', out, built='2026-11-06T11:00:00Z')
    assert (out / 'social/poc/index.html').read_bytes() == before
    result = subprocess.run([sys.executable, 'product/nz_election/pipeline/build.py', '--data', str(tmp_path / 'absent'), '--out', str(out), '--now', '2026-11-07T05:59:59Z'], capture_output=True, text=True)
    assert result.returncode != 0 and 'PUBLICATION_FROZEN' in result.stderr
    assert (out / 'social/poc/index.html').read_bytes() == before
    script = Path('product/nz_election/pipeline/deployment_guard.py')
    for now, code in [('2026-11-06T10:00:00Z', 0), ('2026-11-06T10:59:59Z', 1), ('2026-11-06T11:00:00Z', 1), ('2026-11-07T05:59:59Z', 1), ('2026-11-07T06:00:00Z', 0)]:
        result = subprocess.run([sys.executable, str(script), '--now', now], capture_output=True, text=True)
        assert result.returncode == code
    workflow = Path('.github/workflows/pages.yml').read_text()
    deploy = workflow.split('  deploy:', 1)[1]
    assert deploy.index('Enforce election freeze') < deploy.index('actions/deploy-pages')
    assert '2026-11-06T10:30:00+00:00' in deploy and '2026-11-07T06:00:00+00:00' in deploy
    import textwrap
    guard = textwrap.dedent(deploy.split("python3 - <<'PYTHON'\n", 1)[1].split('          PYTHON', 1)[0])
    for now, expected in [('2026-11-06T11:00:00+00:00', 1), ('2026-11-07T05:59:59+00:00', 1), ('2026-11-07T06:00:00+00:00', 0)]:
        code = guard.replace('datetime.now(timezone.utc)', f'datetime.fromisoformat({now!r})')
        assert subprocess.run([sys.executable, '-c', code], capture_output=True).returncode == expected


def test_reservation_replay_cannot_hide_spend(tmp_path):
    data, replay, remote = (tmp_path / n for n in ('data', 'replay', 'remote.git'))
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    reservation = fixture(data, reserve=True)
    publish(data, remote, family='social')
    shutil.copytree(data, replay)
    fixture(data, reservation=reservation)
    publish(data, remote, family='social')
    # A stale result with a different spend must not be silently merged via max.
    def empty(*args):
        return 200, b'{"tweets":[],"has_next_page":false}'
    social.refresh_social(replay, DAY, now=NOW, reservation=reservation, send=empty, sleep=lambda _: None)
    with pytest.raises(ValueError, match='SOCIAL_LEDGER_CONFLICT'):
        publish(replay, remote, family='social')


def test_durable_claim_rejects_second_runner_before_transport(tmp_path):
    data, remote = tmp_path / 'data', tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    reservation = fixture(data, reserve=True)
    publish(data, remote, family='social')
    assert publish(data, remote, family='social', claim=reservation)['outcome'] == 'published'
    with pytest.raises(ValueError, match='SOCIAL_RESERVATION_CONSUMED'):
        publish(data, remote, family='social', claim=reservation)
    checkout = tmp_path / 'checkout'
    git(tmp_path, 'clone', '-q', '-b', 'data', str(remote), str(checkout))
    record = export.validate_bundle(checkout / DATA)['social/credits']['data'][0]
    assert record['closed'] and record['spent'] == record['reserved'] == 7560
    fixture(data, reservation=reservation)
    publish(data, remote, family='social')
    workflow = Path('.github/workflows/nz-election-social-daily.yml').read_text().split('  collect:', 1)[1]
    assert workflow.index('--claim') < workflow.index('name: Sample X')
    assert "steps.claim.outputs.claimed == 'true'" in workflow


def test_collection_stops_when_sleep_crosses_nz_midnight():
    run = run_row()
    now = ['2026-10-17T10:59:00Z']
    calls = []
    def send(*args):
        calls.append(now[0])
        return 200, b'{"tweets":[],"has_next_page":false}'
    def sleep(_):
        now[0] = '2026-10-17T11:04:30Z'
    with pytest.raises(ValueError, match='SOCIAL_BUDGET_DAY_CHANGED'):
        social.collect(DAY, [run], run, key='fiction', send=send, sleep=sleep, now=lambda: now[0])
    assert calls == ['2026-10-17T10:59:00Z']
    assert run['requests'] == 1 and run['reserved'] == 315
    now[0] = '2026-10-17T10:59:40Z'
    with pytest.raises(ValueError, match='SOCIAL_BUDGET_DAY_CHANGED'):
        social.collect(DAY, [run], run, key='fiction', send=send, sleep=sleep, now=lambda: now[0])
    assert len(calls) == 1


def test_small_fractional_probabilities_survive_publication(tmp_path):
    upstream = social.fixture_send()
    def send(method, *args):
        status, raw = upstream(method, *args)
        if method == 'POST':
            body = json.loads(raw)
            body['answers']['attitude']['probabilities'] = {'0': 1e-10, '1': 0, '2': 0, '3': 0.9999999999, '4': 0}
            raw = json.dumps(body).encode()
        return status, raw
    assert social.refresh_social(tmp_path / 'data', DAY, now=NOW, send=send, sleep=lambda _: None) == 'ok'
    row = export.validate_bundle(tmp_path / 'data')['social/daily']['data'][0]
    assert row['probability_sums']['attitude']['0'] == '0.0000000240'
    assert 'E' not in row['probability_sums']['attitude']['0']


def test_populated_figures_have_shared_source_references(tmp_path):
    fixture(tmp_path / 'data')
    site = build(tmp_path / 'data', tmp_path / 'output', built=NOW)
    provenance((site / 'social/poc/index.html').read_text())
