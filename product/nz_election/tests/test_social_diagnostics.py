"""Offline regressions for query limits and private upstream diagnostics."""
import json
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import pytest

from product.nz_election.pipeline import export, social
from product.nz_election.tests.test_social import DAY, NOW, run_row


@pytest.mark.parametrize('day', [DAY, '2026-11-07', '0002-01-01', '9999-12-30'])
def test_hourly_queries_fit_with_headroom(day):
    queries = [social.QUERY + f' since_time:{start} until_time:{end}'
               for start, end in social.windows(day)]
    assert max(map(len, queries)) <= 490
    calls = []
    def send(method, url, headers, body):
        calls.append(parse_qs(urlsplit(url).query)['query'][0])
        return 200, b'{"tweets":[],"has_next_page":false}'
    run = run_row()
    social.collect(day, [run], run, key='fiction', send=send, sleep=lambda _: None, now=lambda: NOW)
    assert calls == queries


def refresh(tmp_path, send):
    out = tmp_path / 'data'
    assert social.refresh_social(out, DAY, now=NOW, send=send, sleep=lambda _: None) == 'SOCIAL_UPSTREAM_FAILED'
    assert export.validate_bundle(out)['status']['data'][0]['error_code'] == 'SOCIAL_UPSTREAM_FAILED'


def test_rejected_query_reports_status_without_body(tmp_path, capsys):
    refresh(tmp_path, lambda *args: (400, b'private-post @handle secret-key'))
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_COLLECTION_FAILED http_status=400 window_index=0 attempt=1\n'


def test_retry_diagnostic_identifies_window_and_attempt(tmp_path, capsys):
    calls = 0
    def send(*args):
        nonlocal calls
        calls += 1
        return (200, b'{"tweets":[],"has_next_page":false}') if calls == 1 else (503, b'private')
    refresh(tmp_path, send)
    assert calls == 4
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_COLLECTION_FAILED http_status=503 window_index=1 attempt=3\n'


def test_transport_exception_does_not_invent_http_status(tmp_path, capsys):
    def send(*args):
        raise RuntimeError('private-post @handle secret-key')
    refresh(tmp_path, send)
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_TRANSPORT_FAILED http_status=None window_index=0 attempt=3\n'


@pytest.mark.parametrize('value', ['', None, {}, 1.5, 10**100, 'unusual\u2028private'])
def test_invalid_page_reports_only_code(tmp_path, capsys, value):
    raw = json.dumps(dict(tweets=value, has_next_page=False)).encode()
    refresh(tmp_path, lambda *args: (200, raw))
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_INVALID_PAGE http_status=200 window_index=0 attempt=1\n'


@pytest.mark.parametrize('raw,code', [(b'', 'SOCIAL_INVALID_RESPONSE'), (b'null', 'SOCIAL_INVALID_RESPONSE'),
                                    (b' ' * (social.MAX_BYTES + 1), 'SOCIAL_RESPONSE_LIMIT')],
                         ids=['empty', 'null', 'oversized'])
def test_response_error_keeps_inner_code(tmp_path, capsys, raw, code):
    refresh(tmp_path, lambda *args: (200, raw))
    assert capsys.readouterr().err == f'social diagnostic: {code} http_status=200 window_index=0 attempt=1\n'


def test_classification_failure_reports_source_window(tmp_path, capsys):
    upstream = social.fixture_send()
    calls = 0
    def send(method, *args):
        nonlocal calls
        if method == 'POST':
            return 401, b'private-post @handle secret-key'
        calls += 1
        if calls == 1:
            return 200, b'{"tweets":[],"has_next_page":false}'
        return upstream(method, *args)
    refresh(tmp_path, send)
    assert capsys.readouterr().err == 'social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=401 window_index=1 attempt=1\n'


def test_transport_discards_http_error_body(monkeypatch):
    class Opener:
        def open(self, *args, **kwargs):
            raise HTTPError('https://example.invalid', 400, 'private', {}, None)
    monkeypatch.setattr(social, 'build_opener', lambda *args: Opener())
    assert social.transport('GET', 'https://example.invalid', {}, None) == (400, b'')


@pytest.mark.parametrize('value', ['', None, {}, 1.5, 10**100, 'SOCIAL_PRIVATE\nsecret-key'])
def test_unknown_exception_details_are_never_logged(value):
    assert social.diagnostic_code(ValueError(value), 'SOCIAL_UPSTREAM_FAILED') == 'SOCIAL_UPSTREAM_FAILED'


def test_query_keeps_hashtags_leaders_and_parties():
    for term in ('#nzpol', '#nzvotes', '#nzelection', 'Christopher Luxon', 'Chris Hipkins',
                 'David Seymour', 'Winston Peters', 'Chlöe Swarbrick', 'Marama Davidson',
                 'Rawiri Waititi', 'Debbie Ngarewa-Packer', 'Qiulae Wong', 'National',
                 'Labour', 'Greens', 'ACT New Zealand', 'NZ First', 'Te Pāti Māori', 'Opportunities Party'):
        assert term in social.QUERY
