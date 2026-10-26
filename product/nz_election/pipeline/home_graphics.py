"""Home graphics at reference weight: inline SVG with real text, party colours as CSS tokens."""
from datetime import date, datetime
from decimal import Decimal
from fractions import Fraction
from html import escape
import math
from zoneinfo import ZoneInfo
from .build import PREFIX, config, label, table
from .average import display

PARTIES = ('nat', 'lab', 'grn', 'act', 'nzf', 'tpm', 'opp')
SHORT = {'nat': 'National', 'lab': 'Labour', 'grn': 'Green', 'act': 'ACT', 'nzf': 'NZ First', 'tpm': 'Te Pāti Māori', 'opp': 'TOP'}


def pc(party):
    """A party's display colour token; styles.css defines light and dark values."""
    return f'var(--p-{party})' if party in PARTIES else 'var(--p-other)'


def share(d):
    return Decimal(d['value']) / d['scale'] if d and d.get('value') is not None and d.get('scale') else None


def tint(value):
    # Cell tint grows with the share and stops where text would lose contrast.
    return min(62, int(Decimal(value) * 2))


def hidden(html):
    return '<div class="chart-data">' + html + '</div>'


def nz_today(built):
    return datetime.fromisoformat(built.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland')).date()


# Seats

def hemicycle_order(result):
    groups = config('seat-groups')
    opposition = [p for p in ('tpm', 'grn', 'lab') if p in groups['opposition']['parties']]
    government = [p for p in ('nzf', 'act', 'nat') if p in groups['government']['parties']]
    members = set(opposition) | set(government)
    neutral = sorted(p for p in result['seats'] if p not in members)
    return opposition, neutral, government


def hemicycle(result):
    """One dot per seat, left to right in angle order; the radial mark sits where the majority starts."""
    total = result['assumed_house']
    opposition, neutral, government = hemicycle_order(result)
    order = [p for p in opposition + neutral + government for _ in range(result['seats'].get(p, 0))]
    order += [None] * (total - len(order))
    rows = max(5, round(math.sqrt(total / 2.6)))
    outer, inner = Decimal(300), Decimal(300) * Decimal('0.42')
    radii = [inner + (outer - inner) * i / (rows - 1) for i in range(rows)]
    weight = sum(radii)
    counts = [int(total * r / weight) for r in radii]
    # Hand the remainder to the outer rows, which have the most room.
    for i in range(total - sum(counts)):
        counts[-1 - i % rows] += 1
    seats = []
    for r, n in zip(radii, counts):
        for k in range(n):
            angle = math.pi * (1 - k / (n - 1)) if n > 1 else math.pi / 2
            seats.append((angle, -float(r), float(r) * math.cos(angle), float(r) * math.sin(angle)))
    seats.sort(key=lambda s: (-s[0], s[1]))
    spacing = float(outer - inner) / (rows - 1)
    dot = min(spacing * 0.42, math.pi * float(inner) / max(counts[0] - 1, 1) * 0.42)
    marks = ''
    for party, (_, _, x, y) in zip(order, seats):
        fill = pc(party) if party else 'var(--rule)'
        marks += f'<circle cx="{320 + x:.1f}" cy="{316 - y:.1f}" r="{dot:.1f}" style="fill:{fill}"/>'
    majority = result['assumed_majority']
    government_seats = sum(result['seats'].get(p, 0) for p in government)
    # The line sits between the last seat a minority would hold and the first of a majority.
    split = total - majority
    a = (seats[split - 1][0] + seats[split][0]) / 2 if 0 < split < total else math.pi / 2
    x1, y1 = 320 + float(inner - 18) * math.cos(a), 316 - float(inner - 18) * math.sin(a)
    x2, y2 = 320 + float(outer + 14) * math.cos(a), 316 - float(outer + 14) * math.sin(a)
    marks += f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" class="majority-mark"/>'
    marks += f'<text x="320" y="300" class="hemi-need" text-anchor="middle">{majority}</text>'
    marks += '<text x="320" y="324" class="hemi-need-label" text-anchor="middle">for a majority</text>'
    title = (f'One dot per seat in a {total}-seat House. Government parties {government_seats}, '
             f'{majority} needed for a majority.')
    return (f'<svg class="hemicycle" viewBox="0 0 640 330" role="img" aria-label="{escape(title, quote=True)}" aria-describedby="source-seats">'
            + marks + '</svg>')


def seat_legend(result):
    opposition, neutral, government = hemicycle_order(result)
    def chips(parties):
        return ''.join(f'<li><i style="background:{pc(p)}"></i>{escape(SHORT.get(p, label(p)))} <b>{result["seats"][p]}</b></li>'
                       for p in parties if result['seats'].get(p))
    return (f'<div class="seat-legend"><ul>{chips(opposition)}</ul>'
            + (f'<ul class="neutral">{chips(neutral)}</ul>' if any(result['seats'].get(p) for p in neutral) else '')
            + f'<ul>{chips(list(reversed(government)))}</ul></div>')


# Poll trend

def trend(averages, polls, election, *, wide=True):
    """All parties on one plot to election day; dots are polls, lines the 30-day average."""
    W, H = (1000, 430) if wide else (360, 330)
    left, right, top, bottom = (40, 168, 16, 36) if wide else (28, 92, 12, 30)
    font = 15 if wide else 12
    start = date.fromisoformat(averages[0]['date'])
    end = max(election, date.fromisoformat(averages[-1]['date']))
    days = max(1, (end - start).days)
    plotted = [p for p in PARTIES if any(share(a['descriptive'].get(p)) is not None for a in averages)]
    top_value = max((share(a['descriptive'].get(p)) or 0 for a in averages for p in plotted), default=Decimal(40))
    ceiling = max(40, int(top_value / 10 + 1) * 10)
    pw, ph = W - left - right, H - top - bottom

    def x(day):
        return left + Decimal((day - start).days) * pw / days

    def y(value):
        return top + ph - Decimal(value) * ph / ceiling

    marks = ''
    for tick in range(0, ceiling + 1, 10):
        marks += f'<path d="M{left} {y(tick):.1f}H{W - right}" class="grid"/>'
        marks += f'<text x="{left - 8}" y="{y(tick) + font * Decimal("0.35"):.1f}" text-anchor="end" class="axis">{tick}{"%" if tick == ceiling else ""}</text>'
    marks += f'<path d="M{left} {y(5):.1f}H{W - right}" class="threshold"/>'
    marks += f'<text x="{left + 6}" y="{y(5) - 6:.1f}" class="axis">5% threshold</text>'
    month = date(start.year, start.month, 1)
    while month <= end:
        if month >= start:
            marks += f'<path d="M{x(month):.1f} {top + ph}v6" class="grid"/>'
            if wide or month.month % 2 == 0:
                marks += f'<text x="{x(month):.1f}" y="{H - 10}" text-anchor="middle" class="axis">{month:%b}</text>'
        month = date(month.year + month.month // 12, month.month % 12 + 1, 1)
    last_day = date.fromisoformat(averages[-1]['date'])
    if election > last_day:
        ex = x(election)
        marks += f'<rect x="{x(last_day):.1f}" y="{top}" width="{ex - x(last_day):.1f}" height="{ph}" class="future"/>'
        marks += f'<path d="M{ex:.1f} {top}V{top + ph}" class="election-day"/>'
        marks += f'<text x="{ex - 6:.1f}" y="{top + font}" text-anchor="end" class="axis strong">Election day</text>'
    # Polls first, then lines, so the averages read on top.
    for party in plotted:
        for poll in polls:
            day = date.fromisoformat(poll['fieldwork_end'])
            value = poll['shares'].get(party)
            if value is not None and start <= day <= last_day:
                marks += f'<circle cx="{x(day):.1f}" cy="{y(Decimal(value) / poll["scale"]):.1f}" r="{3.2 if wide else 2.4}" class="poll-dot" style="fill:{pc(party)}"/>'
    ends = []
    for party in plotted:
        path, active, last = '', False, None
        for a in averages:
            value = share(a['descriptive'].get(party))
            if value is None:
                active = False
                continue
            day = date.fromisoformat(a['date'])
            path += f'{"L" if active else "M"}{x(day):.1f} {y(value):.1f}'
            active, last = True, (day, value)
        big = last and last[1] >= 15
        marks += f'<path d="{path}" class="trend-line{" major" if big else ""}" style="stroke:{pc(party)}"/>'
        if last:
            marks += f'<circle cx="{x(last[0]):.1f}" cy="{y(last[1]):.1f}" r="{5 if wide else 4}" style="fill:{pc(party)}" class="end-dot"/>'
            ends.append([y(last[1]), party, last[1]])
    # End labels: stack downward from the top so none overlap.
    ends.sort()
    gap = Decimal(font + 5)
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + gap)
    overflow = ends[-1][0] - (top + ph) if ends else 0
    if overflow > 0:
        for item in ends:
            item[0] -= overflow
        for i in range(len(ends) - 2, -1, -1):
            ends[i][0] = min(ends[i][0], ends[i + 1][0] - gap)
    lx = W - right + (12 if wide else 8)
    for ly, party, value in ends:
        name = SHORT[party] if wide else {'tpm': 'TPM', 'nzf': 'NZF', 'nat': 'NAT', 'lab': 'LAB', 'grn': 'GRN'}.get(party, SHORT[party])
        marks += (f'<text x="{lx}" y="{ly + font * Decimal("0.35"):.1f}" class="end-label" style="fill:{pc(party)}">'
                  f'<tspan class="end-name">{escape(name)}</tspan> <tspan class="end-value">{display(int(value * 1000), 1000)}</tspan></text>')
    title = 'Party vote, 30-day poll average and individual polls, ' + f'{start:%-d %B} to {last_day:%-d %B %Y}'
    return (f'<svg class="trend {"wide" if wide else "narrow"}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title, quote=True)}" aria-describedby="source-trend" style="--font:{font}px">'
            + marks + '</svg>')


def trend_table(averages):
    selected = averages[-29::7]
    if averages[-1] not in selected:
        selected.append(averages[-1])
    parties = [p for p in PARTIES if any(share(a['descriptive'].get(p)) is not None for a in selected)]
    return hidden(table('Weekly snapshots of the 30-day average, percent', ['As at'] + [label(p) for p in parties],
                        [[a['date']] + [display(a['descriptive'][p]['value'], a['descriptive'][p]['scale']) if share(a['descriptive'].get(p)) is not None else '' for p in parties] for a in selected],
                        source='source-trend'))


# Latest polls table

def poll_table(polls, average, names, count=8, *, reports=False, caption='Latest national polls, party vote percent'):
    rows = sorted(polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:count]
    parties = [p for p in PARTIES if any(r['shares'].get(p) is not None for r in rows)]
    head = '<tr><th scope="col">Pollster</th><th scope="col" class="dates">Fieldwork</th>' + ''.join(
        f'<th scope="col" class="party" style="--c:{pc(p)}"><span>{escape(SHORT[p])}</span></th>' for p in parties) + ('<th scope="col" class="dates">Sample</th><th scope="col" class="dates">Report</th>' if reports else '') + '</tr>'
    body = ''
    avg = '<tr class="average"><th scope="row">Average</th><td class="dates">30 days</td>'
    for p in parties:
        v = share(average['descriptive'].get(p))
        avg += f'<td style="--c:{pc(p)};--a:{tint(v or 0)}%">{display(average["descriptive"][p]["value"], average["descriptive"][p]["scale"]) if v is not None else ""}</td>'
    body += avg + ('<td class="dates"></td><td class="dates"></td>' if reports else '') + '</tr>'
    for r in rows:
        start, end = date.fromisoformat(r['fieldwork_start']), date.fromisoformat(r['fieldwork_end'])
        span = f'{start:%-d}-{end:%-d %b}' if start.month == end.month else f'{start:%-d %b}-{end:%-d %b}'
        body += f'<tr><th scope="row">{escape(names.get(r["pollster"], r["pollster"]))}</th><td class="dates">{span}</td>'
        for p in parties:
            v = r['shares'].get(p)
            pct = Decimal(v) / r['scale'] if v is not None else None
            body += (f'<td style="--c:{pc(p)};--a:{tint(pct)}%">{display(v, r["scale"])}</td>' if pct is not None else '<td></td>')
        if reports:
            from .build import link
            body += (f'<td class="dates">{r["sample"]:,}</td>' if r.get('sample') else '<td class="dates"></td>')
            body += '<td class="dates">' + ' '.join(link(u, 'Report') for u in r['reference_urls'][:1]) + '</td>'
        body += '</tr>'
    return (f'<div class="poll-table" tabindex="0" role="region" aria-label="{escape(caption, quote=True)}">'
            f'<table aria-describedby="source-polls"><caption class="chart-data">{escape(caption)}</caption>'
            f'<thead>{head}</thead><tbody>{body}</tbody></table></div>')


# Party cards

def party_cards(averages, result, leaders, *, prefix=PREFIX):
    latest = averages[-1]['descriptive']
    month = averages[-31]['descriptive'] if len(averages) > 30 else None
    then = averages[-31]['date'] if len(averages) > 30 else None
    people = {r['party_id']: r for r in leaders if r.get('party_id')}
    ranked = sorted((p for p in PARTIES if share(latest.get(p)) is not None), key=lambda p: -share(latest[p]))
    cards = ''
    for p in ranked:
        value = share(latest[p])
        before = share(month.get(p)) if month else None
        change = ''
        if before is not None:
            delta = value - before
            word = 'up' if delta >= Decimal('0.05') else 'down' if delta <= Decimal('-0.05') else 'level'
            change = (f'<span class="change {word}">{"+" if delta > 0 else ""}{delta:.1f}</span>' if word != 'level'
                      else '<span class="change level">no change</span>')
        leader = people.get(p)
        photo = ''
        if leader and leader.get('photo'):
            photo = f'<img src="{prefix}{leader["photo"]["path"].removeprefix("web/")}" alt="" width="64" height="64" loading="lazy">'
        names = ' and '.join(r['name'] for r in leaders if r.get('party_id') == p)
        seats = result['seats'].get(p) if result else None
        cards += (f'<li class="party-card" style="--c:{pc(p)}"><a href="{prefix}parties/#{p}">'
                  f'<span class="card-head">{photo}<span><strong>{escape(SHORT[p])}</strong>'
                  + (f'<small>{escape(names)}</small>' if names else '') + '</span></span>'
                  f'<span class="card-figures"><span class="share">{display(latest[p]["value"], latest[p]["scale"])}</span>{change}</span>'
                  f'<span class="card-bar"><i style="width:{min(100, value * Decimal('2.5')):.1f}%"></i></span>'
                  + (f'<span class="card-seats">{seats} seat{"s" if seats != 1 else ""}</span>' if seats else '<span class="card-seats">No seats</span>' if result else '')
                  + '</a></li>')
    note = f'Change in points since {date.fromisoformat(then):%-d %B}.' if then else ''
    return f'<ul class="party-cards">{cards}</ul>' + (f'<p class="chart-note">{note} Photos: party and Wikimedia Commons, credited in Methods.</p>' if cards else '')


# Electorate map

def hex_map(envs, cells, rows, held_for):
    size = 17
    w = Decimal(size) * Decimal(3).sqrt()
    marks, records = '', []
    general = [c for c in cells if c['group'] != 'maori']
    maori = [c for c in cells if c['group'] == 'maori']
    gap = -1 if maori else 0
    cx_max = cy_max = Decimal(0)
    for c in cells:
        row = rows[c['electorate_slug']]
        held = held_for(row)
        shift = gap if c['group'] == 'maori' else 0
        cx = (c['x'] + shift) * w + (w / 2 if c['y'] % 2 else 0) + w / 2 + 4
        cy = Decimal(c['y']) * size * Decimal('1.5') + size + 4
        cx_max, cy_max = max(cx_max, cx), max(cy_max, cy)
        points = ' '.join(f'{cx + Decimal(size) * Decimal(str(round(math.cos(math.radians(60 * k - 30)), 4))):.1f},'
                          f'{cy + Decimal(size) * Decimal(str(round(math.sin(math.radians(60 * k - 30)), 4))):.1f}' for k in range(6))
        tone = 'low' if not held else 'close' if held['margin'] < 2000 else 'mid' if held['margin'] < 8000 else 'safe'
        fill = pc(held['party_id']) if held else 'var(--rule)'
        description = (f'{held["party"]} by {held["margin"]:,} votes in 2023' if held else 'no comparable 2023 result')
        title = escape(f'{row["name"]}: {description}')
        marks += (f'<a href="{PREFIX}electorates/{row["slug"]}/" aria-label="{title}"><title>{title}</title>'
                  f'<polygon points="{points}" class="hex {tone}" style="fill:{fill}"/></a>')
        records.append([escape(row['name']), escape(held['party']) if held else '', f'{held["margin"]:,}' if held else ''])
    width, height = cx_max + w / 2 + 6, cy_max + size + 6
    if maori:
        mx = (min(c['x'] for c in maori) + gap) * w + 4
        my = min(c['y'] for c in maori) * size * Decimal('1.5') - 14
        marks += f'<text x="{mx:.1f}" y="{my:.1f}" class="map-label">Māori</text><text x="{mx:.1f}" y="{my + 16:.1f}" class="map-label">electorates</text>'
    svg = (f'<svg class="hex-map" viewBox="0 0 {width:.0f} {height:.0f}" role="group" aria-describedby="source-electorates" '
           f'aria-label="Electorates coloured by 2023 winning party; darker means a larger margin">{marks}</svg>')
    return svg, hidden(table('2023 holders on original boundaries', ['Electorate', 'Party', 'Margin'], records, source='source-electorates'))


def map_key(parties):
    return ('<div class="map-key"><ul>' + ''.join(f'<li><i style="background:{pc(p)}"></i>{escape(SHORT[p])}</li>' for p in parties) + '</ul>'
            '<p class="tones"><span>Margin</span><i class="close"></i>under 2,000<i class="mid"></i>2,000 to 8,000<i class="safe"></i>over 8,000</p></div>')


def closest_list(rows, held_for):
    items = ''
    maximum = max((m for m, _, _, _ in rows), default=1)
    for margin, _, row, _ in rows:
        held = held_for(row) or {}
        p = held.get('party_id')
        items += (f'<li style="--c:{pc(p)}"><a href="{PREFIX}electorates/{row["slug"]}/"><span class="name">{escape(row["name"])}</span>'
                  f'<span class="holder">{escape(SHORT.get(p, held.get("party", "")))}</span>'
                  f'<span class="margin"><i style="width:{max(Decimal(2), Decimal(margin) * 100 / maximum):.1f}%"></i><b>{margin:,}</b></span></a></li>')
    return f'<ol class="closest">{items}</ol>'


# Thresholds

def threshold_bars(rows):
    scale_max = Decimal(10)
    body = ''
    for r in rows:
        v = share(r)
        status = ('Above 5%' if v >= 5 else 'Below 5%, but holds an electorate' if r['electorate_qualifies'] else 'Below 5%, no electorate')
        tone = 'in' if v >= 5 or r['electorate_qualifies'] else 'out'
        body += (f'<li style="--c:{pc(r["party_id"])}"><span class="name">{escape(SHORT.get(r["party_id"], label(r["party_id"])))}</span>'
                 f'<span class="bar"><i style="width:{min(Decimal(100), v * 100 / scale_max):.1f}%"></i></span>'
                 f'<b>{display(r["value"], r["scale"])}</b><small class="{tone}">{status}</small></li>')
    return f'<div class="thresholds"><span class="five" style="--at:50%">5%</span><ul>{body}</ul></div>'


# Markets

def market_cards(entries):
    cards = ''
    for question, price, closed in entries:
        pct = int((Decimal(price) * 100).to_integral_value())
        cards += (f'<li><span class="price">{pct}<small>%</small></span><span class="question">{escape(question)}{" (closed)" if closed else ""}</span>'
                  f'<span class="gauge"><i style="width:{pct}%"></i></span></li>')
    return f'<ul class="markets">{cards}</ul>'


# Key dates

def timeline(records, today):
    wanted = [('overseas-opens', 'Overseas voting opens'), ('enrolment-closes', 'Enrolment closes'), ('advance-opens', 'Advance voting opens'),
              ('advance-closes', 'Last day of advance voting'), ('election-day', 'Election day, polls close 7pm')]
    items = [(date.fromisoformat(records[k]['date']), text, k) for k, text in wanted if records.get(k, {}).get('date')]
    if not items:
        return ''
    out = ''
    for day, text, key in items:
        state = 'past' if day < today else 'today' if day == today else 'next'
        out += (f'<li class="{state}{" big" if key == "election-day" else ""}"><time datetime="{day}">{day:%a} {day.day} {day:%b}</time>'
                f'<span>{escape(text)}</span>' + ('<em>Today</em>' if state == 'today' else '') + '</li>')
    return f'<ol class="timeline">{out}</ol>'
