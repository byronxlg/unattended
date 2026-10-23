"""Synthetic-only social contracts; every transport is injected."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.publish import publish, git, DATA
from product.nz_election.pipeline.social_page import page

NOW = '2026-10-17T03:00:00Z'
DAY = '2026-10-16'


def run_row(reserved=0):
    return dict(id='run-' + 'a'*24, source_ref=[], observed_at=NOW, day='2026-10-17', reserved=reserved,
                spent=0, cap=7800, requests=0, allocation=0, closed=False)


def post(i=0, text=None, lang='en', author=None):
    return dict(id='fiction-' + str(i), text=text or 'Fictional test statement ' + str(i), lang=lang, author=dict(id=author or 'fiction-author-' + str(i)))


def response(relevant=1, evaluable=1, party='National'):
    answers = dict(relevant=dict(type='noul', noul=relevant), evaluable=dict(type='noul', noul=evaluable))
    for name, options, choice in [('party', social.PARTIES, party), ('topic', social.TOPICS, 'health'), ('attitude', [str(i) for i in range(5)], '3')]:
        answers[name] = dict(type=social.QUESTIONS[name]['type'], choice=choice, probabilities={k: int(k == choice) for k in options})
    return dict(model='jev-test-1', answers=answers)


def classifier(body=None, calls=None):
    def send(method, url, headers, payload):
        if calls is not None:
            calls.append(json.loads(payload))
        return 200, json.dumps(body or response()).encode()
    return send


def aggregate(n=30):
    posts = [post(i) for i in range(n)]
    rows, excluded = social.classify(posts, key='fiction-key', send=classifier())
    windows = [dict(start_epoch=a, end_epoch=b, retrieved_at=NOW, page_limit=False) for a, b in social.windows(DAY)]
    return social.aggregate(DAY, posts, rows, excluded, windows, NOW)


def fixture(out, **kw):
    return social.refresh_social(out, DAY, now=NOW, fixture=True, send=social.fixture_send(), sleep=lambda _: None, **kw)


def test_cap_reserves_before_every_attempt_including_empty_and_retry():
    prior = run_row(7560)
    run = dict(run_row(), id='run-' + 'b'*24)
    calls = []
    posts, windows, limited = social.collect(DAY, [prior, run], run, key='fiction', send=lambda *a: calls.append(a), sleep=lambda _: None, now=lambda: NOW)
    assert limited and not posts and not windows and not calls
    run = run_row()
    def fail(*args):
        assert run['reserved'] == run['requests'] * 315
        return 503, b''
    with pytest.raises(ValueError, match='SOCIAL_COLLECTION_FAILED'):
        social.collect(DAY, [run], run, key='fiction', send=fail, sleep=lambda _: None, now=lambda: NOW)
    assert (run['requests'], run['reserved'], run['spent']) == (3, 945, 945)
    run = run_row()
    social.collect(DAY, [run], run, key='fiction', send=lambda *a: (200, b'{"tweets":[],"has_next_page":false}'), sleep=lambda _: None, now=lambda: NOW)
    assert (run['reserved'], run['spent']) == (7560, 360)


def test_one_page_per_hour_and_pacing():
    calls, sleeps, run = [], [], run_row()
    def send(method, url, headers, body):
        calls.append(parse_qs(urlsplit(url).query))
        return 200, b'{"tweets":[],"has_next_page":true}'
    _, windows, limited = social.collect(DAY, [run], run, key='fiction', send=send, sleep=sleeps.append, now=lambda: NOW)
    assert len(calls) == len(windows) == 24 and not limited
    assert sleeps == [330] * 23
    assert all(c['queryType'] == ['Latest'] and 'cursor' not in c for c in calls)
    assert len({c['query'][0] for c in calls}) == 24
    assert all('since_time:' in c['query'][0] and 'until_time:' in c['query'][0] for c in calls)


def test_dedup_language_and_noul_gates():
    calls = []
    rows, excluded = social.classify([post(), post(), post(1, text='  FICTIONAL test statement 0  '), post(2, lang='mi'), post(3)], key='fiction', send=classifier(calls=calls))
    assert len(rows) == 2 and len(calls) == 2
    assert excluded == dict(duplicate=2, unsupported=1, irrelevant=0, classification=0)
    assert calls[0]['questions'] == social.QUESTIONS
    rows, excluded = social.classify([post()], key='fiction', send=classifier(response(relevant=0)))
    assert rows == [] and excluded['irrelevant'] == 1
    rows, excluded = social.classify([post()], key='fiction', send=classifier(response(evaluable=0)))
    data = social.aggregate(DAY, [post()], rows, excluded, [], NOW)
    assert data['party_counts']['National'] == 1 and data['attitude']['National']['eligible'] == 0
    rows, excluded = social.classify([post()], key='fiction', send=classifier(response(party='multiple')))
    assert social.aggregate(DAY, [post()], rows, excluded, [], NOW)['party_counts']['multiple'] == 1


def test_withholding_29_30_and_probability_retention():
    small, enough = aggregate(29), aggregate(30)
    assert small['attitude']['National'] == dict(eligible=29, counts=None, withheld=True)
    assert enough['attitude']['National'] == dict(eligible=30, counts=[0, 0, 0, 30, 0], withheld=False)
    assert enough['probability_sums']['attitude']['3'] == '30'
    assert enough['model_versions'] == ['jev-test-1']
    social.validate_row(enough, 'social/daily')


@pytest.mark.parametrize('now,expected', [('2026-11-06T10:29:59Z', False), ('2026-11-06T10:30:00Z', True), ('2026-11-06T10:59:59Z', True), ('2026-11-06T11:00:00Z', True), ('2026-11-07T05:59:59Z', True), ('2026-11-07T06:00:00Z', False)])
def test_freeze(now, expected, tmp_path):
    assert social.frozen(now) == expected
    if expected:
        assert social.refresh_social(tmp_path / 'data', DAY, now=now, send=lambda *a: pytest.fail('socket attempted')) == 'frozen'
        assert not (tmp_path / 'data').exists()


def test_cap_status_and_last_good_retained(tmp_path):
    out = tmp_path / 'data'
    assert fixture(out) == 'ok'
    old = (out / 'social/daily.json').read_bytes()
    assert fixture(out) == 'budget-spent'
    envs = export.validate_bundle(out)
    status = next(r for r in envs['status']['data'] if r['dataset'] == 'social')
    assert status['message'] == "Day's collection cap was already spent; showing data through 2026-10-16"
    assert (out / 'social/daily.json').read_bytes() == old
    assert sum(r['reserved'] for r in envs['social/credits']['data']) == 7560


def test_durable_reservation_and_single_use(tmp_path):
    out = tmp_path / 'data'
    reservation = fixture(out, reserve=True)
    assert reservation.startswith('run-')
    assert fixture(out) == 'budget-spent'
    assert fixture(out, reservation=reservation) == 'ok'
    with pytest.raises(ValueError, match='SOCIAL_INVALID_RESERVATION'):
        fixture(out, reservation=reservation)
    record = export.validate_bundle(out)['social/credits']['data'][0]
    assert record['reserved'] == 7560 and record['spent'] == 3600 and record['closed']


@pytest.mark.parametrize('field', ['post_id', 'handle', 'text', 'author_id', 'url'])
@pytest.mark.parametrize('nested', [False, True])
def test_validator_rejects_identifiers(field, nested):
    data = aggregate()
    (data['sample'] if nested else data)[field] = 'fictional-private-value'
    env = export.envelope([data], [], 'offline-verification', 'fixture')
    with pytest.raises(ValueError):
        export.validate_envelope(env, 'social/daily')


@pytest.mark.parametrize('value', [None, '', [], {}, True, -1, 1.5, 10**100, 'NaN', 'weird\u2028string'])
def test_malformed_counts_rejected(value):
    data = aggregate()
    data['party_counts']['National'] = value
    with pytest.raises(ValueError):
        export.validate_envelope(export.envelope([data], [], 'offline-verification', 'fixture'), 'social/daily')


def test_size_and_sanitized_errors():
    with pytest.raises(ValueError, match='SOCIAL_RESPONSE_LIMIT'):
        social.decode(b' ' * (social.MAX_BYTES + 1))
    def bad(*args):
        raise RuntimeError('fictional-private-text-and-key')
    with pytest.raises(ValueError, match='^SOCIAL_CLASSIFICATION_FAILED$'):
        social.classify([post()], key='fictional-key', send=bad)
    for value in [None, '', [], {}, True, -1, 'NaN']:
        data = response()
        data['answers']['relevant']['noul'] = value
        rows, excluded = social.classify([post()], key='fiction', send=classifier(data))
        assert rows == []
        assert excluded == dict(duplicate=0, unsupported=0, irrelevant=0, classification=1)


def test_build_present_absent_stale_no_identifiers(tmp_path):
    out = tmp_path / 'data'
    fixture(out)
    site = build(out, tmp_path / 'site' / 'nz-election', built=NOW)
    html = (site / 'social/poc/index.html').read_text()
    assert 'Proof of concept: what X says about the parties' in html
    assert '240 posts sampled from X over 1 days' in html
    assert 'under 5' in html and 'Withheld:' not in html and '@' not in html
    assert 'Posts sampled and classified by this site; counts only' in html
    assert all(b'fiction-author' not in p.read_bytes() and b'Fictional civic' not in p.read_bytes() for p in out.rglob('*') if p.is_file())
    envs = export.validate_bundle(out)
    stale = page(envs, '2026-10-18T23:00:00Z')
    assert 'unavailable' not in stale and '<svg' not in stale
    absent = build(tmp_path / 'absent', tmp_path / 'absent-site', built=NOW)
    html = (absent / 'social/poc/index.html').read_text()
    assert 'unavailable' not in html and '<svg' not in html


def test_social_publish_retains_other_families_and_ledger(tmp_path):
    out, remote = tmp_path / 'data', tmp_path / 'remote.git'
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    reservation = fixture(out, reserve=True)
    publish(out, remote, family='social')
    fixture(out, reservation=reservation)
    publish(out, remote, family='social')
    target = tmp_path / 'checkout'
    git(tmp_path, 'clone', '-q', '-b', 'data', str(remote), str(target))
    envs = export.validate_bundle(target / DATA)
    assert envs['social/credits']['data'][0]['closed']
    assert envs['social/daily']['data'][0]['sample']['eligible'] == 240


@pytest.mark.parametrize('reserve', [False, True])
@pytest.mark.parametrize('published', [False, True])
def test_spent_day_cli_exits_zero_without_transport_or_ledger_changes(tmp_path, monkeypatch, capsys, reserve, published):
    out = tmp_path / 'data'
    fixture(out, reserve=not published)
    unchanged = {p: p.read_bytes() for p in (out / 'social').iterdir()}
    output = tmp_path / 'github-output'
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))
    monkeypatch.setattr(social, 'transport', lambda *a: pytest.fail('spent day must not send'))
    monkeypatch.setattr(social.sys, 'argv', ['social', '--out', str(out), '--day', DAY, '--now', NOW] + (['--reserve'] if reserve else []))
    social.main()
    assert capsys.readouterr().out == 'PASS social\n'
    assert output.read_text() == 'validated=true\n'
    assert {p: p.read_bytes() for p in (out / 'social').iterdir()} == unchanged
    status = next(r for r in export.validate_bundle(out)['status']['data'] if r['dataset'] == 'social')
    assert status['error_code'] is None
    assert status['state'] == ('stale' if published else 'unavailable')
    assert status['message'] == "Day's collection cap was already spent; " + ('showing data through 2026-10-16' if published else 'no earlier sample is published.')


@pytest.mark.parametrize('published', [False, True])
@pytest.mark.parametrize('reserved', [False, True])
def test_mid_run_cap_stays_fatal_and_retains_sample(tmp_path, monkeypatch, published, reserved):
    out = tmp_path / 'data'
    if published:
        fixture(out)
    old = (out / 'social/daily.json').read_bytes() if published else None
    now = '2026-10-18T03:00:00Z'
    reservation = social.refresh_social(out, DAY, now=now, reserve=True) if reserved else None
    calls = []
    def send(method, *args):
        assert method == 'GET'
        calls.append(method)
        return (503, b'') if len(calls) == 1 else (200, b'{"tweets":[],"has_next_page":false}')
    monkeypatch.setattr(social, 'transport', send)
    monkeypatch.setattr(social.clock, 'sleep', lambda _: None)
    monkeypatch.setattr(social.sys, 'argv', ['social', '--out', str(out), '--day', DAY, '--now', now] + (['--reservation', reservation] if reserved else []))
    with pytest.raises(SystemExit, match='^FAIL social: SOCIAL_CREDIT_CAP$'):
        social.main()
    assert len(calls) == 24
    envs = export.validate_bundle(out)
    run = next(r for r in envs['social/credits']['data'] if r['day'] == '2026-10-18')
    assert (run['reserved'], run['spent'], run['requests'], run['closed']) == (7560, 660, 24, True)
    status = next(r for r in envs['status']['data'] if r['dataset'] == 'social')
    assert status['error_code'] == 'SOCIAL_CREDIT_CAP'
    assert status['message'] == 'Collection limit reached; ' + ('showing data through 2026-10-16' if published else 'no earlier sample is published.')
    if published:
        assert (out / 'social/daily.json').read_bytes() == old
    else:
        assert not (out / 'social/daily.json').exists()


@pytest.mark.parametrize('reserve', [False, True])
def test_spent_day_does_not_hide_query_failure(tmp_path, monkeypatch, capsys, reserve):
    out = tmp_path / 'data'
    fixture(out, reserve=True)
    credits = (out / 'social/credits.json').read_bytes()
    monkeypatch.setattr(social, 'QUERY', 'x' * 513)
    result = social.refresh_social(out, DAY, now=NOW, reserve=reserve,
                                   send=lambda *a: pytest.fail('invalid query must not send'))
    assert result == 'SOCIAL_UPSTREAM_FAILED'
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_QUERY_TOO_LONG http_status=None window_index=0 attempt=1\n'
    assert (out / 'social/credits.json').read_bytes() == credits
