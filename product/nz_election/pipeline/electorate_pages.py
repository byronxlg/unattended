"""Static electorate detail presentation, including explicit missing-data states."""
from .presentation import overdue
from decimal import Decimal
from html import escape
from urllib.parse import urlsplit
from .build import PREFIX, link, table, observation_label, compact_time


def publisher(source):
    identity = source['id']
    host = urlsplit(source['url']).hostname or ''
    if 'representation-commission/' in identity:
        return 'Representation Commission'
    if 'Stats NZ' in source['licence']:
        return 'Stats NZ'
    if host.endswith('wikipedia.org') or 'Wikipedia contributors' in source['licence']:
        return 'Wikipedia contributors'
    if host.endswith('wikidata.org'):
        return 'Wikidata contributors'
    if host in ('elections.nz', 'vote.nz', 'www.elections.nz', 'www.vote.nz', 'electionresults.govt.nz', 'www.electionresults.govt.nz'):
        return 'Electoral Commission'
    return host


def source(envs, stem, built=None, *, full=False):
    env = envs.get(stem)
    if not env or not env['source']:
        return (f'<div class="source-note" id="source-{stem}"><p>No validated data bundle.</p><p class="source-actions"><a href="{PREFIX}downloads/">Downloads</a></p></div>' if full else f'<span id="source-{stem}"></span>')
    if not full:
        family = 'geography' if stem == 'electorates' else stem
        status = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == family), {})
        fetched = status.get('last_success_at') or max(entry['fetched_at'] for entry in env['source'])
        return (f'<div class="source-note home-footnote" id="source-{stem}"><p class="source-actions">'
                + f'Data to {compact_time(fetched)}. '
                + f'<a href="{PREFIX}methods/#records-{stem}">Sources and method</a></p></div>')
    result = '<div role="note" class="source-note" id="source-' + stem + '">'
    for entry in env['source']:
        result += '<p class="source-actions">From ' + link(entry['url'], publisher(entry)) + ' <span>' + escape(entry['licence']) + '</span></p>'
        result += '<p>Retrieved ' + f'<time datetime="{entry["fetched_at"]}">{compact_time(entry["fetched_at"])}</time>' + '.</p>'
    result += '<p class="source-actions">' + f'<a href="{PREFIX}downloads/">Downloads and provenance</a>'
    result += f'<a href="{PREFIX}data/{stem}.json">Download data and field sources</a>'
    if env['run_url'] != 'offline-verification':
        result += link(env['run_url'], 'Producing run')
    result += '</p><div><p><strong>Source history and producing run</strong></p>'
    for entry in env['source']:
        if entry['history_url']:
            result += '<p class="source-actions">' + link(entry['history_url'], publisher(entry) + ': contributor history') + '</p>'
    if env['run_url'] == 'offline-verification':
        result += '<p>Offline verification from captured sources. Not live data.</p>'
    family = 'geography' if stem == 'electorates' else stem
    status = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == family), None)
    if status and (status['state'] != 'fresh' or (built and status['last_success_at'] and
            overdue(status['last_success_at'], built, 'daily'))):
        band = f'<p class="state">Update overdue. Last checked {compact_time(status["last_success_at"])}. Showing previous data. <a href="{PREFIX}downloads/">Update details</a>.</p>'
        if status.get('error_code'):
            band = f'<p class="state">The {compact_time(status["last_attempt_at"])} update failed; showing previous data from {compact_time(status["last_success_at"])}. <a href="{PREFIX}downloads/">Update details</a>.</p>'
        result = result.replace('<div>', band + '<div>', 1)
    return result + '</div></div>'


def detail(row, envs, built=None):
    from .snapshot_views import result, map_graphic, footnote, photo, photo_credit, load, winner_name
    from .home_charts import colour
    from .build import label
    held = result(row, envs)
    intro = ''
    if held:
        intro = (f'<p>2023 winner in {escape(held["baseline_name"])}</p><p class="holder">{escape(winner_name(row, held))} <span>{escape(held["party"])}</span></p>'
                 f'<p class="local-margin"><strong>{held["margin"]:,}</strong> vote majority in 2023'
                 + (' by-election' if row['slug'] == 'port-waikato' else '') + '</p>')
    boundary = row['boundary_note']
    if boundary == 'All these electorates remain unchanged from their 2020 boundaries and names.':
        boundary = row['name'] + "'s boundaries and name are unchanged from 2020."
    intro += '<p class="boundary-note">' + escape(boundary) + '</p>'
    candidates = ''
    for c in load('candidates-2026'):
        if c['electorate_slug'] != row['slug']:
            continue
        candidates += (f'<li style="--party:{colour(c.get("party_id"))}"><div class="candidate-photo">{photo(c, credit=False)}</div><div><strong>'
                       + escape(c['name']) + '</strong><p>' + escape(label(c['party_id']) if c.get('party_id') else c['party'])
                       + (' / List ' + str(c['list_rank']) if c.get('list_rank') else '') + '</p>' + photo_credit(c) + '</div></li>')
    candidates = ('<section><h2 id="candidates-title">Standing in 2026</h2><ul class="candidate-list" aria-describedby="source-candidates-2026">'
                  + candidates + '</ul>' + footnote('candidates-2026') + '</section>') if candidates else '<span id="candidates-title"></span>'
    intro += footnote('port-waikato') if row['slug'] == 'port-waikato' else source(envs, 'baseline-2023', built)
    outline = '<figure aria-describedby="source-map">' + map_graphic(envs, row['slug']) + '<figcaption>Highlighted: ' + escape(row['name']) + '</figcaption>' + footnote('map') + '</figure>'
    content = '<div class="electorate-top"><div>' + intro + candidates + '</div>' + outline + '</div>'
    baseline = ''
    for old in envs.get('baseline-2023', {}).get('data', []):
        if old['old_electorate_id'] not in row['baseline_ids']:
            continue
        votes = load('port-waikato-2023') if row['slug'] == 'port-waikato' else old.get('candidate_votes')
        if votes or old['party_votes']:
            baseline += '<h3>' + escape(old['old_name']) + ' (2023)</h3>'
        if votes:
            baseline += table(old['old_name'] + ': candidate votes', ['Candidate', 'Party', 'Votes'],
                              [[escape(v['name']), escape(v['party']), f'{v["votes"]:,}'] for v in sorted(votes, key=lambda v: -v['votes'])], source='source-port-waikato' if row['slug'] == 'port-waikato' else 'source-baseline-2023')
        if old['party_votes']:
            baseline += table(old['old_name'] + ': party votes', ['Party', 'Votes'], [[escape(v['name']), f'{v["votes"]:,}'] for v in old['party_votes']], source='source-baseline-2023')
    if baseline:
        content += '<section class="original-results"><h2>2023 results on the original boundaries</h2><p>These votes have not been moved or added together to fit the 2025 boundaries.</p><details><summary>See the vote counts</summary>' + baseline + '</details></section>'
    roll = next((r for r in load('enrolment') if r['electorate_slug'] == row['slug']), None)
    if roll:
        content += '<section><h2>Enrolment</h2><p aria-describedby="source-enrolment-snapshot">' + f'{roll["enrolled"]:,} enrolled at {observation_label(roll["as_at"])}.</p>' + footnote('enrolment-snapshot') + '</section>'
    polls = [p for p in envs.get('electorate-polls', {}).get('data', []) if p['electorate_id'] == row['id']]
    if polls:
        captions = {}
        content += '<section><h2>Local polls</h2>'
        for poll in polls:
            caption = poll['pollster'] + ': ' + poll['boundary_basis']['fieldwork_label'] + ' / ' + ('Party vote' if poll['measure'] == 'party_vote' else 'Candidate vote')
            captions[caption] = captions.get(caption, 0) + 1
            if captions[caption] > 1:
                caption += f' (report {captions[caption]})'
            content += table(caption, ['Party or candidate', 'Share'],
                             [[escape(n), ('About ' if v['approximate'] else '') + str(Decimal(v['value'])/poll['scale']) + '%'] for n,v in poll['shares'].items() if v['value'] is not None], source='source-electorate-polls')
        content += source(envs, 'electorate-polls', built) + '</section>'
    # Keep legacy fragments without displaying empty modules.
    for stem in ['electorates', 'candidates', 'baseline-2023', 'enrolment', 'electorate-polls']:
        if f'id="source-{stem}"' not in content:
            content += f'<span id="source-{stem}"></span>'
    return content


def candidate_records(envs):
    result = ''
    reviews = {c['id']: c for c in envs.get('candidate-review', {}).get('data', [])}
    for c in envs.get('candidates', {}).get('data', []):
        result += '<div class="candidate-sources"><h3>' + escape(c['name']) + '</h3>'
        for field in ('name', 'party_id'):
            for ref in c['field_sources'][field]:
                src = next(s for s in envs['candidates']['source'] if s['id'] == ref['source_id'])
                result += '<dl><dt>' + ('Candidate name' if field == 'name' else 'Party') + '</dt><dd>' + link(src['url'], publisher(src)) + '</dd><dt>Record location</dt><dd>' + escape(ref['locator']) + '</dd></dl>'
        for identity in c['conflict_ids']:
            conflict = reviews[identity]
            result += '<p>Unresolved: ' + escape(conflict['field']) + '</p><ul>'
            for claim in conflict['claims']:
                result += '<li>' + escape(str(claim['value'])) + ': ' + escape(claim['source_id'] + ' / ' + claim['locator']) + '</li>'
            result += '</ul>'
        result += '</div>'
    return result


def records(envs, built):
    result = ''
    for stem, title in (('electorates', 'Electorate boundaries'), ('candidates', 'Candidate records'),
                        ('baseline-2023', '2023 electorate results'), ('enrolment', 'Enrolment'),
                        ('electorate-polls', 'Local polls')):
        result += f'<section id="records-{stem}"><h2>{title}</h2>'
        result += source(envs, stem, built, full=True)
        if stem == 'baseline-2023':
            winners = [[escape(r['old_name']), escape(c['name']), escape(c['party']), str(c['votes'])]
                       for r in envs.get(stem, {}).get('data', [])
                       for c in sorted(r.get('candidate_votes') or [], key=lambda c: -c['votes'])[:1]]
            if winners:
                result += table('Original Electoral Commission winner records',
                                ['Electorate', 'Candidate', 'Party', 'Votes'], winners,
                                source='source-baseline-2023')
        if stem == 'candidates':
            result += candidate_records(envs)
        result += '</section>'
    return result
