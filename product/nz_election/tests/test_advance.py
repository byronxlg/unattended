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


@pytest.mark.parametrize('probe', ['missing-kind', 'null-start', 'null-advance'])
@pytest.mark.parametrize('retained', [False, True])
def test_bad_descriptor_is_handled_without_blocking_other_families(tmp_path, monkeypatch, probe, retained):
    import json
    from product.nz_election.pipeline import markets
    from product.nz_election.pipeline.fixtures import ROOT
    entry = deepcopy(next(e for e in json.loads((ROOT / 'manifest.json').read_text())['entries'] if 'advance' in e))
    data = tmp_path / 'data'
    if retained:
        daily_refresh(data, historical_advance=True)
    before = {p.name: p.read_bytes() for p in data.glob('advance-voting.*')}
    if probe == 'missing-kind':
        del entry['advance']['kind']
    elif probe == 'null-start':
        entry['advance']['start'] = None
    else:
        entry['advance'] = None
    fixtures = tmp_path / 'fixtures'
    fixtures.mkdir()
    (fixtures / 'manifest.json').write_text(json.dumps(dict(entries=[entry])))
    monkeypatch.setattr(advance, 'ROOT', fixtures)
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        advance.load(historical=True)
    daily_refresh(data, loaders={'advance': lambda: advance.load(historical=True), 'markets': markets.load})
    envs = export.validate_bundle(data)
    statuses = {r['dataset']: r for r in envs['status']['data']}
    assert statuses['advance']['error_code'] == 'INVALID_ADVANCE'
    assert statuses['advance']['state'] == ('stale' if retained else 'unavailable')
    assert statuses['markets']['state'] == 'fresh' and envs['markets']['data']
    assert before == {p.name: p.read_bytes() for p in data.glob('advance-voting.*')}


@pytest.mark.parametrize('field', ['year', 'kind', 'start', 'date_column', 'count_column'])
@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid'])
def test_descriptor_field_types_raise_handled_error(field, bad):
    value = dict(year=2026, kind='daily', start='2026-10-26', date_column='Date', count_column='Votes')
    value[field] = bad
    # Nonempty strings are legitimate CSV column names; the parser checks their presence.
    if field.endswith('_column') and bad == 'ſ-invalid':
        assert advance.descriptor(value) == value
        with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
            advance.parse(b'Date,Votes\n2026-10-26,1', **{k: value[k] for k in ('kind', 'start', 'date_column', 'count_column')})
    else:
        with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
            advance.descriptor(value)


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid'])
def test_descriptor_shape_raises_handled_error(bad):
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        advance.descriptor(bad)


# Synthetic captures stay under tests and are registered only in temporary roots.
def register_2026(tmp_path, monkeypatch, names):
    import json
    from pathlib import Path
    template = next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries'] if 'advance' in e)
    entries = []
    for index, name in enumerate(names):
        raw = (Path(__file__).parent / 'fixtures/advance' / name).read_bytes()
        entry = deepcopy(template)
        entry.update(path=name, sha256=export.digest(raw), captured_at=f'2026-10-{28 + index}T01:00:00Z')
        entry['advance'].update(year=2026, start='2026-10-26', count_column='Daily votes')
        (tmp_path / name).write_bytes(raw)
        entries.append(entry)
    (tmp_path / 'manifest.json').write_text(json.dumps(dict(entries=entries)))
    monkeypatch.setattr(advance, 'ROOT', tmp_path)


def test_2026_whole_replacement_preserves_new_gap(tmp_path, monkeypatch):
    register_2026(tmp_path, monkeypatch, ['daily.csv', 'replacement.csv'])
    payload, sources, hashes = advance.load()
    rows = payload['advance-voting']
    assert [r['date'] for r in rows] == ['2026-10-26', '2026-10-28', '2026-10-29']
    assert [r['daily'] for r in rows] == [11, 31, 40]
    assert [r['cumulative'] for r in rows] == [11, None, None]
    assert list(hashes) == ['fixtures/replacement.csv']
    assert sources[0]['fetched_at'] == '2026-10-29T01:00:00Z'


def test_2026_shorter_replacement_rejected(tmp_path, monkeypatch):
    register_2026(tmp_path, monkeypatch, ['daily.csv', 'shorter.csv'])
    with pytest.raises(ValueError, match='^SHORTER_ADVANCE_CAPTURE$'):
        advance.load()


def test_require_year_missing_and_registered_invalid(tmp_path, monkeypatch):
    from product.nz_election.pipeline import verify
    with pytest.raises(SystemExit, match='FAIL advance: MISSING_ADVANCE_CAPTURE'):
        verify.cli(['advance', '--require-year', '2026'])
    register_2026(tmp_path, monkeypatch, ['daily.csv', 'shorter.csv'])
    with pytest.raises(SystemExit, match='FAIL advance: SHORTER_ADVANCE_CAPTURE'):
        verify.cli(['advance', '--require-year', '2026'])
    (tmp_path / 'shorter.csv').write_bytes(b'corrupt')
    with pytest.raises(SystemExit, match='FAIL advance: CAPTURE_HASH_MISMATCH'):
        verify.cli(['advance', '--require-year', '2026'])


def test_require_year_valid_capture_runs_check(tmp_path, monkeypatch, capsys):
    from product.nz_election.pipeline import verify
    register_2026(tmp_path, monkeypatch, ['daily.csv'])
    called = []
    monkeypatch.setattr(verify, 'verify_advance', lambda *a, **kw: called.append(True))
    verify.cli(['advance', '--require-year', '2026'])
    assert called == [True]
    assert capsys.readouterr().out == 'PASS advance\n'


def test_preflight_output_and_read_only(tmp_path):
    import json
    from pathlib import Path
    import subprocess
    import sys
    source = Path(__file__).parent / 'fixtures/advance/replacement.csv'
    raw = source.read_bytes()
    candidate = tmp_path / 'capture.csv'
    candidate.write_bytes(raw)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    tool = Path(__file__).resolve().parents[1] / 'tools/advance_preflight.py'
    result = subprocess.run([sys.executable, str(tool), str(candidate), '--url', 'https://elections.nz/example',
                             '--archive-url', 'https://web.archive.org/example'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['headers'] == ['Date', 'Daily votes']
    assert report['date_column'] == 'Date' and report['count_column'] == 'Daily votes'
    assert report['kind'] == 'daily' and 'Inferred' in report['kind_inference']
    assert report['row_count'] == report['observation_count'] == 3
    assert report['first_date'] == '2026-10-26' and report['last_date'] == '2026-10-29'
    assert report['gaps'] == ['2026-10-27']
    assert report['sha256'] == export.digest(raw)
    entry = report['manifest_entry']
    old = next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries'] if 'advance' in e)
    assert set(entry) == set(old)
    assert entry['advance'] == dict(year=2026, kind='daily', start='2026-10-26',
                                    date_column='Date', count_column='Daily votes')
    assert entry['archive_url'] == 'https://web.archive.org/example'
    assert entry['captured_at'] is None and entry['bytes'] == len(raw)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    candidate.write_bytes(b'<html>challenge</html>')
    result = subprocess.run([sys.executable, str(tool), str(candidate), '--url', 'https://elections.nz/example'],
                            capture_output=True, text=True)
    assert result.returncode != 0 and result.stderr.strip() == 'INVALID_ADVANCE'
    assert result.stdout == ''


def test_preflight_cumulative_gaps():
    from pathlib import Path
    from product.nz_election.tools.advance_preflight import inspect
    raw = (Path(__file__).parent / 'fixtures/advance/cumulative.csv').read_bytes()
    report = inspect(raw, url='https://elections.nz/example')
    assert report['kind'] == 'cumulative' and report['gaps'] == ['2026-10-27']
    rows = advance.parse(raw, kind='cumulative', start='2026-10-26', count_column='Cumulative votes')
    assert [r['daily'] for r in rows] == [10, None, 15]
    assert [r['cumulative'] for r in rows] == [10, 40, 55]


@pytest.mark.parametrize('raw', [b'', None, [], {}, True, 1.5, 10**100, 'ſ-invalid',
    b'Date,Votes\n2026-10-26,1.5', b'Date,Votes\n2026-10-26,null',
    b'Date,Votes\n2026-10-26,10000001', 'Date,Votes\n2026-10-26,ſ12'.encode(),
    b'Date,Votes\n2026-10-26,', b'Date,Votes\n2026-10-26,1,2',
    b'Date,Votes,Votes\n2026-10-26,1,2', b'Date,Votes\n2027-10-26,1',
    b'Date,Votes\n2026-10-26,"1', b'\xff'])
def test_preflight_and_parser_malformed_input_code(raw):
    from product.nz_election.tools.advance_preflight import inspect
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        inspect(raw, url='https://elections.nz/example')
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        advance.parse(raw, kind='daily', start='2026-10-26', count_column='Votes')


@pytest.mark.parametrize('raw', [b'Date,Votes,Daily count\n2026-10-26,1,2',
                                b'Date,Daily cumulative votes\n2026-10-26,1'])
def test_preflight_rejects_ambiguous_columns(raw):
    from product.nz_election.tools.advance_preflight import inspect
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        inspect(raw, url='https://elections.nz/example')


@pytest.mark.parametrize('header', ['Total votes', 'Votes', '2026 General Election'])
def test_preflight_requires_semantic_evidence(header):
    from product.nz_election.tools.advance_preflight import inspect
    raw = f'Date,{header}\n2026-10-26,10\n2026-10-27,30\n'.encode()
    with pytest.raises(ValueError, match='^INVALID_ADVANCE: missing daily or cumulative evidence'):
        inspect(raw, url='https://elections.nz/example')


@pytest.mark.parametrize('raw', [
    b'Date,Daily votes,Note\n2026-10-26,10,broken"quote\n',
    b'Date,Daily votes\n2026-10-26,10\nTotal,1"0\n',
])
@pytest.mark.parametrize('consumer', ['pipeline', 'preflight'])
def test_shared_reader_rejects_quotes_before_ignoring_fields(raw, consumer):
    from product.nz_election.tools.advance_preflight import inspect
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        if consumer == 'pipeline':
            advance.parse(raw, kind='daily', start='2026-10-26', count_column='Daily votes')
        else:
            inspect(raw, url='https://elections.nz/example')


def test_reviewed_manifest_supersession_preserves_capture_bytes(tmp_path, monkeypatch):
    import json
    register_2026(tmp_path, monkeypatch, ['daily.csv', 'replacement.csv', 'shorter.csv'])
    before = {p.name: p.read_bytes() for p in tmp_path.glob('*.csv')}
    manifest_path = tmp_path / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest['entries'][:-1]:
        entry['superseded_advance'] = dict(
            descriptor=entry.pop('advance'), by_path='shorter.csv',
            reason='Synthetic reviewed correction withdraws a date; https://elections.nz/example',
            reviewed_by='Test reviewer', reviewed_at='2026-10-30T02:00:00Z')
    manifest['entries'][-1]['notes'] = 'Reviewed correction supersedes daily.csv and replacement.csv'
    manifest_path.write_text(json.dumps(manifest))
    payload, _, hashes = advance.load()
    assert [r['date'] for r in payload['advance-voting']] == ['2026-10-26', '2026-10-28']
    assert [r['cumulative'] for r in payload['advance-voting']] == [11, None]
    assert list(hashes) == ['fixtures/shorter.csv']
    assert before == {p.name: p.read_bytes() for p in tmp_path.glob('*.csv')}
    assert len(manifest['entries']) == 3
    for entry in manifest['entries']:
        assert entry['sha256'] == export.digest(before[entry['path']])


@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_shared_reader_accepts_quoted_fields_and_embedded_newlines(newline):
    from product.nz_election.tools.advance_preflight import inspect
    raw = ('"Date","Daily votes","Note"\n'
           '"2026-10-26","1,000","a ""quoted"" note\non two lines"\n'
           'Total,"1,000",ignored\n').replace('\n', newline).encode()
    report = inspect(raw, url='https://elections.nz/example')
    rows = advance.parse(raw, kind='daily', start='2026-10-26', count_column='Daily votes')
    assert report['kind'] == 'daily'
    assert report['row_count'] == 2 and report['observation_count'] == 1
    assert rows == [dict(date='2026-10-26', daily=1000, cumulative=1000)]


def test_preflight_cli_reports_missing_evidence(tmp_path, capsys):
    from product.nz_election.tools.advance_preflight import cli
    path = tmp_path / 'ambiguous.csv'
    path.write_bytes(b'Date,Total votes\n2026-10-26,10\n2026-10-27,30\n')
    with pytest.raises(SystemExit, match='^INVALID_ADVANCE: missing daily or cumulative evidence in count header$'):
        cli([str(path), '--url', 'https://elections.nz/example'])
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize('surface', ['exception', 'stderr'])
def test_preflight_diagnostics_do_not_echo_header(tmp_path, surface):
    from pathlib import Path
    import subprocess
    import sys
    from product.nz_election.tools.advance_preflight import inspect
    marker = 'CAPTURE_HEADER_MARKER_739'
    raw = f'Date,Total votes {marker}\n2026-10-26,10\n2026-10-27,30\n'.encode()
    if surface == 'exception':
        with pytest.raises(ValueError) as caught:
            inspect(raw, url='https://elections.nz/example')
        diagnostic = str(caught.value)
    else:
        path = tmp_path / 'capture.csv'
        path.write_bytes(raw)
        tool = Path(__file__).resolve().parents[1] / 'tools/advance_preflight.py'
        result = subprocess.run([sys.executable, str(tool), str(path), '--url', 'https://elections.nz/example'],
                                capture_output=True, text=True)
        assert result.returncode != 0 and result.stdout == ''
        diagnostic = result.stderr
    assert marker not in diagnostic
    assert diagnostic.strip() == 'INVALID_ADVANCE: missing daily or cumulative evidence in count header'


@pytest.mark.parametrize('raw', [
    b'Date,Daily votes CAPTURE_MARKER,Daily votes CAPTURE_MARKER\n2026-10-26,10,10',
    b'Date,Daily cumulative votes CAPTURE_MARKER\n2026-10-26,10',
    b'Date,Daily votes\nCAPTURE_MARKER,10',
    b'Date,Daily votes\n2026-10-26,CAPTURE_MARKER',
    b'Date,Daily votes,Note\n2026-10-26,10,CAPTURE_MARKER"quote',
    b'Date,Daily votes\n2026-10-26,10\nTotal,CAPTURE_MARKER"quote',
    b'Date,Daily votes\n2026-10-26,10,CAPTURE_MARKER',
    b'Date,Daily votes\n2026-10-26,10\nCAPTURE_MARKER',
    b'Date,Daily votes\n2026-10-26,\xffCAPTURE_MARKER',
    b'Date,Daily votes\n2026-10-26,"CAPTURE_MARKER',
])
def test_capture_validation_diagnostics_are_fixed(raw, tmp_path, capsys):
    from product.nz_election.tools.advance_preflight import inspect, cli
    for operation in (
        lambda: inspect(raw, url='https://elections.nz/example'),
        lambda: advance.parse(raw, kind='daily', start='2026-10-26', count_column='Daily votes'),
    ):
        with pytest.raises(ValueError) as caught:
            operation()
        assert str(caught.value) == 'INVALID_ADVANCE'
    path = tmp_path / 'capture.csv'
    path.write_bytes(raw)
    with pytest.raises(SystemExit) as caught:
        cli([str(path), '--url', 'https://elections.nz/example'])
    assert str(caught.value) == 'INVALID_ADVANCE'
    assert capsys.readouterr() == ('', '')


def test_cli_does_not_forward_unexpected_value_error(tmp_path, monkeypatch):
    from product.nz_election.tools import advance_preflight
    path = tmp_path / 'capture.csv'
    path.write_bytes(b'Date,Daily votes\n2026-10-26,10')
    def fail(*args, **kwargs):
        raise ValueError('INVALID_ADVANCE: missing daily or cumulative evidence CAPTURE_MARKER')
    monkeypatch.setattr(advance_preflight, 'inspect', fail)
    with pytest.raises(SystemExit, match='^INVALID_ADVANCE$'):
        advance_preflight.cli([str(path), '--url', 'https://elections.nz/example'])


def test_accepted_kind_inference_retains_header():
    from product.nz_election.tools.advance_preflight import inspect
    report = inspect(b'Date,Daily votes CAPTURE_MARKER\n2026-10-26,10', url='https://elections.nz/example')
    assert report['kind_inference'] == "Inferred from explicit daily wording in count header 'Daily votes CAPTURE_MARKER'."


@pytest.mark.parametrize('error_type', [RuntimeError, KeyError, TypeError])
def test_cli_sanitizes_unexpected_exceptions(tmp_path, monkeypatch, capsys, error_type):
    from product.nz_election.tools import advance_preflight
    marker = 'CAPTURE_EXCEPTION_MARKER_842'
    path = tmp_path / 'capture.csv'
    path.write_bytes(b'Date,Daily votes\n2026-10-26,10')
    def fail(*args, **kwargs):
        raise error_type(marker)
    monkeypatch.setattr(advance_preflight, 'inspect', fail)
    with pytest.raises(SystemExit) as caught:
        advance_preflight.cli([str(path), '--url', 'https://elections.nz/example'])
    output = capsys.readouterr()
    assert marker not in output.out + output.err + str(caught.value)
    assert output == ('', '')
    assert str(caught.value) == advance.ERROR
    assert caught.value.code == advance.ERROR
    assert caught.value.__suppress_context__


@pytest.mark.parametrize('error', [KeyboardInterrupt(), SystemExit(2)])
def test_cli_preserves_control_exceptions(tmp_path, monkeypatch, error):
    from product.nz_election.tools import advance_preflight
    path = tmp_path / 'capture.csv'
    path.write_bytes(b'Date,Daily votes\n2026-10-26,10')
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(advance_preflight, 'inspect', fail)
    with pytest.raises(type(error)) as caught:
        advance_preflight.cli([str(path), '--url', 'https://elections.nz/example'])
    assert caught.value is error


def test_cli_sanitizes_serialization_errors(tmp_path, monkeypatch, capsys):
    from product.nz_election.tools import advance_preflight
    path = tmp_path / 'capture.csv'
    path.write_bytes(b'Date,Daily votes\n2026-10-26,10')
    def fail(*args, **kwargs):
        raise RuntimeError('CAPTURE_SERIALIZATION_MARKER')
    monkeypatch.setattr(advance_preflight.json, 'dumps', fail)
    with pytest.raises(SystemExit, match='^INVALID_ADVANCE$'):
        advance_preflight.cli([str(path), '--url', 'https://elections.nz/example'])
    assert capsys.readouterr() == ('', '')
