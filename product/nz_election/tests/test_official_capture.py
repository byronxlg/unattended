"""Synthetic offline official acquisition; all HTTP uses injected transport."""
from datetime import datetime
import json
from xml.etree import ElementTree as ET

import pytest

from product.nz_election.pipeline import export, fetch, night_live, result_sources, result_states
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tests.test_result_states import capture
from product.nz_election.tools import official_capture as tool

NOW = '2026-11-28T00:00:00Z'
ROOT = result_sources.ROOTS['official']
SENTINEL = 'UNTRUSTED_OFFICIAL_SENTINEL'


def clock():
    return datetime.fromisoformat(NOW.replace('Z', '+00:00'))


@pytest.fixture
def baseline(tmp_path):
    raw = capture('preliminary')
    live = tmp_path / 'live'
    daily_refresh(live, loaders={'night': lambda: night_live.loaded(raw)}, now=raw['retrieved_at'])
    settled = tmp_path / 'settled'
    result_states.prepare(live, settled, 'settled', now='2026-11-08T06:00:00Z',
                          run_url='offline-verification', captured=None)
    return settled


@pytest.fixture
def synthetic():
    # The old state fixture tests transitions, not cross-file totals. Balance a new
    # synthetic transport fixture without changing any committed fixture bytes.
    raw = capture('official')['raw']
    national = ET.fromstring(raw['election.xml'])
    votes = {p.attrib['p_no']: p.find('votes').text for p in national.find('partystatus')}
    totals = dict(total_votes_cast=0, total_voting_places_counted=0)
    for index, path in enumerate(tool.PATHS[4:]):
        detail = ET.fromstring(raw[path])
        for p in detail.find('partyvotes'):
            p.find('votes').text = votes.get(p.attrib['p_no'], '0') if index == 0 else '0'
        stats = detail.find('statistics')
        count = max(sum(int(p.find('votes').text) for p in detail.find('partyvotes')),
                    sum(int(c.find('votes').text) for c in detail.find('candidatevotes')))
        stats.find('total_votes_cast').text = str(count)
        for key in totals:
            totals[key] += int(stats.find(key).text)
        raw[path] = ET.tostring(detail, encoding='unicode')
    for key, value in totals.items():
        national.find('statistics/' + key).text = str(value)
    raw['election.xml'] = ET.tostring(national, encoding='unicode')
    return raw


class Response:
    headers = {}

    def __init__(self, body, status=200):
        self.body, self.status = body, status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self, limit):
        return self.body[:limit]


def transport(raw, calls):
    def get(request, *, timeout):
        assert timeout == 20
        path = request.full_url.removeprefix(ROOT)
        calls.append(path)
        return Response(raw[path].encode()) if path in raw else Response(SENTINEL.encode(), 404)
    return get


def acquire(baseline, out, raw):
    calls = []
    draft = tool.prepare(baseline, out, ROOT, transport=transport(raw, calls), now=clock,
                         sleep=lambda _: pytest.fail('unexpected retry'))
    return draft, calls


def test_complete_pass_and_official_acceptance(baseline, synthetic, tmp_path, capsys, monkeypatch):
    out = tmp_path / 'draft'
    original = {p.relative_to(baseline): p.read_bytes() for p in baseline.rglob('*') if p.is_file()}
    draft, calls = acquire(baseline, out, synthetic)
    assert calls == list(tool.PATHS)
    raw = (out / tool.CAPTURE).read_bytes()
    captured = json.loads(raw)
    assert draft['sha256'] == export.digest(raw)
    assert draft['capture_kind'] == 'unreviewed' and draft['reviewer'] == ''
    for path, entry in captured['files'].items():
        assert entry == dict(url=ROOT + path, retrieved_at=NOW,
                             sha256=export.digest(synthetic[path].encode()),
                             acquisition_source=result_sources.source('official'))
    result_states.prepare(baseline, tmp_path / 'accepted', 'official', now=NOW,
                          run_url='offline-verification', captured=captured)
    assert export.validate_bundle(tmp_path / 'accepted')['night/live/current']['data'][0]['result_state'] == 'official'
    assert original == {p.relative_to(baseline): p.read_bytes() for p in baseline.rglob('*') if p.is_file()}
    monkeypatch.setattr(tool, 'prepare', lambda *a, **k: draft)
    tool.main(['--data', str(baseline), '--out', str(out), '--base-url', ROOT])
    assert capsys.readouterr().out == tool.PASS + '\n'


@pytest.mark.parametrize('fault,code', [('missing', 'OFFICIAL_INCOMPLETE'),
    ('reference', 'OFFICIAL_REFERENCE_DRIFT'), ('totals', 'OFFICIAL_TOTALS')])
def test_acquisition_failures(baseline, synthetic, tmp_path, fault, code):
    if fault == 'missing':
        del synthetic['e71/e71.xml']
    elif fault == 'reference':
        synthetic['parties.xml'] += SENTINEL
    else:
        synthetic['e01/e01.xml'] = synthetic['e01/e01.xml'].replace('<votes>0</votes>', '<votes>1</votes>', 1)
    out = tmp_path / 'refused'
    with pytest.raises(tool.CaptureError, match='^' + code + '$'):
        acquire(baseline, out, synthetic)
    assert not out.exists()


@pytest.mark.parametrize('fault,code', [('checksum', 'OFFICIAL_CHECKSUM'), ('kind', 'OFFICIAL_SOURCE'),
    ('file-kind', 'OFFICIAL_SOURCE'), ('missing', 'OFFICIAL_INCOMPLETE')])
def test_preflight_failures(baseline, synthetic, tmp_path, fault, code):
    out = tmp_path / 'draft'
    acquire(baseline, out, synthetic)
    captured = json.loads((out / tool.CAPTURE).read_bytes())
    if fault == 'checksum':
        captured['files']['e71/e71.xml']['sha256'] = SENTINEL
    elif fault == 'kind':
        captured['acquisition_source']['kind'] = 'preliminary'
    elif fault == 'file-kind':
        captured['files']['e71/e71.xml']['acquisition_source']['kind'] = 'demo'
    else:
        del captured['raw']['e71/e71.xml']
    with pytest.raises(tool.CaptureError, match='^' + code + '$'):
        tool.preflight(baseline, captured, now=NOW)


@pytest.mark.parametrize('bad', [None, '', [], {}, 1, 1.5, 10**100, SENTINEL + '\x00', 'preliminary'])
def test_bad_sources_have_one_code(bad, tmp_path):
    with pytest.raises(tool.CaptureError, match='^OFFICIAL_SOURCE$'):
        tool.prepare(tmp_path, tmp_path / 'out', bad, now=clock,
                     transport=lambda *a, **k: pytest.fail('network'))
    with pytest.raises(fetch.FetchError, match='^OFFICIAL_SOURCE$'):
        fetch.official_xml(bad, 'election.xml', now=clock,
                           transport=lambda *a, **k: pytest.fail('network'))


def test_clock_gate_before_network(tmp_path):
    early = lambda: datetime.fromisoformat('2026-11-26T10:59:59+00:00')
    with pytest.raises(tool.CaptureError, match='^OFFICIAL_NOT_DUE$'):
        tool.prepare(tmp_path, tmp_path / 'out', ROOT, now=early,
                     transport=lambda *a, **k: pytest.fail('network'))
    with pytest.raises(fetch.FetchError, match='^OFFICIAL_NOT_DUE$'):
        fetch.official_xml(ROOT, 'election.xml', now=early,
                           transport=lambda *a, **k: pytest.fail('network'))
    tool.require_date('2026-11-26T11:00:00Z')


@pytest.mark.parametrize('raw', ['', 'null', '42', '[]', '1.5', str(10**100), json.dumps(SENTINEL + '\x00')])
def test_bad_baseline_sanitized(raw, tmp_path):
    (tmp_path / 'manifest.json').write_text(raw)
    with pytest.raises(tool.CaptureError, match='^OFFICIAL_CAPTURE_FAILED$'):
        tool.prepare(tmp_path, tmp_path.parent / 'refused', ROOT, now=clock,
                     transport=lambda *a, **k: pytest.fail('network'))


def test_cli_sanitizes_errors(monkeypatch, capsys):
    def fail(*a, **k):
        raise tool.CaptureError('OFFICIAL_CHECKSUM')
    monkeypatch.setattr(tool, 'prepare', fail)
    with pytest.raises(SystemExit, match='^OFFICIAL_CHECKSUM$'):
        tool.main(['--data', SENTINEL, '--out', SENTINEL, '--base-url', SENTINEL])
    assert capsys.readouterr().out == ''


def test_transport_retry_bounds():
    calls, delays = [], []
    def get(*a, **k):
        calls.append(1)
        return Response(SENTINEL.encode(), 503)
    with pytest.raises(fetch.FetchError, match='^OFFICIAL_RETRIES_EXHAUSTED$'):
        fetch.official_xml(ROOT, 'election.xml', transport=get, sleep=delays.append, now=clock)
    assert len(calls) == 3 and delays == [1, 2]


def test_output_exclusive(baseline, tmp_path):
    out = tmp_path / 'exists'
    out.mkdir()
    with pytest.raises(tool.CaptureError, match='^OFFICIAL_OUTPUT$'):
        tool.prepare(baseline, out, ROOT, now=clock,
                     transport=lambda *a, **k: pytest.fail('network'))


@pytest.mark.parametrize('status,code', [(302, 'OFFICIAL_HTTP_REJECTED'), (404, 'OFFICIAL_INCOMPLETE')])
def test_http_rejection_is_sanitized(status, code):
    with pytest.raises(fetch.FetchError, match='^' + code + '$'):
        fetch.official_xml(ROOT, 'election.xml', now=clock,
                           transport=lambda *a, **k: Response(SENTINEL.encode(), status),
                           sleep=lambda _: pytest.fail('unexpected retry'))


def test_response_size_bounded():
    with pytest.raises(fetch.FetchError, match='^OFFICIAL_TOO_LARGE$'):
        fetch.official_xml(ROOT, 'election.xml', now=clock,
                           transport=lambda *a, **k: Response(b'x' * 2_000_001))


@pytest.mark.parametrize('bad', [None, '', [], 1, 1.5, 10**100, SENTINEL + '\x00', '../election.xml', 'e72/e72.xml'])
def test_unapproved_paths_never_fetch(bad):
    with pytest.raises(fetch.FetchError, match='^OFFICIAL_SOURCE$'):
        fetch.official_xml(ROOT, bad, now=clock,
                           transport=lambda *a, **k: pytest.fail('network'))
