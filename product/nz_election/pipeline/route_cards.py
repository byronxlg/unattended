"""Shared route summaries and browser-independent social card documents."""
from html import escape
from fractions import Fraction
from .build import PREFIX, config, render, strip, label, source_note, compact_time, link, derivation_note
from .home import note
from .average import display
from .presentation import election_countdown

ORIGIN = 'https://byronxlg.github.io'
RESULTS = 'https://www.electionresults.govt.nz/'
LAW = 'https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM310065.html'


def route_key(path):
    return path.rstrip('/').replace('/', '--') or 'home'


def night(built):
    countdown = election_countdown(built)
    if countdown[0].isdigit():
        number, unit = countdown.split(' ', 1)
        countdown = f'<strong>{number}</strong><br>{unit}'
    return render('night', countdown=countdown, source=note(
        'source-night', 'No results feed is published yet. No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197.',
        f'<a href="{LAW}">Electoral Act s197</a><a href="{RESULTS}">Official Electoral Commission results</a>'))


def summary(route, envs, home, built):
    path = route['path']
    title = ('New Zealand votes on 7 November 2026' if path == '' else
             'Proof of concept: what X says about the parties' if path == 'social/poc/' else route['label'])
    description = {
        '': home['title'],
        'polls/': 'No published polling averages available.',
        'electorates/': 'Find your candidates and the 2025 electorate boundaries. No electorate forecast.',
        'night/': election_countdown(built) + '. Results appear here from 7 pm on 7 November. No results feed is published yet.',
        'parties/': 'Party polling, leaders, policies, coalition positions, list candidates and declared donations.',
        'vote/': 'How and when to enrol, find a voting place and cast your two votes.',
        'campaign/': 'Official voting information and sourced national advance-voting observations.',
        'downloads/': 'Download published data with source dates, licences and producing runs.',
        'methods/': 'How equal-weight polls and Sainte-Laguë allocation calculate seats, with assumptions and limits.',
        'social/poc/': 'Proof of concept: sampled posts are not votes or representative public opinion.',
    }.get(path)
    if path == 'night/' and envs.get('night/index', {}).get('data'):
        description = 'Packaged final results, recorded demo and an illustrative 2023 replay. Preliminary 2026 results remain separate.'
    if path.startswith('electorates/') and path != 'electorates/':
        row = next(r for r in envs.get('electorates', {}).get('data', config('electorates')) if path == 'electorates/' + r['slug'] + '/')
        from .snapshot_views import result
        held = result(row, envs)
        description = row['name'] + ': ' + (f'{held["party"]}, {held["margin"]:,} vote majority in {held["baseline_name"]} in 2023 on the original boundaries.' if held else '2026 candidates and electorate boundaries.')
        title = description
    if path == 'polls/' and envs.get('averages', {}).get('data'):
        values = envs['averages']['data'][-1]['descriptive']
        leaders = sorted(((p, v) for p, v in values.items() if p != 'others' and v['value'] is not None), key=lambda x: (-Fraction(x[1]['value'], x[1]['scale']), x[0]))[:2]
        description = '; '.join(label(p) + ' ' + display(v['value'], v['scale']) for p, v in leaders) or description
    return title, description


def card(route, envs, home, built):
    title, description = summary(route, envs, home, built)
    picture = ''
    source_id = 'source-og'
    source = note('source-og', escape(description), f'<a href="{PREFIX + route["path"]}">Source dates, availability and methods</a>')
    if route['path'] == '':
        title = description
        source_id = 'source-seats'
        picture = strip(home['result']).split('<div class="seat-data">')[0] if home['result'] else ''
        source = home['source'] if home['result'] else note('source-seats', 'Election information and calculation method.', f'<a href="{PREFIX}methods/#home-seats">Sources and method</a>')
    elif route['path'] == 'polls/' and envs.get('averages'):
        source_id = 'source-average'
        title = description
        source = source_note(envs['averages'], 'source-average', 'averages.json', contributing_polls=home['selected']) + derivation_note(envs['averages']['data'][-1])
    elif route['path'].startswith('electorates/') and route['path'] != 'electorates/':
        title = route['label']
        picture = '<p aria-describedby="source-og">' + escape(description.split(': ', 1)[1]) + '</p>'
        baseline = envs.get('baseline-2023')
        if baseline:
            row = next(r for r in envs.get('electorates', {}).get('data', config('electorates')) if route['path'] == 'electorates/' + r['slug'] + '/')
            source_ids = {ref['source_id'] for old in baseline['data'] if old['old_electorate_id'] in row['baseline_ids'] for ref in old['field_sources'].get('candidate_votes', [])}
            links = ''.join(link(s['url'], 'Electoral Commission candidate results') for s in baseline['source'] if s['id'] in source_ids)
            source = note('source-og', '2023 results on original boundaries. Copyright Electoral Commission; no open licence stated. Retrieved ' + compact_time(baseline['fetched_at']) + '.',
                          links + f'<a href="{PREFIX + route["path"]}">Boundary correspondence and sources</a>')
        else:
            source = note('source-og', 'No published 2023 candidate results. Reviewed 2025 boundary correspondence.', f'<a href="{PREFIX + route["path"]}">Boundary correspondence and sources</a>')
    return render('og', title=escape(title), prefix=PREFIX, picture=picture, source=source, source_id=source_id)
