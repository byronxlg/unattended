"""Responsive SVG marks with HTML labels that retain their reading size."""
from datetime import date
from decimal import Decimal
from html import escape
from .build import config, label
from .average import display


def svg(name, title, marks, height):
    return (f'<svg class="home-chart" viewBox="0 0 350 {height}" preserveAspectRatio="none" style="height:{height}px" role="img" '
            f'aria-label="{escape(title, quote=True)}" aria-describedby="source-{name}">'
            + marks + '</svg>')


def fallback(html):
    # Hidden data must not introduce an invisible keyboard stop.
    table = html[html.index('<table'):html.rindex('</table>')+8]
    return '<div class="chart-data">' + table + '</div>'


def colour(party):
    return config('party-colours').get(party, {}).get('colour', 'var(--grey)')


def text(value, css='', style=''):
    return f'<span class="chart-label {css}" style="{style}">{escape(str(value))}</span>'


def poll_chart(rows, parties, names):
    maximum = max([Decimal(40)] + [Decimal(p['shares'][party])/p['scale'] for p in rows for party in parties if p['shares'].get(party) is not None])
    maximum = int((maximum/10).to_integral_value(rounding='ROUND_CEILING'))*10
    legend = '<div class="poll-key">' + ''.join(text(
        f'{["Filled circle", "Open square", "Triangle"][i]}: {names.get(p["pollster"], p["pollster"])} / {p["fieldwork_end"]}' + (' (newest)' if i == 0 else '')) for i, p in enumerate(rows)) + '</div>'
    body = ''
    for party in parties:
        marks = '<path d="M8 24H342" stroke="var(--rule)" stroke-width="0.5"/>'
        for i, poll in reversed(list(enumerate(rows))):
            value = poll['shares'].get(party)
            if value is None:
                continue
            x = 8 + Decimal(value)*334/poll['scale']/maximum
            # Slight vertical separation keeps identical observations visible.
            y = [18, 26, 34][i]
            fill = colour(party)
            if i == 0:
                marks += f'<ellipse cx="{x:.1f}" cy="{y}" rx="5" ry="5" fill="{fill}"/>'
            elif i == 1:
                marks += f'<rect x="{x-4:.1f}" y="{y-4}" width="8" height="8" fill="var(--paper)" stroke="{fill}" stroke-width="2"/>'
            else:
                marks += f'<path d="M{x:.1f} {y-4}l4 8h-8Z" fill="{fill}"/>'
        body += '<div class="chart-row">' + text(label(party)) + svg('polls', label(party) + ' poll shares', marks, 48) + '</div>'
    ticks = '<div class="chart-axis">' + ''.join(text(f'{n}%', 'numeric', f'left:{Decimal(n)*100/maximum:.1f}%') for n in range(0, maximum+1, 10)) + '</div>'
    return legend + body + '<div class="chart-row"><span></span>' + ticks + '</div>'


def threshold_chart(rows):
    maximum = max([Decimal(10)] + [Decimal(r['value'])/r['scale'] for r in rows if r['value'] is not None])
    body = ''
    for r in rows:
        value = display(r['value'], r['scale'])
        status = 'At or above 5%' if r['value'] is not None and r['value'] >= 5*r['scale'] else 'Electorate assumed' if r['electorate_qualifies'] else 'Needs 5%'
        width = Decimal(r['value'] or 0)*350/r['scale']/maximum
        marks = f'<rect x="0" y="12" width="{width:.1f}" height="14" fill="{colour(r["party_id"])}"/><path d="M{1750/maximum:.1f} 0V40" stroke="var(--ink)" stroke-dasharray="4 3"/>'
        body += ('<div class="chart-row threshold-row"><div>' + text(label(r['party_id'])) + text(status, 'chart-status') + '</div>'
                 + svg('thresholds', label(r['party_id']) + ': ' + value + '; ' + status, marks, 40) + text(value, 'numeric') + '</div>')
    return text('Dashed line: 5%', 'chart-status') + body


def trend_chart(averages, parties):
    start = date.fromisoformat(averages[0]['date'])
    days = max(1, (date.fromisoformat(averages[-1]['date'])-start).days)
    values = [Decimal(a['descriptive'][p]['value'])/a['descriptive'][p]['scale'] for a in averages for p in parties if a['descriptive'].get(p, {}).get('value') is not None]
    maximum = max(40, int(max(values, default=40)/10+1)*10)
    def y(v):
        return Decimal(260)-v*240/maximum
    marks, axis = '', ''
    for tick in range(0, maximum+1, 10):
        axis += text(tick, 'numeric', f'top:{y(Decimal(tick))-8:.1f}px')
        marks += f'<path d="M0 {y(Decimal(tick)):.1f}H350" stroke="var(--rule)" stroke-width="0.5"/>'
    marks += f'<path d="M0 {y(Decimal(5)):.1f}H350" stroke="var(--grey)" stroke-dasharray="4 3"/>'
    ends = []
    for party in parties:
        path, active, last = '', False, None
        for a in averages:
            d = a['descriptive'].get(party, {})
            if d.get('value') is None:
                active = False
                continue
            value = Decimal(d['value'])/d['scale']
            x = Decimal((date.fromisoformat(a['date'])-start).days)*330/days
            py = y(value)
            path += f'{"L" if active else "M"}{x:.1f} {py:.1f}'
            active, last = True, (x, py, display(d['value'], d['scale']))
        marks += f'<path d="{path}" fill="none" stroke="{colour(party)}" stroke-width="2"/>'
        if last:
            ends.append((last[1], party, last))
    previous, labels = Decimal(-20), ''
    for py, party, (x, _, value) in sorted(ends):
        position = max(py, previous+22)
        previous = position
        marks += f'<path d="M{x:.1f} {py:.1f}L350 {position:.1f}" stroke="{colour(party)}" fill="none"/>'
        labels += text(label(party) + ' ' + value, '', f'top:{position-8:.1f}px')
    height = max(290, int(previous)+25)
    return (text('Party vote percent; dashed line: 5%', 'chart-status') + f'<div class="trend-layout" style="height:{height}px"><div class="trend-labels">' + axis + '</div>'
            + svg('trend', 'Party averages over time, percent; dashed line marks 5 percent', marks, height)
            + '<div class="trend-labels">' + labels + '</div></div><div class="chart-dates">'
            + text(averages[0]['date'], 'numeric') + text(averages[-1]['date'], 'numeric') + '</div>')
