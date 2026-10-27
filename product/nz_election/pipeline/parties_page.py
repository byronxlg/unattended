"""Party answers from offline snapshots and the published descriptive average."""
from datetime import date
from decimal import Decimal
from html import escape

from .average import display
from .build import PREFIX, config, label, link, observation_label
from .home_charts import colour
from .snapshots import load, load_party_details as supplemental


def party_link(p, text=None):
    title = escape(text if text is not None else label(p))
    if p not in config('party-colours'):
        return title
    return f'<a href="{PREFIX}parties/#{p}">{title}</a>'


def ordered(averages):
    values = averages[-1]['descriptive'] if averages else {}
    def key(p):
        v = values.get(p, {})
        return (v.get('value') is None, -Decimal(v['value']) / v['scale'] if v.get('value') is not None else 0, p)
    return sorted((p['id'] for p in config('party-map')['parties'] if not p['aggregate']), key=key)


def polling(p, averages):
    if not averages or averages[-1]['descriptive'].get(p, {}).get('value') is None:
        return ''
    latest = averages[-1]
    series = [(a['date'], a['descriptive'].get(p, {})) for a in averages]
    available = [(d, v) for d, v in series if v.get('value') is not None]
    first, base = available[0]
    current = latest['descriptive'][p]
    value = display(current['value'], current['scale'])
    change = Decimal(current['value']) / current['scale'] - Decimal(base['value']) / base['scale']
    delta = ''
    if first != latest['date']:
        delta = f'{"Up" if change > 0 else "Down" if change < 0 else "Unchanged"}'
        if change:
            delta += f' {abs(change):.1f} percentage points'
        delta += ' since ' + observation_label(first) + '.'
    start = date.fromisoformat(series[0][0])
    days = max(1, (date.fromisoformat(latest['date']) - start).days)
    maximum = max(Decimal(10), *(Decimal(v['value']) / v['scale'] for _, v in available)) + 2
    def y(v):
        return 84 - v * 72 / maximum
    path, active = '', False
    for day, v in series:
        if v.get('value') is None:
            active = False
            continue
        x = Decimal((date.fromisoformat(day) - start).days) * 270 / days
        py = y(Decimal(v['value']) / v['scale'])
        path += f'{"L" if active else "M"}{x:.1f} {py:.1f}'
        active = True
    source = 'source-average-' + p
    return (f'<div class="party-poll"><p class="party-number"><strong>{value}</strong> polling</p>'
            f'<p>Average on {observation_label(latest["date"])}. {delta}</p>'
            f'<figure class="party-spark" aria-describedby="{source}"><svg viewBox="0 0 270 105" preserveAspectRatio="none" role="img" aria-label="{escape(label(p))} polling trend; dashed rule marks 5 percent" aria-describedby="{source}">'
            f'<path d="M0 {y(Decimal(5)):.1f}H270" stroke="var(--grey)" stroke-dasharray="4 3"/>'
            f'<path d="{path}" fill="none" stroke="{colour(p)}" stroke-width="3.5" vector-effect="non-scaling-stroke"/>'
            f'<circle cx="270" cy="{py:.1f}" r="3" fill="{colour(p)}"/>'
            f'</svg><span class="spark-end" style="top:{py-8:.1f}px">{value}</span><span class="spark-rule" style="top:{y(Decimal(5))-18:.1f}px">5%</span></figure>'
            f'<div class="source-note" id="{source}"><p class="source-actions"><span>{observation_label(first)} to {observation_label(latest["date"])}.</span> '
            f'<a href="{PREFIX}methods/#home-trend">Poll inputs and method.</a> <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0.</a> '
            '<span>5% qualifies for list seats; an electorate win can also qualify.</span></p></div></div>')


def largest_donors(rows):
    donors = {}
    for row in rows:
        # Match exact EC labels only; similar names are not an identity join.
        donor = donors.setdefault(row['donor'], {'amount': Decimal(0), 'dates': set()})
        donor['amount'] += Decimal(row['amount_nzd'])
        donor['dates'].add(row['received'])
    return sorted(donors.items(), key=lambda item: (-item[1]['amount'], item[0]))[:3]


def page(envs, built, facts=None):
    if facts is None:
        facts = {**{n: load(n) for n in ('leaders', 'positions', 'donations')},
                 **{n: supplemental(n) for n in ('policy-links', 'party-list-tops')}}
    averages = sorted(envs.get('averages', {}).get('data', []), key=lambda a: a['date'])
    parties = ordered(averages)
    content = '<div class="parties-page"><nav class="party-picker" aria-label="Choose a party">' + ''.join(
        f'<a href="#{p}" style="--party:{colour(p)}"><i aria-hidden="true"></i>{escape(label(p))}</a>' for p in parties) + '</nav>'
    for index, p in enumerate(parties):
        rows = lambda name: [r for r in facts.get(name, []) if r.get('party_id') == p]
        tag = 'h1' if index == 0 else 'h2'
        answer_tag = 'h2' if index == 0 else 'h3'
        content += f'<section class="party-section" id="{p}" style="--party:{colour(p)}"><{tag}>{escape(label(p))}</{tag}><div class="party-intro"><div class="party-leaders">'
        credits = ''
        for i, leader in enumerate(rows('leaders')):
            photo = leader.get('photo')
            identity = f'photo-{p}-{i}'
            content += f'<figure class="party-portrait" aria-describedby="{identity}">'
            if photo:
                content += f'<img src="{PREFIX}{photo["path"].removeprefix("web/")}" alt="" width="100" height="100" loading="lazy">'
            content += '<figcaption>' + escape(leader['name']) + '<small>' + escape(leader['role']) + '</small></figcaption></figure>'
            credits += f'<div class="source-note party-credit" id="{identity}"><p class="source-actions">'
            if photo:
                attribution = ' '.join(link(url, text.rstrip('.') + '.') for url, text in (
                    (photo['source_url'], photo['author']),
                    (photo['licence_url'], photo['licence'])) if text)
                credits += attribution
            else:
                credits += link(leader['source_url'], 'Leader record')
            credits += '</p></div>'
        content += '</div>' + polling(p, averages) + '</div><div class="party-answers">'
        for row in rows('positions'):
            content += '<p class="party-position"><strong>Who could it govern with?</strong> ' + escape(row.get('context', row['quote'])) + ' ' + link(row['source_url'], row['speaker'] + ', ' + observation_label(row['date'])) + '.</p>'
        for row in rows('policy-links'):
            content += '<p class="party-policy">' + link(row['url'], 'Compare its policies by issue at Policy.nz') + '</p>'
        for row in rows('party-list-tops'):
            candidates = row.get('candidates', [])
            total = row.get('list_size')
            if not candidates and total is None:
                continue
            content += '<div class="party-candidates">'
            if total is not None:
                source = 'source-list-size-' + p
                content += f'<p aria-describedby="{source}"><strong>{total} list candidate{"s" if total != 1 else ""}</strong></p>'
            if candidates:
                heading = 'Top five list candidates' if len(candidates) == 5 else 'Top of the party list'
                content += f'<{answer_tag}>{heading}</{answer_tag}><ol>' + ''.join(f'<li value="{c["rank"]}">{escape(c["name"])}</li>' for c in candidates) + '</ol>'
            if total is not None:
                content += (f'<div class="source-note" id="{source}"><p>'
                            + escape(row['licence']) + ' Retrieved '
                            + f'<time datetime="{escape(row["retrieved_at"], quote=True)}">{observation_label(row["retrieved_at"])}</time>.'
                            + '</p><p class="source-actions">'
                            + link(row['list_size_source_url'], 'EC list candidate count') + ' '
                            + link(row['source_url'], 'EC party list') + '</p></div>')
            else:
                content += '<p>' + link(row['source_url'], 'EC party list') + '</p>'
            content += '</div>'
        donations = [r for r in rows('donations') if r['received'][:4] == built[:4]]
        if donations:
            total = sum((Decimal(r['amount_nzd']) for r in donations), Decimal(0))
            top = largest_donors(donations)
            content += f'<div class="party-donations" data-total="{total:.2f}" data-count="{len(donations)}"><{answer_tag}>Who funds it?</{answer_tag}><p class="funding-total"><span>{built[:4]} returns over NZD 20,000</span><small>NZD </small>{total:,.2f}</p><p class="funding-caveat">Not total party funding.</p><p>{len(donations)} declared returns.</p><ul>'
            content += ''.join('<li>' + escape(name) + f': NZD {donor["amount"]:,.2f}, received ' + ', '.join(observation_label(day) for day in sorted(donor['dates'])) + '.</li>' for name, donor in top)
            content += '</ul><p class="source-actions">' + f'<a href="{PREFIX}funding/#{p}">Every declared return for {escape(label(p))}</a>' + ' ' + link(donations[0]['source_url'], 'EC returns') + '</p><p class="party-credit">As listed by the EC, including returns whose documents have not been independently checked. Largest donors grouped by exact EC name. Return totals may combine donations; not total party funding. Copyright Electoral Commission.</p></div>'
        content += '</div>' + credits + '</section>'
    if any(env.get('run_url') == 'offline-verification' for env in envs.values()):
        content = content.replace('Poll inputs and method.</a>', 'Poll inputs and method.</a> <span>Offline verification, not live data.</span>')
    return content + '</div>'
