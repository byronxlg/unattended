"""Electorate answers in the accepted page order; absent facts omit their blocks."""
from .presentation import overdue
from decimal import Decimal
from datetime import datetime, timezone
from html import escape
from urllib.parse import urlsplit
from .build import PREFIX, link, table, compact_time


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
        band = f'<div class="state"><p>Update overdue. Last checked {compact_time(status["last_success_at"])}. Showing previous data.</p><p class="source-actions"><a href="{PREFIX}downloads/">Update details</a></p></div>'
        if status.get('error_code'):
            band = f'<div class="state"><p>The {compact_time(status["last_attempt_at"])} update failed; showing previous data from {compact_time(status["last_success_at"])}.</p><p class="source-actions"><a href="{PREFIX}downloads/">Update details</a></p></div>'
        result = result.replace('<div>', band + '<div>', 1)
    return result + '</div></div>'


def candidate_cards(row):
    from .snapshot_views import load
    from .home_charts import colour
    reconciliation = next(r for r in load('candidate-reconciliation-2026') if r['electorate_id'] == row['id'])
    originals = {(c['name'], c['party']): c for c in load('candidates-2026') if c['electorate_slug'] == row['slug']}
    parties = {'National Party': 'nat', 'Labour Party': 'lab', 'Green Party': 'grn',
               'ACT New Zealand': 'act', 'New Zealand First Party': 'nzf',
               'Te Pāti Māori': 'tpm', 'Opportunity Party': 'opp'}
    cards = ''
    for c in reconciliation['matched'] + reconciliation['added_by_ec']:
        # The reconciliation explicitly records the source identity; no fuzzy name join.
        original = originals.get((c['snapshot_name'], c['snapshot_party']), {})
        cards += (f'<li style="--party:{colour(parties.get(c["party"]))}"><strong>' + escape(c['ec_name'])
                  + '</strong><p>' + escape(c['party']) + '</p><p>'
                  + (f'List {c["list_rank"]}' if 'list_rank' in c else '')
                  + (' <span class="incumbent">Incumbent</span>' if original.get('sitting_electorate_mp') else '') + '</p></li>')
    return ('<section class="race-candidates"><h2 id="candidates-title">Standing in 2026</h2>'
            '<ul class="race-cards" aria-describedby="source-candidates-2026">' + cards + '</ul></section>') if cards else ''


def policy_link(row):
    from .snapshot_views import load
    entry = next((r for r in load('policy-links') if r.get('electorate_slug') == row['slug']), None)
    return ('<p class="electorate-policy">' + link(entry['url'], 'Compare these candidates at Policy.nz') + '</p>') if entry else ''


def previous_result(row, envs, built):
    from .snapshot_views import load, footnote
    from .home_charts import colour
    if row['slug'] == 'port-waikato':
        votes, name, note = load('port-waikato-2023'), row['name'], footnote('port-waikato')
        source_id = 'source-port-waikato'
    else:
        old = next((r for r in envs.get('baseline-2023', {}).get('data', [])
                    if row['baseline_ids'] and r['old_electorate_id'] == row['baseline_ids'][0]), None)
        if not old:
            return ''
        votes, name, note = old.get('candidate_votes'), old['old_name'], source(envs, 'baseline-2023', built)
        source_id = 'source-baseline-2023'
    if not votes or len(votes) < 2 or not sum(v['votes'] for v in votes):
        return ''
    ranked = sorted(votes, key=lambda v: -v['votes'])
    margin = ranked[0]['votes'] - ranked[1]['votes']
    total = sum(v['votes'] for v in votes)
    aliases = {'National Party': 'nat', 'Labour Party': 'lab', 'Green Party': 'grn',
               'ACT New Zealand': 'act', 'Te Pāti Māori': 'tpm', 'New Zealand First Party': 'nzf'}
    content = '<section class="original-results"><h2>Who won last time?</h2><p>' + escape(name) + ' (2023)'
    content += (' by-election' if row['slug'] == 'port-waikato' else '') + '</p>'
    if row['mapping_status'] != 'unchanged':
        content += '<p>2023 boundaries. These votes have not been moved or added together to fit the 2025 boundaries.</p>'
    content += '<p class="local-margin">' + (escape(ranked[0]['name']) + f' won by <strong>{margin:,}</strong> votes.' if margin else 'Tied on votes; no sole winner.') + '</p>'
    content += f'<figure class="result-bars" aria-describedby="{source_id}">'
    for v in ranked:
        share = Decimal(v['votes']) * 100 / total
        content += ('<div class="result-bar"><p><strong>' + escape(v['name']) + '</strong> ' + escape(v['party'])
                    + f' <span>{share:.1f}% ({v["votes"]:,} votes)</span></p>'
                    + f'<div style="width:{share:.4f}%;background:{colour(v.get("party_id") or aliases.get(v["party"]))}"></div></div>')
    return content + '<figcaption>Share of valid candidate votes.</figcaption></figure>' + note + '</section>'


def night_result(row, envs, built):
    # Only the current live family can answer "now", never an archive or replay.
    if built and datetime.fromisoformat(built) < datetime(2026, 11, 7, 6, tzinfo=timezone.utc):
        return ''
    seq = next((s for s in envs.get('night/index', {}).get('data', []) if s['id'] == 'live'), None)
    if not seq:
        return ''
    result = envs[seq['snapshot_paths'][-1][:-5]]['data'][0]
    refs = envs[seq['reference_path'][:-5]]['data'][0]
    identity = next((k for k, r in refs['electorates'].items() if r['electorate_name'] == row['name']), None)
    item = result.get('leaders', {}).get(identity, {})
    if item.get('status') not in {'provisional', 'final'}:
        return ''
    leader = refs['candidates'].get(item.get('leader'))
    tied = item.get('tied_candidates', [])
    if not leader and not tied:
        return ''
    name = leader['candidate_name'] if leader else 'Tied: ' + ', '.join(refs['candidates'][c]['candidate_name'] for c in tied)
    status = 'Final source count; leader provisional' if item['status'] == 'final' else 'Provisional leader'
    stats = item.get('statistics')
    if stats:
        status += f'; {stats["total_voting_places_counted"]} of {stats["total_voting_places"]} voting places counted'
    content = '<section class="electorate-night"><h2>Who is leading here now?</h2><p><strong>' + escape(name) + '</strong></p>'
    if item.get('margin') is not None:
        content += f'<p>Margin: {item["margin"]:,} votes</p>'
    content += '<p>' + escape(status) + '</p>'
    if result.get('source_updated_local'):
        content += '<p>Source updated ' + escape(result['source_updated_local']) + ' (source local time).</p>'
    return content + f'<div class="source-note" id="source-electorate-night"><p class="source-actions"><a href="{PREFIX}methods/#records-electorate-night">Sources and method</a></p></div></section>'


def detail(row, envs, built=None):
    from .snapshot_views import footnote
    from .electorate_locator import locator
    content = '<div class="electorate-page">' + night_result(row, envs, built) + candidate_cards(row)
    content += ('<p class="enrolled-electorate">' + link('https://vote.nz/', 'Check your enrolled electorate at vote.nz') + '</p>'
                '<figure class="locator-card" aria-describedby="source-boundaries-2025">' + locator(row)
                + '<figcaption>2025 locator, not a legal boundary. Stats NZ, CC BY 4.0.</figcaption></figure>')
    content += policy_link(row)
    content += footnote('candidates-2026', '20 October 2026') + footnote('boundaries-2025', '20 October 2026')
    content += previous_result(row, envs, built)
    # Preserve inbound provenance fragments without displaying empty modules.
    for stem in ['electorates', 'candidates', 'baseline-2023', 'enrolment', 'electorate-polls']:
        if f'id="source-{stem}"' not in content:
            content += f'<span id="source-{stem}"></span>'
    return content + '</div>'


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
    result = '<section id="records-electorate-night"><h2>Current electorate counts</h2><p>Only the current live night family supplies the promoted electorate result. Archive and illustrative counts are excluded. Leaders remain provisional; voting-place coverage is not turnout.</p>'
    for seq in envs.get('night/index', {}).get('data', []):
        if seq['id'] == 'live':
            for path in seq['snapshot_paths']:
                for entry in envs[path[:-5]]['source']:
                    result += '<p>' + link(entry['url'], publisher(entry)) + '. ' + escape(entry['licence']) + '. Retrieved ' + escape(entry['fetched_at']) + '.</p>'
    result += '</section>'
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
