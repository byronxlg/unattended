"""Captured market evidence, strict normalized values and static accessible presentation."""
from copy import deepcopy
import json
import pytest
from product.nz_election.pipeline import markets, export
from product.nz_election.pipeline.fixtures import captures, ROOT
from product.nz_election.pipeline.market_panel import panel, leaders, eligible
from product.nz_election.pipeline.presentation import market_price, market_money
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
    assert first['volume_unit'] == first['liquidity_unit'] == 'USD'
    assert market_money('13164.465509') == '13,164 USD'
    assert market_money('0.5') == '1 USD'
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
                      'liquidity_unit': ['EUR', '$'], 'market_id': ['', None, 1, '١', '1/2'],
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
    assert 'inactive contract without prices' not in panel(env, NOW)
    assert all(r['question'] not in panel(env, NOW) for r in missing)
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
    assert ' USD' in html and '$' not in html
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


def test_home_market_summary_and_all_page_filtering(tmp_path):
    from product.nz_election.pipeline.build import build
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    from product.nz_election.tests.market_checks import check_markup
    daily_refresh(tmp_path / 'data', now=NOW)
    site = build(tmp_path / 'data', tmp_path / 'built', built=NOW)
    envs = export.validate_bundle(tmp_path / 'data')
    for page in site.rglob('*.html'):
        check_markup(page.read_text(), envs['markets']['data'])
    chosen = [r for _, r in leaders(envs['markets']['data']) if r]
    assert len(chosen) == 4 and all(eligible(r) for r in chosen)
    assert 'id="markets"' not in (site / 'index.html').read_text()
    html = (site / 'methods/index.html').read_text()
    assert all(label in html for label in ('Will Christopher Luxon be the next Prime Minister?', 'Will Green Party be part of the next Government?', 'Will the National Party win 35-39 seats?', 'Will the Labour Party win 35-39 seats?'))
    assert html.count('data-market-id=') == 4
    assert (site / 'index.html').read_text().count('href="https://polymarket.com/event/') == 0
    assert (site / 'methods/index.html').read_text().count('href="https://polymarket.com/event/') == 4
    for row in envs['markets']['data']:
        row['question'] = 'Will Person A win?'
    html = panel(envs, NOW)
    assert 'Person A' not in html and html.count('No priced contracts') == 4
    assert 'data-market-id=' not in html


@pytest.mark.parametrize('bad', ['', None, True, [], {}, 0.5, 10**100, '9'*5000, '٢٠٢٦', 'not-a-timestamp'])
@pytest.mark.parametrize('field', ['observed_at', 'updated_at'])
def test_timestamp_error_parity(field, bad):
    event = markets.events()[0]
    body = json.loads((ROOT / ('polymarket/' + event['slug'] + '.json')).read_text())
    observed = bad if field == 'observed_at' else NOW
    if field == 'updated_at':
        body[0]['markets'][0]['updatedAt'] = bad
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        markets.parse(json.dumps(body), event['slug'], event['family'], observed)
    env = environment()['markets']
    env['data'][0][field] = bad
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        export.validate_envelope(env, 'markets')


def test_required_market_fields_error_parity():
    event = markets.events()[0]
    raw = json.loads((ROOT / ('polymarket/' + event['slug'] + '.json')).read_text())
    fields = {'event_id': ('event', 'id'), 'event_title': ('event', 'title'),
              'market_id': ('market', 'id'), 'question': ('market', 'question'),
              'volume': ('market', 'volume'), 'liquidity': ('market', 'liquidity'),
              'resolution_criteria': ('market', 'description'), 'active': ('market', 'active'),
              'closed': ('market', 'closed')}
    for field, (level, source_field) in fields.items():
        bads = ['', None, [], {}, 0.5, 10**100]
        if field not in {'active', 'closed'}:
            bads += [True]
        if field in {'event_id', 'market_id', 'volume', 'liquidity'}:
            bads += ['١', '9'*5000, 'NaN']
        for bad in bads:
            body = deepcopy(raw)
            target = body[0] if level == 'event' else body[0]['markets'][0]
            target[source_field] = bad
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
            env = environment()['markets']
            env['data'][0][field] = bad
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                export.validate_envelope(env, 'markets')
        body = deepcopy(raw)
        target = body[0] if level == 'event' else body[0]['markets'][0]
        del target[source_field]
        with pytest.raises(ValueError, match='^INVALID_MARKET$'):
            markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
        env = environment()['markets']
        del env['data'][0][field]
        with pytest.raises(ValueError, match='^INVALID_MARKET$'):
            export.validate_envelope(env, 'markets')


def test_market_collections_and_identifiers_error_parity():
    event = markets.events()[0]
    original = json.loads((ROOT / ('polymarket/' + event['slug'] + '.json')).read_text())
    original[0]['markets'] = original[0]['markets'][:1]
    for field in ('outcomes', 'outcomePrices', 'clobTokenIds'):
        for bad in ('', None, True, [], {}, 0.5, 10**100, '[]', 'null', '"odd"', '["Yes"]'):
            body = deepcopy(original)
            body[0]['markets'][0][field] = bad
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
    for field in ('event_slug', 'family', 'source_ref', 'outcomes', 'unpriced_outcomes', 'id', 'resolution_url'):
        for bad in ('', None, True, {}, 0.5, 10**100, '١', '9'*5000):
            env = environment()['markets']
            env['data'][0][field] = bad
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                export.validate_envelope(env, 'markets')
    for field in ('event_slug', 'family'):
        for bad in ('', None, True, [], {}, 0.5, 10**100, '١', '9'*5000):
            with pytest.raises(ValueError, match='^INVALID_MARKET$'):
                markets.parse(json.dumps(original), bad if field == 'event_slug' else event['slug'],
                              bad if field == 'family' else event['family'], NOW)
    body = deepcopy(original)
    body[0]['markets'] *= 2
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        markets.parse(json.dumps(body), event['slug'], event['family'], NOW)
    env = environment()['markets']
    env['data'].append(deepcopy(env['data'][0]))
    with pytest.raises(ValueError, match='^INVALID_MARKET$'):
        export.validate_envelope(env, 'markets')


@pytest.mark.parametrize('built,ended', [
    ('2026-11-07T06:00:00Z', False),
    ('2026-11-07T10:00:00Z', False),
    ('2026-11-08T06:01:00Z', False),
    ('2026-11-14T00:00:00Z', False),
    ('2026-11-14T11:00:00Z', True),
    ('2026-11-27T00:00:00Z', True),
])
@pytest.mark.parametrize('failed', [False, True])
@pytest.mark.parametrize('old', [False, True])
def test_retained_markets_scheduled_shutdown(built, ended, failed, old, monkeypatch):
    from datetime import datetime, timedelta, timezone
    from product.nz_election.pipeline import sunsets
    from product.nz_election.pipeline.build import compact_time
    from product.nz_election.tools.check_visible_text import VisibleText
    envs = environment()
    collected = (min(datetime.fromisoformat(built), sunsets.DAILY_CLOSE) - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    observed = NOW if old else collected
    for row in envs['markets']['data']:
        row['observed_at'] = observed
    envs['status'] = {'data': [dict(dataset='markets', state='stale' if failed else 'fresh',
                                  error_code='INVALID_MARKET' if failed else None,
                                  last_attempt_at=collected, last_success_at=NOW if old else collected)]}
    retained = deepcopy(envs)
    monkeypatch.setenv('GITHUB_EVENT_NAME', 'workflow_dispatch')
    text = VisibleText(panel(envs, built)).text
    assert ('Scheduled updates ended.' in text) is ended
    assert f'Observed {compact_time(observed)}.' in text
    assert ('Update overdue or failed.' in text) is (not ended and (failed or old))
    assert ('Source observations are more than 36 hours old.' in text) is (not ended and old)
    assert ('The last update failed.' in text) is (ended and failed)
    assert '52.5%' in text
    assert envs == retained


@pytest.mark.parametrize('built', ['2026-11-14T11:00:00Z', '2026-11-27T00:00:00Z'])
@pytest.mark.parametrize('status', [
    {'dataset': 'markets', 'state': 'stale', 'last_attempt_at': NOW},
    {'dataset': 'markets', 'state': 'stale'},
    {'dataset': 'markets'},
])
def test_sunset_markets_without_failure_evidence(built, status):
    from product.nz_election.pipeline.build import compact_time
    from product.nz_election.tools.check_visible_text import VisibleText
    envs = environment()
    envs['status'] = {'data': [deepcopy(status)]}
    retained = deepcopy(envs)
    text = VisibleText(panel(envs, built)).text
    assert 'Scheduled updates ended.' in text
    assert 'update failed' not in text
    observed = min(row['observed_at'] for row in envs['markets']['data'])
    assert f'Observed {compact_time(observed)}.' in text
    assert '52.5%' in text
    assert envs == retained
