"""Producer branches, physical tail boundaries and metadata races."""
import hashlib
import json

import pytest

from fleet_audit.acceptance import FIXTURES, STAMP
from fleet_audit.files import LocalFiles, tail_regular
from fleet_audit.models import FileMetadata, Observation, TailData
from fleet_audit.receipts import normalize_tick, parse_receipt, read_tail


def tick(**fields):
    return {'ts': STAMP, 'supervisor': {'ran': True, 'rc': '0', 'error': None, **fields}}


def parsed(raw, *, offset=0, boundary=True):
    meta = FileMetadata(1, 1, offset + len(raw), 1, 1, True)
    tail = TailData('/synthetic/ticks', meta, meta, meta, offset, len(raw), boundary, raw, False)
    return parse_receipt(Observation('attempted', STAMP, ('read_tail', tail.path), None, None, tail))


def real(name):
    root = FIXTURES / 'verdicts' / 'real'
    raw = (root / (name + '.jsonl')).read_bytes()
    provenance = json.loads((root / 'provenance.json').read_text())[name]
    assert 'd0dd7de' in provenance['source'] and provenance['kind'] == 'real'
    assert hashlib.sha256(raw[:-1]).hexdigest() == provenance['sha256']
    return normalize_tick(json.loads(raw))


def test_tick_completed_not_ran_null_error():
    assert real('not-ran').outcome == 'completed'
    assert normalize_tick(tick(ran=False, rc=None)).outcome == 'completed'


def test_tick_completed_skip():
    assert real('usage-limit').outcome == 'completed'
    assert normalize_tick(tick(ran=False, error='skipped: next run')).outcome == 'completed'


def test_tick_completed_ran_zero():
    assert real('ran-zero').outcome == 'completed'
    for rc in (0, '0', '+0', '-0'):
        result = normalize_tick(tick(rc=rc))
        assert result.outcome == 'completed' and result.result is None


def test_tick_failed_nonzero_rc():
    for rc in (1, -1, '78', '-2'):
        assert normalize_tick(tick(rc=rc)).outcome == 'failed'


def test_tick_failed_ran_error():
    for error in ('', 'failed', 'skipped: marker'):
        assert normalize_tick(tick(error=error)).outcome == 'failed'


def test_tick_failed_not_ran_error():
    for error in ('', 'failed', 'skip'):
        assert normalize_tick(tick(ran=False, error=error)).outcome == 'failed'


def test_tick_unestablished_other_cases():
    for value in ({}, {'ts': STAMP}, tick(rc=None), tick(rc=True), tick(rc=0.0), tick(rc='0.0'),
                  tick(ran=0), tick(error=False), tick(result=[]), tick(rc='9' * 5000)):
        assert normalize_tick(value).outcome == 'unestablished'
    for key in ('ran', 'rc', 'error'):
        value = tick(); del value['supervisor'][key]
        assert normalize_tick(value).outcome == 'unestablished'
    for ts in ('2026-10-16', '2026-10-16T00:00:00', '2026-99-16T00:00:00Z'):
        assert normalize_tick(tick() | {'ts': ts}).outcome == 'unestablished'
    assert normalize_tick(tick() | {'ts': '2026-10-16T12:00:00+12:00'}).outcome == 'completed'


def test_tail_final_physical_line_only():
    valid = json.dumps(tick()).encode()
    for raw in (valid + b'\n', valid, b'partial\n' + valid + b'\n'):
        assert parsed(raw).data.outcome == 'completed'
    for raw in (valid + b'\n\n', valid + b'\nbad', b''):
        assert parsed(raw).error is not None
    assert parsed(b'partial\n' + valid, offset=10, boundary=False).data.outcome == 'completed'
    assert parsed(valid, offset=10, boundary=False).error is not None


def test_tail_encoding_json_and_bounds(tmp_path):
    for raw in (b'\xff', b'{"x":1,"x":2}', b'[]', b'null', b'{"x":NaN}', b'x' * 65537):
        assert parsed(raw).error is not None
    path = tmp_path / 'ticks'
    valid = json.dumps(tick()).encode()
    exact = b' ' * (65536 - len(valid)) + valid
    path.write_bytes(exact)
    obs = read_tail(str(path), LocalFiles())
    assert obs.data.bytes_read == 65536 and parse_receipt(obs).data.outcome == 'completed'
    path.write_bytes(b'x' + exact)
    assert parse_receipt(read_tail(str(path), LocalFiles())).error is not None
    path.write_bytes(b'x' * 70000 + b'\n' + valid + b'\n')
    assert parse_receipt(read_tail(str(path), LocalFiles())).data.outcome == 'completed'
    assert tail_regular(str(tmp_path)).error.code == 'nonregular'
    assert tail_regular(str(tmp_path / 'missing')).error is not None


@pytest.mark.parametrize('change', ['append', 'truncate', 'replace'])
def test_tail_concurrent_append_truncate_replace(tmp_path, monkeypatch, change):
    import fleet_audit.files as files
    path = tmp_path / 'ticks'; path.write_bytes(json.dumps(tick()).encode())
    original = files.os.read
    calls = []
    def race(fd, size):
        raw = original(fd, size)
        calls.append(size)
        if change == 'append':
            with path.open('ab') as stream: stream.write(b'\n{}')
        elif change == 'truncate':
            path.write_bytes(b'')
        else:
            other = tmp_path / 'replacement'; other.write_bytes(b'{}'); other.replace(path)
        return raw
    monkeypatch.setattr(files.os, 'read', race)
    obs = tail_regular(str(path))
    assert obs.error is not None and obs.data.changed and len(calls) == 1
    assert parse_receipt(obs).data.outcome == 'unestablished'
