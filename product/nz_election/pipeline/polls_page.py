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
    polls = envs.get('polls', {}).get('data', [])
    averages = envs.get('averages', {}).get('data', [])
    average = averages[-1] if averages else {}
    content = '<div class="polls-page">'
    bars = averages_chart(average) if average else ''
    if bars:
        derived = 'Others includes derived remainders. ' if average.get('derivations') else ''
        content += '<section id="polls"><h1>Who is ahead in the polls?</h1>' + bars
        content += (f'<div class="source-note home-footnote" id="source-average"><p class="source-actions">'
                    f'Average {observation_label(average["date"])}. Dashed mark: 5%. {derived}'
                    f'<a href="{PREFIX}methods/#source-average">Sources and method</a></p></div></section>')
    else:
        content += '<h1>Polls</h1>' + aliases('polls', 'source-average')
    selected = averages[-29:]
    parties = [p for p in average.get('descriptive', {}) if p != 'others' and any(
        a['descriptive'].get(p, {}).get('value') is not None for a in selected)]
    if parties:
        content += '<section id="trend" class="home-module"><h2>Has support changed?</h2>'
        content += change_summary(selected[0], average) + '<figure aria-describedby="source-trend">'
        content += trend_chart(selected, parties, polls=polls, previous=selected[0]) + '</figure>'
        content += footnote('trend', 'Wikipedia contributors.', '') + '</section>'
    else:
        content += aliases('source-trend')
    seats = hero(envs, built, presentation, heading='Could these parties reach a majority?', show_change=False)
    if seats:
        seats = seats.replace('class="home-hero"', 'class="home-hero home-module"')
        seats = seats.replace('</figure>', '<figcaption>2023 electorate wins assumed; list capacity not checked. Others are derived as the remainder of reported shares.</figcaption></figure>')
        content += seats
    else:
        content += aliases('seats', 'source-seats')
    content += aliases('source-grouping', 'explorer', 'coalition-explorer', 'coalition-title')
    threshold = threshold_sentences(average)
    if threshold:
        content += '<section id="thresholds" class="home-module"><h2>Who is near 5%?</h2>' + threshold
        content += footnote('thresholds', 'Wikipedia contributors.', '') + '</section>'
    else:
        content += aliases('source-thresholds')
    if polls:
        parties = list(config('party-map')['headers'].values())
        names = {identity: name for name, identity in config('party-map')['pollsters'].items()}
        recent = sorted(polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:10]
        rows = []
        for poll in recent:
            rows.append([aliases(poll['id'], 'source-' + poll['id']) + escape(names.get(poll['pollster'], poll['pollster'])),
                         escape(poll['fieldwork_start'] + ' to ' + poll['fieldwork_end']),
                         str(poll['sample']) if poll['sample'] is not None else '',
                         *[display(poll['shares'][p], poll['scale']) if poll['shares'].get(p) is not None else '' for p in parties],
                         ' '.join(link(url, 'Original report') for url in poll['reference_urls'])])
        content += '<section id="recent-polls" class="home-module"><h2>What did the latest polls find?</h2>'
        content += table('Ten most recent national polls; reported party vote percent', ['Pollster', 'Fieldwork', 'Sample'] + [label(p) for p in parties] + ['Report'], rows, source='source-history')
        content += (f'<div class="source-note home-footnote" id="source-history"><p class="source-actions">Wikipedia contributors. '
                    f'<a href="{PREFIX}methods/#source-history">Sources and method</a></p></div></section>')
        content += ''.join(aliases(p['id'], 'source-' + p['id']) for p in polls if p not in recent)
        state, _ = seat_module(envs, built, presentation)
        content += state
    else:
        content += aliases('source-history')
    content += f'<p class="polls-method"><a href="{PREFIX}methods/#average">How the 30-day average works and which polls it includes</a></p></div>'
    return content
