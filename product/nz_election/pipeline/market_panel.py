"""Four leading priced contracts, without promoting placeholders or implying a forecast."""
from decimal import Decimal
from html import escape
import re
from .build import PREFIX, link, compact_time
from .markets import ATTRIBUTION, events
from .presentation import market_price, market_money, overdue

PLACEHOLDER = re.compile(r'\b(?:person|candidate|party|outcome)\s+(?:[a-z]|[0-9]+)\b', re.I)


def eligible(row):
    return bool(row['outcomes']) and not PLACEHOLDER.search(row['question']) and not any(
        PLACEHOLDER.search(o['name']) for o in row['outcomes'])


def yes(row):
    return next((o for o in row['outcomes'] if o['name'] == 'Yes'), None)


def leaders(rows):
    selected = []
    for event in events():
        if event['family'] == 'excluded-turnout':
            continue
        options = [r for r in rows if r['event_slug'] == event['slug'] and eligible(r) and yes(r)]
        selected.append((event, min(options, key=lambda r: (-Decimal(yes(r)['price']), r['market_id'])) if options else None))
    return selected


def label(row):
    patterns = {'next-pm': r'Will (.+) be the next Prime Minister of New Zealand after the 2026 elections\?',
                'government-membership': r'Will (.+) be part of the next Government of New Zealand\?',
                'seat-bands': r'Will the (.+) win (.+) seats in the New Zealand House of Representatives in the 2026 New Zealand legislative election\?'}
    match = re.fullmatch(patterns[row['family']], row['question'])
    if not match:
        return row['question']
    return ': '.join(match.groups()) + (' seats' if row['family'] == 'seat-bands' else '')


def panel(envs, built):
    env = envs.get('markets')
    status = next((r for r in envs.get('status', {}).get('data', []) if r['dataset'] == 'markets'), {})
    body = '<section id="markets" class="home-module" aria-describedby="source-markets"><h2>What do prediction markets say?</h2>'
    actions = link('https://polymarket.com/tos', 'Polymarket terms') + f'<a href="{PREFIX}downloads/">Data and sources</a>'
    amounts = ''
    if not env:
        body += '<p>Not available: ' + escape(status.get('message') or 'no validated market observations') + '.</p>'
    else:
        selected = leaders(env['data'])
        body += '<p>Highest Yes price per event, not a forecast. Government membership contracts are independent.</p>'
        observed = min(r['observed_at'] for r in env['data'])
        stale = status.get('state') == 'stale' or overdue(status.get('last_success_at'), built, 'daily')
        body += '<p>' + ('Update overdue or failed. ' if stale else '') + 'Observed <time datetime="' + observed + '">' + compact_time(observed) + '</time>.</p>'
        if overdue(observed, built, 'daily'):
            body += '<p>Source observations are more than 36 hours old.</p>'
        for family, title in [('next-pm', 'Next prime minister'), ('government-membership', 'Government membership'), ('seat-bands', 'Seat bands')]:
            body += '<figure aria-describedby="source-markets"><table aria-describedby="source-markets"><caption>' + title + ' / Market price (Yes)</caption><tbody>'
            for event, row in selected:
                if event['family'] != family:
                    continue
                if row is None:
                    name = 'National' if 'national' in event['slug'] else 'Labour' if 'labour' in event['slug'] else title
                    body += '<tr><th scope="row">' + name + '</th><td>No priced contracts</td></tr>'
                    continue
                name = label(row)
                body += '<tr data-market-id="' + row['id'] + '"><th scope="row">' + escape(name) + (' (closed)' if row['closed'] else '') + '</th><td>' + market_price(yes(row)['price']) + '</td></tr>'
                rules_name = {'next-pm': 'PM rules', 'government-membership': 'Government rules'}.get(family, ('National' if 'national' in event['slug'] else 'Labour') + ' seat rules')
                actions += link('https://polymarket.com/event/' + event['slug'], rules_name)
                amounts += '<p>' + escape(name) + ': volume ' + market_money(row['volume']) + '; liquidity ' + market_money(row['liquidity']) + '. Observed ' + escape(row['observed_at']) + '.</p>'
            body += '</tbody></table></figure>'
        amounts = '<section id="market-observations" aria-describedby="source-markets"><h3>Amounts and observation details</h3>' + amounts + '<p>' + escape(status.get('message') or env['run_url']) + '</p></section>'
        actions += f'<a href="{PREFIX}methods/#market-observations">Amounts and observations</a>'
    note = '<div class="source-note" id="source-markets" role="note"><p>' + ATTRIBUTION + '</p><p class="source-actions">' + actions + '</p></div>'
    return body + note + '</section>' + amounts
