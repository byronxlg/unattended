# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Render six offline pages, validating everything before replacing product output."""
import argparse
from datetime import datetime, timedelta
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
from product.nz_election.pipeline import export
from product.nz_election.pipeline.allocator import allocate
from product.nz_election.pipeline.average import display, select_window, threshold_watch
from product.nz_election.pipeline.fixtures import golden
from product.nz_election.pipeline.refresh import PRODUCT, config, source_entries, code_sha, utc_now
from product.nz_election.pipeline.storage import replace_directory

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
    dt = datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(ZoneInfo('Pacific/Auckland'))
    return f"{dt.hour % 12 or 12}:{dt.minute:02d} {'am' if dt.hour < 12 else 'pm'}, {dt:%A} {dt.day} {dt:%B %Y %Z}"


def table(caption, headings, records, css='', source=None):
    description = f' aria-describedby="{source}"' if source else ''
    return (f'<div class="scroll {css}" tabindex="0" role="region" aria-label="{escape(caption)}">'
            f'<table{description}><caption>{escape(caption)}</caption><thead><tr>' +
            ''.join(f'<th scope="col">{escape(h)}</th>' for h in headings) + '</tr></thead><tbody>' +
            ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>' for row in records) + '</tbody></table></div>')


def source_note(env=None, identity='source-polls', inputs='polls.json'):
    sources = env['source'] if env else source_entries()[0]
    p = next(s for s in sources if s['id'] == 'P')
    run = env['run_url'] if env else None
    producing = link(run, 'Producing run') if run and safe_url(run) else 'Offline verification; no producing Action run.' if run else 'No poll data run yet.'
    return render('source-note', id=identity, revision=safe_url(p['url']) or '#', history=safe_url(p['history_url']) or '#',
                  inputs=PREFIX + (inputs if inputs == 'validation-2023.json' else 'data/' + inputs), prefix=PREFIX, run=producing)


def label(p):
    return config('party-colours').get(p, {}).get('label', 'Others' if p == 'others' else p)


def strip(seats):
    colours = config('party-colours')
    ordered = sorted(((p, n) for p, n in seats['seats'].items() if n), key=lambda item: (-item[1], item[0]))
    total = seats['assumed_house']
    segments, lanes, records = [], [], []
    position = 1
    for p, n in ordered:
        base = min(n, seats['entitlements'][p])
        extra = n - base
        colour = colours.get(p, {}).get('colour', '#595959')
        width = Decimal(base) * 100 / total
        small = ' small' if base < 8 else ''
        segments.append(f'<div class="segment{small}" style="width:{width}%;background:{colour}"><span class="seat-label">{escape(label(p))}<strong>{n}</strong></span></div>')
        lanes.append(f'<div class="lane{small}" style="--party:{colour}"><span>{escape(label(p))}</span><strong>{n}</strong><span class="anchor">Base seats {position}-{position + base - 1}</span></div>')
        position += base
        records.append([escape(label(p)), str(base), str(extra), str(n)])
    if seats['overhang']:
        width = Decimal(seats['overhang']) * 100 / total
        segments.append(f'<div class="segment overhang small" style="width:{width}%"><span class="seat-label">Extra<strong>{seats["overhang"]}</strong></span></div>')
    marker = Decimal(seats['assumed_majority']) * 100 / total
    return ('<figure class="seat-figure" aria-describedby="source-seats"><div class="strip" role="img" '
            'aria-label="Theoretical party seats, detailed in the following table">' + ''.join(segments) +
            f'<span class="majority" style="left:{marker}%"></span></div><div class="lanes">' + ''.join(lanes) +
            '</div><figcaption class="strip-note">120-seat base; appended extra seats are overhang. '
            f'{seats["overhang"]} overhang seats. Counts assume sufficient list candidates.</figcaption></figure>' +
            f'<p>Seats needed for a majority: <strong>{seats["assumed_majority"]}</strong>, assuming sufficient list candidates '
            f'in a House of {total}.</p>' +
            table('Theoretical seats and overhang', ['Party', 'Base seats', 'Overhang', 'Seats'], records, source='source-seats'))


def polls_page(envs, built):
    if 'polls' not in envs:
        return render('polls', state='<div class="state"><p><strong>No data yet.</strong> This page will show the national poll average, '
                      'the seats it would give each party, and parties near the 5% threshold. The first validated data run is expected '
                      'by 19 October 2026, after the hourly refresh is connected. Until then, read the method and official 2023 example.</p></div>',
                      picture='', source='', details=f'<p><a href="{PREFIX}methods/">Read the method and 2023 example</a></p>')
    polls, average, seats = envs['polls']['data'], envs['averages']['data'][-1], envs['seats']['data']
    status = next(s for s in envs['status']['data'] if s['dataset'] == 'polls')
    acquisition = datetime.fromisoformat(envs['polls']['fetched_at'].replace('Z', '+00:00'))
    stale = status['state'] != 'fresh' or datetime.fromisoformat(built.replace('Z', '+00:00')) - acquisition > timedelta(hours=3)
    offline = envs['polls']['run_url'] == 'offline-verification'
    state = '<div class="state"><p>Offline verification from captured sources. Not live data.</p>' if offline else '<div class="state">'
    if stale:
        state += '<p>Update overdue. These are retained observations, not a current seat picture. Check the source revision and return after the next validated refresh.</p>'
    last = datetime.fromisoformat(max(p['fieldwork_end'] for p in polls))
    state += f'<p>Last poll ended {last.day} {last:%B}. Updated {escape(local_time(envs["polls"]["fetched_at"]))}.</p></div>'
    if seats['available'] and (offline or not stale):
        picture = strip(seats)
    else:
        reason = seats['reason'] or 'Current seats withheld until a fresh acquisition.'
        picture = f'<p>{escape(reason)} <a href="{PREFIX}methods/">How missing coverage affects seats</a></p>'
    details = '<div class="grid"><section><h2>Average party vote</h2>'
    details += f'<p>Window: {average["window_start"]} to {average["window_end"]}. Equal weight for {len(average["poll_ids"])} polls.</p>'
    details += table('Descriptive shares and coverage', ['Party', 'Share', 'Polls'],
                     [[escape(label(p)), display(d['value'], d['scale']), str(len(d['poll_ids']))]
                      for p, d in average['descriptive'].items()], source='source-average')
    if average['missing']:
        details += '<p>Missing observations:</p><ul>' + ''.join(f'<li>{escape(m["poll_id"])}: {escape(label(m["party_id"]))}</li>' for m in average['missing']) + '</ul>'
    if average['exclusions']:
        details += '<ul>' + ''.join(f'<li>{escape(e["poll_id"])}: {escape(e["reason"])}</li>' for e in average['exclusions']) + '</ul>'
    details += source_note(envs['averages'], 'source-average', 'averages.json')
    details += '</section><section><h2>Threshold watch</h2><p class="threshold-rule">5% of the party vote qualifies a party with a list. An electorate win can also qualify it below 5%.</p>'
    watch = threshold_watch(select_window(polls, average['date']), average, seats['assumptions'])
    details += table('Parties near the threshold', ['Party', 'Share', 'Below 5%'],
                     [[escape(label(row['party_id'])), display(row['value'], row['scale']),
                       'Electorate assumed' if row['electorate_qualifies'] else 'Needs 5%'] for row in watch], source='source-thresholds')
    for row in watch:
        if row['missing_poll_ids']:
            details += f'<p>{escape(label(row["party_id"]))}: missing in {len(row["missing_poll_ids"])} window polls.</p>'
    details += '<p>2023 electorate seats assumed; 2026 has different boundaries. List capacity not checked.</p>'
    details += source_note(envs['seats'], 'source-thresholds', 'seats.json') + '</section></div>'
    parties = list(config('party-map')['headers'].values())
    history = []
    for poll in sorted(polls, key=lambda p: (p['fieldwork_end'], p['id']), reverse=True):
        refs = ' '.join(link(url, 'Original report') for url in poll['reference_urls'])
        history.append([f'<span id="{escape(poll["id"])}">{escape(poll["pollster"])}</span>',
                        escape(poll['fieldwork_start'] + ' to ' + poll['fieldwork_end']),
                        'Not reported' if poll['sample'] is None else str(poll['sample']),
                        *[display(poll['shares'].get(p), poll['scale']) for p in parties], refs])
    details += '<h2>Poll history</h2>' + table('All national 2026 observations in the source revision; scroll for all parties',
                                            ['Pollster', 'Fieldwork', 'Sample'] + [label(p) for p in parties] + ['Reports'], history, source='source-history')
    details += source_note(envs['polls'], 'source-history', 'polls.json')
    details += f'<p><a href="{PREFIX}data/averages.json">Daily average series and exact inputs</a></p>'
    return render('polls', state=state, picture=picture,
                  source=source_note(envs['seats'], 'source-seats', 'seats.json'), details=details)


def methods_page(stage, built, sha, run_url):
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
                          inputs={e['path']: e['sha256'] for e in json.loads((PRODUCT / 'fixtures/manifest.json').read_text())['entries'] if e['path'].startswith('ec-')},
                          method='official-2023-validation-v1', generated=built)
    (stage / 'validation-2023.json').write_text(export.canonical(env) + '\n')
    (stage / 'validation-2023.csv').write_bytes(export.csv_bytes(env))
    return render('methods', votes=f'{sum(official["input"]["partyVotes"].values()):,}',
                  table=table('Official 2023 entitlement and occupied seats', ['Party', 'Votes', 'Entitlement', 'Electorates', 'Seats'], records, source='source-polls'),
                  prefix=PREFIX, source=source_note(inputs='validation-2023.json'))


def downloads(envs, data_sha):
    catalogue = '<p>No poll downloads yet. The first validated data run is expected by 19 October 2026.</p>'
    if envs:
        records = []
        for entry in envs['manifest']['data']:
            name = entry['path']
            immutable = ''
            if data_sha:
                immutable = link(f'https://raw.githubusercontent.com/byronxlg/unattended/{data_sha}/product/nz_election/data/{name}', 'Pinned copy')
            records.append([f'<a href="{PREFIX}data/{escape(name)}">{escape(name)}</a>',
                            escape(', '.join(entry['licences'])), str(entry['row_count']),
                            escape(entry['fetched_at'] or 'Not acquired'), immutable])
        catalogue = table('Published data inventory', ['File', 'Licence', 'Rows', 'Acquired (UTC)', 'Immutable download'], records, 'downloads')
        catalogue += f'<p><a href="{PREFIX}data/LICENCES.md">Licences and CSV format</a></p>'
    catalogue += f'<p><a href="{PREFIX}validation-2023.json">Official 2023 normalized validation (JSON)</a> <a href="{PREFIX}validation-2023.csv">Validation (CSV)</a></p>'
    return render('downloads', catalogue=catalogue, prefix=PREFIX,
                  source=source_note(envs.get('polls'), inputs='polls.json' if 'polls' in envs else 'validation-2023.json'))


def build(data, out, *, built=None, data_sha=None, sha=None, run_url=None):
    data, out = Path(data), Path(out).absolute()
    if out.name == 'site' or out.is_symlink() or PRODUCT.is_relative_to(out.resolve()) or out.resolve().is_relative_to(PRODUCT):
        raise ValueError('UNSAFE_OUTPUT_PATH')
    out = out.parent.resolve() / out.name
    if data_sha and not re.fullmatch('[0-9a-f]{40}', data_sha):
        raise ValueError('INVALID_DATA_SHA')
    envs = export.validate_bundle(data) if data.exists() else {}
    built, sha = built or utc_now(), sha or code_sha()
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
        methods = methods_page(stage, built, sha, run_url)
        manifest = export.envelope(dict(id='build', source_ref=[], observed_at=built, code_sha=sha,
                         data_sha=data_sha if envs else None, build_run_url=run_url, built_at=built,
                         data_available='polls' in envs), [], run_url, sha)
        export.pair(stage, 'build-manifest', manifest)
        descriptions = {
            'electorates/': 'This page will help you find your electorate and candidates using the 2025 boundaries. The directory and maps are planned for 26 October; no electorate forecast is available yet.',
            'night/': 'This page will show the count on election night, with replay practice planned for 1 November. There are no live results here yet; polling day is 7 November 2026.',
            'campaign/': 'This page will bring together advance voting and disclosed donations, with source dates and limits. It is planned for 1 November; no campaign totals are available here yet.'}
        routes = config('routes')
        if len(routes) != 6 or {r['path'] for r in routes} != {'', 'electorates/', 'night/', 'campaign/', 'downloads/', 'methods/'}:
            raise ValueError('INVALID_ROUTES')
        for route in routes:
            slug = route['path']
            nav = ''.join(f'<a href="{PREFIX + r["path"]}"' + (' aria-current="page"' if r == route else '') +
                          f'>{escape(r["label"])}</a>' for r in routes)
            if slug == '':
                body = polls_page(envs, built)
            elif slug == 'methods/':
                body = methods
            elif slug == 'downloads/':
                body = downloads(envs, data_sha)
            else:
                body = render('placeholder', description=descriptions[slug])
            target = stage / slug
            target.mkdir(exist_ok=True)
            (target / 'index.html').write_text(render('base', title=route['label'], prefix=PREFIX, nav=nav, body=body,
                                                    built='Page built ' + escape(local_time(built)) + '. Age labels are checked at build time.'))
        shutil.copyfile(PRODUCT / 'web/styles.css', stage / 'styles.css')
        shutil.copyfile(PRODUCT / 'web/allocator.mjs', stage / 'allocator.mjs')
        replace_directory(stage, out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--data-sha')
    args = parser.parse_args()
    build(args.data, args.out, data_sha=args.data_sha)
    print('PASS build: 6 routes')


if __name__ == '__main__':
    main()
