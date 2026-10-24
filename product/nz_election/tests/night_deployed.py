# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Record real deployed acceptance; only --faults changes clocks or transport."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urljoin, urlsplit

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, night, xml_parser
from product.nz_election.pipeline.fetch import night_xml
from product.nz_election.tests.night_browser import launch_chromium, SIZES

FEED = 'https://media.election.net.nz/xml/'
NATIONAL = ('electorates.xml', 'parties.xml', 'candidates.xml', 'election.xml')


def utc():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def golden(votes, house):
    return type(votes) is int and type(house) is int and votes == 2851211 and house == 122


class Record:
    def __init__(self, mode, base, root=Path('artifacts/nz-election/deployed')):
        self.out = Path(root) / (mode + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        self.out.mkdir(parents=True)
        self.data = dict(mode=mode, origin=origin(base), base_url=base, start_utc=utc(), end_utc=None,
                         browser=None, browser_version=None, code_sha=None, data_sha=None,
                         urls=[], requests=[], checks=[], screenshots=[], phases=[], console_errors=[])

    def check(self, name, passed, reason):
        self.data['checks'].append(dict(check=name, status='PASS' if passed else 'FAIL', reason=reason))
        return passed

    def inconclusive(self, name, reason):
        self.data['checks'].append(dict(check=name, status='INCONCLUSIVE', reason=reason))

    def phase(self, name, start):
        self.data['phases'].append(dict(phase=name, wall_seconds=round(time.monotonic() - start, 3)))

    def write(self):
        self.data['end_utc'] = utc()
        failures = [c['check'] for c in self.data['checks'] if c['status'] != 'PASS']
        self.data['status'] = 'FAIL' if failures else 'PASS'
        (self.out / 'record.json').write_text(json.dumps(self.data, indent=2) + '\n')
        return ('FAIL deployed-' + self.data['mode'] + ': ' + ', '.join(failures) if failures
                else 'PASS deployed-' + self.data['mode']), bool(failures)


def origin(url):
    parsed = urlsplit(url)
    return parsed.scheme + '://' + parsed.netloc


def observe(context, record):
    responses = []
    entries = {}
    def request(req):
        record.data['urls'].append(req.url)
        entry = dict(url=req.url, method=req.method, resource_type=req.resource_type, status=None, state='pending')
        entries[req] = entry
        record.data['requests'].append(entry)
    def response(res):
        responses.append(res)
        if res.request in entries:
            entries[res.request]['status'] = res.status
    def finished(req):
        if req in entries:
            entries[req]['state'] = 'finished'
    context.on('requestfinished', finished)
    context.on('request', request)
    context.on('response', response)
    context.on('requestfailed', lambda req: record.data.setdefault('failed_requests', []).append(
        dict(url=req.url, failure=req.failure)))
    context.on('page', lambda page: (
        page.on('pageerror', lambda error: record.data['console_errors'].append(dict(kind='pageerror', text=str(error)))),
        page.on('console', lambda msg: record.data['console_errors'].append(dict(kind='console', text=msg.text, location=msg.location)) if msg.type == 'error' else None)))
    return responses


def provenance(page, base, record):
    result = page.evaluate('''async url => {
      try { const r = await fetch(url, {credentials:'omit', signal:AbortSignal.timeout(20000)});
        return {status:r.status, body:await r.json()};
      } catch(e) {return {error:String(e)}}
    }''', urljoin(base, 'build-manifest.json'))
    record.data['provenance'] = result
    envelope = result.get('body')
    body = envelope.get('data') if isinstance(envelope, dict) else None
    if isinstance(body, list):
        body = body[0] if len(body) == 1 else None
    valid = (result.get('status') == 200 and isinstance(body, dict) and
             all(isinstance(body.get(key), str) and re.fullmatch(r'[0-9a-fA-F]{40}', body[key])
                 for key in ('code_sha', 'data_sha')))
    record.check('provenance', bool(valid), json.dumps(result))
    if valid:
        record.data.update(code_sha=body['code_sha'], data_sha=body['data_sha'])


def pictures(page, record, state):
    for width, height in SIZES:
        page.set_viewport_size(dict(width=width, height=height))
        page.evaluate('scrollTo(0, 0)')
        name = f'{state}-{width}x{height}.png'
        page.screenshot(path=str(record.out / name))
        record.data['screenshots'].append(dict(state=state, path=name, width=width, height=height))


def validate_response(page, response, base):
    """Use the deployed client contract for its rendered package, Python for envelopes."""
    body = response.json()
    if response.url.split('?')[0].endswith('/night-live.json'):
        if body == {'available': False}:
            return 'Valid unavailable package (no complete live cycle)'
        result = page.evaluate('''async ({url, body}) => {
          const {NightLive, OPEN} = await import(url);
          const live = new NightLive({fetcher:async()=>({ok:true,json:async()=>body}),
            now:()=>Math.max(Date.now(), OPEN)});
          await live.tick(); return live.last !== null;
        }''', dict(url=urljoin(base, 'night-live.mjs'), body=body))
        if not result:
            raise ValueError('PACKAGE_INVALID (NightLive rejected response)')
        return 'Accepted by deployed NightLive validator'
    stem = urlsplit(response.url).path.split('/data/', 1)[1].removesuffix('.json')
    env = export.validate_envelope(body, stem)
    for row in env['data']:
        night.validate_row(row, stem)
    return 'Accepted by export.validate_envelope and night.validate_row'


def host_fetch(url):
    """Independent, bounded read: never proxy these bytes into the browser."""
    root, filename = url.rsplit('/', 1)
    # The existing fetcher permits only reviewed roots and returns bytes only on HTTP 200.
    return dict(status=200, raw=night_xml(root + '/', filename))


def cors_probe(page, record, *, feed_root=FEED, acquire=None):
    acquire = acquire or host_fetch
    evidence, bodies = {}, {}
    for filename in NATIONAL:
        url = urljoin(feed_root, filename)
        offset = len(record.data['console_errors'])
        browser = page.evaluate('''async url => {
          try {const r = await fetch(url, {mode:'cors', credentials:'omit', signal:AbortSignal.timeout(20000)});
            return {outcome:'readable', status:r.status, text:await r.text()};
          } catch(e) {return {outcome:'blocked-or-network-error', name:e.name, error:String(e)}}
        }''', url)
        for error in record.data['console_errors'][offset:]:
            location = error.get('location', {}).get('url', '')
            if error['kind'] == 'console' and not urlsplit(location).path.endswith(('.js', '.mjs')) and (
                    url in error['text'] and 'blocked by CORS policy' in error['text'] or
                    location == url and error['text'].startswith('Failed to load resource:')):
                error['expected'] = 'explicit CORS evidence fetch'
        item = dict(url=url, browser={k:v for k,v in browser.items() if k != 'text'})
        evidence[filename] = item
        if browser['outcome'] == 'readable':
            raw = browser['text'].encode('utf-8')
            item.update(status='PASS', reason='Readable browser response')
            if browser['status'] != 200:
                item.update(status='FAIL', reason=f"Browser HTTP {browser['status']}")
        else:
            item.update(status='INCONCLUSIVE', reason='Browser failure without confirmed CORS blocking')
            diagnostics = [e['text'] for e in record.data['console_errors'][offset:]
                           if url in e['text'] and 'cors' in e['text'].lower()]
            item['cors_diagnostics'] = diagnostics
            try:
                host = acquire(url)
                raw = host['raw']
                item['host'] = dict(status=host['status'], bytes=len(raw))
                if host['status'] != 200 or not raw.strip():
                    raise ValueError(f"Upstream HTTP {host['status']}, {len(raw)} bytes")
            except Exception as exc:
                item['reason'] = 'Upstream reachability unconfirmed: ' + str(exc)
                continue
            if diagnostics and browser.get('name') == 'TypeError':
                item.update(status='PASS', reason='Browser CORS diagnostic and independently reachable upstream')
        item['bytes'] = len(raw)
        try:
            xml_parser.document(raw, filename.removesuffix('.xml'))
            bodies[filename] = raw
        except ValueError as exc:
            item.update(status='FAIL', reason='Invalid XML: ' + str(exc))
    # Reuse the complete reference/result contract, including cross-file relationships.
    try:
        refs = xml_parser.references(*(bodies[name + '.xml'] for name in ('parties', 'electorates', 'candidates')))
    except KeyError:
        for item in evidence.values():
            if item['status'] == 'PASS':
                item.update(status='INCONCLUSIVE', reason='Complete reference set unavailable for validation')
    except ValueError as exc:
        for item in evidence.values():
            if item['status'] == 'PASS':
                item.update(status='FAIL', reason='Invalid reference set: ' + str(exc))
    else:
        if 'election.xml' in bodies:
            try:
                xml_parser.election(bodies['election.xml'], refs)
            except ValueError as exc:
                evidence['election.xml'].update(status='FAIL', reason='Invalid election: ' + str(exc))
    record.data['cors_evidence'] = list(evidence.values())
    for filename, item in evidence.items():
        name, reason = 'cors-evidence-' + filename, json.dumps(item)
        if item['status'] == 'INCONCLUSIVE':
            record.inconclusive(name, reason)
        else:
            record.check(name, item['status'] == 'PASS', reason)


def host_now():
    return datetime.now(timezone.utc)


def probe_phase(page, base, *, now=None):
    url = urljoin(base, 'night-live.mjs')
    # Reading the schedule must not execute a module and repair a broken page init.
    result = page.evaluate('''async url => {
      const response = await fetch(url, {credentials:'omit', signal:AbortSignal.timeout(20000)});
      return {status:response.status, source:await response.text(), now_ms:Date.now()};
    }''', url)
    match = re.search(r"export const OPEN = Date.parse\('([^']+)'\);", result['source'])
    if result['status'] != 200 or not match:
        raise ValueError('NIGHT_SCHEDULE_UNAVAILABLE')
    opening = datetime.fromisoformat(match[1].replace('Z', '+00:00'))
    opening_ms = opening.timestamp() * 1000
    observed = (now or host_now)().astimezone(timezone.utc)
    return dict(name='before-close' if observed < opening else 'after-close',
                schedule_url=url, opening_utc=match[1], opening_ms=opening_ms,
                clock_source='host-utc', observed_utc=observed.isoformat(),
                page_now_ms=result.get('now_ms'))


def page_errors(record, expected_resources=()):
    unexpected = []
    for error in record.data['console_errors']:
        expected_resource = (error['kind'] == 'console' and
                             error.get('location', {}).get('url') in expected_resources and
                             error['text'].startswith('Failed to load resource:'))
        if error['kind'] == 'pageerror' or not (error.get('expected') or expected_resource):
            unexpected.append(error)
    record.data['unexpected_page_errors'] = unexpected
    record.check('page-errors', not unexpected, json.dumps(unexpected))
    return unexpected


def night_data_url(url, base):
    path = urlsplit(url).path
    return origin(url) == origin(base) and (path.endswith('/night-live.json') or
                                           '/data/night/' in path and path.endswith('.json'))


def probe(page, base, record, responses, feed_root=FEED, *, now=None):
    started = time.monotonic()
    page.goto(urljoin(base, 'night/'))
    page.wait_for_load_state('networkidle')
    record.data['fallback'] = dict(status=page.locator('#night-live-status').inner_text(),
                                 snapshot=page.locator('#night-snapshot').inner_text())
    fallback = record.data['fallback']
    live = page.locator('#night-snapshot').get_attribute('data-retrieved-at')
    record.check('dated-fallback', bool(live) or (
        bool(re.search(r'20\d\d-\d\d-\d\d', fallback['snapshot'])) and
        'Official results' in fallback['snapshot'] and
        ('Final snapshot' in fallback['snapshot'] or 'Recorded demo' in fallback['snapshot'])),
        'Live retrieval: ' + str(live) if live else json.dumps(fallback))
    requests = list(record.data['requests'])
    record.check('page-same-origin', all(origin(r['url']) == origin(base) for r in requests), json.dumps(requests))
    pictures(page, record, 'fallback')
    cors_probe(page, record, feed_root=feed_root)
    phase = probe_phase(page, base, now=now)
    record.data['probe_phase'] = phase
    seen = []
    for response in list(responses):
        if not night_data_url(response.url, base):
            continue
        item = dict(url=response.url, status=response.status, parses=False, validates=False,
                    started_ms=response.request.timing['startTime'])
        try:
            response.json()
            item['parses'] = True
            item['validation'] = validate_response(page, response, base)
            item['validates'] = True
        except Exception as exc:
            item['validation'] = str(exc)
        record.check('night-data-' + str(len(seen)), response.ok and item['validates'], json.dumps(item))
        seen.append(item)
    record.data['night_data_responses'] = seen
    failures = [r for r in record.data.get('failed_requests', []) if night_data_url(r['url'], base)]
    pending = [r for r in record.data['requests'] if night_data_url(r['url'], base) and r.get('state') != 'finished']
    errors = page_errors(record)
    before_state = (page.locator('.night-page > .countdown').is_visible() and
                    page.locator('.night-page a[href$="vote/"]').is_visible())
    valid_after_open = [r for r in seen if 200 <= r['status'] < 300 and r['validates'] and
                        r['started_ms'] >= phase['opening_ms']]
    acceptable = (before_state if phase['name'] == 'before-close' else bool(valid_after_open))
    record.check('night-data-transport', acceptable and not failures and not pending and not errors,
                 json.dumps(dict(phase=phase['name'], before_close_state=before_state,
                                 valid_after_open=len(valid_after_open), responses=len(seen),
                                 failed_requests=failures, pending_requests=pending, page_errors=errors)))
    record.phase('probe', started)


def rehearse(page, base, record, speed=60):
    started = time.monotonic()
    page.goto(urljoin(base, 'night/?sequence=2023-illustrative'))
    page.wait_for_load_state('networkidle')
    label = page.locator('#night-snapshot .night-mode')
    def labelled():
        return night.LABEL in label.inner_text()
    record.check('initial-paused-label', labelled() and page.locator('#night-clock').inner_text() == 'Paused: 0 seconds', label.inner_text())
    page.locator('#night-speed').select_option(str(speed))
    pictures(page, record, 'start')
    record.phase('start', started)
    started = time.monotonic()
    page.locator('#night-play').click()
    page.locator('[data-frame="1"]').wait_for(state='visible', timeout=600000 // speed + 10000)
    page.locator('#night-play').click()
    record.phase('play-to-middle', started)
    paused = page.locator('#night-clock').inner_text()
    started = time.monotonic()
    pictures(page, record, 'middle')
    page.wait_for_timeout(250)
    record.check('pause-label', labelled() and paused.startswith('Paused:') and page.locator('#night-clock').inner_text() == paused, paused)
    record.phase('paused', started)
    started = time.monotonic()
    page.locator('#night-play').click()
    page.wait_for_function("document.querySelector('#night-announcement').textContent === 'Replay ended.'", timeout=600000 // speed + 10000)
    record.phase('resume-to-end', started)
    elapsed = sum(p['wall_seconds'] for p in record.data['phases'] if p['phase'] in {'play-to-middle', 'resume-to-end'})
    expected = 600 / speed
    record.check('real-time-speed', expected - 1 <= elapsed <= expected + max(3, expected * .2),
                 f'{elapsed:.3f}s playing; expected {expected:.3f}s, allowing browser interaction overhead')
    votes = int(page.locator('#night-snapshot .night-votes strong').inner_text().replace(',', ''))
    match = re.search(r'House (\d+)', page.locator('#night-snapshot').inner_text())
    house = int(match[1]) if match else None
    record.check('golden', golden(votes, house), f'{votes} valid party votes; House {house}')
    record.check('end-label-paused', labelled() and page.locator('#night-clock').inner_text() == 'Paused: 600 seconds', label.inner_text())
    pictures(page, record, 'end')
    started = time.monotonic()
    page.locator('#night-reset').click()
    record.check('reset', labelled() and page.locator('#night-clock').inner_text() == 'Paused: 0 seconds' and page.locator('[data-frame="0"]').is_visible(), 'Reset returns to labelled, paused first frame')
    record.phase('reset', started)
    for year in ('2017', '2020', '2023'):
        started = time.monotonic()
        page.locator(f'nav[aria-label="Packaged results"] a[href="?sequence={year}"]').click()
        page.wait_for_load_state('networkidle')
        record.check('archive-' + year, 'Final snapshot' in label.inner_text() and year in label.inner_text() and not page.locator('#night-controls').is_visible() and page.locator('#night-snapshot .night-votes').is_visible(), label.inner_text())
        record.phase('archive-' + year, started)
    official = [r for r in record.data['requests'] if re.search(r'(electionresults\.govt\.nz|election\.net\.nz)', urlsplit(r['url']).hostname or '')]
    record.data['official_feed_requests'] = official
    record.check('no-official-feed', not official, json.dumps(official))
    record.check('console-errors', not record.data['console_errors'], json.dumps(record.data['console_errors']))


def fault_package(record_dir):
    from product.nz_election.pipeline import night_live
    from product.nz_election.pipeline.night_page import live_package
    from product.nz_election.tests.night_live_cases import Clock, captures
    clock = Clock()
    cycle = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
    root = Path(record_dir) / 'fault-fixture'
    night.prepare(root, night_live.loaded(cycle), 'offline-verification', 'a' * 40, cycle['retrieved_at'])
    envs = {p.relative_to(root).as_posix()[:-5]: json.loads(p.read_text()) for p in root.rglob('*.json')}
    pack = live_package(envs)
    pack['html'] = '<p>Fault injection: offline verification fixture, not live results.</p>' + pack['html']
    return pack


def faults(page, base, record):
    pack = fault_package(record.out)
    instant = datetime.fromisoformat(pack['retrieved_at'].replace('Z', '+00:00'))
    page.clock.install(time=instant)
    state = {'fail': False}
    injected = []
    def route(r):
        injected.append(dict(url=r.request.url, status=503 if state['fail'] else 200))
        r.fulfill(status=503 if state['fail'] else 200, content_type='application/json',
                  body='{}' if state['fail'] else json.dumps(pack))
    page.route(urljoin(base, 'night-live.json'), route)
    record.data['injection'] = dict(description='Validated offline fixtures; simulated post-close clock; packaged JSON only', retrieved_at=pack['retrieved_at'])
    for scenario in ('failure', 'unchanged-stale'):
        started = time.monotonic()
        state['fail'] = False
        page.clock.set_system_time(instant)
        offset = len(injected)
        page.goto(urljoin(base, 'night/'))
        page.wait_for_function("document.querySelector('#night-snapshot').textContent.includes('Fault injection:')")
        page.wait_for_function("document.querySelector('#night-live-status').textContent.includes('Packaged by the site')")
        before = page.locator('#night-snapshot').inner_html()
        state['fail'] = scenario == 'failure'
        with page.expect_response(lambda response: response.url == urljoin(base, 'night-live.json')):
            page.clock.run_for(16 * 60000)
        page.wait_for_function("document.querySelector('#night-live-status').textContent.includes('Stale')")
        record.check(scenario + '-last-good', page.locator('#night-snapshot').inner_html() == before, page.locator('#night-live-status').inner_text())
        record.check(scenario + '-transport', any(r['status'] == (503 if state['fail'] else 200) for r in injected[offset + 1:]),
                     json.dumps(injected[offset:]))
        pictures(page, record, scenario)
        record.phase(scenario, started)


def run(mode, base, root=Path('artifacts/nz-election/deployed'), speed=60):
    record = Record(mode, base, root)
    started = time.monotonic()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw, launch_chromium(pw) as browser:
            record.data.update(browser='chromium', browser_version=browser.version)
            with browser.new_context(viewport=dict(width=390, height=844), reduced_motion='reduce') as context:
                responses = observe(context, record)
                page = context.new_page()
                page.set_default_timeout(15000)
                if mode == 'probe':
                    probe(page, base, record, responses)
                elif mode == 'rehearse':
                    rehearse(page, base, record, speed)
                else:
                    faults(page, base, record)
                provenance(page, base, record)
    except Exception as exc:
        record.check('execution', False, str(exc))
    page_errors(record, (urljoin(base, 'night-live.json'),) if mode == 'faults' else ())
    record.phase('total', started)
    line, failed = record.write()
    print(str(record.out / 'record.json'))
    print(line)
    return int(failed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for name in ('probe', 'rehearse', 'faults'):
        modes.add_argument('--' + name, dest='mode', action='store_const', const=name)
    parser.add_argument('--origin', default='https://byronxlg.com')
    parser.add_argument('--base-url', help='Product root URL, e.g. http://localhost:8000/unattended/nz-election/')
    parser.add_argument('--speed', type=int, choices=(1, 10, 60), default=60)
    args = parser.parse_args()
    base = (args.base_url or args.origin.rstrip('/') + '/unattended/nz-election/').rstrip('/') + '/'
    return run(args.mode, base, speed=args.speed)


if __name__ == '__main__':
    sys.exit(main())
