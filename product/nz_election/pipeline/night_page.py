"""Static night snapshots enhanced by a local, initially paused replay."""
from datetime import datetime
from html import escape
from itertools import combinations
from .build import PREFIX, table, render, config
from . import home_graphics as g
from .presentation import election_countdown
from .result_states import sentence, comparison
from .result_sources import official_results_at, official_results_notice

RESULTS = 'https://www.electionresults.govt.nz/'
LAW = 'https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM310065.html'
FREEZE_NOTICE = 'No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197.'



def reader_update(clock):
    stamp = datetime.fromisoformat(clock)
    return f'{stamp.day} {stamp:%B %Y} at {stamp:%H:%M}'


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
            context.append('Final archive updated ' + reader_update(archive_updated) + '.')
    elif row.get('source_updated_local'):
        clock = row['source_updated_local']
        context.append('Results last updated ' + reader_update(clock) + '.')
    context_html = '<p class="night-frame-context">' + escape(' '.join(context)) + '</p>' if context else ''
    if row['mode'] == 'Packaged 2026 preliminary snapshot':
        context_html += '<p>This dated packaged snapshot is not a live connection. Electorates without a captured detail file have not yet reported here.</p>'
    reporting = ''
    stats = row.get('statistics')
    if stats:
        percent = stats['percent_voting_places_counted']
        clock = row.get('source_updated_local')
        updated = ', updated ' + clock[11:16] if clock else ''
        reporting = (f'<p class="night-reporting">Results cover <strong>{percent} percent</strong> of voting places{updated}.</p>'
                    f'<progress aria-label="Voting places reported" max="100" value="{percent}">{percent}%</progress>')
    combinations_html = ''
    content = context_html + reporting
    if row.get('reported_house'):
        house = row['reported_house']
        majority = house // 2 + 1
        seats = [(p, r['total_seats']) for p, r in parties if r['total_seats']]
        mapping = {'NAT': 'nat', 'LAB': 'lab', 'GP': 'grn', 'ACT': 'act', 'NZF': 'nzf', 'TPMAO': 'tpm', 'MAOR': 'tpm'}
        totals = {}
        for p, n in seats:
            key = mapping.get(refs['parties'][p]['abbrev'], 'other')
            totals[key] = totals.get(key, 0) + n
        result = dict(seats=totals, assumed_house=house, assumed_majority=majority)
        groups = config('seat-groups')
        bloc = {key: sum(totals.get(p, 0) for p in groups[key]['parties']) for key in ('government', 'opposition')}
        gov = bloc['government']
        answer = f'National, ACT and NZ First hold {gov} seats; {majority} are needed for a majority.'
        mode = row['mode']
        kicker = 'Live' if mode == 'Live preliminary results' else mode
        if mode == 'Final snapshot' and refs.get('id') in {'2017', '2020', '2023'}:
            kicker = 'Replay of ' + refs['id']
        content = (f'<section class="hero night-hero"><p class="kicker">{escape(kicker)}</p>'
                   '<h1>Who is winning?</h1>' + f'<p class="answer">{answer}</p>')
        content += reporting
        content += f'<figure aria-describedby="{source}">' + g.hemicycle(result).replace('source-seats', source)
        content += (f'<div class="blocs"><p class="bloc opposition"><span class="n">{bloc["opposition"]}</span><span class="who">Labour, Green<br>and Māori</span></p>'
                    f'<p class="bloc government"><span class="n">{gov}</span><span class="who">National, ACT<br>and NZ First</span></p></div>')
        content += g.seat_legend(result) + '</figure>'
        content += f'<p class="hero-dek night-house">House {house}; <strong>{majority} for a majority</strong>. Grouped by the 2023 coalition; government formation is separate.</p>'
        content += f'<p class="home-footnote"><a href="{PREFIX}data/{path}">Electoral Commission snapshot</a></p></section>'
        if 'leaders' in row:
            content += f'<p class="night-find"><a href="#night-search-{identity}">Find your electorate</a></p>'
        content += context_html
        winners = [group for size in range(1, len(seats)+1) for group in combinations(seats, size)
                   if sum(n for _, n in group) >= majority and all(sum(n for _, n in group)-n < majority for _, n in group)]
        cards = g.majority_cards(winners, names, {p: mapping.get(refs['parties'][p]['abbrev']) for p, _ in seats})
        from .home import section, footnote
        combinations_html = section('combinations-' + identity, 'Who has enough seats?',
                           'These combinations currently reach a majority; government formation is separate.',
                           cards, 'Electoral Commission', row.get('source_updated_local', 'Replay')).replace(
                               footnote('combinations-' + identity, 'Electoral Commission', row.get('source_updated_local', 'Replay')),
                               f'<div class="source-note" id="source-combinations-{identity}"><p>Electoral Commission.</p><p class="source-actions"><a href="{RESULTS}">Official results</a></p></div>')
    if not row.get('reported_house'):
        content = '<section class="hero night-hero"><p class="kicker">' + escape(row['mode']) + '</p><h1>Who is winning?</h1></section>' + content
    from .night_electorates import electorate_view, seat_chart, comparison_view
    content += electorate_view(row, refs, source, identity) + combinations_html
    content += f'<p class="night-votes"><strong>{row["valid_party_votes"]:,}</strong> valid party votes</p>'
    caption = 'Party results: ' + row['mode'] + ', ' + (row.get('source_updated_local') or str(row['elapsed_seconds']) + ' seconds')
    content += '<details><summary>Party votes and source-reported seats</summary>' + table(caption, ['Party', 'Valid party votes'] + (['Source-reported seats'] if 'reported_house' in row else []),
                     [[escape(names[p]), f'{r["votes"]:,}'] + ([str(r['total_seats'])] if 'reported_house' in row else []) for p, r in parties], source=source) + '</details>'
    content += seat_chart(row, source)
    if row.get('result_state') == 'official':
        content += comparison_view(comparison(row['preliminary_package']['data'][0], 'preliminary'), comparison(row, 'official'), source, names=names)
    else:
        content += comparison_view(row.get('preliminary_baseline'), row.get('official_result'), source)
    clock = row.get('source_updated_local')
    provenance = ('Results last updated ' + reader_update(clock) + '. Time shown as published by the Electoral Commission; no timezone was supplied.' if clock else
                  'Illustrative elapsed time ' + str(row['elapsed_seconds']) + ' seconds; scaled final party votes, not observed election-night counts.')
    if row.get('packaging_label'):
        provenance += ' Packaged by the site at ' + row['retrieved_at'] + '.'
    return (content + f'<div class="source-note" id="{source}"><p>Electoral Commission. {escape(provenance)} Copyright Electoral Commission; no open licence stated.</p><p>{FREEZE_NOTICE}</p>'
            f'<p class="source-actions"><a href="{PREFIX}data/{path}">{"Snapshot JSON (Packaged by the site)" if row.get("packaging_label") else "Snapshot JSON"}</a><a href="{PREFIX}data/{path[:-5]}.csv">{"CSV (Packaged by the site)" if row.get("packaging_label") else "CSV"}</a><a href="{RESULTS}">Official results</a><a href="{LAW}">Electoral Act s197</a></p></div>')


def live_status(built, retrieval):
    now = datetime.fromisoformat(built.replace('Z', '+00:00'))
    opening = datetime.fromisoformat('2026-11-07T06:00:00+00:00')
    if now < opening:
        return 'Results start at 19:00 NZDT on 7 November.'
    if not retrieval or datetime.fromisoformat(retrieval.replace('Z', '+00:00')) < opening:
        return 'Showing the dated packaged snapshot; check official results.'
    age = (now - datetime.fromisoformat(retrieval.replace('Z', '+00:00'))).total_seconds()
    if age >= 900:
        return f'Stale: last complete cycle retrieved {escape(retrieval)}. Check official results.'
    return f'Preliminary results. Packaged by the site at {escape(retrieval)}.'


def page(envs, built):
    from .night_live import CLOSE, stamp
    sequences = envs.get('night/index', {}).get('data', [])
    pre_close = datetime.fromisoformat(built.replace('Z', '+00:00')) < datetime.fromisoformat('2026-11-07T19:00:00+13:00')
    before = f'<section class="countdown"><div class="ribbon night-countdown"><p>{escape(election_countdown(built))}</p><p><a href="{PREFIX}vote/">How to vote</a></p></div></section>'
    from .snapshots import load_voting
    dates = ('<section class="night-timeline" aria-label="Voting dates">' + g.timeline({r['id']: r for r in load_voting()}, g.nz_today(built)) + '</section>') if pre_close else ''
    absent_source = (f'<div class="source-note" id="source-night"><p>{FREEZE_NOTICE}</p>'
                     f'<p class="source-actions"><a href="{LAW}">Electoral Act s197</a>'
                     f'<a href="{RESULTS}">Official Electoral Commission results</a></p></div>')
    if not sequences and not pre_close:
        return f'<section class="night-page"><h1>Who is winning?</h1>{absent_source}</section>'
    if not sequences:
        return '<h1>Who is winning?</h1>' + render('night', countdown=escape(election_countdown(built)), source=absent_source, timeline=dates)
    links = '<nav aria-label="Packaged results">' + ''.join(f'<a href="?sequence={s["id"]}">{escape("Latest 2026 results" if s["id"] == "live" else s["mode"])}{(' (' + escape(s["id"]) + ')') if s['id'] != 'live' else ''}</a>' for s in sequences) + '</nav>'
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
        panels.append(f'<section data-sequence="{seq["id"]}">' + ''.join(frames) + f'<p class="night-mode">{escape(seq["mode"])}{(' (' + escape(seq["id"]) + ')') if seq['id'] != 'live' else ''}</p></section>')
    # Keep replay explicit before close; prefer the complete live cycle after close.
    default = next((s for s in sequences if s['id'] == ('2023' if pre_close else 'live')),
                   next((s for s in sequences if s['id'] == '2026-media'), sequences[0]))
    selected = next(p for p in panels if f'data-sequence="{default["id"]}"' in p)
    retrieval = ''
    if default['id'] == 'live':
        retrieval = envs[default['snapshot_paths'][0][:-5]]['data'][0]['retrieved_at']
    current = envs.get('night/live/current', {}).get('data', [{}])[0] if default['id'] == 'live' else {}
    status = sentence(current, built) if current.get('result_state') else live_status(built, retrieval)
    if current.get('result_state') and envs['night/live/current'].get('run_url') == 'offline-verification':
        status += ' Offline verification: synthetic data.'
    result_notice = official_results_notice(built, [current])
    result_notice_at = official_results_at().isoformat()
    post_date_notice = official_results_notice(result_notice_at, [current])
    controls = ('<div id="night-controls" hidden><button type="button" id="night-play">Play</button> '
                '<button type="button" id="night-reset">Reset</button> <label for="night-speed">Speed</label> '
                '<select id="night-speed"><option value="1">1x</option><option value="10">10x</option><option value="60">60x</option></select>'
                '<span id="night-clock" aria-live="off">Paused</span>'
                '<span id="night-announcement" role="status" aria-live="polite" aria-atomic="true"></span></div>')
    return (f'<link rel="stylesheet" href="{PREFIX}night.css"><div class="night-page">' + (before if pre_close else '') + f'<p id="night-live-status" role="status">{status}</p>' + controls + f'<div id="night-snapshot" data-result-notice="{escape(result_notice, quote=True)}" data-result-notice-at="{result_notice_at}" data-post-date-notice="{escape(post_date_notice, quote=True)}" data-loop-ends-at="{stamp(lambda: CLOSE)}" data-retrieved-at="{escape(retrieval)}" data-mode="{escape(current.get("mode", ""))}">' + selected.replace('combinations-' + default['id'], 'combinations-static-' + default['id']).replace('night-row-' + default['id'], 'night-row-static-' + default['id']).replace('night-search-' + default['id'], 'night-search-static-' + default['id']).replace('source-' + default['id'], 'source-static-' + default['id']).replace('aria-label="', 'aria-label="Static ') + '</div>'
            + ('' if current.get('result_state') else f'<p id="night-result-status">2026: Preliminary; {result_notice[0].lower() + result_notice[1:]}</p>') + dates + links +
            ''.join(f'<template id="sequence-{s["id"]}">{p}</template>' for s, p in zip(sequences, panels)) +
            f'</div><script type="module" src="{PREFIX}night.mjs"></script><script type="module" src="{PREFIX}night-live.mjs"></script>')


def live_package(envs, *, now=None):
    """Render only validated local rows; source XML never supplies markup."""
    from datetime import datetime, timezone
    from product.nz_election.pipeline.night_live import CLOSE, stamp
    now = now or datetime.now(timezone.utc)
    built = stamp(lambda: now)
    stop = dict(loop_ends_at=stamp(lambda: CLOSE), loop_ended=now >= CLOSE)
    sequences = envs.get('night/index', {}).get('data', [])
    seq = next((s for s in sequences if s['id'] == 'live'), None)
    if seq is None:
        return dict(available=False, **stop)
    path = seq['snapshot_paths'][0]
    env = envs[path[:-5]]
    row = env['data'][0]
    refs = envs[seq['reference_path'][:-5]]['data'][0]
    from .home import night_summary
    return dict(available=True, home_html=night_summary(envs, built), **stop, retrieved_at=row['retrieved_at'], reference_version=row['reference_version'],
                mode=row['mode'], result_notice=official_results_notice(built, [row]), state_sentence=sentence(row, built) + (' Offline verification: synthetic data.' if env.get('run_url') == 'offline-verification' else ''), html=snapshot(row, refs, 'live-current', path),
                provenance=dict(label='Packaged by the site', sources=env['source'], code_sha=env['code_sha'],
                                run_url=env['run_url'], retrieved_at=row['retrieved_at']),
                json_path='data/' + path, csv_path='data/' + path[:-5] + '.csv')
