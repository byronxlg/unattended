"""Static aggregate-only proof of concept with small-cell suppression."""
from datetime import datetime, time, timedelta
from decimal import Decimal
from html import escape
from .social import NZ, PARTIES, TOPICS, ATTITUDES, EXCLUSIONS

TITLE = 'Proof of concept: what X says about the parties'


def count(n):
    return 'under 5' if n < 5 else str(n)


def page(envs, built):
    from .build import config, table, compact_time, PREFIX
    records = envs.get('social/daily', {}).get('data', [])
    status = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == 'social'), {})
    latest = max((r['day'] for r in records), default=None)
    now = datetime.fromisoformat(built.replace('Z', '+00:00'))
    if not latest or now - datetime.combine(datetime.fromisoformat(latest).date() + timedelta(days=1), time(), NZ) > timedelta(hours=36):
        message = 'X proof of concept unavailable: no sample is available yet.' if not latest else 'X proof of concept unavailable: the last sampled day is more than 36 hours old.'
        return '<p class="state">' + message + '</p>'
    n = sum(r['sample']['eligible'] for r in records)
    start, end = (datetime.fromisoformat(d) for d in (min(r['day'] for r in records), latest))
    dates = f'{start.day} {start:%B %Y}' if start == end else f'{start.day} {start:%B %Y} to {end.day} {end:%B %Y}'
    intro = f'<p class="numeric">{count(n)} posts sampled from X over {len(records)} days, {dates}, one page per hour, not a complete count.</p>'
    if any(r['provenance']['fixture'] for r in records):
        intro += '<p class="state">Offline verification: synthetic examples, not live data.</p>'
    if status.get('error_code'):
        intro += '<p class="state">' + escape(status['message']) + '</p>'
    counts = {p: sum(r['party_counts'][p] for r in records) for p in PARTIES}
    colours = {v['label']: v['colour'] for v in config('party-colours').values()}
    colours['Green'] = config('party-colours')['grn']['colour']
    source = ('<div role="note" class="source-note" id="source-social"><p>From twitterapi.io, '
              f'X posts sampled {dates}. Retrieved {compact_time(max(w["retrieved_at"] for r in records for w in r["provenance"]["windows"]))}. '
              'Posts sampled and classified by this site; counts only. '
              'X terms apply; no CC licence asserted for X data. '
              'Wikipedia-derived data elsewhere on this site is CC BY-SA 4.0.</p>'
              '<p class="source-actions"><a href="https://twitterapi.io/">twitterapi.io</a>'
              f'<a href="{PREFIX}data/social/daily.json">Inputs</a><a href="#social-method">method</a>'
              f'<a href="{PREFIX}downloads/">data run</a></p></div>')
    bars, rows = [], []
    for i, p in enumerate(PARTIES):
        value = counts[p]
        share = f'{Decimal(value)*100/max(n, 1):.1f}%' if value >= 20 else 'Share withheld: fewer than 20 posts'
        width = Decimal(value)*160/max(n, 1) if value >= 5 else 0
        y = i * 25 + 2
        bars.append(f'<text x="0" y="{y+16}">{escape(p)}</text><rect x="125" y="{y}" width="{width}" height="18" fill="{colours.get(p, "var(--surface)" )}"/><text x="295" y="{y+16}">{count(value)}</text>')
        rows.append((escape(p), count(value), share))
    primary = ('<section><h2>Primary-party share of sampled posts</h2><figure aria-describedby="source-social">'
               '<svg class="social-chart" role="img" aria-label="Primary party counts" aria-describedby="source-social" viewBox="0 0 355 255">' + ''.join(bars) +
               '</svg><figcaption>Primary subjects in sampled X posts, not party support or all NZ posts. Search coverage and prolific authors affect the result.</figcaption></figure>' + source +
               '<details><summary>Party counts and shares</summary>' + table('Primary subjects', ('Party', 'Posts', 'Share'), rows, source='source-social') + '</details></section>')
    fills = ('var(--ink)', 'var(--grey)', 'var(--surface)', 'var(--rule)', 'var(--paper)')
    bars, rows = [], []
    for i, p in enumerate(PARTIES[:7]):
        values = [r['attitude'][p] for r in records]
        withheld = any(v['withheld'] for v in values)
        bars.append(f'<text x="0" y="{i*31+20}">{escape(p)}</text>')
        if withheld:
            bars.append(f'<text x="125" y="{i*31+20}">Withheld: daily sample below 30</text>')
            rows.append((escape(p), 'Withheld: fewer than 30 evaluable posts in a day', '', '', '', ''))
            continue
        totals = [sum(v['counts'][j] for v in values) for j in range(5)]
        # Small cells have no geometry from which to recover their exact values.
        if any(0 < v < 5 for v in totals):
            bars.append(f'<text x="125" y="{i*31+20}">Small cells: see table</text>')
        else:
            x = Decimal(125)
            for j, v in enumerate(totals):
                width = Decimal(v)*220/max(sum(totals), 1)
                bars.append(f'<rect x="{x}" y="{i*31+4}" width="{width}" height="20" fill="{fills[j]}"/>')
                x += width
        rows.append((escape(p), *(count(v) for v in totals)))
    attitude = ('<section><h2>Attitude toward each party</h2><figure aria-describedby="source-social-attitude"><svg class="social-chart" role="img" aria-label="Attitude distributions" aria-describedby="source-social-attitude" viewBox="0 0 355 220">' + ''.join(bars) +
                '</svg><figcaption>Left to right: strongly negative, negative, neutral, positive, strongly positive. Estimated tone among sampled X authors, not voters. Sarcasm, quotations and missing context can change classification.</figcaption></figure>' + source.replace('id="source-social"', 'id="source-social-attitude"') +
                '<details><summary>Attitude counts</summary>' + table('Ordered attitude classes', ('Party', *ATTITUDES), rows, source='source-social-attitude') + '</details></section>')
    topics = table('Topics in this sample', ('Topic', 'Posts'), [(escape(t), count(sum(r['topic_counts'][t] for r in records))) for t in TOPICS], source='source-social')
    concentration = max(r['sample']['top_author_share_ppm'] for r in records)
    models = ', '.join(sorted({m for r in records for m in r['model_versions']})) or 'No eligible classifications'
    exclusions = {k: sum(r['sample']['exclusions'][k] for r in records) for k in EXCLUSIONS}
    caption = (f'<section id="social-method"><h2>How this sample was made</h2><p>One latest page from each hourly window of the NZ day: a time-stratified, recency-biased convenience sample. '
               "The search matches each party's name and common short form as quoted phrases; the exact phrase list is recorded in each day's provenance. "
               f'{count(sum(r["sample"]["returned"] for r in records))} posts returned; {count(n)} eligible after deduplication and the relevance gate. '
               f'{count(sum(r["sample"]["unique_authors"] for r in records))} daily unique authors summed across days (authors may repeat between days). '
               f'The largest daily share from one author was {Decimal(concentration)/10000:.1f}%. '
               f'{count(sum(r["sample"]["capped_windows"] for r in records))} hourly windows hit the page limit.</p>'
               '<p>IDs and normalized repeated text are deduplicated in memory. Original posts, replies and quote commentary may enter the sample. '
               'Only English text of at most 8,000 characters is classified in this pilot; language coverage is incomplete. '
               f'Excluded: duplicates {count(exclusions["duplicate"])}, unsupported language or length {count(exclusions["unsupported"])}, relevance below 0.8 {count(exclusions["irrelevant"])}, invalid classification {count(exclusions["classification"])}. '
               'Attitudes require evaluability of at least 0.8 and one named primary party; other, multiple and unclear subjects have no attitude row. '
               'Each post counts once; author influence is not equalised. Official accounts are not separated in this pilot. No voter affiliation is inferred.</p>'
               f'<p>Jev System One: {escape(models)}. Question text version nz-politics-poc-1. Classification is unvalidated on NZ text. '
               'Counts under 5 are shown as under 5; party percentages below 20 posts are withheld. Attitude rows require at least 30 evaluable posts per party per day. '
               'The distribution uses the most likely ordered class, not a rounded expected score. Aggregate probability sums remain in the inputs; individual answers and posts are discarded.</p>'
               '<p>X terms apply; no CC licence is asserted for X data. This sample does not measure platform totals, voter support or a representative population. '
               'The pilot has no bot detector. Collection has a 7,800-credit daily cap. Publication freezes on 7 November 2026 until 19:00 NZDT.</p></section>')
    return intro + '<div class="social-grid">' + primary + attitude + '</div><h2>Topics</h2>' + topics + caption
