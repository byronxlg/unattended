"""Task-ordered voting guidance from the reviewed Electoral Commission snapshot."""
from datetime import date, datetime, timezone
from html import escape
from .sunsets import post_election
from zoneinfo import ZoneInfo

from .snapshots import load_voting


def advance_open(records, today):
    start, end = records.get('advance-opens', {}).get('date'), records.get('election-day', {}).get('date')
    last = records.get('advance-closes', {}).get('date') or end
    return bool(start and last and date.fromisoformat(start) <= today <= date.fromisoformat(last))


def page(built, rows=None, envs=None):
    from .build import PREFIX, link, compact_time, local_time
    rows = load_voting() if rows is None else rows
    records = {row['id']: row for row in rows}
    now = datetime.fromisoformat(built.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland'))
    today = now.date()
    close = records.get('enrolment-closes', {})
    enrolment_closed = (now >= datetime.fromisoformat(close['at']) if close.get('at') else
                        bool(close.get('date') and today > date.fromisoformat(close['date'])))

    def summary(key):
        if key == 'enrolment-closes' and enrolment_closed:
            return 'The enrolment close has passed.'
        return records[key]['summary']

    def action(key, label):
        row = records.get(key, {})
        return link(row['url'], label) if row.get('url') else ''

    def sentence(key):
        row = records.get(key, {})
        return '<p>' + escape(summary(key)) + '</p>' if row.get('date') else ''

    def section(identity, title, body, source=''):
        from .home import section as module
        return module(identity, title, '', body, 'Electoral Commission', '', prose=True, source=source)

    def date_source(identity, keys):
        dates = [records[key]['retrieved_at'] for key in keys
                 if records.get(key, {}).get('date') and records[key].get('source_url')]
        return (f'<p class="home-footnote" id="{identity}">Source: Electoral Commission. Retrieved '
                + escape(compact_time(max(dates))) + '.</p>') if dates else ''

    if enrolment_closed:
        enrol_action = (link(close['source_url'], 'Electoral Commission enrolment information')
                        if close.get('source_url') else '')
    else:
        enrol_action = action('check-or-update-enrolment', 'Check or update your enrolment')
    enrol = section('enrol', 'Am I enrolled, and is it too late?', sentence('enrolment-closes') + enrol_action)
    from .home_graphics import timeline as key_dates
    election = records.get('election-day', {})
    countdown = ''
    if election.get('date'):
        days = (date.fromisoformat(election['date']) - today).days
        countdown = (f'<p class="countdown" aria-describedby="source-countdown"><strong>{days}</strong> {"day" if days == 1 else "days"} to election day</p>' if days > 0
                     else '<p class="countdown" aria-describedby="source-countdown"><strong>Today</strong> is election day. Voting closes at 7pm.</p>' if days == 0 else '')
    dates = key_dates(records, today)
    timeline_source = date_source('source-timeline', ('overseas-opens', 'enrolment-closes', 'advance-opens',
                                                    'advance-closes', 'election-day'))
    graphic = (f'<div class="vote-dates"><figure aria-describedby="source-timeline">{dates}</figure>'
               f'<div class="module-foot">{timeline_source}</div></div>') if dates else ''
    finder = action('find-where-to-vote', 'Find a voting place near you')
    button = finder.replace('<a ', '<a class="button big" ', 1) if finder else ''
    lede = ''
    if advance_open(records, today):
        until = records.get('advance-closes', {}).get('date')
        lede = ('<p class="vote-lede">Advance voting is open' + (f' until {date.fromisoformat(until):%-d %B}' if until else '')
                + '. You can vote at any voting place in the country.</p>')
    places_body = lede + button + countdown
    if not places_body and graphic:
        # A date-only answer still belongs under the where-and-when question.
        places_body, graphic = graphic, ''
    places = section('places', 'Where can I vote, and when?', places_body,
                     date_source('source-countdown', ('election-day',)) if countdown else '')
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
                deadlines += '<p class="dek">' + escape(summary(identity)) + ' Deadline: ' + escape(local_time(datetime.fromisoformat(row['at']).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'))) + ' (New Zealand time).</p>'
        help_body += '<div class="vote-help"><h3>' + anchor + '</h3><div><p>' + escape(records[key]['summary']) + '</p>' + deadlines + '</div></div>'
    help_section = section('help', 'Overseas or need help voting?', sentence('overseas-opens') + ('<div class="help-grid">' + help_body + '</div>' if help_body else ''))
    compare = section('compare', 'Where can I compare candidates and policies?',
                      f'<p><a href="{PREFIX}electorates/">Find your electorate and candidates</a></p>'
                      '<p><a href="https://policy.nz/2026">Compare policies at Policy.nz</a></p>')
    if post_election(built):
        first = section('places', 'Where can I find election results?',
                        f'<p>Voting closed on 7 November.</p><p><a href="{PREFIX}night/">Election results</a></p>')
        from .result_sources import official_results_notice
        notice = official_results_notice(built, (envs or {}).get('night/live/current', {}).get('data', []))
        basics = section('two-votes', 'Official results', '<p>' + notice + '</p>'
                         '<p><a href="https://www.electionresults.govt.nz/">Electoral Commission results</a></p>')
        help_section = ''
        graphic = ''
    sources = {r['source_url']: r for r in rows if r.get('source_url')}
    source = ('<div class="source-note" id="source-vote"><p>Source: Electoral Commission. Copyright Electoral Commission; '
              'no open licence stated. Independent summaries. Retrieved ' +
              escape(compact_time(max(r['retrieved_at'] for r in rows))) + '.</p><p class="source-actions">' +
              link('https://vote.nz/', 'vote.nz') + f'<a href="{PREFIX}methods/#vote-sources">All {len(sources)} pages used</a>' + '</p></div>') if rows else ''
    content = '<div class="vote-first">' + first + basics + '</div>' + graphic + help_section + compare
    # With sparse records, the first answer can be guidance, help or comparison.
    content = content.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1).replace('class="module"', 'class="hero vote-hero"', 1)
    return '<div class="vote-page">' + content + source + '</div>'


def sources_section(rows=None):
    """Every Electoral Commission page the vote summaries come from, kept on Methods."""
    from .build import link
    rows = load_voting() if rows is None else rows
    seen = {}
    for r in rows:
        if r.get('source_url'):
            seen.setdefault(r['source_url'], r['summary'])
    items = ''.join(f'<li>{link(url, url.removeprefix("https://"))}</li>' for url in seen)
    return f'<section id="vote-sources"><h2>Voting guidance sources</h2><p>Electoral Commission pages summarised on Vote. Copyright Electoral Commission; no open licence stated.</p><ul>{items}</ul></section>' if items else ''
