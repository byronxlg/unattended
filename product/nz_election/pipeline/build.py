# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Render 81 offline pages, validating everything before replacing product output."""
import argparse
from datetime import datetime
from decimal import Decimal
from html import escape
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, coalitions
from product.nz_election.pipeline.scripts import validate_scripts
from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.average import display, threshold_watch, derive_others
from product.nz_election.pipeline.fixtures import golden, GOLDEN_PATHS
from product.nz_election.pipeline.refresh import PRODUCT, config, source_entries, code_sha, utc_now
from product.nz_election.pipeline.storage import replace_directory
from product.nz_election.pipeline.presentation import overdue

PREFIX = '/unattended/nz-election/'
TEMPLATES = PRODUCT / 'web/templates'


def safe_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or any(ord(c) < 32 for c in value):
        return None
    return escape(value, quote=True)


def link(url, label):
    safe = safe_url(url)
    return f'<a href="{safe}">{escape(str(label))}</a>' if safe else escape(str(label))


def render(name, **values):
    template = (TEMPLATES / (name + '.html')).read_text()
    def replacement(match):
        if match[1] not in values:
            raise ValueError('MISSING_TEMPLATE_VALUE: ' + match[1])
        return str(values[match[1]])
    return re.sub(r'\{\{([a-z_]+)\}\}', replacement, template)


def local_time(value):
    export.timestamp(value, 'local_time')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland'))
    return f"{dt.hour % 12 or 12}:{dt.minute:02d} {'am' if dt.hour < 12 else 'pm'}, {dt:%A} {dt.day} {dt:%B %Y %Z}"


def compact_time(value):
    export.timestamp(value, 'source.retrieved')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland'))
    return f'{dt.day} {dt:%b}, {dt:%H:%M %Z}'


def observation_label(value):
    # Poll observation dates have no time zone; operational observations have timestamps.
    return local_time(value) if value and 'T' in value else (datetime.fromisoformat(value).strftime('%d %b %Y').lstrip('0') if value else 'Not available')


def table(caption, headings, records, css='', source=None):
    description = f' aria-describedby="{source}"' if source else ''
    return (f'<div class="scroll {css}" tabindex="0" role="region" aria-label="{escape(caption)}">'
            f'<table{description}><caption>{escape(caption)}</caption><thead><tr>' +
            ''.join(f'<th scope="col">{escape(h)}</th>' for h in headings) + '</tr></thead><tbody>' +
            ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>' for row in records) + '</tbody></table></div>')


def source_note(env=None, identity='source-polls', inputs='polls.json', *,
                calculation='Polls parsed by this site.', contributing_polls=None):
    if inputs == 'validation-2023.json':
        captured = max(s['fetched_at'] for s in (env['source'] if env else source_entries()[1]))
        return (f'<div role="note" class="source-note" id="{identity}"><p>From '
                'Electoral Commission. '
                f'Final results <time datetime="2023-11-03">3 Nov 2023</time>. Retrieved <time datetime="{captured}">{compact_time(captured)}</time>. Copyright Electoral Commission; no open licence stated. '
                f'</p><p class="source-actions"><a href="https://electionresults.govt.nz/electionresults_2023/">Electoral Commission</a><a href="{PREFIX}downloads/">Downloads</a></p><div><p><strong>Calculation and producing run</strong></p>'
                '<p>Calculation verified against captured final results.</p>'
                f'<p class="source-actions"><a href="{PREFIX}validation-2023.json">Official validation inputs</a>'
                f'<a href="{PREFIX}build-manifest.json">Build and run record</a></p></div></div>')
    sources = env['source'] if env else source_entries()[0]
    p = next(s for s in sources if s['id'] == 'P')
    run = env['run_url'] if env else None
    producing = link(run, 'Data run') if run and safe_url(run) else f'<a href="{PREFIX}downloads/">Data run</a>' if run else 'No poll data run yet.'
    dates = ''
    if env:
        rows = contributing_polls if contributing_polls is not None else env['data'] if isinstance(env['data'], list) else []
        ends = [r['fieldwork_end'] for r in rows if r.get('fieldwork_end')]
        if ends:
            end = max(ends)
            dates += f' Fieldwork ended <time datetime="{end}">{observation_label(end)}</time>.'
        fetched = env['fetched_at']
        dates += f' Retrieved <time datetime="{fetched}">{compact_time(fetched)}</time>.'
    result = render('source-note', id=identity, revision=safe_url(p['url']) or '#',
                  inputs=PREFIX + (inputs if inputs == 'validation-2023.json' else 'data/' + inputs), prefix=PREFIX,
                  dates=dates, run=producing, calculation=escape(calculation))
    return result



def derivation_note(average):
    ids = set(average.get('poll_ids', []))
    derived = {d['poll_id'] for d in average.get('derivations', [])} & ids
    if not derived:
        return ''
    return (f'<p class="poll-dates">Others derived as 100 minus the named parties for {len(derived)} of {len(ids)} polls; '
            f'<a href="{PREFIX}methods/#derived-polls">see sources</a>.</p>')


def label(p):
    return config('party-colours').get(p, {}).get('label', 'Others' if p == 'others' else p)


def party_link(p):
    from product.nz_election.pipeline.parties_page import party_link as anchor
    return anchor(p)


def label_positions(anchors, width):
    # Reserve 60 px for an abbreviation and a three-digit count at 14 px.
    result, cursor = {}, 0
    columns = len(anchors) if width >= 600 else max(1, (len(anchors) + 1) // 2)
    for index, (party, anchor) in enumerate(anchors):
        row = index // columns
        if index % columns == 0:
            cursor = 0
        start = float(anchor) * width / 100
        remaining = min(columns - index % columns, len(anchors) - index)
        left = min(max(cursor, start if row == 0 else 0), width - remaining * 68 + 8)
        result[party] = (row, left * 100 / width, start * 100 / width)
        cursor = left + 68
    return result


def label_lanes(anchors, width):
    return {party: position[0] for party, position in label_positions(anchors, width).items()}


def default_scenario(envs):
    try:
        data = coalitions.inputs(envs['averages']['data'][-1], envs['seats']['data'], '0' * 64)
        return coalitions.scenario(data, data['initial'])
    except (KeyError, ValueError, IndexError):
        return None


def home_presentation(envs, built):
    """One availability decision and the exact poll provenance for page and card."""
    polls = envs.get('polls')
    average = envs.get('averages', {}).get('data', [])
    selected = [p for p in polls['data'] if average and p['id'] in average[-1]['poll_ids']] if polls else []
    status = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == 'polls'), None)
    stale = not status or status['state'] != 'fresh' or overdue(status['last_attempt_at'], built, 'hourly')
    result = default_scenario(envs) if selected and not stale and envs.get('seats', {}).get('data', {}).get('available') else None
    if result and not result.get('seats'):
        result = None
    provenance = dict(polls, data=selected) if result else polls
    return dict(result=result, selected=selected, stale=stale,
                title=home_sentence(result), source=source_note(provenance, 'source-seats',
                    'seats.json' if result else 'polls.json' if polls else 'validation-2023.json',
                    calculation='Seats calculated by this site.' if result else 'Seats withheld; see the headline.') +
                    (derivation_note(average[-1]) if result else ''))


def home_sentence(result):
    if not result or not result.get('seats'):
        return 'New Zealand votes on 7 November 2026.'
    ordered = sorted(result['seats'].items(), key=lambda item: (-item[1], item[0]))
    maximum = ordered[0][1]
    leaders = [label(p) for p, n in ordered if n == maximum]
    majority = result['assumed_majority']
    if len(leaders) > 1:
        names = ' and '.join(leaders) if len(leaders) == 2 else ', '.join(leaders[:-1]) + ' and ' + leaders[-1]
        return f'{names} are level on {maximum} calculated seats; no party reaches the assumed majority of {majority}.'
    if maximum >= majority:
        return f'{leaders[0]}: {maximum} calculated seats, reaching the assumed majority of {majority}.'
    return f'{leaders[0]} leads with {maximum} calculated seats; no party reaches the assumed majority of {majority}.'


def seat_topline(result):
    if not result or not result.get('seats'):
        return ('<div class="topline" aria-describedby="source-seats"><p>'
                'Seat totals are withheld until a complete, up-to-date poll average is available.</p></div>')
    groups = config('seat-groups')
    def sentence(group):
        row = groups[group]
        total = sum(result['seats'].get(party, 0) for party in row['parties'])
        return f'<p class="bloc-{row["token"]}">{escape(row["label"])}: {total} seats</p>'
    return ('<div class="topline" aria-describedby="source-seats source-grouping">' +
            sentence('government') + '<p>on the current poll average, ' +
            str(result['assumed_majority']) + ' needed</p>' + sentence('opposition') +
            '</div><div class="source-note" id="source-grouping"><p>' + escape(groups['caption']) +
            '</p><p class="source-actions">' + link(groups['source_url'], groups['source_label']) + '</p></div>')


def ungrouped_seats(result):
    groups = config('seat-groups')
    members = set(groups['government']['parties']) | set(groups['opposition']['parties'])
    rows = [f'{escape(label(party))}: {count} seats' for party, count in sorted(result['seats'].items()) if party not in members]
    return ('<p class="bloc-neutral" aria-describedby="source-seats">Outside these groups: ' +
            '; '.join(rows) + '.</p>') if rows else ''


def strip(seats, note=''):
    colours = config('party-colours')
    groups = config('seat-groups')
    order = groups['government']['parties'] + sorted(set(seats['seats']) - set(groups['government']['parties']) - set(groups['opposition']['parties'])) + groups['opposition']['parties']
    ordered = [(p, seats['seats'][p]) for p in order if seats['seats'].get(p)]
    total = seats['assumed_house']
    segments, labels, records = [], [], []
    anchors, offset = [], 0
    for p, n in ordered:
        anchors.append((p, Fraction(offset * 100, total)))
        offset += n
    mobile, desktop = label_positions(anchors, 328), label_positions(anchors, 1072)
    for p, n in ordered:
        base = min(n, seats['entitlements'][p])
        extra = n - base
        grouped = groups['government']['parties'] + groups['opposition']['parties']
        colour = colours.get(p, {}).get('colour', '#595959') if p in grouped else '#595959'
        width = Decimal(base) * 100 / total
        segments.append(f'<div class="segment" data-party="{p}" style="width:{width:.6f}%;background:{colour}"></div>')
        if extra:
            width = Decimal(extra) * 100 / total
            segments.append(f'<div class="segment overhang" data-overhang-party="{p}" style="width:{width:.6f}%;background:{colour}"></div>')
        row, left, anchor = mobile[p]
        _, large_left, _ = desktop[p]
        for mode, (line_row, line_left, line_anchor) in [('phone', mobile[p]), ('wide', desktop[p])]:
            if abs(line_left - line_anchor) > .01 or line_row:
                side = 'right' if line_anchor > line_left else 'left'
                labels.append(f'<span class="label-connector {mode}" aria-hidden="true" style="left:{min(line_left, line_anchor):.6f}%;width:{abs(line_left-line_anchor):.6f}%;height:{6+line_row*21}px;border-{side}:1px solid var(--ink)"></span>')
        labels.append(f'<div class="lane" role="group" data-party="{p}" style="--row:{row};--left:{left:.6f}%;--large-left:{large_left:.6f}%" aria-label="{escape(label(p))}: {n} calculated seats"><span>{p.upper()}</span> <strong>{n}</strong></div>')
        records.append([party_link(p), str(base), str(extra), str(n)])
    marker = Decimal(seats['assumed_majority']) * 100 / total
    return (note + '<figure class="seat-figure" aria-describedby="source-seats"><div class="strip" role="img" '
            'aria-describedby="source-seats" aria-label="Theoretical party seats, detailed in the following table">' + ''.join(segments) +
            f'<span class="majority" style="left:{marker:.6f}%"></span></div>'
            '<div class="lanes">' + ''.join(labels) + '</div>'
            f'<p class="majority-label">{seats["assumed_majority"]} for a majority</p>'
            '<figcaption class="strip-note">Calculated seats; list capacity not checked.</figcaption></figure>' +
            render('party-rows', majority=seats['assumed_majority'], total=total,
                   rows=table('Theoretical seats and overhang', ['Party', 'Base seats', 'Overhang', 'Seats'], records, source='source-seats')).rstrip())



def explorer(envs, available=True):
    note = 'The explorer requires JavaScript and complete matching poll inputs. Published seats remain above.'
    attrs, controls = '', ''
    try:
        if not available:
            raise ValueError('UPDATE_OVERDUE')
        average_hash = envs['seats']['input_hashes']['averages.json']
        seats_hash = next(e['sha256'] for e in envs['manifest']['data'] if e['path'] == 'seats.json')
        fingerprint = export.digest((average_hash + seats_hash).encode())
        data = coalitions.inputs(envs['averages']['data'][-1], envs['seats']['data'], fingerprint)
        attrs = f' data-averages="{average_hash}" data-seats="{seats_hash}" data-fingerprint="{fingerprint}"'
        for p in data['parties']:
            colour = config('party-colours').get(p, {}).get('colour', '#595959')
            controls += (f'<div class="coalition-row" data-party-row="{p}" data-name="{escape(label(p))}" data-colour="{colour}">'
                         f'<label><input type="checkbox" data-select="{p}"> {escape(label(p))}</label>'
                         f'<label class="electorate-count">Electorate seats assumed for {escape(label(p))}'
                         f'<input type="text" inputmode="numeric" maxlength="2" data-count="{p}" value="{data["initial"]["counts"][p]}"></label></div>')
    except (KeyError, ValueError):
        note = ('The explorer is unavailable because the poll inputs are incomplete. Published information remains above.' if available else
                'The explorer is unavailable while the poll update is overdue. Previous poll observations remain above.')
    return (f'<section id="coalition-explorer" aria-labelledby="coalition-title"{attrs}>'
            '<h2 id="coalition-title">Choose parties</h2>'
            f'<p data-note>{note}</p>' + derivation_note((envs.get('averages', {}).get('data') or [{}])[-1]) + '<fieldset hidden disabled><legend>Choose parties and electorate seats assumed</legend>'
            + controls + '<div class="coalition-actions"><button type="button" data-reset>Reset</button>'
            '<button type="button" data-share>Share this scenario</button></div></fieldset>'
            '<p data-warning role="status"></p><div data-results hidden><p data-live aria-describedby="source-seats" aria-live="polite" aria-atomic="true"></p>'
            '<p data-unassigned aria-describedby="source-seats"></p><p>List capacity not checked. Vacancies and the occupied House are unknown; '
            'the majority requirement is assumed.</p><div data-picture></div>'
            f'<p><a href="{PREFIX}data/averages.json">Poll inputs</a> <a href="{PREFIX}data/seats.json">Seat assumptions</a> '
            f'<a href="#source-seats">Sources and method</a></p></div></section>'
            f'<script type="module" src="{PREFIX}coalitions.mjs"></script>')


def seat_module(envs, built, presentation=None):
    presentation = presentation if presentation is not None else home_presentation(envs, built)
    if 'polls' not in envs:
        status = next((r for r in envs.get('status', {}).get('data', []) if r['dataset'] == 'polls'), None)
        failed = f' The {compact_time(status["last_attempt_at"])} update failed.' if status and status.get('error_code') else ''
        state = '<div class="state"><p>No data yet. Polls are checked hourly.' + failed + '</p><p class="source-actions"><a href="https://github.com/byronxlg/unattended/actions">Update details</a>.</p></div>'
        return state, render('seat-module', picture=seat_topline(None) + f'<p><a href="{PREFIX}methods/">Read how seats are calculated.</a></p>', source=presentation['source'], thresholds='<p id="source-thresholds">Threshold watch not available: no published polls.</p>')
    polls, average, seats = envs['polls']['data'], envs['averages']['data'][-1], envs['seats']['data']
    status = next(s for s in envs['status']['data'] if s['dataset'] == 'polls')
    checked = status['last_attempt_at'] if status['state'] == 'fresh' else status['last_success_at']
    stale = presentation['stale']
    state = ''
    update = link(envs['status']['run_url'], 'Update details') if safe_url(envs['status']['run_url']) else f'<a href="{PREFIX}downloads/">Update details</a>'
    last = max(p['fieldwork_end'] for p in polls)
    if status.get('error_code'):
        state = f'<div class="state"><p>The {compact_time(status["last_attempt_at"])} update failed; showing previous data from {compact_time(status["last_success_at"])}. </p><p class="source-actions">{update}</p></div>'
    elif stale:
        state = f'<div class="state"><p>Update overdue. Last checked {compact_time(checked)}. Showing polls to {observation_label(last)}. </p><p class="source-actions">{update}</p></div>'
    if presentation['result']:
        dates = [(p['fieldwork_start'], p['fieldwork_end']) for p in presentation['selected']]
        first, end = min(a for a, b in dates), max(b for a, b in dates)
        date_line = (f'<p class="poll-dates" aria-describedby="source-seats">Polls <time datetime="{first}">{observation_label(first)}</time> '
                     f'to <time datetime="{end}">{observation_label(end)}</time>. <a href="{PREFIX}methods/">How seats are calculated</a>.</p>')
        picture = seat_topline(presentation['result']) + strip(presentation['result'], presentation['source']) + ungrouped_seats(presentation['result']) + date_line
    else:
        picture = (seat_topline(None) + f'<p aria-describedby="source-seats">Seat estimate unavailable. Polls to {observation_label(last)} are below.</p>'
                   f'<p><a href="{PREFIX}methods/">Read how seats are calculated.</a></p>'
                   f'<div><p><strong>Why seats are unavailable</strong></p><p>{escape(seats["reason"] or "Update overdue.")}</p></div>')
    for tie in seats.get('unresolved_ties', []):
        names = [label(p) for p in tie.get('candidates', [])]
        if names:
            picture += '<p class="missing" aria-describedby="source-seats">Tie for the last seat between ' + escape(' and '.join(names)) + '; shown unassigned.</p>'
    thresholds = '<section><h2>Which parties are near the 5 percent threshold?</h2><p class="threshold-rule" aria-describedby="source-thresholds">5% of the party vote qualifies a party with a list. An electorate win can also qualify it below 5%.</p>'
    watch = threshold_watch(polls, average, seats['assumptions'])
    thresholds += table('Parties near the threshold', ['Party', 'Share', 'Below 5%'],
                     [[party_link(row['party_id']), display(row['value'], row['scale']),
                       'Electorate assumed' if row['electorate_qualifies'] else 'Needs 5%'] for row in watch], source='source-thresholds')
    for row in watch:
        if row['missing_poll_ids']:
            thresholds += f'<p aria-describedby="source-thresholds">{escape(label(row["party_id"]))}: based on reported observations only.</p>'
    thresholds += '<p aria-describedby="source-thresholds">2023 electorate seats assumed; 2026 has different boundaries. List capacity not checked.</p>'
    thresholds += derivation_note(average)
    thresholds += source_note(envs['seats'], 'source-thresholds', 'seats.json',
                           calculation='Threshold shares averaged with equal weight by this site.',
                           contributing_polls=presentation['selected']) + '</section>'
    return state, render('seat-module', picture=picture,
                         source='' if presentation['result'] else presentation['source'],
                         thresholds=render('threshold-watch', content=thresholds))


def polls_page(envs, built, presentation=None, *, full_sources=False):
    presentation = presentation if presentation is not None else home_presentation(envs, built)
    state, picture = seat_module(envs, built, presentation)
    if not full_sources and not presentation['result']:
        picture = '<span id="source-seats"></span>'
        from product.nz_election.pipeline.home import thresholds, footnote, updated
        graphic = thresholds(envs) if 'seats' in envs else ''
        if graphic:
            picture += '<section><h2>Which parties are near the 5 percent threshold?</h2>' + graphic + footnote('thresholds', 'Wikipedia contributors', updated(envs, 'polls', built)) + '</section>'
        else:
            picture += '<span id="source-thresholds"></span>'
        for tie in envs.get('seats', {}).get('data', {}).get('unresolved_ties', []):
            names = [label(p) for p in tie.get('candidates', [])]
            if names:
                picture += '<p>Tie for the last seat between ' + escape(' and '.join(names)) + '; shown unassigned.</p>'
    if 'polls' not in envs:
        return render('polls', state='', picture=picture, explorer='', details='')
    polls, average = envs['polls']['data'], envs['averages']['data'][-1]
    details = '<div class="grid"><section><h2>What is the average party vote?</h2>'
    details += f'<p aria-describedby="source-average">Window: {average["window_start"]} to {average["window_end"]}. Equal weight for {len(average["poll_ids"])} polls.</p>'
    details += table('Descriptive shares and coverage', ['Party', 'Share', 'Polls'],
                     [[party_link(p), display(d['value'], d['scale']), str(len(d['poll_ids']))]
                      for p, d in average['descriptive'].items() if d['value'] is not None], source='source-average')
    if full_sources and average['missing']:
        details += '<p>Missing observations:</p><ul>' + ''.join(f'<li>{escape(m["poll_id"])}: {escape(label(m["party_id"]))}</li>' for m in average['missing']) + '</ul>'
    if full_sources and average['exclusions']:
        details += '<ul>' + ''.join(f'<li>{escape(e["poll_id"])}: {escape(e["reason"])}</li>' for e in average['exclusions']) + '</ul>'
    details += derivation_note(average)
    details += source_note(envs['averages'], 'source-average', 'averages.json',
                           calculation='Available poll shares averaged with equal weight by this site.',
                           contributing_polls=presentation['selected'])
    details += '</section></div>'
    if not full_sources and not any(d['value'] is not None for d in average['descriptive'].values()):
        details = '<span id="source-average"></span>'
    parties = list(config('party-map')['headers'].values())
    history, row_notes = [], []
    for poll in sorted(polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True):
        poll = derive_others(poll, parties)
        identity = 'source-' + poll['id']
        refs = f'<a href="{PREFIX}methods/#{identity}">Source and dates</a>'
        if 'derivation' in poll:
            refs += ' Others derived: 100 minus named shares (0 to 10 points).'
        row_notes.append(f'<div class="source-note" id="{identity}"><p>{escape(poll["pollster"])}. Fieldwork ended <time datetime="{poll["fieldwork_end"]}">{observation_label(poll["fieldwork_end"])}</time>.</p><p class="source-actions">' + ' '.join(link(url, 'Original report') for url in poll['reference_urls']) + f' <a href="#source-history">Revision, retrieval, licence and data run</a></p></div>')
        history.append([f'<span id="{escape(poll["id"])}" aria-describedby="source-history">{escape(poll["pollster"])}</span>',
                        escape(poll['fieldwork_start'] + ' to ' + poll['fieldwork_end']),
                        '' if poll['sample'] is None else str(poll['sample']),
                        *[display(poll['shares'][p], poll['scale']) if poll['shares'].get(p) is not None else '' for p in parties], refs])
    details += '<h2>How have the polls moved?</h2>' + table('All national 2026 observations in the source revision; scroll for all parties',
                                            ['Pollster', 'Fieldwork', 'Sample'] + [label(p) for p in parties] + ['Reports'], history, source='source-history')
    if full_sources:
        details += source_note(envs['polls'], 'source-history', 'polls.json').rstrip()[:-6] + '<div><p><strong>Individual poll sources and fieldwork dates</strong></p>' + ''.join(row_notes) + '</div></div>'
    else:
        note = source_note(envs['polls'], 'source-history', 'polls.json').split('</p>', 1)[0]
        aliases = ''.join(f'<span id="source-{escape(p["id"], quote=True)}"></span>' for p in polls)
        details += note.replace('class="source-note"', 'class="source-note home-footnote route-note"') + '</p><p class="source-actions">' + aliases + f'<a href="{PREFIX}methods/#source-history">Sources and method</a></p></div>'

    details += f'<p><a href="{PREFIX}data/averages.json">Daily average series and exact inputs</a></p>'
    if not full_sources:
        def compact(match):
            identity, paragraph = match.group(1), match.group(2)
            return (f'<div class="source-note home-footnote route-note" id="{identity}"><p>{paragraph}</p>'
                    f'<p class="source-actions"><a href="{PREFIX}methods/#{identity}">Sources and method</a></p></div>')
        pattern = r'<div[^>]*class="source-note"[^>]*id="(source-(?:average|thresholds))"[^>]*>\s*<p>(.*?)</p>.*?</div>'
        picture = re.sub(pattern, compact, picture, flags=re.S)
        details = re.sub(pattern, compact, details, flags=re.S)
    return render('polls', state=state, picture=picture,
                  explorer=explorer(envs, not presentation['stale']) if presentation['result'] or full_sources else '<span id="coalition-explorer"></span><span id="coalition-title"></span>', details=details)


def methods_page(stage, built, sha, run_url, envs=None):
    official = golden()
    result = allocate(official['input'])
    if (result['seats'] != official['expectedSeats'] or result['listMembers'] != official['expectedListMembers']
            or len(result['quotients']) != len(official['quotients']) or len(result['quotients']) != 120):
        raise ValueError('FIXTURE_2023_MISMATCH')
    for actual, expected in zip(result['quotients'], official['quotients']):
        if (any(actual[k] != expected[k] for k in ('rank', 'party_id', 'divisor')) or
                abs(Fraction(int(actual['numerator']), int(actual['divisor'])) - Fraction(Decimal(expected['display']))) > Fraction(1, 2000)):
            raise ValueError('FIXTURE_2023_MISMATCH')
    records = []
    normalized = []
    for p, votes in official['input']['partyVotes'].items():
        normalized.append(dict(id='official-' + p, source_ref=[dict(source_id='E:ec-2023/party-votes.csv', row=p)], observed_at='2023-11-03',
                               party_id=p, name=official['partyNames'][p], votes=votes,
                               electorate_wins=official['input']['electorateWins'][p],
                               list=official['input']['lists'].get(p, []), winners=official['input']['electorateWinners'][p],
                               entitlement=result['entitlements'][p], list_members=result['listMembers'][p], seats=result['seats'][p],
                               quotients=[q for q in result['quotients'] if q['party_id'] == p]))
        if result['seats'][p]:
            records.append([escape(official['partyNames'][p]), f'{votes:,}', str(result['entitlements'][p]),
                            str(official['input']['electorateWins'][p]), str(result['seats'][p])])
    env = export.envelope(normalized, source_entries()[1], run_url, sha,
                          inputs={e['path']: e['sha256'] for e in json.loads((PRODUCT / 'fixtures/manifest.json').read_text())['entries'] if e['path'] in GOLDEN_PATHS},
                          method='official-2023-validation-v1', generated=built)
    (stage / 'validation-2023.json').write_text(export.canonical(env) + '\n')
    (stage / 'validation-2023.csv').write_bytes(export.csv_bytes(env))
    derived = [derive_others(p, config('party-map')['headers'].values()) for p in (envs or {}).get('polls', {}).get('data', [])]
    names = {identity: name for name, identity in config('party-map')['pollsters'].items()}
    pollsters = sorted({names.get(p['pollster'], p['pollster']) for p in derived if 'derivation' in p})
    affected_rows = [p for p in derived if 'derivation' in p]
    listing = '<section id="derived-polls"><h2>Polls with derived Others</h2>'
    listing += '<ul>' + ''.join(
        f'<li><a href="{PREFIX}polls/#source-{escape(p["id"], quote=True)}">'
        f'{escape(names.get(p["pollster"], p["pollster"]))}, {escape(p["fieldwork_start"])} to {escape(p["fieldwork_end"])}</a>: '
        f'Others {display(p["shares"]["others"], p["scale"])} derived as 100 minus the named parties.</li>'
        for p in affected_rows) + '</ul>' if affected_rows else '<p>No affected polls in the published data.</p>'
    listing += '</section>'
    poll_sources = (envs or {}).get('polls', {}).get('source', source_entries()[0])
    history = next(s['history_url'] for s in poll_sources if s['id'] == 'P')
    return render('methods', history=safe_url(history) or '#', derivations=listing, affected=escape(', '.join(pollsters) or 'None in the published data'), votes=f'{sum(official["input"]["partyVotes"].values()):,}',
                  table=table('Official 2023 entitlement and occupied seats', ['Party', 'Votes', 'Entitlement', 'Electorates', 'Seats'], records, source='source-polls'),
                  prefix=PREFIX, source=source_note(env, inputs='validation-2023.json'))


def downloads(envs, data_sha):
    catalogue = ''
    if envs:
        records = []
        for entry in envs['manifest']['data']:
            name = entry['path']
            immutable = 'Not available'
            if data_sha:
                immutable = link(f'https://raw.githubusercontent.com/byronxlg/unattended/{data_sha}/product/nz_election/data/{name}', 'Pinned copy')
            run = entry['producing_run_url']
            producing = link(run, run) if run and safe_url(run) else 'fixture run (offline verification)'
            fields = [
                ('Size', str(entry['bytes']) + ' bytes' if entry['bytes'] is not None else 'Not available'),
                ('SHA-256', escape(entry['sha256'] or 'Not available')),
                ('Licence', escape(', '.join(entry['licences']) or 'Not available')),
                ('Rows', str(entry['row_count'])),
                ('Observation start', f'<time datetime="{entry["observation_start"]}">{escape(observation_label(entry["observation_start"]))}</time>' if entry['observation_start'] else 'Not available'),
                ('Observation end', f'<time datetime="{entry["observation_end"]}">{escape(observation_label(entry["observation_end"]))}</time>' if entry['observation_end'] else 'Not available'),
                ('Retrieved (Pacific/Auckland)', escape(local_time(entry['fetched_at']) if entry['fetched_at'] else 'Not available')),
                ('Producing run', producing), ('Immutable download', immutable)]
            metadata = '<dl class="download-fields">' + ''.join(
                f'<dt>{key}</dt><dd>{value}</dd>' for key, value in fields if value != 'Not available') + '</dl>'
            metadata += ('<div><p><strong>Full manifest record (stored UTC)</strong></p>'
                         '<dl><dt>Retrieved (UTC)</dt><dd>' + escape(entry['fetched_at'] or '') +
                         '</dd></dl><pre>' + escape(json.dumps(entry, ensure_ascii=False, sort_keys=True, indent=2)) + '</pre></div>')
            records.append(f'<tr data-file="{escape(name)}"><th scope="row"><a href="{PREFIX}data/{escape(name)}">{escape(name)}</a></th><td>{metadata}</td></tr>')
        catalogue = '<table class="download-catalogue" aria-describedby="source-polls"><caption>Published data inventory</caption><tbody>' + ''.join(records) + '</tbody></table>'
        catalogue += f'<p><a href="{PREFIX}data/LICENCES.md">Licences and CSV format</a></p>'
    catalogue += f'<p><a href="{PREFIX}validation-2023.json">Official 2023 normalized validation (JSON)</a> <a href="{PREFIX}validation-2023.csv">Validation (CSV)</a></p>'
    return render('downloads', catalogue=catalogue, prefix=PREFIX,
                  source=source_note(envs.get('polls'), inputs='polls.json' if 'polls' in envs else 'validation-2023.json'))


def electorates_page(envs, built=None):
    from product.nz_election.pipeline.geography import svg
    rows = envs.get('electorates', {}).get('data', config('electorates'))
    collections = {k: envs[k + '-2025'] for k in ('general', 'maori') if k + '-2025' in envs}
    mappings = {e['new_id']: e for e in config('electorate-correspondence')['entries'] if e['new_id'] is not None}
    directory = ''
    for kind, heading in [('general', 'General electorates'), ('maori', 'Māori electorates')]:
        directory += '<h2>' + heading + '</h2><ul>'
        for row in rows:
            if row['kind'] == kind:
                directory += (f'<li id="electorate-{escape(row["slug"])}" data-search-key="{escape(row["search_key"], quote=True)}">'
                              f'<a href="{PREFIX}electorates/{escape(row["slug"])}/">{escape(row["name"])}</a>'
                              f'<p>{escape(row['boundary_note'] if row['stats_id'] in mappings else 'Comparison unresolved')}</p></li>')
        directory += '</ul>'
    from product.nz_election.pipeline.electorate_pages import source as family_source
    source = family_source(envs, 'electorates', built).replace('id="source-electorates"', 'id="source-geography"')
    unmatched = [r for r in envs.get('electorate-polls', {}).get('data', []) if r['electorate_id'] is None]
    if unmatched:
        directory += '<h2>Local polls not matched</h2><ul aria-describedby="source-electorate-polls">' + ''.join(
            '<li>Not matched: ' + escape(r['boundary_basis']['source_name']) + ' (local poll)</li>' for r in unmatched) + '</ul>'
        directory += family_source(envs, 'electorate-polls', built)
    controls = ('<input type="radio" name="map-kind" id="map-general" checked><label for="map-general">General electorates</label>'
                '<input type="radio" name="map-kind" id="map-maori"><label for="map-maori">Māori electorates</label>') if collections else '<span id="map-general"></span><span id="map-maori"></span>'
    graphic = '<figure aria-describedby="source-geography">' + svg(collections, rows).replace('<svg ', '<svg aria-describedby="source-geography" ') + '<figcaption>2025 boundaries. Select an area or use the name directory.</figcaption></figure>' if collections else ''
    return render('electorates', map=graphic, controls=controls, directory=directory, source=source)


def output_path(out):
    out = Path(out).absolute()
    resolved = out.resolve()
    if out.is_symlink() or PRODUCT.is_relative_to(resolved) or resolved.is_relative_to(PRODUCT):
        raise ValueError('UNSAFE_OUTPUT_PATH')
    # A site tree belongs to the blog except for this one replaceable route root.
    for candidate in (out, resolved):
        for parent in (candidate, *candidate.parents):
            if parent.name == 'site' and candidate != parent / 'nz-election':
                raise ValueError('UNSAFE_OUTPUT_PATH')
    return resolved


def build(data, out, *, built=None, data_sha=None, sha=None, run_url=None, historical_advance=False):
    data, out = Path(data), output_path(out)
    if data_sha and not re.fullmatch('[0-9a-f]{40}', data_sha):
        raise ValueError('INVALID_DATA_SHA')
    envs = export.validate_bundle(data) if data.exists() else {}
    if not historical_advance and any(r['date'][:4] != '2026' for r in envs.get('advance-voting', {}).get('data', [])):
        raise ValueError('HISTORICAL_ADVANCE_REQUIRES_VERIFICATION')
    built = export.timestamp(utc_now() if built is None else built, 'build.built_at')
    from product.nz_election.pipeline.deployment_guard import require_publication_allowed
    require_publication_allowed(built)
    sha = sha or code_sha()
    if run_url is None:
        repository, run_id = os.environ.get('GITHUB_REPOSITORY'), os.environ.get('GITHUB_RUN_ID')
        run_url = (os.environ.get('GITHUB_SERVER_URL', 'https://github.com') + '/' + repository + '/actions/runs/' + run_id
                   if repository and run_id else 'offline-verification')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.build-', dir=out.parent) as tmp:
        stage = Path(tmp) / 'site'
        stage.mkdir()
        if envs:
            shutil.copytree(data, stage / 'data')
            export.validate_bundle(stage / 'data')
        home = home_presentation(envs, built)
        (stage / 'home-presentation.json').write_text(export.canonical(home) + '\n')
        methods = methods_page(stage, built, sha, run_url, envs)
        from product.nz_election.pipeline.home import sources, directory_links
        from product.nz_election.pipeline.electorate_pages import records
        from product.nz_election.pipeline.snapshot_views import sources as snapshot_sources
        from product.nz_election.pipeline.campaign_page import source as advance_source
        methods = sources(envs, built, home) + records(envs, built) + snapshot_sources(envs) + advance_source(envs, historical_advance) + methods
        manifest = export.envelope(dict(id='build', source_ref=[], observed_at=built, code_sha=sha,
                         data_sha=data_sha if envs else None, build_run_url=run_url, built_at=built,
                         data_available='polls' in envs), [], run_url, sha)
        export.pair(stage, 'build-manifest', manifest)
        routes = config('routes')
        if len(routes) != 10 or {r['path'] for r in routes} != {'', 'polls/', 'electorates/', 'night/', 'vote/', 'parties/', 'campaign/', 'downloads/', 'methods/', 'social/poc/'}:
            raise ValueError('INVALID_ROUTES')
        primary_routes = [dict(r, label={'': 'Overview', 'polls/': 'Polls', 'night/': 'Night', 'vote/': 'Vote'}.get(r['path'], r['label'])) for r in routes if r['path'] in {'', 'polls/', 'electorates/', 'night/', 'vote/', 'parties/', 'methods/'}]
        routes = routes + [dict(path='electorates/' + r['slug'] + '/', label=r['name']) for r in config('electorates')]
        from product.nz_election.pipeline.route_cards import route_key, summary, card, ORIGIN
        keys = [route_key(r["path"]) for r in routes]
        if len(set(keys)) != len(routes):
            raise ValueError("DUPLICATE_ROUTE_KEY")
        (stage / "og").mkdir()
        cards = []
        for route in routes:
            slug = route['path']
            visible_routes = [r for r in primary_routes if r['path'] != 'polls/' or envs.get('polls', {}).get('data')]
            nav = ''.join(f'<a href="{PREFIX + r["path"]}"' + (' aria-current="page"' if r["path"] == slug else '') +
                          f'>{escape(r["label"])}</a>' for r in visible_routes)
            if slug == '':
                from product.nz_election.pipeline.home import page
                body = page(envs, built, home)
            elif slug == 'polls/':
                body = polls_page(envs, built, home)
            elif slug == 'campaign/':
                from product.nz_election.pipeline.campaign_page import page
                body = page(envs, built, historical_advance)
                from product.nz_election.pipeline.m3_checks import check_markup
                check_markup(body, envs, historical_advance)
            elif slug == 'parties/':
                from product.nz_election.pipeline.parties_page import page
                body = page(envs, built)
            elif slug == 'vote/':
                from product.nz_election.pipeline.vote_page import page
                body = page(built)
            elif slug == 'night/':
                from product.nz_election.pipeline.night_page import page
                body = page(envs, built)
            elif slug == 'electorates/':
                body = electorates_page(envs, built)
            elif slug.startswith('electorates/'):
                from product.nz_election.pipeline.electorate_pages import detail
                row = next(r for r in envs.get('electorates', {}).get('data', config('electorates')) if slug == 'electorates/' + r['slug'] + '/')
                body = detail(row, envs, built)
            elif slug == 'social/poc/':
                from product.nz_election.pipeline.social_page import page
                body = page(envs, built)
            elif slug == 'methods/':
                body = methods
            elif slug == 'downloads/':
                body = downloads(envs, data_sha)
            else:
                raise ValueError('UNHANDLED_ROUTE: ' + slug)
            target = stage / slug
            target.mkdir(parents=True, exist_ok=True)
            title = ('New Zealand votes on 7 November 2026' if slug == '' else
                     'Proof of concept: what X says about the parties' if slug == 'social/poc/' else route['label'])
            heading = ('' if slug in {'', 'vote/', 'parties/'} else
                       '<h1>What do the polls tell us?</h1>' + ('<p aria-describedby="source-seats">' + escape(home['title']) + '</p>' if home['result'] else '') if slug == 'polls/' else
                       '<h1>' + escape({'night/': 'Election night results', 'electorates/': 'Who is standing in your electorate?', 'methods/': 'How are these numbers calculated?', 'downloads/': 'Where does the data come from?', 'campaign/': 'What is happening in the campaign?', 'social/poc/': 'What are people posting about the parties?'}.get(slug, title)) + '</h1>')
            title, description = summary(route, envs, home, built)
            key = route_key(slug)
            cards.append(dict(route=slug, key=key, title=title, description=description, html='og/' + key + '.html', png='og/' + key + '.png'))
            (stage / cards[-1]['html']).write_text(card(route, envs, home, built))
            page_html = render('base', title=escape(title), description=escape(description, quote=True),
                               image=ORIGIN + PREFIX + cards[-1]['png'], heading=heading, prefix=PREFIX, nav=nav, body=body,
                               directory=directory_links(envs) if slug == '' else '',
                               built='Page built ' + escape(local_time(built)) + '. Age labels are checked at build time.')
            if slug in {'', 'polls/', 'methods/'}:
                page_html = page_html.replace('</head>', f'<link rel="stylesheet" href="{PREFIX}party-links.css"></head>')
            if slug == 'parties/':
                page_html = page_html.replace('</head>', f'<link rel="stylesheet" href="{PREFIX}parties.css"></head>')
            if slug == 'vote/':
                # Navigation follows the task so first-screen actions stay on EC services.
                header = re.search(r'<header>.*?</header>', page_html, flags=re.S)[0]
                page_html = page_html.replace(header, '').replace('<footer>', header + '<footer>')
            (target / 'index.html').write_text(page_html)
        (stage / 'og-manifest.json').write_text(export.canonical(cards) + '\n')
        for asset in ('favicon.svg', 'icon-180.png', 'icon-512.png', 'manifest.webmanifest'):
            shutil.copyfile(PRODUCT / 'web' / asset, stage / asset)
        for page in stage.rglob('*.html'):
            validate_scripts(page.read_text())
        shutil.copyfile(PRODUCT / 'web/party-links.css', stage / 'party-links.css')
        shutil.copyfile(PRODUCT / 'web/parties.css', stage / 'parties.css')
        shutil.copyfile(PRODUCT / 'web/night.css', stage / 'night.css')
        shutil.copyfile(PRODUCT / 'web/night-seats.mjs', stage / 'night-seats.mjs')
        shutil.copyfile(PRODUCT / 'web/night.mjs', stage / 'night.mjs')
        shutil.copyfile(PRODUCT / 'web/night-parser.mjs', stage / 'night-parser.mjs')
        shutil.copyfile(PRODUCT / 'web/coalitions.mjs', stage / 'coalitions.mjs')
        shutil.copyfile(PRODUCT / 'web/styles.css', stage / 'styles.css')
        shutil.copytree(PRODUCT / 'web/fonts', stage / 'fonts')
        shutil.copytree(PRODUCT / 'web/people', stage / 'people')
        shutil.copyfile(PRODUCT / 'web/allocator.mjs', stage / 'allocator.mjs')
        shutil.copyfile(PRODUCT / 'web/electorates.mjs', stage / 'electorates.mjs')
        replace_directory(stage, out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--data-sha')
    parser.add_argument('--now')
    parser.add_argument('--historical-advance', action='store_true', help='Label historical advance verification')
    args = parser.parse_args()
    build(args.data, args.out, built=args.now, data_sha=args.data_sha or os.environ.get('NZ_DATA_SHA') or None,
          sha=os.environ.get('NZ_CODE_SHA'), historical_advance=args.historical_advance)
    print('PASS build: 81 routes')


if __name__ == '__main__':
    main()
