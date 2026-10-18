"""Normalize the reviewed Gamma event allowlist without interpreting contract prices."""
from datetime import datetime
import json
import re
from . import daily_sources as ds, export
from .refresh import config

ATTRIBUTION = 'Source: Polymarket. Subject to Polymarket terms. No open licence asserted.'
FAMILIES = {'next-pm', 'government-membership', 'seat-bands'}


def events():
    return config('markets')['events']


def parse(raw, slug, family, observed):
    try:
        body = json.loads(raw, parse_float=str)
        if not isinstance(body, list) or len(body) != 1:
            raise ValueError
        event = body[0]
        if event['slug'] != slug or not event['markets'] or not isinstance(event['markets'], list):
            raise ValueError
        rows = []
        for market in event['markets']:
            names, ids = [json.loads(market[k]) for k in ('outcomes', 'clobTokenIds')]
            unpriced = 'outcomePrices' not in market and market['active'] is False and market['closed'] is False
            prices = [None] * len(names) if unpriced else json.loads(market['outcomePrices'])
            if not all(isinstance(v, list) for v in (names, prices, ids)) or not names or not len(names) == len(prices) == len(ids):
                raise ValueError
            updated = market['updatedAt']
            if not isinstance(updated, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', updated):
                raise ValueError
            datetime.fromisoformat(updated)
            row = dict(id='gamma-' + market['id'], event_id=event['id'], event_slug=slug,
                       event_title=event['title'], market_id=market['id'], family=family,
                       question=market['question'], outcomes=[] if unpriced else [dict(id=i, name=n, price=p) for i, n, p in zip(ids, names, prices)],
                       unpriced_outcomes=[dict(id=i, name=n) for i, n in zip(ids, names)] if unpriced else [],
                       volume=market['volume'], volume_unit=None, liquidity=market['liquidity'], liquidity_unit=None,
                       resolution_url='https://polymarket.com/event/' + slug + '/' + market['slug'],
                       resolution_criteria=market['description'], updated_at=updated,
                       closed=market['closed'], active=market['active'], observed_at=observed,
                       source_ref=ds.refs('polymarket/' + slug + '.json', 'market:' + market['id'],
                                          sorted(export.FIELDS['markets'] - export.ROW)))
            export.validate_market_row(row, allow_turnout=family == 'excluded-turnout')
            rows.append(row)
        if len({r['id'] for r in rows}) != len(rows):
            raise ValueError
        return rows
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError):
        raise ValueError('INVALID_MARKET') from None


def load(input_loader=ds.inputs):
    mapping = events()
    raw, sources, hashes = input_loader({'polymarket/' + e['slug'] + '.json' for e in mapping}, ('markets',))
    rows = []
    for event in mapping:
        path = 'polymarket/' + event['slug'] + '.json'
        parsed = parse(raw[path], event['slug'], event['family'], ds.acquired(sources, path))
        if event['family'] in FAMILIES:
            rows.extend(parsed)
    if {r['family'] for r in rows} != FAMILIES or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('INVALID_MARKET')
    return {'markets': rows}, sources, hashes
