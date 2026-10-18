"""Feed presentation over validated, unchanged data families."""
from decimal import Decimal
from fractions import Fraction
from html import escape
from .build import (PREFIX, config, render, label, source_note, seat_module,
                    observation_label, compact_time, link, derivation_note)
from .average import display
from .presentation import election_countdown, overdue


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
    return note(identity, ' '.join(dict.fromkeys(text)), ''.join(dict.fromkeys(actions)))


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
        figures += f'<p><span class="swatch" style="background:{colour}"></span>{escape(label(party))} <strong class="{"leading" if i < 2 else "remaining"}">{display(value["value"], value["scale"])}</strong></p>'
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
    return (f'<section id="{name}" class="home-module"><h2>{heading}</h2><p class="dek">{dek}</p>'
            f'<figure id="home-{name}" aria-describedby="source-{name}">{graphic}</figure>'
            f'<p><a href="{PREFIX}{route}">{action}</a></p>' + footnote(name, publisher, date) + '</section>')


def hero(envs, built, presentation):
    result = presentation['result']
    content = '<p>No seat estimate available yet.</p>'
    if result:
        groups = config('seat-groups')
        totals = [(key, sum(result['seats'].get(p, 0) for p in groups[key]['parties'])) for key in ('government', 'opposition')]
        content = '<div class="topline">' + ''.join(
            f'<p class="bloc-{groups[key]["token"]}">{key.title()} {n} seats</p>' for key, n in totals)
        content += f'<p>{result["assumed_majority"]} needed</p></div>'
        total = result['assumed_house']
        remainder = total - sum(n for _, n in totals)
        bars = [(groups[key]['token'], n) for key, n in totals]
        if remainder:
            bars.append(('neutral', remainder))
        content += '<div class="strip" role="img" aria-label="Seats ordered by government, opposition, then ungrouped">' + ''.join(
            f'<span class="segment bloc-fill-{token}" style="width:{Decimal(n) * 100 / total:.6f}%"></span>' for token, n in bars)
        content += f'<span class="majority" style="left:{Decimal(result["assumed_majority"]) * 100 / total:.6f}%"></span></div>'
        if remainder:
            content += f'<p class="bloc-neutral">{remainder} seats outside these groups or unassigned</p>'
    averages = envs.get('averages', {}).get('data', [])
    date = 'Average ' + observation_label(averages[-1]['date']) if averages else 'No published average'
    return ('<section id="seats" class="home-hero"><h1>Who is favoured to form the next government?</h1>'
            '<figure id="home-seats" aria-describedby="source-seats">' + content + '</figure>'
            '<div class="source-note home-footnote" id="source-seats"><p class="source-actions">' + date +
            f'. <a href="{PREFIX}methods/#home-seats">How it is made</a></p></div></section>')


def latest_polls(envs):
    from .build import table
    rows = sorted(envs.get('polls', {}).get('data', []), key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    if not rows:
        return '<p>' + unavailable(envs, 'polls') + '</p>'
    return table('Latest national polls; party vote percent', ['Pollster / fieldwork ended', 'National', 'Labour', 'Green'],
                 [[escape(p['pollster']) + '<br>' + observation_label(p['fieldwork_end']),
                   *[display(p['shares'].get(party), p['scale']) for party in ('nat', 'lab', 'grn')]] for p in rows], source='source-polls')


def trend_graphic(envs):
    from .build import table
    averages = envs.get('averages', {}).get('data', [])
    if not averages:
        return '<p>Not available: no published poll averages.</p>'
    # Weekly observations retain the last available day without duplicating it.
    selected = averages[-29::7]
    if averages[-1] not in selected:
        selected.append(averages[-1])
    parties = ('nat', 'lab', 'grn', 'act', 'nzf', 'tpm')
    return table('Weekly snapshots of the 30-day average, percent', ['As at'] + [label(p) for p in parties],
                 [[observation_label(a['date'])] + [display(a['descriptive'].get(p, {}).get('value'), a['descriptive'].get(p, {}).get('scale', 100)) for p in parties] for a in selected], source='source-trend')


def thresholds(envs):
    from .average import threshold_watch
    from .build import table
    if 'seats' not in envs:
        return '<p>Not available: no published threshold shares.</p>'
    rows = threshold_watch(envs['polls']['data'], envs['averages']['data'][-1], envs['seats']['data']['assumptions'])
    return table('Parties near the threshold', ['Party', 'Share', 'Below 5%'],
                 [[escape(label(r['party_id'])), display(r['value'], r['scale']), 'Electorate assumed' if r['electorate_qualifies'] else 'Needs 5%'] for r in rows], source='source-thresholds')


def market_graphic(envs):
    from .market_panel import leaders, label, yes
    from .presentation import market_price
    if 'markets' not in envs:
        return '<p>' + unavailable(envs, 'markets') + '</p>'
    rows = ''
    for event, row in leaders(envs['markets']['data']):
        if row:
            rows += f'<tr data-market-id="{row["id"]}"><th scope="row">{escape(label(row))}{" (closed)" if row["closed"] else ""}</th><td>{market_price(yes(row)["price"])}</td></tr>'
        else:
            rows += '<tr><th scope="row">' + escape(event['family']) + '</th><td>No priced contracts</td></tr>'
    return '<div class="scroll"><table aria-describedby="source-markets"><caption>Highest Yes price per event</caption><tbody>' + rows + '</tbody></table></div>'


def closest(envs):
    from .build import table
    if any(f not in envs for f in ('baseline-2023', 'candidates')):
        return '<p>' + ' '.join(unavailable(envs, f) for f in ('baseline-2023', 'candidates') if f not in envs) + '</p>'
    rows = watch_rows(envs)
    return '<div class="watch-rows">' + table('2023 winning margins on comparable boundaries', ['Electorate', 'Margin'],
                 [[f'<a href="{PREFIX}electorates/{r["slug"]}/">{escape(r["name"])}</a>', f'{margin:,} votes'] for margin, _, r, _ in rows], source='source-electorates') + '</div>'


def page(envs, built, presentation):
    state, _ = seat_module(envs, built, presentation)
    if envs.get('seats', {}).get('data', {}).get('unresolved_ties'):
        state += '<p>Allocation tie: seats remain unassigned; see the calculation.</p>'
    if any(env.get('run_url') == 'offline-verification' for env in envs.values()):
        state += '<p class="fixture-note">Offline verification: historical or synthetic data, not live data.</p>'
    date = updated(envs, 'polls', built)
    modules = module('polls', 'What are the latest polls?', 'Latest national observations; missing party shares are not zero.', latest_polls(envs), 'Wikipedia contributors', date, 'polls/#polls', 'See all polls')
    modules += module('trend', 'How have the polls moved?', 'Equal-weight 30-day averages describe polls, not a forecast; coverage differs by party.', trend_graphic(envs), 'Wikipedia contributors', date, 'polls/#source-average', 'See all averages')
    modules += module('electorates', 'Which electorates are closest?', 'The six smallest 2023 margins on unchanged boundaries, including East Cape; changed boundaries and tied winners are excluded.', closest(envs), 'Electoral Commission and boundary registry', updated(envs, 'baseline-2023', built), 'electorates/', 'See all electorates')
    modules += module('thresholds', 'Which parties are near the 5 percent threshold?', 'An electorate win can qualify a party below 5%; 2023 electorate seats are assumed.', thresholds(envs), 'Wikipedia contributors', date, 'polls/#source-thresholds', 'See all threshold assumptions')
    market_date = updated(envs, 'markets', built)
    market_dek = 'Market prices are not a forecast; government membership contracts are independent.'
    market_env = envs.get('markets')
    market_status = next((r for r in envs.get('status', {}).get('data', []) if r['dataset'] == 'markets'), {})
    if market_env and (market_status.get('state') == 'stale' or overdue(market_status.get('last_success_at'), built, 'daily')):
        market_dek += ' Update overdue or failed.'
    if market_env and overdue(min(r['observed_at'] for r in market_env['data']), built, 'daily'):
        market_dek += ' Observations are more than 36 hours old.'
    modules += module('markets', 'What do prediction markets say?', market_dek, market_graphic(envs), 'Polymarket', market_date, 'methods/#home-markets', 'See all market details')
    modules += module('night', 'When is election night?', 'New Zealand votes on 7 November 2026.', '<p class="countdown">' + escape(election_countdown(built)) + '</p>', 'Electoral Commission', 'Updated ' + compact_time(built), 'night/', 'See all election night information')
    return render('home', prefix=PREFIX, hero=hero(envs, built, presentation), state=state, modules=modules)


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
    marker = '<details><summary>Threshold watch and legend</summary>'
    seat_body, found, threshold_body = seats.partition(marker)
    if found:
        seat_body += '</div>'
        threshold_body = threshold_body.rsplit('</details>', 1)[0]
    else:
        threshold_body = '<p>Not available: no published threshold shares.</p>'
    selected = poll_inputs(presentation['selected'])
    all_polls = envs.get('polls', {}).get('data', [])
    trend_ids = {p for a in envs.get('averages', {}).get('data', []) for p in a['poll_ids']}
    trend_inputs = poll_inputs([p for p in all_polls if p['id'] in trend_ids])
    latest = sorted(all_polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:3]
    sections = [('seats', 'Seat calculation and grouping', seat_body + selected),
                ('polls', 'Latest poll inputs', poll_inputs(latest) + poll_figures(envs, presentation).replace('id="source-average"', 'id="source-home-average"').replace('aria-describedby="source-average"', 'aria-describedby="source-home-average"')),
                ('trend', 'Poll trend inputs', trend_inputs + polls_page(envs, built, presentation).replace(seats, '').replace(explorer(envs, not presentation['stale']) if 'polls' in envs else '', '')),
                ('electorates', 'Closest electorate inputs', watch(envs) + family_note(envs, 'source-watch', ('electorates', 'baseline-2023', 'candidates'))),
                ('thresholds', 'Threshold inputs', threshold_body + selected),
                ('markets', 'Market observations and terms', panel(envs, built) + family_note(envs, 'source-market-metadata', ('markets',))),
                ('night', 'Election date', note('source-election', 'Election date: Electoral Commission, 7 November 2026. Countdown updated ' + compact_time(built) + '.', link('https://vote.nz/', 'Electoral Commission') + f'<a href="{PREFIX}build-manifest.json">Build record</a>')),
                ('directory', 'Electorate directory inputs', family_note(envs, 'source-directory', ('electorates', 'baseline-2023'))),
                ('social', 'Social sample inputs', social(envs, built)),
                ('method', 'Calculation inputs', source_note(envs.get('polls'), 'source-method', 'polls.json' if 'polls' in envs else 'validation-2023.json'))]
    return ''.join(f'<section id="home-{name}" class="home-module"><h2>{heading}</h2>{body}</section>' for name, heading, body in sections)
