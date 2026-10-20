"""Advance series semantics and atomic replacement of independently owned bytes."""
from copy import deepcopy
import pytest
from product.nz_election.pipeline import advance, export
from product.nz_election.pipeline.daily_refresh import daily_refresh


def test_advance_daily_not_cumulative():
    rows = advance.normalize([('2023-10-02', 10), ('2023-10-03', 20)], kind='daily', start='2023-10-02')
    assert [r['cumulative'] for r in rows] == [10, 30]
    data, sources, hashes = advance.load(historical=True)
    assert data['advance-voting'][-1]['cumulative'] == 1640204
    assert data['advance-voting'][-1]['daily'] == 260219
    assert sources and hashes


def test_advance_missing_day_no_zero_fill():
    rows = advance.normalize([('2023-10-02', 10), ('2023-10-04', 20), ('2023-10-05', 30)], kind='daily', start='2023-10-02')
    assert [r['date'] for r in rows] == ['2023-10-02', '2023-10-04', '2023-10-05']
    assert [r['cumulative'] for r in rows] == [10, None, None]
    assert [r['daily'] for r in rows] == [10, 20, 30]


def test_advance_cumulative_gap():
    rows = advance.normalize([('2023-10-02', 10), ('2023-10-04', 40), ('2023-10-05', 55)], kind='cumulative', start='2023-10-02')
    assert [r['daily'] for r in rows] == [10, None, 15]
    assert [r['cumulative'] for r in rows] == [10, 40, 55]


def test_advance_revision_replaces_observation(tmp_path):
    original = advance.load(historical=True)
    daily_refresh(tmp_path / 'data', loaders={'advance': lambda: original}, now='2026-10-20T01:00:00Z')
    revised = deepcopy(original)
    revised[0]['advance-voting'][-1]['daily'] += 1
    revised[0]['advance-voting'][-1]['cumulative'] += 1
    revised[1][0]['revision'] = 'controlled correction'
    daily_refresh(tmp_path / 'data', loaders={'advance': lambda: revised}, now='2026-10-20T02:00:00Z')
    rows = export.validate_bundle(tmp_path / 'data')['advance-voting']['data']
    assert len(rows) == len(original[0]['advance-voting'])
    assert rows[-1]['cumulative'] == 1640205


def test_advance_capture_failure_retains_bytes(tmp_path):
    path = tmp_path / 'data'
    daily_refresh(path, historical_advance=True, now='2026-10-20T01:00:00Z')
    before = [(path / ('advance-voting' + ext)).read_bytes() for ext in ('.json', '.csv')]
    def fail():
        raise ValueError('CAPTURE_HASH_MISMATCH')
    daily_refresh(path, loaders={'advance': fail}, now='2026-10-20T02:00:00Z')
    assert before == [(path / ('advance-voting' + ext)).read_bytes() for ext in ('.json', '.csv')]
    status = next(r for r in export.validate_bundle(path)['status']['data'] if r['dataset'] == 'advance')
    assert status['state'] == 'stale' and status['error_code'] == 'CAPTURE_HASH_MISMATCH'


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ12', -1])
def test_advance_malformed_counts(bad):
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        advance.normalize([('2023-10-02', bad)], kind='daily', start='2023-10-02')


def test_advance_rejects_bad_capture_and_unsupported_totals():
    for raw in (b'', b'<html>challenge</html>', b'Date,2023 General Election\n2023-10-02,1.5'):
        with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
            advance.parse(raw, kind='daily', start='2023-10-02')
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        advance.normalize([('2023-10-02', 2), ('2023-10-02', 3)], kind='daily', start='2023-10-02')
    rows = advance.normalize([('2023-10-03', 5)], kind='daily', start='2023-10-02')
    assert rows[0]['cumulative'] is None


def test_advance_publication_orders_captures(tmp_path):
    from product.nz_election.pipeline.publish import publish, git, DATA
    original = advance.load(historical=True)
    revised = deepcopy(original)
    revised[0]['advance-voting'][-1]['daily'] += 1
    revised[0]['advance-voting'][-1]['cumulative'] += 1
    revised[1][0]['fetched_at'] = '2026-10-21T01:00:00Z'
    older, newer, remote = [tmp_path / n for n in ('older', 'newer', 'remote.git')]
    daily_refresh(older, loaders={'advance': lambda: original}, now='2026-10-20T01:00:00Z')
    daily_refresh(newer, loaders={'advance': lambda: revised}, now='2026-10-21T01:00:00Z')
    remote.mkdir()
    git(remote, 'init', '--bare', '-q')
    publish(older, remote, family='daily')
    publish(newer, remote, family='daily')
    publish(older, remote, family='daily')
    empty = tmp_path / 'empty'
    daily_refresh(empty, loaders={'advance': lambda: None}, now='2026-10-22T01:00:00Z')
    publish(empty, remote, family='daily')
    for ext in ('.json', '.csv'):
        name = 'advance-voting' + ext
        assert git(remote, 'show', 'data:' + str(DATA / name)).stdout.encode() == (newer / name).read_bytes()


def test_newest_immutable_capture_replaces_series(tmp_path, monkeypatch):
    import json
    from product.nz_election.pipeline.fixtures import ROOT
    entry = next(e for e in json.loads((ROOT / 'manifest.json').read_text())['entries'] if 'advance' in e)
    old = dict(entry, path='original.csv')
    new = dict(entry, path='revised.csv', captured_at='2026-10-21T01:00:00Z', revision='controlled revision')
    raw = (ROOT / entry['path']).read_bytes()
    revised = raw.replace(b'260219', b'260220').replace(b'1640204', b'1640205')
    new['sha256'] = export.digest(revised)
    (tmp_path / old['path']).write_bytes(raw)
    (tmp_path / new['path']).write_bytes(revised)
    (tmp_path / 'manifest.json').write_text(json.dumps(dict(entries=[old, new])))
    monkeypatch.setattr(advance, 'ROOT', tmp_path)
    payload, sources, hashes = advance.load(historical=True)
    assert payload['advance-voting'][-1]['cumulative'] == 1640205
    assert sources[0]['id'] == 'V:advance-voting' and sources[0]['revision'] == 'controlled revision'
    assert hashes == {'fixtures/revised.csv': export.digest(revised)}
    assert (tmp_path / old['path']).read_bytes() == raw
    (tmp_path / new['path']).write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='CAPTURE_HASH_MISMATCH'):
        advance.load(historical=True)
