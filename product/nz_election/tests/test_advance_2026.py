"""The reviewed EC transcription supplies sourced text, with no historical fallback."""
from copy import deepcopy
from html.parser import HTMLParser
import json
import pytest
from product.nz_election.pipeline import advance, export, home, vote_page
from product.nz_election.pipeline.build import home_presentation
from product.nz_election.tools.advance_preflight import inspect

NOW = '2026-10-28T07:08:00Z'
ORIGINAL = 'ec-2026/advance-voting-2026-10-28.csv'


def test_advance_require_year_committed_capture(capsys):
    from product.nz_election.pipeline import verify
    verify.cli(['advance', '--require-year', '2026'])
    assert capsys.readouterr().out == 'PASS advance\n'


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.parts = []
        self.links = []
        self.feed(html)

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))


@pytest.fixture
def captured(tmp_path, monkeypatch):
    entry = next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries']
                 if e['path'] == ORIGINAL)
    target = tmp_path / ORIGINAL
    target.parent.mkdir(parents=True)
    target.write_bytes((advance.ROOT / ORIGINAL).read_bytes())
    (tmp_path / 'manifest.json').write_text(json.dumps(dict(entries=[entry])))
    with monkeypatch.context() as pinned:
        pinned.setattr(advance, 'ROOT', tmp_path)
        data, sources, hashes = advance.load()
    return {'advance-voting': export.envelope(data['advance-voting'], sources, 'offline-verification',
                                             'test', inputs=hashes, method='advance-v1', generated=NOW)}


def test_advance_2026_capture_and_provenance(captured):
    env = captured['advance-voting']
    export.validate_envelope(env, 'advance-voting')
    assert [r['daily'] for r in env['data']] == [69034, 106714]
    assert [r['cumulative'] for r in env['data']] == [69034, 175748]
    assert env['fetched_at'] == NOW
    source = env['source'][0]
    assert 'Transcribed from the EC page, not downloaded.' in source['provenance']
    assert source['caveat'] == 'Informal count, subject to revision; excludes overseas votes.'
    entry = next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries']
                 if e['path'] == ORIGINAL)
    raw = (advance.ROOT / entry['path']).read_bytes()
    assert inspect(raw, url=entry['url'], kind=entry['advance']['kind'])['manifest_entry']['advance'] == entry['advance']
    with pytest.raises(ValueError, match='missing daily or cumulative evidence'):
        inspect(raw, url=entry['url'])


@pytest.mark.parametrize('kind', ['', [], {}, True, 1.5, 10**100, 'ſ-invalid'])
def test_advance_declared_kind_invalid(kind):
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        inspect(b'Date,2026 General Election\n26 October,1', url='https://vote.nz/', kind=kind)


def test_advance_declared_kind_cannot_contradict_header():
    with pytest.raises(ValueError, match='^INVALID_ADVANCE$'):
        inspect(b'Date,Cumulative votes\n26 October,1', url='https://vote.nz/', kind='daily')


@pytest.mark.parametrize('render', [lambda env: vote_page.page(NOW, envs=env),
                                   lambda env: home.page(env, NOW, home_presentation(env, NOW))])
def test_advance_vote_and_home_text(render, captured):
    envs = captured
    rendered = Text(render(envs))
    text = ' '.join(rendered.parts)
    assert '175,748 advance votes reported through 27 October.' in text
    assert envs['advance-voting']['source'][0]['caveat'] in text
    assert envs['advance-voting']['source'][0]['url'] in rendered.links
    assert 'Retrieved 28 Oct, 20:08 NZDT' in text
    disclosure = 'Transcribed from the EC page, not downloaded.'
    assert disclosure in text
    changed_provenance = deepcopy(envs)
    changed_provenance['advance-voting']['source'][0]['provenance'] = 'Manually recorded & checked against the EC table.'
    changed_text = ' '.join(Text(render(changed_provenance)).parts)
    assert 'Manually recorded & checked against the EC table.' in changed_text
    assert disclosure not in changed_text
    del changed_provenance['advance-voting']['source'][0]['provenance']
    without_provenance = ' '.join(Text(render(changed_provenance)).parts)
    assert without_provenance.split() == text.replace(disclosure, '').split()
    assert 'advance votes reported' not in ' '.join(Text(render({})).parts)
    historical, sources, _ = advance.load(historical=True)
    assert 'advance votes reported' not in ' '.join(Text(render({'advance-voting': {
        'data': historical['advance-voting'], 'source': sources}})).parts)
    changed = deepcopy(envs)
    changed['advance-voting']['data'][-1].update(cumulative=123456, date='2026-10-28')
    assert '123,456 advance votes reported through 28 October.' in ' '.join(Text(render(changed)).parts)
    changed['advance-voting']['data'][-1]['cumulative'] = None
    assert 'advance votes reported' not in ' '.join(Text(render(changed)).parts)


@pytest.mark.parametrize('reverse_entries', [False, True])
@pytest.mark.parametrize('gap', [False, True])
def test_successive_captures_revise_history_and_retain_sources(tmp_path, monkeypatch, reverse_entries, gap):
    from product.nz_election.pipeline.daily_sources import live_loaders
    entries = []
    manifest = tmp_path / 'manifest.json'

    def register(raw, acquired):
        entry = inspect(raw, url='https://vote.nz/example', kind='daily')['manifest_entry']
        entry.update(captured_at=acquired, reviewer='Synthetic test', revision=acquired)
        path = tmp_path / entry['path']
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        entries.append(entry)
        manifest.write_text(json.dumps(dict(entries=list(reversed(entries)) if reverse_entries else entries)))
        return entry

    old_raw = b'Date,2026 General Election\n26 October,10\n27 October,20\n'
    old = register(old_raw, '2026-10-28T01:00:00Z')
    monkeypatch.setattr(advance, 'ROOT', tmp_path)
    loader = live_loaders(now='2026-10-30T01:00:00Z')[0]['advance']
    first, _, first_hashes = loader()
    assert [r['cumulative'] for r in first['advance-voting']] == [10, 30]
    assert first_hashes == {'fixtures/' + old['path']: export.digest(old_raw)}

    new_raw = (b'Date,2026 General Election\n26 October,11\n' +
               (b'' if gap else b'27 October,20\n') + b'28 October,30\n29 October,40\n')
    new = register(new_raw, '2026-10-29T01:00:00Z')
    before = manifest.read_bytes()
    payload, sources, hashes = loader()
    rows = payload['advance-voting']
    assert [r['date'] for r in rows] == (['2026-10-26', '2026-10-28', '2026-10-29'] if gap else
                                       ['2026-10-26', '2026-10-27', '2026-10-28', '2026-10-29'])
    assert [r['daily'] for r in rows] == ([11, 30, 40] if gap else [11, 20, 30, 40])
    assert [r['cumulative'] for r in rows] == ([11, None, None] if gap else [11, 31, 61, 101])
    assert sources[0]['fetched_at'] == new['captured_at']
    assert sources[0]['revision'] == new['revision']
    assert hashes == {'fixtures/' + new['path']: export.digest(new_raw)}
    assert manifest.read_bytes() == before
    assert (tmp_path / old['path']).read_bytes() == old_raw
    assert (tmp_path / new['path']).read_bytes() == new_raw
    assert len(json.loads(before)['entries']) == 2

    # Retained history still participates in validation after a newer capture arrives.
    (tmp_path / old['path']).write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='CAPTURE_HASH_MISMATCH'):
        loader()
