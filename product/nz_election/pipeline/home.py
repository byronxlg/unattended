"""Feed presentation over validated, unchanged data families."""
from decimal import Decimal
from fractions import Fraction
from html import escape
from .build import (PREFIX, config, render, label, source_note, seat_module,
                    observation_label, compact_time, link, derivation_note)
from .average import display
from .parties_page import party_link
from .presentation import overdue
from .home_charts import svg, fallback, poll_chart, trend_chart, threshold_chart, text


def unavailable(envs, family):
    state = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == family), {})
    return 'Not available: ' + escape(state.get('message') or 'no published ' + family + ' data') + '.'


def note(identity, text, actions):
    return f'<div class="source-note" id="{identity}"><p>{text}</p><p class="source-actions">{actions}</p></div>'


def family_note(envs, identity, families):
    from .electorate_pages import publisher
    text, actions = [], []
    for family in families:
        env = envs.get(family)
        if not env and family == 'electorates':
            import json
            from .fixtures import ROOT
            entries = json.loads((ROOT / 'manifest.json').read_text())['entries']
            sources = [e for e in entries if e['path'] in {'stats-nz/general-2025.geojson', 'stats-nz/maori-2025.geojson', 'representation-commission/report-2025.pdf'}]
            text.append('Reviewed 2025 electorate registry and boundary correspondence; not live geography.')
            for src in sources:
                actions.append(link(src['url'], 'Representation Commission' if src['path'].endswith('.pdf') else 'Stats NZ'))
                text.append(escape(src['licence']) + '. Retrieved ' + compact_time(src['captured_at']) + '.')
            continue
        if not env:
            text.append(unavailable(envs, family))
            continue
        for src in env['source']:
            actions.append(link(src['url'], publisher(src)))
            text.append('From ' + escape(publisher(src)) + '. ' + escape(src['licence']) + '. Retrieved ' + compact_time(src['fetched_at']) + '.')
        actions.append(f'<a href="{PREFIX}data/{family}.json">{escape(family)} inputs</a>')
    actions.append(f'<a href="{PREFIX}downloads/">Sources and producing runs</a>')
    return note(identity, ' '.join(dict.fromkeys(text)), ' '.join(dict.fromkeys(actions)))


def electorate_summary(row, envs, correspondence=None):
    entries = correspondence if correspondence is not None else config('electorate-correspondence')['entries']
    entry = next((e for e in entries if e['new_id'] == row['stats_id']), None)
    if not entry or row['mapping_status'] == 'unresolved':
        return None, 'Comparison unresolved: no reviewed boundary correspondence.'
    eligible = entry['relationship'] == 'unchanged' or (entry['new_id'] == '008' and entry['relationship'] == 'renamed' and entry['old_ids'] == [9])
    if not eligible:
        return None, 'Boundary changed; 2023 holder not comparable.'
    if len(entry['old_ids']) != 1 or row['baseline_ids'] != entry['old_ids']:
        return None, 'Comparison unresolved: baseline identities do not match.'
    old = next((r for r in envs.get('baseline-2023', {}).get('data', []) if r['old_electorate_id'] == entry['old_ids'][0]), None)
    votes = sorted((old or {}).get('candidate_votes') or [], key=lambda v: -v['votes'])
    if len(votes) < 2:
        return None, 'Held-by information not available: missing 2023 candidate results.'
    margin = votes[0]['votes'] - votes[1]['votes']
    if margin == 0:
        return None, 'Held-by information not available: tied 2023 result.'
    return margin, f'Held by {votes[0]["party"]}, {margin:,} votes in 2023 on the original boundaries'


def watch_rows(envs, registry=None, correspondence=None):
    rows = registry if registry is not None else envs.get('electorates', {}).get('data', config('electorates'))
    ranked = [(margin, row['id'], row, text) for row in rows
              for margin, text in [electorate_summary(row, envs, correspondence)] if margin is not None]
    return sorted(ranked, key=lambda r: (r[0], r[1]))[:6]


def watch(envs):
    explanation = '<p>The six smallest 2023 winning margins on unchanged boundaries, including the East Cape rename. Changed boundaries, missing candidate results and tied winners are excluded.</p>'
    if any(f not in envs for f in ('baseline-2023', 'candidates')):
        return explanation + '<p>' + ' '.join(unavailable(envs, f) for f in ('baseline-2023', 'candidates') if f not in envs) + '</p>'
    selected = watch_rows(envs)
    content = '<div class="watch-rows">'
    for _, _, row, text in selected:
        candidates = sorted((c for c in envs['candidates']['data'] if c['electorate_id'] == row['id']), key=lambda c: (c['party_id'], c['name'], c['id']))
        names = '; '.join('<span class="swatch" aria-hidden="true"></span>' + escape(c['name'] + ' (' + c['party_id'] + ')') + ('; unresolved source conflict' if c['conflict_ids'] else '') for c in candidates)
        content += (f'<article><h3>{escape(row["name"])}</h3><p>{escape(text)}</p><p>{names or "Published candidates not available for this electorate."}</p>'
                    f'<a href="{PREFIX}electorates/{row["slug"]}/" aria-label="More about {escape(row["name"], quote=True)}">More</a></article>')
    content += '</div>'
    if len(selected) < 6:
        content += '<p>Fewer than six eligible baselines are available; no changed-boundary substitutes are shown.</p>'
    return explanation + content


def poll_figures(envs, presentation):
    averages = envs.get('averages', {}).get('data', [])
    if not averages:
        return '<p>' + unavailable(envs, 'polls') + '</p>' + note('source-average', 'No published average.', f'<a href="{PREFIX}methods/">Polling method</a>')
    average = averages[-1]
    ordered = sorted(average['descriptive'].items(), key=lambda item: (item[0] == 'others', -Fraction(item[1]['value'], item[1]['scale']) if item[1]['value'] is not None else 1, item[0]))
    figures = '<div class="poll-figures" aria-describedby="source-average">'
    for i, (party, value) in enumerate(ordered):
        colour = config('party-colours').get(party, {}).get('colour', 'var(--surface)')
        figures += f'<p><span class="swatch" style="background:{colour}"></span>{party_link(party)} <strong class="{"leading" if i < 2 else "remaining"}">{display(value["value"], value["scale"])}</strong></p>'
    figures += '</div>'
    selected = presentation['selected']
    if selected:
        first, last = min(p['fieldwork_start'] for p in selected), max(p['fieldwork_end'] for p in selected)
        figures += f'<p aria-describedby="source-average">Fieldwork {observation_label(first)} to {observation_label(last)}; {len({p["pollster"] for p in selected})} pollsters. Equal weight per poll; coverage differs by party. Missing observations are not zero.</p>'
    figures += derivation_note(average)
    figures += source_note(envs['averages'], 'source-average', 'averages.json', calculation='Available poll shares averaged with equal weight by this site.', contributing_polls=selected)
    return figures


def social(envs, built):
    from .social_page import primary_chart
    records = envs.get('social/daily', {}).get('data', [])
    if not records:
        return '<p class="state">Proof of concept. Not available: no published sample.</p>' + note('source-social', unavailable(envs, 'social'), f'<a href="{PREFIX}social/poc/">Social method and availability</a>')
    intro, chart, _ = primary_chart(envs)
    retrieved = max(w['retrieved_at'] for r in records for w in r['provenance']['windows'])
    dated = '<p class="state">Update overdue. Showing the last published sample with its original dates.</p>' if overdue(retrieved, built, 'daily') else ''
    return ('<p class="state">Proof of concept</p>' + dated + intro + chart).replace('href="#social-method"', f'href="{PREFIX}social/poc/#social-method"')


def footnote(name, publisher, updated):
    return (f'<div class="source-note home-footnote" id="source-{name}">'
            f'<p class="source-actions">{publisher}. {updated} '
            f'<a href="{PREFIX}methods/#home-{name}">Sources and method</a></p></div>')


def updated(envs, family, built):
    env = envs.get(family)
    return 'Updated ' + compact_time(env['fetched_at']) if env else 'Checked ' + compact_time(built)


def module(name, heading, dek, graphic, publisher, date, route, action):
    if not graphic:
        return f'<span id="{name}"></span>'
    return (f'<section id="{name}" class="home-module"><h2>{heading}</h2><p class="dek">{dek}</p>'
            f'<figure id="home-{name}" aria-describedby="source-{name}">{graphic}</figure>'
            f'<p><a href="{PREFIX}{route}">{action}</a></p>' + footnote(name, publisher, date) + '</section>')


def voting_dates(built, rows=None):
    from datetime import datetime, date
    from zoneinfo import ZoneInfo
    from .snapshots import load_voting
    records = {r['id']: r for r in (load_voting() if rows is None else rows)}
    today = datetime.fromisoformat(built.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland')).date()
    clauses = []
    for key, caption in [('enrolment-closes', 'Enrol by'), ('advance-opens', 'advance voting from'), ('election-day', 'election day')]:
        row = records.get(key, {})
        if not row.get('date'):
            continue
        day = date.fromisoformat(row['date'])
        if key == 'enrolment-closes' and today > day:
            caption = 'Enrolment closed on'
        clauses.append(f'{caption} {day.day} {day:%B}')
    if not clauses:
        return ''
    source = records.get('election-day', next(iter(records.values())))['source_url']
    return ('<section id="dates" class="home-dates"><p>' + '; '.join(clauses) + '.</p><p>'
            + f'<a href="{PREFIX}vote/">How to vote</a>' + ' ' + link(source, 'EC key dates') + '</p></section>')


def night_summary(envs, built):
    from datetime import datetime
    if datetime.fromisoformat(built.replace('Z', '+00:00')) < datetime.fromisoformat('2026-11-07T19:00:00+13:00'):
        return ''
    # Consume only published 2026 observations through the validated family.
    observations = []
    for seq in envs.get('night/index', {}).get('data', []):
        refs = envs.get(seq['reference_path'][:-5], {}).get('data', [])
        for path in seq['snapshot_paths']:
            for row in envs.get(path[:-5], {}).get('data', []):
                if (row.get('source_updated_local', '').startswith('2026-')
                        and 'reported_house' in row and row.get('statistics')
                        and row.get('mode') not in {'Recorded demo', 'Illustrative replay based on 2023 final results'} and refs):
                    observations.append((row['source_updated_local'], row, refs[0]))
    if not observations:
        return ''
    clock, row, refs = max(observations, key=lambda item: item[0])
    seats = '; '.join(escape(refs['parties'][p]['short_name']) + ' ' + str(r['total_seats'])
                      for p, r in sorted(row['party_results'].items(), key=lambda item: -item[1]['total_seats']) if r['total_seats'] or row['reported_house'] == 0)
    if row['reported_house'] == 0:
        seats = '0 national seats reported.'
    return ('<section id="night-summary" class="home-hero"><h1>Who is winning now?</h1>'
            '<figure id="home-night" aria-describedby="source-night"><p class="seat-answer">' + seats + '</p>'
            f'<p>{row["statistics"]["percent_voting_places_counted"]}% of voting places reported. House: {row["reported_house"]} seats.</p>'
            '<p>' + escape(row['mode']) + '. Updated ' + escape(clock.replace('T', ' ')) + ' (source local time).</p></figure>'
            + footnote('night', 'Electoral Commission', updated(envs, 'night/index', built))
            + f'<p><a href="{PREFIX}night/">Election night results</a></p></section>')


def hero(envs, built, presentation):
    from .home_charts import colour
    result = presentation['result']
    if not result:
        return ''
    groups = config('seat-groups')
    totals = [(key, sum(result['seats'].get(p, 0) for p in groups[key]['parties'])) for key in ('government', 'opposition')]
    difference = totals[0][1] - result['assumed_majority']
    answer = ('exactly enough seats to govern' if difference == 0 else
              f'{difference} more than the {result["assumed_majority"]} needed' if difference > 0 else f'{-difference} short of the {result["assumed_majority"]} needed')
    content = f'<p class="seat-answer">Governing parties: {totals[0][1]} seats, {answer}.</p>'
    content += '<p class="seat-dek">Poll average using 2023 groups, not who forms government.</p>'
    content += '<div class="topline">' + ''.join(
        f'<p aria-label="{key.title()} {n} seats" class="bloc-{groups[key]["token"]}">{key.title()} <strong>{n}</strong></p>' for key, n in totals) + '</div>'
    total = result['assumed_house']
    remainder = total - sum(n for _, n in totals)
    content += f'<div class="majority-label" style="left:{Decimal(result["assumed_majority"])*100/total:.6f}%">{result["assumed_majority"]} needed</div>'
    content += '<div class="strip" role="img" aria-label="One block per seat; government from left, opposition from right">'
    ungrouped = [p for p in result['seats'] if all(p not in groups[k]['parties'] for k in ('government', 'opposition'))]
    for key, n, order in [('government', totals[0][1], 0), ('opposition', totals[1][1], 2), ('neutral', remainder, 1)]:
        if not n:
            continue
        token = groups[key]['token'] if key in groups else 'neutral'
        parties = groups[key]['parties'] if key in groups else ungrouped
        if key == 'opposition':
            parties = list(reversed(parties))
        content += f'<span class="segment bloc-fill-{token}" style="width:{Decimal(n)*100/total:.6f}%;order:{order}">'
        for party in parties:
            content += ''.join(f'<span class="seat" style="background:{colour(party)}" title="{escape(label(party))}"></span>' for _ in range(result['seats'].get(party, 0)))
        if key == 'neutral':
            content += '<span class="seat"></span>' * (total-sum(result['seats'].values()))
        content += '</span>'
    content += f'<span class="majority" style="left:{Decimal(result["assumed_majority"])*100/total:.6f}%"></span></div>'
    content += (f'<p class="seat-dek" aria-label="{result["assumed_majority"]} seats are needed in the assumed '
                f'{total}-seat House, including {result["overhang"]} overhang seats.">{total} seats, including {result["overhang"]} overhang.</p>')
    if remainder:
        content += f'<p class="bloc-neutral">{remainder} seats outside these groups or unassigned</p>'
    averages = envs.get('averages', {}).get('data', [])
    stamp = 'Average ' + observation_label(averages[-1]['date']) if averages else ''
    return ('<section id="seats" class="home-hero"><h1 class="chart-data">Who is favoured to form the next government?</h1>'
            '<figure id="home-seats" aria-describedby="source-seats">' + content + '</figure>'
            + footnote('seats', stamp, '') + '</section>')


def party_order():
    return [p['id'] for p in config('party-map')['parties'] if not p['aggregate']]


def latest_polls(envs):
    from .build import table
    rows = sorted(envs.get('polls', {}).get('data', []), key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    if not rows:
        return '<p>' + unavailable(envs, 'polls') + '</p>'
    wins = envs.get('seats', {}).get('data', {}).get('assumptions', {}).get('electorate_wins', {})
    parties = [party for party in party_order() if wins.get(party, 0) > 0 or any(
        p['shares'].get(party) is not None and p['shares'][party] >= 5 * p['scale'] for p in rows)]
    names = {identity: name for name, identity in config('party-map')['pollsters'].items()}
    return poll_chart(rows, parties, names) + fallback(table('Latest national polls; party vote percent', ['Pollster / fieldwork ended'] + [label(p) for p in parties],
                 [[escape(names.get(p['pollster'], p['pollster'])) + '<br>' + observation_label(p['fieldwork_end']),
                   *[display(p['shares'][party], p['scale']) if p['shares'].get(party) is not None else '' for party in parties]] for p in rows], source='source-polls'))


def trend_graphic(envs):
    from .build import table
    averages = envs.get('averages', {}).get('data', [])
    if not averages:
        return '<p>Not available: no published poll averages.</p>'
    # Weekly observations retain the last available day without duplicating it.
    selected = averages[-29::7]
    if averages[-1] not in selected:
        selected.append(averages[-1])
    parties = party_order()
    wins = envs.get('seats', {}).get('data', {}).get('assumptions', {}).get('electorate_wins', {})
    plotted = [p for p in parties if wins.get(p, 0) or any(a['descriptive'].get(p, {}).get('value') is not None and a['descriptive'][p]['value'] >= 5*a['descriptive'][p]['scale'] for a in selected)]
    large = [p for p in plotted if any(a['descriptive'].get(p, {}).get('value') is not None and a['descriptive'][p]['value'] >= 15*a['descriptive'][p]['scale'] for a in selected)]
    small = [p for p in plotted if p not in large]
    charts = f'<p><a href="{PREFIX}methods/#home-thresholds">5% or an electorate win qualifies for list seats</a></p>' + ''.join(trend_chart(selected, group, maximum=maximum, polls=envs.get('polls', {}).get('data', []), previous=averages[-2] if len(averages) > 1 else None) for group, maximum in [(large, None), (small, 15)] if group)
    return charts + fallback(table('Weekly snapshots of the 30-day average, percent', ['As at'] + [label(p) for p in parties],
                 [[observation_label(a['date'])] + [display(a['descriptive'][p]['value'], a['descriptive'][p]['scale']) if a['descriptive'].get(p, {}).get('value') is not None else '' for p in parties] for a in selected], source='source-trend'))


def thresholds(envs):
    from .average import threshold_watch
    from .build import table
    if 'seats' not in envs:
        return '<p>Not available: no published threshold shares.</p>'
    rows = threshold_watch(envs['polls']['data'], envs['averages']['data'][-1], envs['seats']['data']['assumptions'])
    rows = [r for r in rows if r['value'] is not None]
    if not rows:
        return ''
    return threshold_chart(rows) + fallback(table('Parties near the threshold', ['Party', 'Share', 'Qualification'],
                 [[escape(label(r['party_id'])), display(r['value'], r['scale']), 'At or above 5%' if r['value'] is not None and r['scale'] and r['value'] >= 5 * r['scale'] else 'Electorate assumed' if r['electorate_qualifies'] else 'Needs 5%'] for r in rows], source='source-thresholds'))


def market_graphic(envs):
    from .market_panel import leaders, question, yes
    from .presentation import market_price
    if 'markets' not in envs:
        return '<p>' + unavailable(envs, 'markets') + '</p>'
    rows = ''
    summary = '<ul class="market-summary" aria-label="Leading market choices: price for Yes">'
    for event, row in leaders(envs['markets']['data']):
        if row:
            width = Decimal(yes(row)['price'])*350
            price = market_price(yes(row)['price'])
            graphic = svg('markets', 'Yes price: ' + price,
                f'<path d="M0 5H350" stroke="var(--rule)"/><path d="M0 5H{width:.1f}" stroke="var(--grey)" stroke-width="6"/>', 12)
            summary += (f'<li>{escape(question(row))}{" (closed)" if row["closed"] else ""} '
                        f'<strong class="numeric">{price}</strong>{graphic}</li>')
            rows += f'<tr data-market-id="{row["id"]}"><th scope="row">{escape(question(row))}{" (closed)" if row["closed"] else ""}</th><td>{market_price(yes(row)["price"])}</td></tr>'
        else:
            summary += '<li>' + escape(event['family']) + ': No priced contracts</li>'
            rows += '<tr><th scope="row">' + escape(event['family']) + '</th><td>No priced contracts</td></tr>'
    return summary + '</ul>' + fallback('<div class="scroll"><table aria-describedby="source-markets"><caption>Leading market choices: price for Yes</caption><tbody>' + rows + '</tbody></table></div>')


def closest(envs):
    from .build import table
    from .snapshot_views import result as held_result
    from .home_charts import colour
    if 'baseline-2023' not in envs:
        return ''
    rows = watch_rows(envs)
    maximum = max((m for m, _, _, _ in rows), default=1)
    content = '<div class="watch-rows">'
    for margin, _, r, _ in rows:
        width = Decimal(margin)*130/maximum
        marks = f'<rect x="0" y="9" width="{width:.1f}" height="12" fill="{colour((held_result(r, envs) or {}).get('party_id'))}"/>'
        content += (f'<div class="margin-row"><a href="{PREFIX}electorates/{r["slug"]}/">{escape(r["name"])}</a>'
                    + '<div style="position:relative;padding-right:48px">'
                    + svg('electorates', f'{r["name"]}: {margin:,} votes', marks, 30).replace('0 0 350', '0 0 130')
                    + text(f'{margin:,}', 'numeric', f'position:absolute;top:5px;left:calc((100% - 48px)*{Decimal(margin)/maximum:.6f} + 4px)') + '</div></div>')
    return content + '</div>' + fallback(table('2023 winning margins on comparable boundaries', ['Electorate', 'Margin'],
                 [[escape(r['name']), f'{margin:,} votes'] for margin, _, r, _ in rows], source='source-electorates'))



def directory_links(envs):
    if all(f in envs for f in ('baseline-2023', 'candidates')) and watch_rows(envs):
        return ''
    return (f'<ul class="home-directory"><li><a href="{PREFIX}electorates/">'
            'Browse all electorates</a></li></ul>')


def poll_change(envs):
    averages = envs.get('averages', {}).get('data', [])
    if len(averages) < 2:
        return 'Equal-weight 30-day averages, not a forecast.'
    latest, previous = averages[-1], averages[-2]
    ranked = sorted(((p, d) for p, d in latest['descriptive'].items() if p != 'others' and d.get('value') is not None), key=lambda item: -Fraction(item[1]['value'], item[1]['scale']))
    changes = []
    for party, value in ranked[:2]:
        old = previous['descriptive'].get(party, {})
        if old.get('value') is not None:
            delta = Decimal(value['value'])/value['scale'] - Decimal(old['value'])/old['scale']
            changes.append(label(party) + (f' {delta:+.1f} pp' if delta else ' unchanged'))
    return ('; '.join(changes) + ' since ' + observation_label(previous['date']) + '. ' if changes else '') + 'Poll averages, not a forecast.'


def page(envs, built, presentation):
    from .snapshot_views import map_graphic, footnote as snapshot_note
    state, _ = seat_module(envs, built, presentation)
    if 'polls' not in envs:
        state = ''
    if envs.get('seats', {}).get('data', {}).get('unresolved_ties'):
        state += '<p>Allocation tie: seats remain unassigned; see the calculation.</p>'
    if any(env.get('run_url') == 'offline-verification' for env in envs.values()):
        state += '<p class="fixture-note">Offline verification: historical or synthetic data, not live data.</p>'
    modules = ''
    if envs.get('averages', {}).get('data') or envs.get('polls', {}).get('data'):
        graphic = ''
        if envs.get('averages', {}).get('data'):
            graphic += '<div id="trend">' + trend_graphic(envs) + footnote('trend', 'Wikipedia contributors', updated(envs, 'polls', built)) + '</div>'
        if envs.get('polls', {}).get('data'):
            graphic += '<div id="latest-polls"><h3>Dated latest polls</h3>' + latest_polls(envs) + '</div>'
        modules += module('polls', 'What changed in the latest polls?', poll_change(envs), graphic, 'Wikipedia contributors', updated(envs, 'polls', built), 'polls/', 'See all polls and averages')
    graphic = '<div class="home-picker"><div>' + map_graphic(envs, hexagons=True) + snapshot_note('map') + '</div><div><h3>Find your electorate</h3>'
    if watch_rows(envs):
        graphic += '<p>Closest 2023 margins on unchanged boundaries</p>' + closest(envs)
    graphic += f'<ul class="home-directory"><li><a href="{PREFIX}electorates/">Browse all electorates and candidates</a></li></ul></div></div>'
    modules += module('electorates', 'Who is standing where I live?', 'Choose an electorate for its candidates. Map colours show 2023 holders, not 2026 predictions.', graphic, 'Electoral Commission and boundary registry', updated(envs, 'baseline-2023', built), 'electorates/', 'See all electorates')
    top = night_summary(envs, built) or hero(envs, built, presentation)
    if not top:
        top = '<h1>New Zealand votes on 7 November</h1>'
    return render('home', dates=voting_dates(built), hero=top, state=state, modules=modules)


def poll_inputs(polls):
    return '<ul>' + ''.join(
        '<li data-poll-id="' + escape(p['id'], quote=True) + '">' + escape(p['pollster']) + ': ' +
        escape(p['fieldwork_start'] + ' to ' + p['fieldwork_end']) + '; revision ' + escape(str(p['revision'])) +
        '. ' + ' '.join(link(url, 'Original report') for url in p['reference_urls']) + '</li>' for p in polls) + '</ul>'


def sources(envs, built, presentation):
    """Keep the full previous home provenance together, behind each figure's link."""
    from .market_panel import panel
    from .build import polls_page, explorer
    _, seats = seat_module(envs, built, presentation)
    marker = '<div><p><strong>Threshold watch and legend</strong></p>'
    seat_body, found, threshold_body = seats.partition(marker)
    if found:
        seat_body += '</div>'
        threshold_body = threshold_body.rsplit('</div>', 2)[0]
    else:
        threshold_body = '<p>Not available: no published threshold shares.</p>'
    selected = poll_inputs(presentation['selected'])
    all_polls = envs.get('polls', {}).get('data', [])
    trend_ids = {p for a in envs.get('averages', {}).get('data', []) for p in a['poll_ids']}
    trend_inputs = poll_inputs([p for p in all_polls if p['id'] in trend_ids])
    latest = sorted(all_polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    sections = [('seats', 'Seat calculation and grouping', seat_body + selected),
                ('polls', 'Latest poll inputs', poll_inputs(latest) + poll_figures(envs, presentation).replace('id="source-average"', 'id="source-home-average"').replace('aria-describedby="source-average"', 'aria-describedby="source-home-average"')),
                ('trend', 'Poll trend inputs', trend_inputs + polls_page(envs, built, presentation, full_sources=True).replace(seats, '').replace(explorer(envs, not presentation['stale']) if 'polls' in envs else '', '')),
                ('electorates', 'Closest electorate inputs', watch(envs) + family_note(envs, 'source-watch', ('electorates', 'baseline-2023', 'candidates'))),
                ('thresholds', 'Threshold inputs', threshold_body + selected),
                ('markets', 'Market observations and terms', panel(envs, built) + family_note(envs, 'source-market-metadata', ('markets',))),
                ('night', 'Election night inputs', (family_note(envs, 'source-night-family', ('night/index',)) if 'night/index' in envs else '') + note('source-election', 'Election date: Electoral Commission, 7 November 2026. Countdown updated ' + compact_time(built) + '.', link('https://vote.nz/', 'Electoral Commission') + f'<a href="{PREFIX}build-manifest.json">Build record</a>')),
                ('directory', 'Electorate directory inputs', family_note(envs, 'source-directory', ('electorates', 'baseline-2023'))),
                ('social', 'Social sample inputs', social(envs, built)),
                ('method', 'Calculation inputs', source_note(envs.get('polls'), 'source-method', 'polls.json' if 'polls' in envs else 'validation-2023.json'))]
    return ''.join(f'<section id="home-{name}" class="home-module"><h2>{heading}</h2>{body}</section>' for name, heading, body in sections)
