"""Presentation of reviewed snapshots, with attribution kept reachable in Methods."""
from html import escape
from functools import cache
from . import snapshots
from .build import PREFIX, config, table, link, label
from .home_charts import colour, fallback

load = cache(snapshots.load)


def result(row, envs):
    if row['slug'] == 'port-waikato':
        votes = load('port-waikato-2023')
    else:
        old = [r for r in envs.get('baseline-2023', {}).get('data', [])
               if r['old_electorate_id'] in row['baseline_ids']]
        if len(old) != 1:
            # The correspondence lists the named predecessor first. Never imply
            # that votes have been reallocated to the new boundary.
            primary = next((r for r in old if r['old_electorate_id'] == row['baseline_ids'][0]), None)
            old = [primary] if primary else []
        if not old:
            return None
        votes = old[0].get('candidate_votes') or []
    ranked = sorted(votes, key=lambda r: -r['votes'])
    if len(ranked) < 2:
        return None
    if ranked[0]['votes'] == ranked[1]['votes']:
        return None
    winner = ranked[0]
    names = config('party-map')['headers']
    party = winner.get('party_id') or names.get(winner['party'])
    if not party:
        aliases = {'National Party': 'nat', 'Labour Party': 'lab', 'Green Party': 'grn',
                   'ACT New Zealand': 'act', 'Te Pāti Māori': 'tpm'}
        party = aliases.get(winner['party'])
    return dict(baseline_name='Port Waikato' if row['slug'] == 'port-waikato' else old[0]['old_name'], name=winner['name'], party=winner['party'], party_id=party,
                margin=winner['votes']-ranked[1]['votes'])


def footnote(name, date='19 October 2026'):
    return (f'<div class="source-note home-footnote" id="source-{name}"><p class="source-actions">'
            f'Data to {date}. <a href="{PREFIX}methods/#home-{name}">Sources and method</a></p></div>')


def photo_credit(row):
    p = row.get('photo')
    return f'<small class="photo-credit">{escape(p["author"])} / {escape(p["licence"])}</small>' if p else ''


def photo(row, *, credit=True):
    p = row.get('photo')
    if not p:
        return ''
    return (f'<img src="{PREFIX}{p["path"].removeprefix("web/")}" alt="" width="160" height="160" loading="lazy">'
            + (photo_credit(row) if credit else ''))


def people():
    content = '<div class="leaders">'
    for row in load('leaders'):
        if not row.get('photo'):
            continue
        content += (f'<article style="--party:{colour(row.get("party_id"))}">{photo(row)}'
                    f'<h3>{escape(row["name"])}</h3><p>{escape(label(row["party_id"]) if row.get("party_id") else row["party"])}</p></article>')
    return content + '</div>'


def map_graphic(envs, selected=None):
    rows = {r['slug']: r for r in config('electorates')}
    cells = load('hexmap')
    width = (max(c['x'] for c in cells)+1)*26
    height = (max(c['y'] for c in cells)+1)*26
    marks, records = '', []
    for c in cells:
        row = rows[c['electorate_slug']]
        held = result(row, envs)
        fill = colour(held['party_id']) if held else 'var(--grey)'
        opacity = min(1, .45 + held['margin']/16000) if held else .25
        description = (f'{held["baseline_name"]} (2023): {held["party"]}, {held["margin"]:,} votes' if held else 'Boundary correspondence in Methods')
        title = row['name'] + ': ' + description
        rect = (f'<rect x="{c["x"]*26+2}" y="{c["y"]*26+2}" width="22" height="22" '
                f'fill="{fill}" fill-opacity="{opacity:.2f}"'
                + (' stroke="var(--ink)" stroke-width="3"' if selected == row['slug'] else '') + '/>')
        if selected:
            marks += '<g><title>' + escape(title) + '</title>' + rect + '</g>'
        else:
            marks += f'<a href="{PREFIX}electorates/{row["slug"]}/" aria-label="{escape(title)}"><title>{escape(title)}</title>{rect}</a>'
        records.append([escape(row['name']), escape(held['party']) if held else '', f'{held["margin"]:,}' if held else ''])
    graphic = (f'<svg class="tile-map" viewBox="0 0 {width} {height}" role="img" aria-label="2023 holders on original boundaries; schematic 2025 locations" aria-describedby="source-map">{marks}</svg>')
    if selected:
        return graphic
    legend = '<div class="map-key">' + ''.join(f'<span><i style="background:{colour(p)}"></i>{escape(label(p))}</span>' for p in ['nat','lab','grn','act','tpm']) + '</div>'
    return graphic + legend + '<p class="map-caption">Darker tiles mean larger 2023 margins. Locations are schematic; Māori seats sit in a separate column. For changed boundaries, tiles show the named 2023 predecessor, not a recalculated result.</p>' + fallback(table('2023 holders on original boundaries', ['Electorate', 'Party', 'Margin'], records, source='source-map'))


def sources():
    content = ''
    for name, title in [('map','Electorate tile map'), ('leaders','Party leaders'), ('candidates-2026','2026 candidates'), ('enrolment-snapshot','Electorate enrolment'), ('history','Election history'), ('positions','Coalition positions'), ('port-waikato','Port Waikato by-election')]:
        stem = {'map':'hexmap','enrolment-snapshot':'enrolment','port-waikato':'port-waikato-2023'}.get(name,name)
        rows = load(stem)
        content += f'<section id="home-{name}"><h2>{title}</h2>'
        if name == 'map':
            content += '<p>Square tiles from the reviewed hexmap snapshot. Colour uses the 2023 result on the original boundaries, not a prediction for 2026. For changed seats, the first named predecessor in the reviewed correspondence supplies the original result. This is historical context, not an allocation of votes to new boundaries. Margins are votes, not percentages. Port Waikato uses the November by-election.</p>'
        if name == 'history':
            content += table('General election history', ['Year', 'Party', 'Vote share', 'Seats'], [[str(r['year']), escape(r['party']), r['party_vote_share'] + '%', str(r['seats'])] for r in rows], source='source-history-snapshot') + '<div class="source-note" id="source-history-snapshot"><p>Electoral Commission, sources below.</p><p class="source-actions">' + link(rows[0]['source_url'], 'Election results') + '</p></div>'
        for row in rows:
            if name == 'positions':
                content += '<blockquote>' + escape(row['quote']) + '</blockquote><p>' + escape(row['speaker'] + ', ' + row['date']) + '</p>'
            content += '<p>' + escape(row.get('name', row.get('electorate_slug', row.get('party', row.get('party_id', ''))))) + ': ' + link(row['source_url'], 'Record') + '. ' + escape(row['licence']) + '. Retrieved ' + escape(row['retrieved_at']) + '.</p>'
            if row.get('list_rank'):
                content += '<p>' + link(row['list_rank_source_url'], 'List rank') + ': ' + str(row['list_rank']) + '. ' + escape(row.get('list_rank_licence','')) + '</p>'
            if row.get('photo'):
                p = row['photo']
                content += '<p>' + link(p['source_url'], 'Photo: ' + p['author']) + '. ' + link(p['licence_url'], p['licence']) + '. ' + escape(p['changes']) + '</p>'
        content += '</section>'
    return content
