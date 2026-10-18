"""Static market contracts, separate from poll shares and seat allocation."""
from html import escape
from .build import PREFIX, table, link, compact_time
from .markets import ATTRIBUTION
from .presentation import market_price, overdue


def panel(envs, built):
    env = envs.get('markets')
    status = next((r for r in envs.get('status', {}).get('data', []) if r['dataset'] == 'markets'), {})
    note = ('<div class="source-note" id="source-markets" role="note"><p>' + ATTRIBUTION + '</p>'
            '<p class="source-actions">' + link('https://polymarket.com/', 'Polymarket') +
            link('https://polymarket.com/tos', 'Polymarket terms') +
            (f'<a href="{PREFIX}data/markets.json">Market inputs</a>' if env else '') +
            f'<a href="{PREFIX}downloads/">Sources and producing runs</a></p></div>')
    body = '<section id="markets" class="home-module" aria-describedby="source-markets"><h2>Market prices</h2>'
    if not env:
        return body + '<p>Not available: ' + escape(status.get('message') or 'no validated market observations') + '.</p>' + note + '</section>'
    body += '<p>Daily observations of contract prices. These are not voter surveys or inputs to the seat calculation. Government membership contracts are independent.</p>'
    if status.get('state') == 'stale' or overdue(status.get('last_success_at'), built, 'daily'):
        body += '<p>Update overdue or failed. Showing last-good prices with their original observation times.</p>'
    if overdue(min(r['observed_at'] for r in env['data']), built, 'daily'):
        body += '<p>Source observations are more than 36 hours old.</p>'
    body += '<p>' + escape(status.get('message') or '') + '</p>'
    for family, title in [('next-pm', 'Next prime minister'), ('government-membership', 'Government membership'), ('seat-bands', 'Seat bands')]:
        records = []
        for row in env['data']:
            if row['family'] != family:
                continue
            wording = ('<strong>' + escape(row['event_title']) + '</strong><br>' + escape(row['question']) +
                       ('<p>Closed</p>' if row['closed'] else '<p>Open</p>' if row['active'] else '<p>Inactive</p>') +
                       '<details><summary>Resolution criteria</summary><p>' + escape(row['resolution_criteria']) + '</p>' +
                       '<p class="source-actions">' + link(row['resolution_url'], 'Individual contract rules') + '</p></details>')
            prices = '<br>'.join(escape(o['name']) + ': <strong>' + market_price(o['price']) + '</strong>' for o in row['outcomes']) or 'Not available: inactive contract without prices'
            observation = '<time datetime="' + row['observed_at'] + '">' + compact_time(row['observed_at']) + '</time>'
            records.append([wording, prices + '<p>Observed ' + observation + '</p>',
                            escape(row['volume']) + '<br>Unit unavailable', escape(row['liquidity']) + '<br>Unit unavailable'])
        body += '<figure aria-describedby="source-markets">' + table(title, ['Contract', 'Market price', 'Volume', 'Liquidity'], records, css='downloads', source='source-markets') + '</figure>'
    return body + note + '</section>'
