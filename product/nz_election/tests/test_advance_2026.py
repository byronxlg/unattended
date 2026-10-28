"""The reviewed EC transcription supplies sourced text, with no historical fallback."""
from copy import deepcopy
from html.parser import HTMLParser
import json
import pytest
from product.nz_election.pipeline import advance, export, home, vote_page
from product.nz_election.tools.advance_preflight import inspect

NOW = '2026-10-28T07:08:00Z'


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


def captured():
    data, sources, hashes = advance.load()
    return {'advance-voting': export.envelope(data['advance-voting'], sources, 'offline-verification',
                                             'test', inputs=hashes, method='advance-v1', generated=NOW)}


def test_advance_2026_capture_and_provenance():
    env = captured()['advance-voting']
    export.validate_envelope(env, 'advance-voting')
    assert [r['daily'] for r in env['data']] == [69034, 106714]
    assert [r['cumulative'] for r in env['data']] == [69034, 175748]
    assert env['fetched_at'] == NOW
    source = env['source'][0]
    assert 'Transcribed from the EC page, not downloaded.' in source['provenance']
    assert source['caveat'] == 'Informal count, subject to revision; excludes overseas votes.'
    entry = next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries']
                 if e.get('advance', {}).get('year') == 2026)
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
                                   lambda env: home.ribbon(NOW, env)])
def test_advance_vote_and_home_text(render):
    envs = captured()
    rendered = Text(render(envs))
    text = ' '.join(rendered.parts)
    assert '175,748 advance votes reported through 27 October.' in text
    assert envs['advance-voting']['source'][0]['caveat'] in text
    assert envs['advance-voting']['source'][0]['url'] in rendered.links
    assert 'Retrieved 28 Oct, 20:08 NZDT' in text
    assert 'advance votes reported' not in ' '.join(Text(render({})).parts)
    historical, sources, _ = advance.load(historical=True)
    assert 'advance votes reported' not in ' '.join(Text(render({'advance-voting': {
        'data': historical['advance-voting'], 'source': sources}})).parts)
    changed = deepcopy(envs)
    changed['advance-voting']['data'][-1].update(cumulative=123456, date='2026-10-28')
    assert '123,456 advance votes reported through 28 October.' in ' '.join(Text(render(changed)).parts)
    changed['advance-voting']['data'][-1]['cumulative'] = None
    assert 'advance votes reported' not in ' '.join(Text(render(changed)).parts)
