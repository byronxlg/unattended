"""Partial coverage preserves strict provenance, privacy and exclusion gates."""
from copy import deepcopy
import json

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.social_page import page, notice
from product.nz_election.tests.test_social import DAY, NOW, aggregate, fixture, run_row


@pytest.mark.parametrize('field', ['start_epoch', 'end_epoch', 'page_limit'])
@pytest.mark.parametrize('value', ['', None, {}, [], 1.5, 10**100, 'odd\u2028value'])
def test_malformed_partial_window_rejected_by_both_validators(field, value):
    row = aggregate()
    row['provenance']['windows'].pop()
    row['provenance']['windows'][0][field] = value
    with pytest.raises(ValueError, match='^INVALID_SOCIAL_WINDOW$'):
        social.validate_row(row, 'social/daily')
    # Envelope validation rejects floats before inspecting any family schema.
    code = 'INEXACT_NUMBER' if type(value) is float else 'INVALID_SOCIAL_WINDOW'
    with pytest.raises(ValueError, match=f'^{code}$'):
        export.validate_envelope(export.envelope([row], [], 'offline-verification', 'fixture'), 'social/daily')


@pytest.mark.parametrize('mutation', ['empty', 'duplicate', 'reordered', 'outside', 'bool_epoch', 'too_many_posts', 'capped_mismatch'])
def test_partial_provenance_rejects_inconsistent_coverage(mutation):
    row = aggregate()
    windows = row['provenance']['windows']
    if mutation == 'empty':
        windows.clear()
    elif mutation == 'duplicate':
        windows[1] = deepcopy(windows[0])
    elif mutation == 'reordered':
        windows.reverse()
    elif mutation == 'outside':
        windows[0]['start_epoch'] -= 1
    elif mutation == 'bool_epoch':
        windows[0]['start_epoch'] = True
    elif mutation == 'too_many_posts':
        del windows[1:]
    else:
        windows[0]['page_limit'] = True
    with pytest.raises(ValueError):
        export.validate_envelope(export.envelope([row], [], 'offline-verification', 'fixture'), 'social/daily')


def test_partial_windows_can_have_gaps_and_captions_count_them():
    row = aggregate()
    row['provenance']['windows'].pop(5)
    social.validate_row(row, 'social/daily')
    assert '23 of 24 hours sampled' in notice([row])
    assert '23 of 24 hours sampled' in page({'social/daily': {'data': [row]}}, NOW)
    assert '23 of 24 hours sampled' in page({'social/daily': {'data': [row]}}, '2026-10-20T03:00:00Z')


@pytest.mark.parametrize('invalid', [23, 24])
def test_partial_classification_bound_uses_only_sent_posts(tmp_path, capsys, invalid):
    upstream = social.fixture_send()
    gets = posts = 0
    def send(method, *args):
        nonlocal gets, posts
        if method == 'GET':
            gets += 1
            if gets == 6:
                return 503, b'private-key and post content'
        status, raw = upstream(method, *args)
        if method == 'POST':
            posts += 1
            if posts <= invalid:
                data = json.loads(raw)
                data['model'] = 'private-unreviewed-model'
                raw = json.dumps(data).encode()
        return status, raw
    out = tmp_path / 'data'
    result = social.refresh_social(out, DAY, now=NOW, send=send, sleep=lambda _: None, fixture=True)
    envs = export.validate_bundle(out)
    assert gets == 24
    assert envs['social/credits']['data'][0]['spent'] == 7560
    logs = capsys.readouterr().err
    assert 'SOCIAL_COLLECTION_RETRY http_status=503 window_index=5 attempt=1' in logs
    assert 'private' not in logs
    if invalid == 23:
        assert result == 'ok' and posts == 230
        row = envs['social/daily']['data'][0]
        assert row['sample']['eligible'] == 207
        assert row['sample']['exclusions']['classification'] == 23
        assert len(row['provenance']['windows']) == 23
    else:
        assert result == 'SOCIAL_UPSTREAM_FAILED'
        assert 'social/daily' not in envs


def test_no_window_fetched_when_last_request_retries():
    prior = dict(run_row(7245), requests=23, spent=7245, closed=True)
    run = dict(run_row(), id='run-' + 'b'*24)
    calls = []
    def send(*args):
        calls.append(1)
        return 429, b'private'
    posts, windows, limited = social.collect(DAY, [prior, run], run, key='private',
                                            send=send, sleep=lambda _: None, now=lambda: NOW)
    assert limited and posts == windows == [] and len(calls) == 1
    assert run['reserved'] == run['spent'] == 315
    social.validate_ledger([prior, run])


@pytest.mark.parametrize('published', [False, True])
def test_zero_fetched_retains_previous_data(tmp_path, monkeypatch, published):
    out = tmp_path / 'data'
    if published:
        fixture(out)
    before = (out / 'social/daily.json').read_bytes() if published else None
    monkeypatch.setattr(social, 'collect', lambda *a, **kw: ([], [], True))
    result = social.refresh_social(out, DAY, now='2026-10-18T03:00:00Z')
    assert result == 'SOCIAL_CREDIT_CAP'
    if published:
        assert (out / 'social/daily.json').read_bytes() == before
    else:
        assert not (out / 'social/daily.json').exists()
    assert export.validate_bundle(out)['status']['data'][0]['error_code'] == 'SOCIAL_CREDIT_CAP'
