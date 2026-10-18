"""Captured market evidence, strict normalized values and static accessible presentation."""
from copy import deepcopy
import json
import pytest
from product.nz_election.pipeline import markets, export
from product.nz_election.pipeline.fixtures import captures, ROOT
from product.nz_election.pipeline.market_panel import panel
from product.nz_election.pipeline.presentation import market_price
from product.nz_election.tests.design_checks import provenance

NOW = '2026-10-18T01:00:00Z'


def environment():
    payloads, sources, hashes = markets.load()
    return {'markets': export.envelope(payloads['markets'], sources, 'offline-verification', 'a' * 40,
                                      inputs=hashes, method='markets-v1', generated=NOW)}


def test_required_gamma_captures():
    mapping = markets.events()
    raw = captures(paths={'polymarket/' + e['slug'] + '.json' for e in mapping})
    assert len(raw) == 5
    assert [len(markets.parse(raw['polymarket/' + e['slug'] + '.json'], e['slug'], e['family'], NOW)) for e in mapping] == [34, 6, 7, 7, 6]
    event = mapping[0]
    for body in ([], [{}], [dict(slug='wrong', markets=[{}])], [dict(slug=event['slug'], markets=[])]):
        with pytest.raises(ValueError, match='^INVALID_MARKET$'):
            markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
    manifest = json.loads((ROOT / 'manifest.json').read_text())['entries']
    turnout = next(e for e in manifest if e['path'].endswith('new-zealand-election-turnout.json'))
    assert 'exclu' in turnout['notes'].lower()


def test_three_contract_families():
    env = environment()['markets']
    assert {r['family'] for r in env['data']} == markets.FAMILIES
    assert len(env['data']) == 54
    assert all('turnout' not in r['event_slug'] for r in env['data'])
    assert export.FAMILIES['markets'] == {'markets'}
    assert export.FAMILIES['polls'].isdisjoint(export.FAMILIES['markets'])


def test_exact_prices_units_and_resolution():
    env = environment()['markets']
    export.validate_envelope(env, 'markets')
    first = env['data'][0]
    assert first['outcomes'][0]['price'] == '0.525'
    assert first['volume'] == '13164.465509'
    assert first['volume_unit'] is first['liquidity_unit'] is None
    assert first['resolution_url'].startswith('https://polymarket.com/event/' + first['event_slug'] + '/')
    assert 'Governor-General' in first['resolution_criteria']
    assert first['observed_at'] != first['updated_at']
    assert market_price('0.525') == '52.5%'
    assert market_price('0.00055') == '0.1%'
    assert market_price('1') == '100.0%'


@pytest.mark.parametrize('bad', ['', None, True, [], {}, 0.5, 10**100, '1.0001', '-0.1', 'NaN', 'Infinity', '1e-2', '١', '9'*5000])
def test_malformed_price_parser_export_parity(bad):
    event = markets.events()[0]
    body = json.loads((ROOT / ('polymarket/' + event['slug'] + '.json')).read_text())
    body[0]['markets'][0]['outcomePrices'] = json.dumps([bad, '0.475'])
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
    env = environment()['markets']
    env['data'][0]['outcomes'][0]['price'] = bad
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        export.validate_envelope(env, 'markets')


def test_market_malformed_fields():
    original = environment()['markets']['data'][0]
    for key, bads in {'volume': ['', None, 1.2, 'NaN', '-1', '1e999'],
                      'liquidity_unit': ['USD', '$'], 'market_id': ['', None, 1, '١', '1/2'],
                      'resolution_url': ['javascript:alert(1)', '//example.com', 'https://x\n.invalid', 'https://user@x.test', 'https://x\\y'],
                      'updated_at': ['', None, '2026-02-30T00:00:00Z'],
                      'closed': [None, 0, 'false']}.items():
        for bad in bads:
            row = deepcopy(original)
            row[key] = bad
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                export.validate_market_row(row)


def test_inactive_unpriced_contracts():
    env = environment()
    rows = env['markets']['data']
    missing = [r for r in rows if r['unpriced_outcomes']]
    assert len(missing) == 27
    assert all(not r['outcomes'] and not r['active'] and len(r['unpriced_outcomes']) == 2 for r in missing)
    assert 'inactive contract without prices' in panel(env, NOW)
    row = deepcopy(missing[0])
    row['active'] = True
    with pytest.raises(ValueError, match='INVALID_MARKET'):
        export.validate_market_row(row)


def test_missing_market_capture_unavailable(tmp_path, monkeypatch):
    from product.nz_election.pipeline import daily_sources
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    original = daily_sources.captures
    def missing(*args, **kwargs):
        if any(p.startswith('polymarket/') for p in kwargs['paths']):
            raise ValueError('MISSING_CAPTURE: polymarket/required.json')
        return original(*args, **kwargs)
    monkeypatch.setattr(daily_sources, 'captures', missing)
    daily_refresh(tmp_path / 'data', now=NOW, loaders={'markets': markets.load})
    envs = export.validate_bundle(tmp_path / 'data')
    assert 'markets' not in envs
    state = next(r for r in envs['status']['data'] if r['dataset'] == 'markets')
    assert state['state'] == 'unavailable' and state['error_code'].startswith('MISSING_CAPTURE')
    assert 'Not available' in panel(envs, NOW) and 'MISSING_CAPTURE' in panel(envs, NOW)


def test_market_terms_and_observation_rendered():
    envs = environment()
    html = panel(envs, NOW)
    provenance(html)
    assert html.count('<table') == html.count('<figure') == 3
    assert markets.ATTRIBUTION in html and 'Market price' in html
    assert 'Unit unavailable' in html and '$' not in html
    assert 'Update overdue' in html
    assert envs['markets']['data'][0]['observed_at'] in html
    assert 'Source observations are more than 36 hours old' in panel(envs, '2026-10-20T00:00:00Z')
    row = envs['markets']['data'][0]
    row['question'] = '<script>alert(1)</script>'
    row['resolution_criteria'] = '<img src=x onerror=alert(1)>'
    html = panel(envs, NOW)
    assert '<script>' not in html and '<img' not in html and '&lt;script&gt;' in html


def test_markets_csv_roundtrip():
    import csv
    import io
    env = environment()['markets']
    records = list(csv.DictReader(io.StringIO(export.csv_bytes(env).decode())))
    for record, row in zip(records, env['data']):
        assert json.loads(record['outcomes_json']) == row['outcomes']
        assert record['volume'] == row['volume']
