"""Static electorate detail presentation, including explicit missing-data states."""
from .presentation import overdue
from decimal import Decimal
from html import escape
from . import geography
from urllib.parse import urlsplit
from .build import PREFIX, render, link, table, observation_label, compact_time


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


def source(envs, stem, built=None):
    env = envs.get(stem)
    if not env:
        return f'<div class="source-note" id="source-{stem}"><p>Not available: no validated data bundle.</p><p class="source-actions"><a href="{PREFIX}downloads/">Sources and availability</a></p></div>'
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
    def data(stem):
        return envs.get(stem, {}).get('data', [])
    official = [c for c in data('candidates') if c['electorate_id'] == row['id']]
    official.sort(key=lambda c: (c['party_id'], c['name'], c['id']))
    candidates = '<ul class="candidate-list" aria-describedby="source-candidates">'
    reviews = {c['id']: c for c in data('candidate-review')}
    for c in official:
        candidates += '<li><strong>' + escape(c['name']) + '</strong><p>' + escape(c['party_id']) + '</p>'
        candidates += '<small aria-describedby="source-candidates">List rank: ' + (str(c['list_rank']) if c['list_rank'] is not None else 'Not available') + '. ' + escape(c['join_status']) + '.</small>'
        candidates += '<small>Wikipedia: ' + (link(c['wikipedia_url'], 'Candidate article') if c['wikipedia_url'] else 'Not available') + '. Wikidata: ' + escape(c['wikidata_id'] or 'Not available') + '.</small>'
        candidates += '<div><p><strong>Candidate sources</strong></p>'
        for field in ('name', 'party_id'):
            for ref in c['field_sources'][field]:
                src = next(s for s in envs['candidates']['source'] if s['id'] == ref['source_id'])
                candidates += '<p>' + link(src['url'], publisher(src)) + ': ' + escape(ref['locator']) + ' (' + escape(field) + ')</p>'
        for identity in c['conflict_ids']:
            conflict = reviews[identity]
            candidates += '<p>Unresolved: ' + escape(conflict['field']) + '</p><ul>'
            for claim in conflict['claims']:
                candidates += '<li>' + escape(str(claim['value'])) + ': ' + escape(claim['source_id'] + ' / ' + claim['locator']) + '</li>'
            candidates += '</ul>'
        candidates += '</div></li>'
    candidates += '</ul>'
    if not official:
        candidates = '<p>Official candidates not available for this electorate.</p>'
    baseline = ''
    old_rows = {r['old_electorate_id']: r for r in data('baseline-2023')}
    for identity in row['baseline_ids']:
        old = old_rows.get(identity)
        if not old:
            baseline += '<p>No candidate baseline or party baseline available for original electorate ' + str(identity) + '.</p>'
            continue
        baseline += '<section><h3>' + escape(old['old_name']) + ' (2023)</h3><p aria-describedby="source-baseline-2023">Election: ' + f'<time datetime="{old["election_date"]}">{observation_label(old["election_date"])}</time>' + '. Final results as at ' + f'<time datetime="{old["result_as_of"]}">{observation_label(old["result_as_of"])}</time>' + '.</p>'
        baseline += table(old['old_name'] + ': party votes', ['Party', 'Votes'],
                          [[escape(v['name']), f'{v["votes"]:,}'] for v in old['party_votes']], source='source-baseline-2023')
        if old['candidate_votes'] is None:
            baseline += '<div class="missing"><p><strong>No 2023 candidate results for this electorate</strong></p><p>No candidate baseline. ' + escape(old['field_sources']['candidate_status']) + '</p></div>'
        else:
            baseline += table(old['old_name'] + ': candidate votes', ['Candidate', 'Party', 'Votes'],
                              [[escape(v['name']), escape(v['party']), f'{v["votes"]:,}'] for v in old['candidate_votes']], source='source-baseline-2023')
        baseline += '</section>'
    if not row['baseline_ids'] or row['mapping_status'] == 'unresolved':
        baseline = '<p>Comparison unresolved: no reviewed boundary correspondence.</p>'
    roll = next((r for r in data('enrolment') if r['electorate_id'] == row['id']), None)
    enrolment = '<p>Not available: no dated electorate enrolment observation.</p>'
    if roll:
        enrolment = '<p aria-describedby="source-enrolment">Enrolment at ' + f'<time datetime="{roll["as_of"]}">{escape(observation_label(roll["as_of"]))}</time>' + '.</p><p>' + escape(roll['roll_basis'] or 'Roll basis not available.') + '</p>'
        enrolment += '<p aria-describedby="source-enrolment">Enrolled: ' + (f'{roll["enrolled"]:,}' if roll['enrolled'] is not None else 'Not available') + '. Eligible: ' + (f'{roll["eligible"]:,}' if roll['eligible'] is not None else 'Not available') + '.</p>'
    polls = ''
    poll_captions = {}
    for poll in data('electorate-polls'):
        if poll['electorate_id'] != row['id']:
            continue
        heading = poll['pollster'] + ': ' + ('Party vote' if poll['measure'] == 'party_vote' else 'Candidate vote')
        caption = heading + ', ' + poll['boundary_basis']['fieldwork_label'] + ': reported local shares'
        poll_captions[caption] = poll_captions.get(caption, 0) + 1
        if poll_captions[caption] > 1:
            caption += f' (report {poll_captions[caption]})'
        polls += '<section class="local-poll"><h3>' + escape(heading) + '</h3>'
        polls += '<p aria-describedby="source-electorate-polls">Fieldwork: ' + escape(poll['boundary_basis']['fieldwork_label']) + '. Sample: ' + str(poll['sample'] or 'Not reported') + '.</p>'
        polls += table(caption, ['Party or candidate', 'Share'],
                       [[escape(name), ('Not reported' if share['value'] is None else ('About ' if share['approximate'] else '') + str(Decimal(share['value']) / poll['scale']) + '%')]
                        for name, share in poll['shares'].items()], source='source-electorate-polls')
        polls += '<p>' + escape(poll['boundary_basis']['basis']) + '.</p>'
        polls += ' '.join(link(url, 'Original report') for url in poll['reference_urls']) + '</section>'
    if not polls:
        polls = '<p>No mapped local polls in the captured source. This is not a forecast.</p>'
    collections = {k: envs[k + '-2025'] for k in geography.KINDS if k + '-2025' in envs}
    from .home import electorate_summary
    return render('electorate', historical=escape(electorate_summary(row, envs)[1]), prefix=PREFIX, boundary=escape(row['boundary_note']),
                  outline=geography.svg(collections, [row], row['id']).replace('<svg ', '<svg aria-describedby="source-electorates" '), geography_source=source(envs, 'electorates', built),
                  candidates=candidates, candidate_source=source(envs, 'candidates', built),
                  baseline=baseline, baseline_source=source(envs, 'baseline-2023', built),
                  enrolment=enrolment, enrolment_source=source(envs, 'enrolment', built),
                  polls=polls, poll_source=source(envs, 'electorate-polls', built))
