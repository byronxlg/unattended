"""Campaign observations appear only when backed by a dated national series."""
from datetime import date, timedelta
from html import escape
from .advance import ATTRIBUTION


def eligible(envs, historical=False):
    rows = envs.get('advance-voting', {}).get('data', [])
    return rows if historical else [r for r in rows if '2026-10-26' <= r['date'] <= '2026-11-06']


def window_note(envs, historical=False):
    rows = eligible(envs, historical)
    if rows and len(rows) != len(envs['advance-voting']['data']):
        return ('<p>Observations outside 26 October to 6 November 2026 are omitted from this view. '
                'Cumulative totals retain the full source series; downloads include all observations.</p>')
    return ''


def source(envs, historical=False):
    from .build import PREFIX, link
    rows = eligible(envs, historical)
    if not rows:
        return ''
    env = envs['advance-voting']
    links = ''.join(link(s['url'], 'Electoral Commission capture') for s in env['source'])
    links += f'<a href="{PREFIX}data/advance-voting.json">JSON and calculation inputs</a><a href="{PREFIX}data/advance-voting.csv">CSV</a>'
    if env['run_url'] != 'offline-verification':
        links += link(env['run_url'], 'Producing run')
    return (f'<div class="source-note" id="source-advance"><p>{ATTRIBUTION} '
            f'Observed through {rows[-1]["date"]}. Retrieved {escape(env["fetched_at"])}.</p>'
            f'<p class="source-actions">{links}</p>'
            '<p>National votes only. Daily inputs are summed only from the recorded start across consecutive dates. '
            'Cumulative inputs are differenced only across adjacent dates. Gaps are never zero. '
            'The JSON records the input column type and start date for each row. '
            'A revised capture replaces the series. Acquisition time is preserved.</p>' + window_note(envs, historical) + '</div>')


def page(envs, built=None, historical=False):
    from .build import render, table, PREFIX
    rows = eligible(envs, historical)
    if not rows:
        return render('campaign', module='')
    env = envs['advance-voting']
    historical_label = '<p class="notice">Offline verification: historical 2023 advance voting. Not live data.</p>' if historical else ''
    status = next((r for r in envs.get('status', {}).get('data', []) if r['dataset'] == 'advance'), {})
    retained = ('<p>Retained capture: latest observation ' + rows[-1]['date'] + '.</p>') if status.get('state') == 'stale' else ''
    first = date.fromisoformat(rows[0]['date'])
    span = max(1, (date.fromisoformat(rows[-1]['date']) - first).days)
    peak = max([r['cumulative'] or 0 for r in rows] + [1])
    marks, previous = [], None
    for row in rows:
        day, value = date.fromisoformat(row['date']), row['cumulative']
        if value is None:
            previous = None
            continue
        x, y = 10 + (day - first).days * 280 // span, 140 - value * 130 // peak
        if previous and day - previous[0] == timedelta(days=1):
            marks.append(f'<path d="M{previous[1]} {previous[2]} L{x} {y}" fill="none" stroke="currentColor" stroke-width="2"/>')
        marks.append(f'<circle cx="{x}" cy="{y}" r="3" fill="currentColor"/>')
        previous = day, x, y
    chart = ''
    if marks:
        chart = ('<figure aria-describedby="source-advance"><figcaption>Cumulative advance votes</figcaption>'
                 '<svg viewBox="0 0 300 150" role="img" aria-label="Cumulative advance votes; exact dates and counts in the table below" aria-describedby="source-advance" style="width:100%;max-height:300px">' + ''.join(marks) + '</svg>'
                 f'<p>{rows[0]["date"]} to {rows[-1]["date"]}; scale 0 to {peak:,} votes.</p></figure>')
    records = [[r['date'], *(f'{r[k]:,}' if r[k] is not None else 'Unknown across gap' for k in ('daily', 'cumulative'))] for r in rows]
    module = (f'<section id="advance" data-campaign-module="advance-voting">{historical_label}'
              '<h2>How many people have voted early?</h2><p>National daily votes and the running total. Days without a published count are left as gaps.</p>' + window_note(envs, historical) + retained + chart +
              table('Daily advance votes', ['Date', 'Daily', 'Cumulative'], records, source='source-advance') +
              f'<div class="source-note" id="source-advance"><p>{ATTRIBUTION} Observed through {rows[-1]["date"]}. '
              f'Retrieved {escape(env["fetched_at"])}.</p><p class="source-actions"><a href="{PREFIX}methods/#source-advance">Sources and method</a></p></div></section>')
    return render('campaign', module=module)
