"""Static electorate detail presentation, including explicit missing-data states."""
from .presentation import overdue
from decimal import Decimal
from html import escape
from . import geography
from .build import PREFIX, render, link, table, observation_label, local_time, compact_time


def source(envs, stem, built=None):
    env = envs.get(stem)
    if not env:
        return f'<p class="source-note" id="source-{stem}">Not available: no validated data bundle.</p>'
    result = '<div role="note" class="source-note" id="source-' + stem + '"><p>From ' + ('Stats NZ' if stem == 'electorates' else 'Wikipedia contributors' if stem == 'electorate-polls' else 'Electoral Commission') + f'. <a href="{PREFIX}downloads/">Downloads and provenance</a>.</p><details><summary>Sources and dates</summary>'
    if env.get('fetched_at'):
        value = env['fetched_at']
        result = result.replace('</p><details>', f' Retrieved <time datetime="{value}">{compact_time(value)}</time>.</p><details>', 1)
    for s in env['source']:
        result += '<p>From ' + link(s['url'], 'Stats NZ' if stem == 'electorates' else 'Wikipedia contributors' if stem == 'electorate-polls' else 'Electoral Commission') + ' ' + escape(s['licence']) + ' Retrieved ' + f'<time datetime="{s["fetched_at"]}">{escape(local_time(s["fetched_at"]))}</time>' + '.</p>'
        if s['history_url']:
            result += link(s['history_url'], 'Contributor history')
    result += f'<p><a href="{PREFIX}data/{stem}.json">Download data and field sources</a></p>'
    result += '<p>' + (link(env['run_url'], 'Producing run') if env['run_url'] != 'offline-verification' else 'Offline verification from captured sources. Not live data.') + '</p>'
    family = 'geography' if stem == 'electorates' else stem
    status = next((s for s in envs.get('status', {}).get('data', []) if s['dataset'] == family), None)
    if status and (status['state'] != 'fresh' or (built and status['last_success_at'] and
            overdue(status['last_success_at'], built, 'daily'))):
        band = f'<p class="state">Update overdue. Last checked {compact_time(status["last_success_at"])}. Showing previous data. <a href="{PREFIX}downloads/">Update details</a>.</p>'
        if status.get('error_code'):
            band = f'<p class="state">The {compact_time(status["last_attempt_at"])} update failed; showing previous data from {compact_time(status["last_success_at"])}. <a href="{PREFIX}downloads/">Update details</a>.</p>'
        result = result.replace('<details>', band + '<details>', 1)
    return result + '</details></div>'


def detail(row, envs, built=None):
    def data(stem):
        return envs.get(stem, {}).get('data', [])
    official = [c for c in data('candidates') if c['electorate_id'] == row['id']]
    candidates = '<ul class="candidate-list">'
    reviews = {c['id']: c for c in data('candidate-review')}
    for c in official:
        candidates += '<li><strong>' + escape(c['name']) + '</strong><p>' + escape(c['party_id']) + '</p>'
        candidates += '<small aria-describedby="source-candidates">List rank: ' + (str(c['list_rank']) if c['list_rank'] is not None else 'Not available') + '. ' + escape(c['join_status']) + '.</small>'
        candidates += '<small>Wikipedia: ' + (link(c['wikipedia_url'], 'Candidate article') if c['wikipedia_url'] else 'Not available') + '. Wikidata: ' + escape(c['wikidata_id'] or 'Not available') + '.</small>'
        candidates += '<details><summary>Candidate sources</summary>'
        for field in ('name', 'party_id'):
            for ref in c['field_sources'][field]:
                src = next(s for s in envs['candidates']['source'] if s['id'] == ref['source_id'])
                candidates += '<p>' + link(src['url'], 'Electoral Commission') + ': ' + escape(ref['locator']) + ' (' + escape(field) + ')</p>'
        for identity in c['conflict_ids']:
            conflict = reviews[identity]
            candidates += '<p>Unresolved: ' + escape(conflict['field']) + '</p><ul>'
            for claim in conflict['claims']:
                candidates += '<li>' + escape(str(claim['value'])) + ': ' + escape(claim['source_id'] + ' / ' + claim['locator']) + '</li>'
            candidates += '</ul>'
        candidates += '</details></li>'
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
            baseline += '<details class="missing"><summary>No 2023 candidate results for this electorate</summary><p>No candidate baseline. ' + escape(old['field_sources']['candidate_status']) + '</p></details>'
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
    for poll in data('electorate-polls'):
        if poll['electorate_id'] != row['id']:
            continue
        polls += '<section class="local-poll"><h3>' + escape(poll['pollster']) + ': ' + ('Party vote' if poll['measure'] == 'party_vote' else 'Candidate vote') + '</h3>'
        polls += '<p aria-describedby="source-electorate-polls">Fieldwork: ' + escape(poll['boundary_basis']['fieldwork_label']) + '. Sample: ' + str(poll['sample'] or 'Not reported') + '.</p>'
        polls += table('Reported local shares', ['Party or candidate', 'Share'],
                       [[escape(name), ('Not reported' if share['value'] is None else ('About ' if share['approximate'] else '') + str(Decimal(share['value']) / poll['scale']) + '%')]
                        for name, share in poll['shares'].items()], source='source-electorate-polls')
        polls += '<p>' + escape(poll['boundary_basis']['basis']) + '.</p>'
        polls += ' '.join(link(url, 'Original report') for url in poll['reference_urls']) + '</section>'
    if not polls:
        polls = '<p>No mapped local polls in the captured source. This is not a forecast.</p>'
    collections = {k: envs[k + '-2025'] for k in geography.KINDS if k + '-2025' in envs}
    return render('electorate', prefix=PREFIX, boundary=escape(row['boundary_note']),
                  outline=geography.svg(collections, [row], row['id']).replace('<svg ', '<svg aria-describedby="source-electorates" '), geography_source=source(envs, 'electorates', built),
                  candidates=candidates, candidate_source=source(envs, 'candidates', built),
                  baseline=baseline, baseline_source=source(envs, 'baseline-2023', built),
                  enrolment=enrolment, enrolment_source=source(envs, 'enrolment', built),
                  polls=polls, poll_source=source(envs, 'electorate-polls', built))
