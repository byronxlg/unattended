"""Task-ordered voting guidance from the reviewed Electoral Commission snapshot."""
from datetime import date, datetime, timezone
from html import escape
from .sunsets import post_election
from zoneinfo import ZoneInfo

from .snapshots import load_voting


def page(built, rows=None):
    from .build import PREFIX, link, compact_time, local_time
    rows = load_voting() if rows is None else rows
    records = {row['id']: row for row in rows}
    today = datetime.fromisoformat(built.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland')).date()

    def action(key, label):
        row = records.get(key, {})
        return link(row['url'], label) if row.get('url') else ''

    def sentence(key):
        row = records.get(key, {})
        return '<p>' + escape(row['summary']) + '</p>' if row.get('date') else ''

    def section(identity, title, body):
        return f'<section id="{identity}"><h2>{title}</h2>{body}</section>' if body else ''

    enrol = section('enrol', 'Am I enrolled, and is it too late?',
                    sentence('enrolment-closes') + action('check-or-update-enrolment', 'Check or update your enrolment'))
    timeline = []
    for key, label in [('enrolment-closes', 'Enrol by'), ('advance-opens', 'Advance voting'), ('election-day', 'Election day')]:
        row = records.get(key, {})
        if row.get('date'):
            day = date.fromisoformat(row['date'])
            timeline.append(f'<li><time datetime="{day}">{day.day} {day:%b}</time><span>{label}</span></li>')
    election = records.get('election-day', {})
    countdown = ''
    if election.get('date'):
        days = (date.fromisoformat(election['date']) - today).days
        countdown = (f'<strong>{days}</strong> {"day" if days == 1 else "days"} until election day' if days > 0
                     else 'Election day' if days == 0 else 'Election day has passed')
    graphic = ('<figure class="vote-dates" aria-describedby="source-vote"><figcaption>' + countdown +
               '</figcaption><ol>' + ''.join(timeline) + '</ol></figure>') if timeline or countdown else ''
    places = section('places', 'Where can I vote, and when?',
                     action('find-where-to-vote', 'Use the official finder for places and opening hours') + graphic)
    bring = '<p>' + escape(records['what-to-bring']['summary']) + '</p>' if records.get('what-to-bring') else ''
    votes = '<p>' + escape(records['two-votes']['summary']) + '</p>' if records.get('two-votes') else ''
    guidance = action('two-votes', 'Official voting guidance') or action('what-to-bring', 'Official voting guidance')
    basics = section('two-votes', 'What do I bring? How do I vote?', bring + votes + guidance)
    advance = records.get('advance-opens', {}).get('date')
    first = places + enrol if advance and today >= date.fromisoformat(advance) else enrol + places
    help_body = ''
    for key, label in [('overseas-voting', 'Vote overseas'), ('accessible-formats', 'Accessible formats'),
                       ('assisted-voting', 'Help marking your vote'), ('takeaway-voting', 'Someone can collect your papers'),
                       ('telephone-dictation', 'Telephone dictation')]:
        anchor = action(key, label)
        if not anchor:
            continue
        deadlines = ''
        for identity in records[key].get('deadline_ids', []):
            row = records.get(identity, {})
            if row.get('date') and row.get('at'):
                deadlines += '<p>' + escape(row['summary']) + ' Deadline: ' + escape(local_time(datetime.fromisoformat(row['at']).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'))) + ' (New Zealand time).</p>'
        help_body += '<div class="vote-help"><h3>' + anchor + '</h3><p>' + escape(records[key]['summary']) + '</p>' + deadlines + '</div>'
    help_section = section('help', 'Overseas or need help voting?', sentence('overseas-opens') + help_body)
    compare = section('compare', 'Where can I compare candidates and policies?',
                      f'<p><a href="{PREFIX}electorates/">Find your electorate and candidates</a></p>'
                      '<p><a href="https://policy.nz/2026">Compare policies at Policy.nz</a></p>')
    if post_election(built):
        first = section('places', 'Where can I find election results?',
                        f'<p>Voting closed on 7 November.</p><p><a href="{PREFIX}night/">Election results</a></p>')
        basics = section('two-votes', 'When are official results due?', '<p>Official results due 27 November 2026.</p>')
        help_section = ''
    sources = {r['source_url']: r for r in rows if r.get('source_url')}
    source = ('<div class="source-note" id="source-vote"><p>Source: Electoral Commission. Copyright Electoral Commission; '
              'no open licence stated. Independent summaries. Retrieved ' +
              escape(compact_time(max(r['retrieved_at'] for r in rows))) + '.</p><p class="source-actions">' +
              ''.join(link(url, 'Electoral Commission guidance') for url in sources) + '</p></div>') if rows else ''
    return '<div class="vote-page"><div class="vote-first">' + first.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1) + basics + '</div>' + help_section + compare + source + '</div>'
