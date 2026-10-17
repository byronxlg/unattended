"""Invalid classifications are private, counted exclusions with a daily bound."""
import json

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.pipeline.social_page import page
from product.nz_election.tests.test_social import DAY, NOW, post, response


def test_tied_choice_and_per_post_exclusion(capsys):
    tied = response()
    tied['answers']['party'].update(choice='Labour', probabilities={p: .5 if p in ('National', 'Labour') else 0 for p in social.PARTIES})
    bad = response()
    del bad['answers']['topic']
    bodies = iter([bad, tied, response()])
    diagnostic = {'post_windows': [3, 4, 5]}
    rows, exclusions = social.classify([post(i) for i in range(3)], key='private-key',
                                      send=lambda *args: (200, json.dumps(next(bodies)).encode()), diagnostic=diagnostic)
    assert len(rows) == 2
    assert exclusions == dict(duplicate=0, unsupported=0, irrelevant=0, classification=1)
    assert diagnostic['check'] == 'complete'
    assert diagnostic['code'] is None
    assert diagnostic['last_exclusion']['check'] == 'answers'
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=3 attempt=1 check=answers\n'


@pytest.mark.parametrize('sent,expected', [(11, 'ok'), (10, 'ok'), (9, 'SOCIAL_UPSTREAM_FAILED')])
def test_daily_bound_uses_sent_posts_and_retains_last_good(tmp_path, capsys, sent, expected):
    out = tmp_path / 'data'
    assert social.refresh_social(out, DAY, now=NOW, send=social.fixture_send(), sleep=lambda _: None, fixture=True) == 'ok'
    old = (out / 'social/daily.json').read_bytes()
    get_calls = post_calls = 0
    def send(method, *args):
        nonlocal get_calls, post_calls
        if method == 'GET':
            get_calls += 1
            posts = [post(i) for i in range(sent)] + [post(), post(50, lang='mi')] if get_calls == 1 else []
            return 200, json.dumps(dict(tweets=posts, has_next_page=False)).encode()
        post_calls += 1
        body = response(relevant=0 if post_calls == 2 else 1)
        if post_calls == 1:
            del body['answers']['topic']
        return 200, json.dumps(body).encode()
    now = '2026-10-18T03:00:00Z'
    assert social.refresh_social(out, '2026-10-17', now=now, send=send, sleep=lambda _: None) == expected
    assert post_calls == (sent if expected == 'ok' else 1)
    line = 'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=0 attempt=1 check=answers\n'
    assert capsys.readouterr().err == line * (1 if expected == 'ok' else 2)
    bundle = export.validate_bundle(out)
    if expected == 'ok':
        row = bundle['social/daily']['data'][-1]
        assert row['sample']['exclusions'] == dict(duplicate=1, unsupported=1, irrelevant=1, classification=1)
        assert row['sample']['eligible'] == sent - 2
        assert 'invalid classification under 5' in page(bundle, now)
    else:
        assert (out / 'social/daily.json').read_bytes() == old


@pytest.mark.parametrize('value', ['', None, [], {}, True, -1, 1.5, 10**100, 'private-post @handle secret-key\u2028'])
@pytest.mark.parametrize('check', ['model', 'answers', 'type', 'probabilities', 'choice', 'value'])
def test_malformed_structures_name_only_fixed_check(value, check, capsys):
    body = response()
    if check in ('model', 'answers'):
        body[check] = value
    elif check == 'value':
        body['answers']['relevant']['noul'] = value
    else:
        body['answers']['party'][check] = value
    diagnostic = {}
    rows, exclusions = social.classify([post(text='private-post @handle secret-key')], key='secret-key',
                                      send=lambda *args: (200, json.dumps(body).encode()), diagnostic=diagnostic)
    assert rows == []
    assert exclusions == dict(duplicate=0, unsupported=0, irrelevant=0, classification=1)
    assert diagnostic['code'] is None
    assert diagnostic['check'] == 'complete'
    assert diagnostic['last_exclusion']['code'] == 'SOCIAL_CLASSIFICATION_FAILED'
    assert diagnostic['last_exclusion']['check'] == check
    assert capsys.readouterr().err == f'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=None attempt=1 check={check}\n'


@pytest.mark.parametrize('raw', [b'', b'null', b'[]', b'1.5', b'"private-post"', b' ' * (social.MAX_BYTES + 1)],
                         ids=['empty', 'null', 'array', 'float', 'string', 'oversized'])
def test_decode_failures_stay_fatal(raw, tmp_path, capsys):
    code = 'SOCIAL_RESPONSE_LIMIT' if len(raw) > social.MAX_BYTES else 'SOCIAL_INVALID_RESPONSE'
    diagnostic = {}
    with pytest.raises(ValueError, match='^' + code + '$'):
        social.classify([post()], key='k', send=lambda *args: (200, raw), diagnostic=diagnostic)
    assert diagnostic['check'] == 'decode'
    assert diagnostic['code'] == code
    assert capsys.readouterr().err == ''
    calls = {'GET': 0, 'POST': 0}
    def send(method, *args):
        calls[method] += 1
        if method == 'GET':
            return 200, json.dumps(dict(tweets=[post(i) for i in range(10)] if calls[method] == 1 else [], has_next_page=False)).encode()
        return 200, raw if calls[method] == 10 else json.dumps(response()).encode()
    out = tmp_path / 'data'
    assert social.refresh_social(out, DAY, now=NOW, send=send, sleep=lambda _: None) == 'SOCIAL_UPSTREAM_FAILED'
    assert calls['POST'] == 10
    assert 'social/daily' not in export.validate_bundle(out)
    assert capsys.readouterr().err == f'social diagnostic: {code} http_status=200 window_index=0 attempt=1 check=decode\n'


@pytest.mark.parametrize('probability,excluded', [('0.999', 0), ('0.9989', 1), ('1.001', 1)])
def test_sum_tolerance_and_probability_range(probability, excluded, capsys):
    raw = json.dumps(response()).replace('"National": 1', '"National": ' + probability).encode()
    diagnostic = {}
    rows, exclusions = social.classify([post()], key='k', send=lambda *args: (200, raw), diagnostic=diagnostic)
    assert len(rows) == 1 - excluded
    assert exclusions == dict(duplicate=0, unsupported=0, irrelevant=0, classification=excluded)
    check = 'value' if probability == '1.001' else 'sum'
    assert capsys.readouterr().err == (f'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=None attempt=1 check={check}\n' if excluded else '')


def test_aggregate_failure_does_not_reuse_exclusion(tmp_path, monkeypatch, capsys):
    calls = {'GET': 0, 'POST': 0}
    def send(method, *args):
        calls[method] += 1
        if method == 'GET':
            return 200, json.dumps(dict(tweets=[post(i) for i in range(10)] if calls[method] == 1 else [], has_next_page=False)).encode()
        body = response()
        if calls[method] == 1:
            del body['answers']['topic']
        return 200, json.dumps(body).encode()
    def fail(*args):
        raise RuntimeError('private aggregate detail')
    monkeypatch.setattr(social, 'aggregate', fail)
    out = tmp_path / 'data'
    assert social.refresh_social(out, DAY, now=NOW, send=send, sleep=lambda _: None) == 'SOCIAL_UPSTREAM_FAILED'
    assert calls['POST'] == 10
    assert 'social/daily' not in export.validate_bundle(out)
    assert capsys.readouterr().err == (
        'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=0 attempt=1 check=answers\n'
        'social diagnostic: SOCIAL_UPSTREAM_FAILED http_status=None window_index=None attempt=None\n')


def test_certain_failure_stops_after_49_requests(tmp_path, capsys):
    calls = {'GET': 0, 'POST': 0}
    def send(method, *args):
        calls[method] += 1
        if method == 'GET':
            start = (calls[method] - 1) * 20
            return 200, json.dumps(dict(tweets=[post(i) for i in range(start, start + 20)], has_next_page=False)).encode()
        body = response()
        del body['answers']['topic']
        return 200, json.dumps(body).encode()
    out = tmp_path / 'data'
    assert social.refresh_social(out, DAY, now=NOW, send=send, sleep=lambda _: None) == 'SOCIAL_UPSTREAM_FAILED'
    assert calls == {'GET': 24, 'POST': 49}
    assert 'social/daily' not in export.validate_bundle(out)
    line = lambda window: f'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index={window} attempt=1 check=answers\n'
    assert capsys.readouterr().err == ''.join(line(i // 20) for i in range(49)) + line(2)
