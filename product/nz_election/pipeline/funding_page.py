"""Declared large returns, in reader question order, from the offline EC snapshot."""
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from html import escape

from . import donations, home_graphics as g
from .build import PREFIX, link, observation_label, table
from .home import note, section


def money(cents):
    whole, fraction = divmod(cents, 100)
    return f'NZD {whole:,}' + (f'.{fraction:02d}' if fraction else '')


def whole_money(cents):
    """Round only the displayed total, half up, after summing exact cents."""
    return f'NZD {(cents + 50) // 100:,}'


def ranking(ranked):
    maximum = max(total(rows) for _, rows in ranked)
    bars = ''
    equivalents = []
    for party, rows in ranked:
        label = escape(name(party, rows))
        amount = whole_money(total(rows))
        count = return_count(rows)
        width = Decimal(total(rows)) * 358 / maximum
        bars += ('<div class="funding-bar"><div class="funding-bar-label"><strong>' + label
                 + '</strong><span>' + amount + f' <span>({count})</span></span></div>'
                 f'<svg viewBox="0 0 358 12" role="img" aria-describedby="source-funding" '
                 f'aria-label="{label}: {amount}, {count}">'
                 f'<rect width="{width:.4f}" height="12" style="fill:{g.pc(party)}"/></svg></div>')
        equivalents.append([label, amount, str(len(rows))])
    return '<div class="funding-bars">' + bars + '</div>' + g.hidden(table(
        'Declared totals by party, rounded to whole NZD', ['Party', 'Declared NZD', 'Returns'],
        equivalents, source='source-funding'))


def name(party, rows):
    return g.SHORT.get(party, {'nzof': 'Outdoors & Freedom', 'tttp': 'Te Tai Tokerau Party'}.get(party, rows[0]['party']))


def groups(records):
    result = defaultdict(list)
    for row in records:
        result[row['party_id']].append(row)
    return sorted(result.items(), key=lambda item: (-total(item[1]), item[0]))


def return_count(rows):
    return f'{len(rows)} return' + ('s' if len(rows) != 1 else '')


def total(rows):
    return sum(donations.amount_cents(r['amount_nzd']) for r in rows)


def headline(records):
    if not records:
        return ''
    party, rows = groups(records)[0]
    years = {r['received'][:4] for r in records if r.get('received')}
    period = ' in ' + next(iter(years)) if len(years) == 1 else ''
    count = return_count(rows)
    return f'{name(party, rows)} has declared {whole_money(total(rows))} across {count}, the most of any party{period}.'


def returns_table(records, caption, *, parties=False):
    headings = ['Donor'] + (['Party'] if parties else []) + ['Amount', 'Received']
    values = []
    for r in records:
        donor = link(r['document_url'], r['donor'])
        party = (f'<span class="funding-party" style="--c:{g.pc(r["party_id"])}">'
                 + escape(name(r['party_id'], [r])) + '</span>')
        values.append([donor] + ([party] if parties else []) + [money(donations.amount_cents(r['amount_nzd'])),
                      observation_label(r['received']) if r.get('received') else ''])
    html = table(caption, headings, values, css='funding-table', source='source-funding')
    # Preserve table semantics in browsers that drop them when rows become CSS grids.
    for tag, role in [('table', 'table'), ('thead', 'rowgroup'), ('tbody', 'rowgroup'),
                      ('tr', 'row'), ('th', 'columnheader'), ('td', 'cell')]:
        if tag in {'table', 'th'}:
            html = html.replace('<' + tag + ' ', f'<{tag} role="{role}" ')
        else:
            html = html.replace('<' + tag + '>', f'<{tag} role="{role}">')
    return html


def credit(records):
    latest = max(records, key=lambda row: row['retrieved_at'])
    retrieved = observation_label(latest['retrieved_at'][:10])
    return note('source-funding', donations.LICENCE + ' Retrieved ' + retrieved + '.',
                link(latest['source_url'], 'Electoral Commission returns over NZD 20,000'))


def page(records=None):
    records = donations.load_donations() if records is None else records
    if not records:
        return '<h1>Party funding</h1>'
    ranked = groups(records)
    retrieved = max(r['retrieved_at'] for r in records)
    date_label = observation_label(retrieved[:10])
    source = credit(records)
    content = ('<div class="funding-page"><header class="funding-intro"><h1>Who funds the parties?</h1>'
               '<p class="dek">' + escape(headline(records)) + '</p>'
               '<p>Declared returns over NZD 20,000, not total party funding. Retrieved '
               + link(donations.INDEX_URL, date_label) + '.</p>'
               '<p><a href="#largest-returns">See the ten biggest donations and who gave them</a></p>'
               '</header><figure aria-describedby="source-funding">'
               + ranking(ranked) + '</figure>')
    top = sorted(records, key=lambda r: (-donations.amount_cents(r['amount_nzd']), r['id']))[:10]
    biggest = top[0]
    answer = (money(donations.amount_cents(biggest['amount_nzd'])) + ' from ' + biggest['donor']
              + ' to ' + name(biggest['party_id'], [biggest])
              + (' on ' + observation_label(biggest['received']) if biggest.get('received') else '') + '.')
    content += section('largest-returns', 'Who gave the most?', escape(answer),
                       returns_table(top, 'Ten largest declared donations', parties=True), '', '',
                       prose=True, source='')
    dated = [r for r in records if r.get('received')]
    if dated:
        cutoff = date.fromisoformat(max(r['received'] for r in dated)) - timedelta(days=30)
        recent = sum(r['received'] >= cutoff.isoformat() for r in dated)
        eligible = [(p, rs) for p, rs in ranked if sum(bool(r.get('received')) for r in rs) >= 3]
        omitted = [rs[0]['party'] for p, rs in ranked if (p, rs) not in eligible]
        caption = ('Cumulative declared NZD by received date. Aggregate returns use the last receipt date; '
                   'a return can combine several payments. Retrieved ' + date_label + '.')
        if omitted:
            caption += ' Fewer than three dated returns, omitted: ' + ', '.join(omitted) + '.'
        if eligible:
            content += section('funding-time', 'When did the money arrive?',
                               f'{recent} of {len(records)} declared returns were received since {observation_label(cutoff.isoformat())}.',
                               g.funding_steps(eligible), '', '', source_id='source-funding-time',
                               source_note=note('source-funding-time', escape(caption), link(donations.INDEX_URL, 'EC returns')))
    content += '<section class="module" id="all-returns"><h2>Every declared return</h2><p>Newest received first within each party. Donor links open the EC document. Includes returns whose documents have not been independently checked.</p>'
    for party, rows in ranked:
        content += f'<section id="{party}"><h3>{escape(name(party, rows))}: {return_count(rows)}</h3>'
        content += returns_table(sorted(rows, key=lambda r: (r.get('received', ''), r['id']), reverse=True),
                                 name(party, rows) + ' declared returns') + '</section>'
    return content + '</section>' + source + '</div>'


def feed():
    records = donations.load_donations()
    if not records:
        return ''
    return ('<aside class="module"><h2>Who funds the parties?</h2><p>' + escape(headline(records))
            + '</p><p>Returns over NZD 20,000, not total party funding.</p><p>'
            + f'<a href="{PREFIX}funding/">Compare funding and see every return</a>' + '</p>' + credit(records) + '</aside>')
