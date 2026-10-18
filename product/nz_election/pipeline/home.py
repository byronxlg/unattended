"""Feed presentation over validated, unchanged data families."""
from fractions import Fraction
from html import escape
from .build import (PREFIX, config, render, label, source_note, seat_module,
                    observation_label, compact_time, link)
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


def page(envs, built, presentation):
    from .market_panel import panel
    state, seats = seat_module(envs, built, presentation)
    markets = panel(envs, built)
    registry = envs.get('electorates', {}).get('data', config('electorates'))
    directory = '<ul class="home-directory" aria-describedby="source-directory">' + ''.join(
        f'<li><a href="{PREFIX}electorates/{r["slug"]}/"><span class="swatch" aria-hidden="true"></span>{escape(r["name"])}</a><p>{escape(electorate_summary(r, envs)[1])}</p></li>' for r in registry) + '</ul>'
    countdown = election_countdown(built)
    if countdown[0].isdigit():
        number, unit = countdown.split(' ', 1)
        countdown = f'<strong>{number}</strong><br>{unit}'
    return render('home', prefix=PREFIX, state=state, countdown=countdown,
                  updated=compact_time(built), sentence=escape(presentation['title']), seats=seats,
                  markets=markets, market_nav='<a href="#markets">Markets</a>' if markets else '', polls=poll_figures(envs, presentation), watch=watch(envs), directory=directory,
                  watch_source=family_note(envs, 'source-watch', ('electorates', 'baseline-2023', 'candidates')),
                  directory_source=family_note(envs, 'source-directory', ('electorates', 'baseline-2023')),
                  social=social(envs, built),
                  method_source=source_note(envs.get('polls'), 'source-method', 'polls.json' if 'polls' in envs else 'validation-2023.json'))
