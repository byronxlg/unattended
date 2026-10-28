"""Night-only leader map and searchable static electorate table."""
from html import escape
import json
from .build import PREFIX, PRODUCT, config, table
from .night_seats import waterfall
from . import home_graphics as g


def display_name(name):
    if ", " in name:
        surname, given = name.split(", ", 1)
        if surname.isupper():
            return given + " " + surname.title()
    return name


def seat_chart(row, source):
    result = waterfall(row.get('allocation_input'), complete='allocation_input' in row, capacity_verified=row.get('capacity_verified', False))
    calc = result['calculation']
    if calc is None:
        return '<p class="night-calculation">' + ('Allocation tie requires official lot evidence.' if result['status'] == 'unresolved tie' else 'Seat calculation needs complete inputs.') + '</p>'
    stages = [('Proportional entitlement', sum(calc['entitlements'].values())), ('Overhang', calc['overhang'])]
    if 'vacancies' in calc:
        stages += [('Vacancies', -calc['vacancies']), ('Calculated occupied House', calc['occupiedHouse'])]
    content = '<h3>How the calculated seats add up</h3><p>Application calculation, separate from source-reported seats.</p>'
    if 'vacancies' not in calc:
        content += '<p>List capacity is unchecked; occupied House and vacancies need verified candidate lists.</p>'
    content += f'<figure class="night-waterfall" aria-describedby="{source}">'
    offset = 0
    for label, n in stages:
        start = 0 if label in {'Proportional entitlement', 'Calculated occupied House'} else offset + min(0, n)
        content += f'<div class="night-step"><span>{label}: {n}</span><div><i style="margin-left:{start * 100 / 140:.2f}%;width:{abs(n) * 100 / 140:.2f}%"></i></div></div>'
        offset = n if start == 0 else offset + n
    context = row['mode'] + (', ' + row['source_updated_local'] if row.get('source_updated_local') else
                             ', ' + str(row['elapsed_seconds']) + ' seconds' if 'elapsed_seconds' in row else '')
    return content + '</figure>' + table('Calculated seats: ' + context, ['Component', 'Seats'], [[label, str(n)] for label, n in stages], source=source)


def electorate_view(row, refs, source, identity):
    if 'leaders' not in row:
        return ''
    official = row.get('result_state') == 'official'
    registry = config('electorates')
    by_name = {r['name']: r for r in registry}
    layout = json.loads((PRODUCT / 'snapshots/hexmap.json').read_text())['records']
    positions = {r['electorate_slug']: (r['x'], r['y']) for r in layout}
    rows, cells, map_rows = [], [], {}
    extra = 0
    legend = {}
    for e, ref in refs['electorates'].items():
        name = ref['electorate_name']
        current = by_name.get(name)
        item = row['leaders'].get(e, {})
        leader = refs['candidates'].get(item.get('leader'), {})
        party = refs['parties'].get(leader.get('party'), {})
        label = display_name(leader.get('candidate_name', 'Tied; no sole leader' if item.get('status') in {'provisional', 'final'} else 'Not yet reported'))
        if item.get('tied_candidates'):
            label = 'Tied: ' + ', '.join(display_name(refs['candidates'][c]['candidate_name']) for c in item['tied_candidates'])
        margin = item.get('margin')
        status = item.get('status', 'not yet reported')
        if status == 'final':
            status = 'Final source count' if official else 'Final source count; leader provisional'
        elif leader:
            status = 'Source-reported leader' if official else 'Provisional leader'
        stats = item.get('statistics')
        if stats:
            status += f"; {stats['total_voting_places_counted']} of {stats['total_voting_places']} voting places"
        link = (f'<a href="{PREFIX}electorates/{current["slug"]}/">{escape(name)}</a>' if current else
                f'<a href="{PREFIX}electorates/">{escape(name)} (2023 electorate)</a>')
        source_name = leader.get('candidate_name', '')
        if source_name and display_name(source_name) != source_name:
            status += '; source name: ' + source_name
        rows.append([link, escape(label + (' (' + party['short_name'] + ')' if party else '')), str(margin) if margin is not None else 'Not yet reported', escape(status)])
        if not current:
            related = [r for r in registry if int(e) in r['baseline_ids']]
            if related:
                rows[-1][0] = escape(name) + ' (2023); today: ' + ', '.join(f'<a href="{PREFIX}electorates/{r["slug"]}/">{escape(r["name"])}</a>' for r in related)
        x, y = positions[current['slug']] if current else (extra % 6, 24 + extra // 6)
        if not current:
            extra += 1
        abbrev = party.get('abbrev')
        mapping = {'NAT':'nat','LAB':'lab','GP':'grn','ACT':'act','NZF':'nzf','TPMAO':'tpm','MAOR':'tpm'}
        party_id = mapping.get(abbrev, 'other')
        colour = g.pc(party_id)
        if leader:
            legend[party.get('short_name', 'Independent')] = colour
        description = label + (' (' + party['short_name'] + ')' if party else '') + (f', margin {margin}' if margin is not None else '') + '; ' + status
        cell = next((c.copy() for c in layout if current and c['electorate_slug'] == current['slug']), dict(x=x, y=y, group='general'))
        cell['electorate_slug'] = e
        cells.append(cell)
        map_rows[e] = dict(name=name, slug=current['slug'] if current else '', description=description,
                           held=dict(party_id=party_id, party=party.get('short_name', ''), margin=margin or 0) if leader else None)
        rows[-1][1] = f'<span class="night-party-cell" style="--c:{colour};--a:18%">{rows[-1][1]}</span>'
    content = '<section class="night-electorates module"><h2>Who is ahead in my electorate?</h2>'
    guidance = '<p>Provisional leaders, not elected members.</p>'
    if official:
        guidance = guidance.replace('Provisional leaders, not elected members.', 'Official source-reported leaders.')
    if '2023' in row['mode'] or row['source_ref'] == ['ec-2023-xml/election.xml']:
        guidance += '<p>2023 electorates, on their original boundaries. Links lead to today’s electorate information; no votes are transferred to new boundaries.</p>'
    content += f'<label for="night-search-{identity}">Find an electorate</label><input id="night-search-{identity}" class="night-search" type="search" placeholder="Electorate name">'
    content += guidance
    content += '<div class="night-map-key map-key"><p>Grey means no reported leader; deeper colour means a larger margin.</p>'
    if legend:
        content += '<ul>' + ''.join(f'<li><i style="background:{colour}"></i>{escape(name)}</li>' for name, colour in sorted(legend.items())) + '</ul><p class="tones"><span>Margin</span><i class="close"></i>under 2,000<i class="mid"></i>2,000 to 8,000<i class="safe"></i>over 8,000</p>'
    content += '</div>'
    svg, _ = g.hex_map({}, cells, map_rows, lambda r: r['held'], source=source, night=True)
    content += f'<figure class="night-map" aria-describedby="{source}">' + svg + '<figcaption>Find an electorate in the searchable table below.</figcaption></figure>'
    context = row['mode'] + (', ' + row['source_updated_local'] if row.get('source_updated_local') else
                             ', ' + str(row['elapsed_seconds']) + ' seconds' if 'elapsed_seconds' in row else '')
    rendered = table('Electorate provisional leaders: ' + context, ['Electorate', 'Leader', 'Margin (votes)', 'Reporting status'], rows, css="poll-table", source=source)
    for e in refs['electorates']:
        rendered = rendered.replace('<tr><td>', f'<tr id="night-row-{identity}-{e}"><td>', 1)
    if official:
        content = content.replace('Electorate provisional leaders', 'Official electorate leaders')
        rendered = rendered.replace('Electorate provisional leaders', 'Official electorate leaders')
    return content + rendered + '</section>'


def comparison_view(preliminary, official, source, *, names=None):
    from .night_seats import official_change
    result = official_change(preliminary, official)
    if result is None:
        return ''
    names = names or {}
    content = '<h2>Change since preliminary result</h2><p>' + escape(result['preliminary_date'] + ' to ' + result['official_date']) + '</p>'
    content += table('Change since preliminary result', ['Party', 'Seat change'], [[escape(names.get(p, p)), f'{n:+d}'] for p, n in result['changes'].items()], source=source)
    if 'specials' in result:
        content += table('Source-identified special votes', ['Party', 'Special votes'], [[escape(p), str(v)] for p,v in result['specials']['votes'].items()], source=source)
        content += '<p><a href="' + escape(result['specials']['source'], quote=True) + '">Special votes source</a></p>'
    return content
