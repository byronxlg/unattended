"""Small static SVGs with exact, accessible data alongside each graphic."""
from datetime import date
from decimal import Decimal
from html import escape
from .build import config, label
from .average import display


def svg(name, title, marks, height):
    return (f'<svg class="home-chart" viewBox="0 0 350 {height}" role="img" '
            f'aria-label="{escape(title, quote=True)}" aria-describedby="source-{name}">'
            + marks + '</svg>')


def fallback(html):
    # A hidden scroll region must not introduce an invisible keyboard stop.
    table = html[html.index('<table'):html.rindex('</table>')+8]
    return '<div class="chart-data">' + table + '</div>'


def colour(party):
    return config('party-colours').get(party, {}).get('colour', 'var(--grey)')


def poll_chart(rows, parties, names):
    marks = ''
    y = 18
    maximum = max([Decimal(50)] + [Decimal(p['shares'][party])/p['scale'] for p in rows for party in parties if p['shares'].get(party) is not None])
    for poll in rows:
        marks += f'<text x="0" y="{y}">{escape(names.get(poll["pollster"], poll["pollster"]))} / {poll["fieldwork_end"]}</text>'
        for party in parties:
            y += 23
            value = poll['shares'].get(party)
            marks += f'<text x="0" y="{y}">{escape(label(party))}</text>'
            if value is not None:
                share = Decimal(value) / poll['scale']
                x = 125 + share * 160 / maximum
                marks += f'<path d="M125 {y-4}H{x:.1f}" stroke="{colour(party)}" stroke-width="3"/><circle cx="{x:.1f}" cy="{y-4}" r="3" fill="{colour(party)}"/><text class="numeric" x="{x+8:.1f}" y="{y}">{display(value, poll['scale'])}</text>'
            else:
                marks += f'<text x="125" y="{y}">Not reported</text>'
        y += 36
    return svg('polls', 'Latest national polls, party vote percent', marks, y-15)


def trend_chart(averages, parties):
    start = date.fromisoformat(averages[0]['date'])
    days = max(1, (date.fromisoformat(averages[-1]['date'])-start).days)
    values = [Decimal(a['descriptive'][p]['value']) / a['descriptive'][p]['scale'] for a in averages for p in parties if a['descriptive'].get(p, {}).get('value') is not None]
    maximum = max(40, int(max(values, default=40)/10+1)*10)
    def y(v):
        return Decimal(260)-v*240/maximum
    marks = ''
    for tick in range(0, maximum+1, 10):
        marks += f'<text class="numeric" x="0" y="{y(Decimal(tick)):.1f}">{tick}</text><path d="M25 {y(Decimal(tick)):.1f}H230" stroke="var(--rule)" stroke-width="0.5"/>'
    marks += f'<path d="M25 {y(Decimal(5)):.1f}H230" stroke="var(--grey)" stroke-dasharray="4 3"/><text x="25" y="{y(Decimal(5))-5:.1f}">5%</text>'
    ends = []
    for party in parties:
        path, active, last = '', False, None
        for a in averages:
            d = a['descriptive'].get(party, {})
            if d.get('value') is None:
                active = False
                continue
            value = Decimal(d['value']) / d['scale']
            x = 25 + Decimal((date.fromisoformat(a['date'])-start).days)*205/days
            py = y(value)
            path += f'{"L" if active else "M"}{x:.1f} {py:.1f}'
            active, last = True, (x, py, display(d['value'], d['scale']).removesuffix('%'))
        marks += f'<path d="{path}" fill="none" stroke="{colour(party)}" stroke-width="2"/>'
        if last:
            ends.append((last[1], party, last))
    previous = Decimal(-20)
    for py, party, (x, _, value) in sorted(ends):
        position = max(py, previous+17)
        previous = position
        marks += f'<path d="M{x:.1f} {py:.1f}L239 {position:.1f}" stroke="{colour(party)}" fill="none"/><text x="242" y="{position+4:.1f}">{escape(label(party))} {value}</text>'
    bottom = max(300, int(previous)+25)
    marks += f'<text x="25" y="{bottom}">{averages[0]["date"]}</text><text x="230" y="{bottom}" text-anchor="end">{averages[-1]["date"]}</text>'
    return svg('trend', 'Party averages over time, percent; dashed line marks 5 percent', marks, bottom+15)
