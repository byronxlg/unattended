"""The accepted polls questions, with legacy destinations retained as aliases."""
from decimal import Decimal
from fractions import Fraction
from html import escape

from .average import display
from .build import PREFIX, config, label, link, observation_label, table, seat_module
from .home import footnote, hero
from .home_charts import colour, trend_chart


def aliases(*identities):
    return ''.join(f'<span id="{escape(identity, quote=True)}"></span>' for identity in identities)


def averages_chart(average):
    rows = sorted(((p, d) for p, d in average['descriptive'].items() if d['value'] is not None),
                  key=lambda row: (-Fraction(row[1]['value'], row[1]['scale']), row[0]))
    if not rows:
        return ''
    maximum = max(Decimal(10), max(Decimal(d['value']) / d['scale'] for _, d in rows))
    body = ''
    for party, data in rows:
        width = Decimal(data['value']) / data['scale'] * 100 / maximum
        body += (f'<div class="average-row" data-party="{party}"><span>{escape(label(party))}</span>'
                 f'<div class="average-track"><span class="average-bar" style="width:{width:.6f}%;background:{colour(party)}"></span>'
                 f'<span class="average-threshold" style="left:{500 / maximum:.6f}%"></span>'
                 f'<strong style="left:{width:.6f}%">{display(data["value"], data["scale"])}</strong></div></div>')
    return '<figure class="average-bars" aria-describedby="source-average">' + body + '</figure>'


def threshold_sentences(average):
    rows = [(p, d) for p, d in average.get('descriptive', {}).items()
            if p != 'others' and d.get('value') is not None and 3 * d['scale'] <= d['value'] <= 7 * d['scale']]
    return ''.join(f'<p data-threshold-party="{p}">{escape(label(p))} averages {display(d["value"], d["scale"])}; '
                   'an electorate win can qualify it for list seats below 5%.</p>' for p, d in rows)


def change_summary(first, latest):
    ranked = sorted(((p, d) for p, d in latest['descriptive'].items()
                     if p != 'others' and d.get('value') is not None),
                    key=lambda row: -Fraction(row[1]['value'], row[1]['scale']))
    leaders = {p for p, _ in ranked[:2]} | {'nat', 'lab'}
    changes = []
    for party, after in ranked:
        before = first['descriptive'].get(party, {})
        if party not in leaders or before.get('value') is None:
            continue
        delta = Decimal(after['value']) / after['scale'] - Decimal(before['value']) / before['scale']
        changes.append(f'<span data-change-party="{party}">{escape(label(party))} {delta:+.1f} points</span>')
    if not changes:
        return ''
    return ('<p class="poll-change-summary" aria-describedby="source-trend">' + '; '.join(changes)
            + f' since <time datetime="{first["date"]}">{observation_label(first["date"])}</time>.</p>')


def page(envs, built, presentation):
    from datetime import date
    from . import home_graphics as g
    from .home import seat_hero, section
    from .snapshots import load_voting
    polls = envs.get('polls', {}).get('data', [])
    averages = envs.get('averages', {}).get('data', [])
    average = averages[-1] if averages else {}
    content = '<div class="polls-page">'
    rows = sorted(((p, d) for p, d in average.get('descriptive', {}).items() if d['value'] is not None),
                  key=lambda row: (row[0] == 'others', -Fraction(row[1]['value'], row[1]['scale']), row[0]))
    if rows:
        month = averages[-31] if len(averages) > 30 else averages[0]
        bars = ''
        for party, d in rows:
            v = g.share(d)
            before = g.share(month['descriptive'].get(party))
            delta = f'{v - before:+.1f}' if before is not None else ''
            bars += (f'<li style="--c:{g.pc(party)}"><span class="name">{escape(g.SHORT.get(party, label(party)))}</span>'
                     f'<span class="bar"><i style="width:{min(Decimal(100), v * Decimal("2.5")):.2f}%"></i></span>'
                     f'<b>{display(d["value"], d["scale"])}</b><small>{delta}</small></li>')
        derived = ' Others includes derived remainders.' if average.get('derivations') else ''
        content += ('<section id="polls" class="page-head"><p class="kicker">Polls</p><h1>Who is ahead in the polls?</h1>'
                    + change_summary(month, average)
                    + f'<figure aria-describedby="source-average"><ul class="average-list"><li class="head"><span></span><span class="axis"><span style="left:0">0</span><span style="left:12.5%">5%</span><span style="left:50%">20%</span><span style="left:100%">40%</span></span><span>Average</span><small>30 days</small></li>{bars}</ul></figure>'
                    f'<div class="source-note home-footnote" id="source-average"><p class="source-actions">'
                    f'Average {observation_label(average["date"])}, every poll from the previous 30 days weighted equally.{derived} '
                    f'<a href="{PREFIX}methods/#source-average">Sources and method</a></p></div></section>')
    else:
        content += '<h1>Polls</h1>' + aliases('polls', 'source-average')
    if averages:
        records = {r['id']: r for r in load_voting()}
        election = date.fromisoformat(records['election-day']['date']) if records.get('election-day', {}).get('date') else date(2026, 11, 7)
        graphic = g.trend(averages, polls, election) + g.trend(averages, polls, election, wide=False) + g.trend_table(averages)
        content += section('trend', 'How has support changed this year?',
                           'Each dot is a poll; each line is the 30-day average.', graphic, 'Wikipedia contributors', '')
    else:
        content += aliases('source-trend')
    seats = seat_hero(envs, built, presentation)
    if seats:
        seats = seats.replace('<h1>Who is favoured to form the next government?</h1>', '<h2>Could these parties reach a majority?</h2>')
        seats = seats.replace('</figure>', '<figcaption class="chart-note">List capacity not checked. Others are derived as the remainder of reported shares.</figcaption></figure>', 1)
        content += seats.replace('class="hero"', 'class="hero module"')
    else:
        content += aliases('seats', 'source-seats')
    content += aliases('source-grouping', 'explorer', 'coalition-explorer', 'coalition-title')
    if 'seats' in envs and average and polls:
        from .average import threshold_watch
        rows_t = [r for r in threshold_watch(polls, average, envs['seats']['data']['assumptions']) if r['value'] is not None]
        content += section('thresholds', 'Who is near 5%?',
                           'A party needs 5% of the party vote, or one electorate, to share in list seats.',
                           g.threshold_bars(rows_t) if rows_t else '', 'Wikipedia contributors', '') or aliases('source-thresholds')
    else:
        content += aliases('source-thresholds')
    if polls:
        names = {identity: name for name, identity in config('party-map')['pollsters'].items()}
        content += ('<section id="recent-polls" class="module"><header class="module-head"><h2>Every poll this year</h2>'
                    f'<p class="dek">All {len(polls)} national polls since January, newest first. Darker cells are larger shares.</p></header>'
                    + g.poll_table(polls, average, names, count=len(polls), reports=True, caption='Every national poll this year, party vote percent').replace('aria-describedby="source-polls"', 'aria-describedby="source-history"')
                    + f'<div class="module-foot"><div class="source-note home-footnote" id="source-history"><p class="source-actions">Wikipedia contributors. '
                    f'<a href="{PREFIX}methods/#source-history">Sources and method</a></p></div></div></section>')
        content += ''.join(aliases(p['id'], 'source-' + p['id']) for p in polls)
        state, _ = seat_module(envs, built, presentation)
        content += state
    else:
        content += aliases('source-history')
    content += f'<p class="polls-method"><a class="more" href="{PREFIX}methods/#average">How the 30-day average works and which polls it includes</a></p></div>'
    return content
