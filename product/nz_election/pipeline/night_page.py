"""Static night snapshots enhanced by a local, initially paused replay."""
from datetime import datetime
from decimal import Decimal
from html import escape
from itertools import combinations
from .build import PREFIX, table, render, config
from .presentation import election_countdown

RESULTS = 'https://www.electionresults.govt.nz/'
LAW = 'https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM310065.html'
FREEZE_NOTICE = 'No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197.'


def snapshot(row, refs, identity, path, frame=1, frame_count=1, archive_updated=None):
    source = 'source-' + identity
    parties = sorted(row['party_results'].items(), key=lambda p: (-p[1]['votes'], p[0]))
    names = {p: refs['parties'][p]['short_name'] for p, _ in parties}
    context = []
    if 'elapsed_seconds' in row:
        minutes, seconds = divmod(row['elapsed_seconds'], 60)
        context.append(f'Replay frame {frame} of {frame_count}, {minutes}:{seconds:02d} elapsed.')
        if 'statistics' not in row and 'reported_house' not in row:
            context.append('Scaled final party votes; voting-place coverage and seats are published only in the final archive.')
        elif 'statistics' not in row:
            context.append('Voting-place coverage is published only in the final archive.')
        elif 'reported_house' not in row:
            context.append('Seats are published only in the final archive.')
        elif archive_updated:
            context.append(f'Final archive updated {archive_updated[11:16]} on {archive_updated[:10]} (source local time; timezone unverified).')
    elif row.get('source_updated_local'):
        clock = row['source_updated_local']
        context.append(f'Source updated {clock[11:16]} on {clock[:10]} (source local time; timezone unverified).')
    content = '<p class="night-frame-context">' + escape(' '.join(context)) + '</p>' if context else ''
    if row['mode'] == 'Packaged 2026 preliminary snapshot':
        content += '<p>This dated packaged snapshot is not a live connection. Electorates without a captured detail file have not yet reported here.</p>'
    stats = row.get('statistics')
    if stats:
        percent = stats['percent_voting_places_counted']
        clock = row.get('source_updated_local')
        updated = ', updated ' + clock[11:16] if clock else ''
        content += (f'<p class="night-reporting">Results cover <strong>{percent} percent</strong> of voting places{updated}.</p>'
                    f'<progress aria-label="Voting places reported" max="100" value="{percent}">{percent}%</progress>')
    if 'reported_house' in row and row['reported_house']:
        house = row['reported_house']
        majority = house // 2 + 1
        seats = [(p, r['total_seats']) for p, r in parties if r['total_seats']]
        content += f'<h2>Who has enough seats?</h2><p class="night-house">House {house}; <strong>{majority} for a majority</strong></p>'
        content += f'<figure aria-describedby="{source}"><div class="strip" role="img" aria-label="Reported party seats; {majority} needed">'
        # Archive IDs belong to their reference set, never the current party registry.
        mapping = {'NAT': 'nat', 'LAB': 'lab', 'GP': 'grn', 'ACT': 'act', 'NZF': 'nzf', 'TPMAO': 'tpm', 'MAOR': 'tpm'}
        colours = config('party-colours')
        for p, n in seats:
            colour = colours.get(mapping.get(refs['parties'][p]['abbrev']), {}).get('colour', '#595959')
            content += f'<span class="segment" style="width:{Decimal(n)*100/house:.6f}%;background:{colour}" title="{escape(names[p])}: {n}"></span>'
        content += f'<span class="majority" style="left:{Decimal(majority)*100/house:.6f}%"></span></div><figcaption>'
        content += '; '.join(f'{escape(names[p])} {n}' for p, n in seats) + '</figcaption></figure>'
        winners = [group for size in range(1, len(seats)+1) for group in combinations(seats, size)
                   if sum(n for _, n in group) >= majority and all(sum(n for _, n in group)-n < majority for _, n in group)]
        content += '<p>These combinations currently reach a majority; government formation is separate.</p>'
        content += '<ul class="night-combinations">' + ''.join('<li>' + ' + '.join(escape(names[p]) for p, _ in g) + f': {sum(n for _, n in g)} seats</li>' for g in winners) + '</ul>'
    content += f'<p class="night-votes"><strong>{row["valid_party_votes"]:,}</strong> valid party votes</p>'
    caption = 'Party results: ' + row['mode'] + ', ' + (row.get('source_updated_local') or str(row['elapsed_seconds']) + ' seconds')
    content += '<details><summary>Party votes and source-reported seats</summary>' + table(caption, ['Party', 'Valid party votes'] + (['Source-reported seats'] if 'reported_house' in row else []),
                     [[escape(names[p]), f'{r["votes"]:,}'] + ([str(r['total_seats'])] if 'reported_house' in row else []) for p, r in parties], source=source) + '</details>'
    from .night_electorates import electorate_view, seat_chart, comparison_view
    content += electorate_view(row, refs, source, identity) + seat_chart(row, source)
    content += comparison_view(row.get('preliminary_baseline'), row.get('official_result'), source)
    clock = row.get('source_updated_local')
    provenance = ('Source local timestamp ' + clock + ' (timezone unverified).' if clock else
                  'Illustrative elapsed time ' + str(row['elapsed_seconds']) + ' seconds; scaled final party votes, not observed election-night counts.')
    return (content + f'<div class="source-note" id="{source}"><p>Electoral Commission. {escape(provenance)} Copyright Electoral Commission; no open licence stated.</p><p>{FREEZE_NOTICE}</p>'
            f'<p class="source-actions"><a href="{PREFIX}data/{path}">Snapshot JSON</a><a href="{PREFIX}data/{path[:-5]}.csv">CSV</a><a href="{RESULTS}">Official results</a><a href="{LAW}">Electoral Act s197</a></p></div>')


def page(envs, built):
    sequences = envs.get('night/index', {}).get('data', [])
    pre_close = datetime.fromisoformat(built.replace('Z', '+00:00')) < datetime.fromisoformat('2026-11-07T19:00:00+13:00')
    before = f'<p class="countdown">{escape(election_countdown(built))}</p><p><a href="{PREFIX}vote/">How to vote</a></p>'
    absent_source = (f'<div class="source-note" id="source-night"><p>{FREEZE_NOTICE}</p>'
                     f'<p class="source-actions"><a href="{LAW}">Electoral Act s197</a>'
                     f'<a href="{RESULTS}">Official Electoral Commission results</a></p></div>')
    if not sequences and not pre_close:
        return f'<section class="night-page">{absent_source}</section>'
    if not sequences:
        return render('night', countdown=escape(election_countdown(built)), source=absent_source)
    links = '<nav aria-label="Packaged results">' + ''.join(f'<a href="?sequence={s["id"]}">{escape(s["mode"])} ({escape(s["id"])})</a>' for s in sequences) + '</nav>'
    panels = []
    for seq in sequences:
        refs = envs[seq['reference_path'][:-5]]['data'][0]
        rows = [envs[p[:-5]]['data'][0] for p in seq['snapshot_paths']]
        frames = []
        for i, (row, path) in enumerate(zip(rows, seq['snapshot_paths'])):
            elapsed = row.get('elapsed_seconds', 0)
            if len(rows) > 1 and 'elapsed_seconds' not in row:
                elapsed = (datetime.fromisoformat(row['source_updated_local']) - datetime.fromisoformat(rows[0]['source_updated_local'])).total_seconds()
            identity = seq['id'] + '-' + str(i)
            basis = row.get('derivation', {}).get('basis', '')
            archive = envs.get(basis.removesuffix('.json'), {}).get('data', [])
            archive_updated = archive[0].get('source_updated_local') if archive else None
            frames.append(f'<div data-frame="{i}" data-elapsed="{elapsed}">' + snapshot(row, refs, identity, path, i + 1, len(rows), archive_updated) + '</div>')
        panels.append(f'<section data-sequence="{seq["id"]}"><p class="night-mode">{escape(seq["mode"])} ({escape(seq["id"])})</p>' + ''.join(frames) + '</section>')
    # Default is the dated final snapshot. All other states stay in inert templates.
    default = next((s for s in sequences if s['id'] == '2023'), sequences[0])
    selected = next(p for p in panels if f'data-sequence="{default["id"]}"' in p)
    controls = ('<div id="night-controls" hidden><button type="button" id="night-play">Play</button> '
                '<button type="button" id="night-reset">Reset</button> <label for="night-speed">Speed</label> '
                '<select id="night-speed"><option value="1">1x</option><option value="10">10x</option><option value="60">60x</option></select>'
                '<span id="night-clock" aria-live="off">Paused</span>'
                '<span id="night-announcement" role="status" aria-live="polite" aria-atomic="true"></span></div>')
    return (f'<link rel="stylesheet" href="{PREFIX}night.css"><div class="night-page">' + (before if pre_close else '') + controls + '<div id="night-snapshot">' + selected.replace('night-row-' + default['id'], 'night-row-static-' + default['id']).replace('night-search-' + default['id'], 'night-search-static-' + default['id']).replace('source-' + default['id'], 'source-static-' + default['id']).replace('aria-label="', 'aria-label="Static ') + '</div>'
            '<p>2026: Preliminary; official results due 27 November.</p>' + links +
            ''.join(f'<template id="sequence-{s["id"]}">{p}</template>' for s, p in zip(sequences, panels)) +
            f'</div><script type="module" src="{PREFIX}night.mjs"></script>')
