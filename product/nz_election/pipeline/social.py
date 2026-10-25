# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Bounded X sampling and in-memory Jev classification; only aggregates survive."""
import argparse
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time as clock
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export
from product.nz_election.pipeline.refresh import code_sha, utc_now
from product.nz_election.pipeline.sunsets import require_collection, SunsetReached, ended
from product.nz_election.pipeline.storage import replace_directory

NZ = ZoneInfo('Pacific/Auckland')
CAP, RESERVATION, MAX_BYTES = 7800, 315, 1024 * 1024
MAX_QUERY_LENGTH = 512
QUERY = '''(#nzpol OR #nzvotes OR #nzelection OR
"Christopher Luxon" OR "Chris Hipkins" OR "David Seymour" OR
"Winston Peters" OR "Chlöe Swarbrick" OR "Chloe Swarbrick" OR
"Marama Davidson" OR "Rawiri Waititi" OR "Debbie Ngarewa-Packer" OR
"Qiulae Wong" OR "Te Pāti Māori" OR "Te Pati Maori" OR
"NZ First" OR "New Zealand First" OR "ACT New Zealand" OR
"Opportunities Party" OR
((National OR Labour OR Greens) (NZ OR "New Zealand" OR Aotearoa)))
-filter:retweets'''
PARTIES = ('National', 'Labour', 'Green', 'ACT', 'NZ First', 'Te Pāti Māori', 'Opportunity', 'other', 'multiple', 'none/unclear')
TOPICS = ('economy/tax', 'housing', 'health', 'education', 'crime', 'Treaty/Māori affairs', 'climate', 'immigration', 'campaign/personality', 'other/unclear')
ATTITUDES = ('strongly negative', 'negative', 'neutral', 'positive', 'strongly positive')
# Pin requests and validation together so upstream default rotations cannot change the model.
MODEL_VERSION = 'jev-1.13.0'
MODEL_VERSIONS = frozenset({MODEL_VERSION, 'jev-fixture-1', 'jev-test-1'})
QUESTION_VERSION = 'nz-politics-poc-1'
QUESTIONS = {
    'relevant': dict(type='noul', instructions='Is this about current NZ national politics?'),
    'party': dict(type='choice', instructions='Which party is the primary subject?', criteria=dict(zip(PARTIES, PARTIES))),
    'topic': dict(type='choice', instructions='Main topic:', criteria=dict(zip(TOPICS, TOPICS))),
    'evaluable': dict(type='noul', instructions='Does the author express an interpretable attitude toward that primary party?'),
    'attitude': dict(type='score', instructions='Attitude toward that party, ordered strongly negative, negative, neutral, positive, strongly positive.', criteria=list(ATTITUDES)),
}
# Dated mappings are criteria, not an assertion that author accounts are verified.
QUESTIONS['party']['criteria'].update({
    'National': 'National; Christopher Luxon (leader mapping 17 October 2026)',
    'Labour': 'Labour; Chris Hipkins (leader mapping 17 October 2026)',
    'Green': 'Green; Chlöe or Chloe Swarbrick, Marama Davidson (leader mapping 17 October 2026)',
    'ACT': 'ACT; David Seymour (leader mapping 17 October 2026)',
    'NZ First': 'NZ First; Winston Peters (leader mapping 17 October 2026)',
    'Te Pāti Māori': 'Te Pāti Māori; Rawiri Waititi, Debbie Ngarewa-Packer (leader mapping 17 October 2026)',
    'Opportunity': 'Opportunity; Qiulae Wong (leader mapping 17 October 2026)',
})


def frozen(now):
    from product.nz_election.pipeline.deployment_guard import require_publication_allowed
    try:
        require_publication_allowed(now)
    except ValueError as exc:
        if str(exc) != 'PUBLICATION_FROZEN':
            raise
        return True
    return False


def windows(day):
    export.calendar_date(day, 'day')
    start = datetime.combine(date.fromisoformat(day), time(), NZ).astimezone(timezone.utc)
    end = datetime.combine(date.fromisoformat(day) + timedelta(days=1), time(), NZ).astimezone(timezone.utc)
    # Never invent or silently drop an hour on a daylight-saving transition.
    if end - start != timedelta(hours=24):
        raise ValueError('SOCIAL_NON_24_HOUR_DAY')
    return [(int((start + timedelta(hours=h)).timestamp()), int((start + timedelta(hours=h+1)).timestamp())) for h in range(24)]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def transport(method, url, headers, body, *, now=None):
    """Bounded response, no redirect of credentials, no upstream diagnostics."""
    require_collection('social', (now or utc_now)())
    try:
        request = Request(url, data=body, headers=headers, method=method)
        with build_opener(NoRedirect).open(request, timeout=30) as response:
            return response.status, response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        return exc.code, b''
    except Exception:
        raise ValueError('SOCIAL_TRANSPORT_FAILED') from None


def decode(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('SOCIAL_RESPONSE_LIMIT')
    try:
        body = json.loads(raw, parse_float=Decimal)
        if not isinstance(body, dict):
            raise ValueError()
        return body
    except Exception:
        raise ValueError('SOCIAL_INVALID_RESPONSE') from None


# Only locally defined codes may reach logs; exception messages can contain secrets.
DIAGNOSTIC_CODES = frozenset({
    'SOCIAL_COLLECTION_FAILED', 'SOCIAL_COLLECTION_RETRY', 'SOCIAL_TRANSPORT_FAILED', 'SOCIAL_INVALID_PAGE',
    'SOCIAL_QUERY_TOO_LONG', 'SOCIAL_UPSTREAM_FAILED',
    'SOCIAL_RESPONSE_LIMIT', 'SOCIAL_INVALID_RESPONSE', 'SOCIAL_CLASSIFICATION_FAILED',
    'SOCIAL_INVALID_CLASSIFICATION', 'SOCIAL_BUDGET_DAY_CHANGED', 'SOCIAL_FROZEN',
})


def diagnostic_code(exc, fallback):
    code = exc.args[0] if len(exc.args) == 1 else None
    return code if isinstance(code, str) and code in DIAGNOSTIC_CODES else fallback


CLASSIFICATION_CHECKS = frozenset({'model', 'answers', 'type', 'probabilities', 'sum', 'choice', 'value', 'decode', 'http', 'transport'})
EXCLUSIONS = ('duplicate', 'unsupported', 'irrelevant', 'classification')


def print_diagnostic(diagnostic):
    code = diagnostic_code(ValueError(diagnostic.get('code')), 'SOCIAL_CLASSIFICATION_FAILED')
    check = diagnostic.get('check')
    suffix = f' check={check}' if isinstance(check, str) and check in CLASSIFICATION_CHECKS else ''
    print(f"social diagnostic: {code} http_status={diagnostic.get('http_status')} window_index={diagnostic.get('window')} attempt={diagnostic.get('attempt')}{suffix}", file=sys.stderr)


def classification_response(body, diagnostic):
    # Check labels are local constants, never derived from upstream fields.
    check = 'model'
    try:
        model = body.get('model')
        if not isinstance(model, str) or model not in MODEL_VERSIONS:
            raise ValueError()
        check = 'answers'
        answers = body.get('answers')
        if not isinstance(answers, dict) or set(answers) != set(QUESTIONS):
            raise ValueError()
        clean = {}
        for name, question in QUESTIONS.items():
            check = 'type'
            answer = answers[name]
            if not isinstance(answer, dict) or answer.get('type') != question['type']:
                raise ValueError()
            if question['type'] == 'noul':
                check = 'value'
                clean[name] = probability(answer.get('noul'))
            else:
                check = 'probabilities'
                keys = set(question['criteria']) if question['type'] == 'choice' else {str(i) for i in range(5)}
                probs = answer.get('probabilities')
                if not isinstance(probs, dict) or set(probs) != keys:
                    raise ValueError()
                check = 'value'
                clean[name] = {k: probability(v) for k, v in probs.items()}
                check = 'sum'
                if abs(sum(clean[name].values()) - 1) > Decimal('.001'):
                    raise ValueError()
                check = 'choice'
                if question['type'] == 'choice':
                    choice = answer.get('choice')
                    if not isinstance(choice, str) or choice not in probs or clean[name][choice] != max(clean[name].values()):
                        raise ValueError()
        return model, clean
    except Exception:
        diagnostic.update(code='SOCIAL_CLASSIFICATION_FAILED', check=check)
        raise ValueError('SOCIAL_CLASSIFICATION_FAILED') from None


def hourly_queries(day, diagnostic=None):
    # Preflight the whole day so a longer later suffix cannot incur partial spend.
    queries = []
    for index, (start, end) in enumerate(windows(day)):
        query = QUERY + f' since_time:{start} until_time:{end}'
        if len(query) > MAX_QUERY_LENGTH:
            if diagnostic is not None:
                diagnostic.update(window=index, attempt=1, http_status=None, code=None)
            raise ValueError('SOCIAL_QUERY_TOO_LONG')
        queries.append((start, end, query))
    return queries


def collect(day, ledger, run, *, key, send, sleep, now=None, checkpoint=lambda: None, diagnostic=None):
    diagnostic = {} if diagnostic is None else diagnostic
    now = now or utc_now
    require_collection('social', now())
    diagnostic['post_windows'] = []
    posts, provenance = [], []
    retries = []
    def report_retries(final=None):
        # A terminal diagnostic already identifies retries with the same status.
        for retry in retries:
            if final is None or (retry['window'], retry['http_status']) != (final['window'], final['http_status']):
                print_diagnostic(retry)
        retries.clear()
    for window_index, (start, end, query) in enumerate(hourly_queries(day, diagnostic)):
        for attempt in range(3):
            diagnostic.update(window=window_index, attempt=attempt + 1, http_status=None, code=None)
            allocated = run['allocation']
            used = run['requests'] * RESERVATION
            if (allocated and used + RESERVATION > allocated) or (not allocated and sum(r['reserved'] for r in ledger if r['day'] == run['day']) + RESERVATION > CAP):
                # An incomplete run retains worst-case charges for every attempt.
                run['spent'] = run['requests'] * RESERVATION
                report_retries()
                return posts, provenance, True
            instant = now()
            require_collection('social', instant)
            # Leave room for the bounded HTTP timeout before the budget day closes.
            if (datetime.fromisoformat(instant.replace('Z', '+00:00')) + timedelta(seconds=31)).astimezone(NZ).date().isoformat() != run['day']:
                raise ValueError('SOCIAL_BUDGET_DAY_CHANGED')
            if frozen(instant):
                raise ValueError('SOCIAL_FROZEN')
            if run['requests']:
                # 20 returns every 310 seconds: at most 12 pages in any rolling hour.
                # Use 330 seconds so strictly fewer than 240 can fall in a rolling hour.
                sleep(330)
            instant = now()
            require_collection('social', instant)
            # Leave room for the bounded HTTP timeout before the budget day closes.
            if (datetime.fromisoformat(instant.replace('Z', '+00:00')) + timedelta(seconds=31)).astimezone(NZ).date().isoformat() != run['day']:
                raise ValueError('SOCIAL_BUDGET_DAY_CHANGED')
            if frozen(instant):
                raise ValueError('SOCIAL_FROZEN')
            unspent = {k: run[k] for k in ('reserved', 'requests', 'spent')}
            if not allocated:
                run['reserved'] += RESERVATION
            run['requests'] += 1
            run['spent'] += RESERVATION
            try:
                checkpoint()
                url = 'https://api.twitterapi.io/twitter/tweet/advanced_search?' + urlencode(dict(query=query, queryType='Latest'))
                # Atomic checkpointing can outlast the pre-reservation clock check.
                instant = now()
                require_collection('social', instant)
                if (datetime.fromisoformat(instant.replace('Z', '+00:00')) + timedelta(seconds=31)).astimezone(NZ).date().isoformat() != run['day']:
                    raise ValueError('SOCIAL_BUDGET_DAY_CHANGED')
                if frozen(instant):
                    raise ValueError('SOCIAL_FROZEN')
            except SunsetReached:
                run.update(unspent)
                checkpoint()
                raise
            try:
                status, raw = send('GET', url, {'X-API-Key': key, 'Accept': 'application/json'}, None)
                diagnostic['http_status'] = status if type(status) is int and 100 <= status <= 599 else None
            except SunsetReached:
                run.update(unspent)
                checkpoint()
                raise
            except Exception:
                diagnostic['code'] = 'SOCIAL_TRANSPORT_FAILED'
                status, raw = 503, b''
            if status in {429, 500, 502, 503, 504} and attempt < 2:
                retries.append({k: diagnostic[k] for k in ('window', 'attempt', 'http_status')})
                retries[-1]['code'] = 'SOCIAL_COLLECTION_RETRY'
                continue
            if status != 200:
                report_retries(diagnostic)
                raise ValueError('SOCIAL_COLLECTION_FAILED')
            report_retries()
            body = decode(raw)
            batch = body.get('tweets')
            if body.get('status') == 'error' or not isinstance(batch, list) or len(batch) > 20 or type(body.get('has_next_page')) is not bool:
                raise ValueError('SOCIAL_INVALID_PAGE')
            run['spent'] -= RESERVATION - max(15, len(batch) * 15)
            checkpoint()
            provenance.append(dict(start_epoch=start, end_epoch=end, retrieved_at=now(), page_limit=body['has_next_page'] or len(batch) == 20))
            diagnostic['post_windows'].extend([window_index] * len(batch))
            posts.extend(batch)
            break
    return posts, provenance, False


def probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)) or not Decimal(value).is_finite() or not 0 <= value <= 1:
        raise ValueError('SOCIAL_INVALID_CLASSIFICATION')
    if Decimal(value).as_tuple().exponent < -1000:
        raise ValueError('SOCIAL_INVALID_CLASSIFICATION')
    return Decimal(value)


def classify(posts, *, key, send, diagnostic=None, enforce_bound=False, now=None):
    diagnostic = {} if diagnostic is None else diagnostic
    now = now or utc_now
    require_collection('social', now())
    result, ids, texts = [], set(), set()
    excluded = Counter(dict.fromkeys(EXCLUSIONS, 0))
    diagnostic['last_exclusion'] = None
    candidates = []
    origins = diagnostic.get('post_windows', [])
    for index, post in enumerate(posts):
        diagnostic.update(window=origins[index] if index < len(origins) else None, attempt=1, http_status=None, code=None, check=None)
        if not isinstance(post, dict):
            raise ValueError('SOCIAL_INVALID_PAGE')
        identity, text = post.get('id'), post.get('text')
        author = post.get('author', {}).get('id') if isinstance(post.get('author'), dict) else None
        if not all(isinstance(v, str) and v for v in (identity, text, author)):
            raise ValueError('SOCIAL_INVALID_PAGE')
        normalized = ' '.join(text.casefold().split())
        if identity in ids or normalized in texts:
            excluded['duplicate'] += 1
            continue
        ids.add(identity)
        texts.add(normalized)
        if post.get('lang') != 'en' or len(text) > 8000:
            excluded['unsupported'] += 1
            continue
        candidates.append((index, text, author))
    sent = len(candidates)
    for index, text, author in candidates:
        diagnostic.update(window=origins[index] if index < len(origins) else None, attempt=1, http_status=None, code=None, check=None)
        require_collection('social', now())
        payload = dict(model=MODEL_VERSION, state=text, questions=QUESTIONS)
        try:
            diagnostic['check'] = 'transport'
            status, raw = send('POST', 'https://api.typesafe.ai/v1/systemone', {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, export.canonical(payload).encode())
            diagnostic['check'] = 'http'
            diagnostic['http_status'] = status if type(status) is int and 100 <= status <= 599 else None
            if status != 200:
                raise ValueError()
        except SunsetReached:
            raise
        except Exception as exc:
            diagnostic['code'] = diagnostic_code(exc, 'SOCIAL_CLASSIFICATION_FAILED')
            raise ValueError('SOCIAL_CLASSIFICATION_FAILED') from None
        diagnostic['check'] = 'decode'
        try:
            body = decode(raw)
        except ValueError as exc:
            diagnostic['code'] = diagnostic_code(exc, 'SOCIAL_INVALID_RESPONSE')
            raise
        try:
            model, clean = classification_response(body, diagnostic)
        except ValueError:
            excluded['classification'] += 1
            diagnostic['last_exclusion'] = {k: diagnostic[k] for k in ('window', 'attempt', 'http_status', 'code', 'check')}
            print_diagnostic(diagnostic)
            if enforce_bound and excluded['classification'] * 10 > sent:
                raise ValueError('SOCIAL_CLASSIFICATION_FAILED') from None
            continue
        diagnostic['check'] = None
        if clean['relevant'] < Decimal('.8'):
            excluded['irrelevant'] += 1
            continue
        result.append(dict(author=author, probabilities=clean, model=model))
    # Completion is distinct from a failed check for existing diagnostic readers.
    diagnostic.update(window=None, attempt=None, http_status=None, code=None, check='complete')
    return result, dict(excluded)


def aggregate(day, posts, classified, excluded, provenance, now):
    parties, topics = dict.fromkeys(PARTIES, 0), dict.fromkeys(TOPICS, 0)
    attitudes = {p: [0] * 5 for p in PARTIES[:7]}
    authors = Counter(r['author'] for r in classified)
    sums = {q: dict.fromkeys(QUESTIONS[q]['criteria'] if q != 'attitude' else [str(i) for i in range(5)], Decimal(0)) for q in ('party', 'topic', 'attitude')}
    sums.update(relevant={'yes': Decimal(0)}, evaluable={'yes': Decimal(0)})
    for row in classified:
        probs = row['probabilities']
        party, topic = (max(probs[q], key=probs[q].get) for q in ('party', 'topic'))
        parties[party] += 1
        topics[topic] += 1
        if party in attitudes and probs['evaluable'] >= Decimal('.8'):
            attitudes[party][int(max(probs['attitude'], key=probs['attitude'].get))] += 1
        for q in sums:
            for k in sums[q]:
                sums[q][k] += probs[q] if q in ('relevant', 'evaluable') else probs[q][k]
    n = len(classified)
    return dict(id='social-' + day, source_ref=[], observed_at=now, day=day,
                sample=dict(returned=len(posts), eligible=n, unique_authors=len(authors),
                            top_author_share_ppm=max(authors.values(), default=0)*1000000//max(n, 1),
                            capped_windows=sum(w['page_limit'] for w in provenance), exclusions=excluded),
                party_counts=parties, topic_counts=topics,
                attitude={p: dict(eligible=sum(v), counts=v if sum(v) >= 30 else None, withheld=sum(v) < 30) for p, v in attitudes.items()},
                model_versions=sorted({r['model'] for r in classified}), question_version=QUESTION_VERSION,
                probability_sums={q: {k: format(v, 'f') for k, v in values.items()} for q, values in sums.items()},
                provenance=dict(query=QUERY, windows=provenance, fixture=False))


def validate_row(row, stem):
    """Closed nested schemas prevent identifiers leaking in arbitrary metadata."""
    def natural(v, maximum=10**9):
        if type(v) is not int or not 0 <= v <= maximum:
            raise ValueError('INVALID_SOCIAL_NUMBER')
    def keys(v, expected):
        if not isinstance(v, dict) or set(v) != set(expected):
            raise ValueError('INVALID_SOCIAL_FIELDS')
    export.calendar_date(row['day'], 'day')
    if row['source_ref'] != []:
        raise ValueError('INVALID_SOCIAL_FIELDS')
    if stem == 'social/credits':
        if not re.fullmatch(r'run-[0-9a-f]{24}', row['id']):
            raise ValueError('INVALID_SOCIAL_RUN')
        for k in ('reserved', 'spent', 'allocation'):
            natural(row[k], CAP)
        natural(row['requests'], 24)
        if row['cap'] != CAP or row['spent'] > row['reserved'] or row['reserved'] % RESERVATION or type(row['closed']) is not bool or row['allocation'] not in (0, row['reserved']):
            raise ValueError('INVALID_SOCIAL_CREDITS')
        return
    if row['id'] != 'social-' + row['day'] or row['question_version'] != QUESTION_VERSION:
        raise ValueError('INVALID_SOCIAL_VERSION')
    sample = row['sample']
    keys(sample, ('returned', 'eligible', 'unique_authors', 'top_author_share_ppm', 'capped_windows', 'exclusions'))
    for k in ('returned', 'eligible', 'unique_authors'):
        natural(sample[k], 480)
    natural(sample['top_author_share_ppm'], 1000000)
    natural(sample['capped_windows'], 24)
    keys(sample['exclusions'], EXCLUSIONS)
    for v in sample['exclusions'].values():
        natural(v, 480)
    if sample['eligible'] + sum(sample['exclusions'].values()) != sample['returned'] or sample['unique_authors'] > sample['eligible']:
        raise ValueError('INVALID_SOCIAL_TOTAL')
    for field, options in (('party_counts', PARTIES), ('topic_counts', TOPICS)):
        keys(row[field], options)
        for v in row[field].values():
            natural(v, 480)
        if sum(row[field].values()) != sample['eligible']:
            raise ValueError('INVALID_SOCIAL_TOTAL')
    keys(row['attitude'], PARTIES[:7])
    for p, value in row['attitude'].items():
        keys(value, ('eligible', 'counts', 'withheld'))
        natural(value['eligible'], row['party_counts'][p])
        if type(value['withheld']) is not bool or value['withheld'] != (value['eligible'] < 30):
            raise ValueError('INVALID_SOCIAL_WITHHOLDING')
        if value['withheld']:
            if value['counts'] is not None:
                raise ValueError('INVALID_SOCIAL_WITHHOLDING')
        else:
            if not isinstance(value['counts'], list) or len(value['counts']) != 5:
                raise ValueError('INVALID_SOCIAL_FIELDS')
            for v in value['counts']:
                natural(v, 480)
            if sum(value['counts']) != value['eligible']:
                raise ValueError('INVALID_SOCIAL_TOTAL')
    if not isinstance(row['model_versions'], list) or any(not isinstance(m, str) or m not in MODEL_VERSIONS for m in row['model_versions']):
        raise ValueError('INVALID_SOCIAL_MODEL')
    keys(row['probability_sums'], QUESTIONS)
    for q, values in row['probability_sums'].items():
        options = ('yes',) if q in ('relevant', 'evaluable') else [str(i) for i in range(5)] if q == 'attitude' else QUESTIONS[q]['criteria']
        keys(values, options)
        for v in values.values():
            if not isinstance(v, str) or not re.fullmatch(r'[0-9]{1,3}(\.[0-9]{1,1000})?', v) or not 0 <= Decimal(v) <= sample['eligible']:
                raise ValueError('INVALID_SOCIAL_PROBABILITY')
    prov = row['provenance']
    keys(prov, ('query', 'windows', 'fixture'))
    if prov['query'] != QUERY or type(prov['fixture']) is not bool or not isinstance(prov['windows'], list) or not 1 <= len(prov['windows']) <= 24:
        raise ValueError('INVALID_SOCIAL_PROVENANCE')
    expected = windows(row['day'])
    previous = -1
    for w in prov['windows']:
        keys(w, ('start_epoch', 'end_epoch', 'retrieved_at', 'page_limit'))
        pair = (w['start_epoch'], w['end_epoch'])
        if any(type(v) is not int for v in pair) or pair not in expected or type(w['page_limit']) is not bool:
            raise ValueError('INVALID_SOCIAL_WINDOW')
        index = expected.index(pair)
        if index <= previous:
            raise ValueError('INVALID_SOCIAL_WINDOW')
        previous = index
        export.timestamp(w['retrieved_at'])
    if sample['returned'] > 20 * len(prov['windows']) or sample['capped_windows'] != sum(w['page_limit'] for w in prov['windows']):
        raise ValueError('INVALID_SOCIAL_TOTAL')


def validate_ledger(rows):
    for day in {r['day'] for r in rows}:
        if sum(r['reserved'] for r in rows if r['day'] == day) > CAP:
            raise ValueError('SOCIAL_CREDIT_CAP')


def fixture_send():
    page = 0
    def send(method, url, headers, body):
        nonlocal page
        if method == 'GET':
            page += 1
            data = dict(tweets=[dict(id=f'fiction-{page}-{i}', text=f'Fictional civic example {page}-{i}', lang='en', author=dict(id=f'fiction-author-{i}')) for i in range(10)], has_next_page=False)
        else:
            index = int(json.loads(body)['state'].rsplit('-', 1)[1])
            party = PARTIES[index % 7]
            answers = {q: dict(type='noul', noul=1) for q in ('relevant', 'evaluable')}
            for q, choices, selected in [('party', PARTIES, party), ('topic', TOPICS, TOPICS[index % 10]), ('attitude', [str(i) for i in range(5)], str(index % 5))]:
                answers[q] = dict(type=QUESTIONS[q]['type'], probabilities={p: int(p == selected) for p in choices}, choice=selected)
            data = dict(model='jev-fixture-1', answers=answers)
        return 200, export.canonical(data).encode()
    return send


def refresh_social(out, day, *, now, x_key='', jev_key='', send=transport, sleep=clock.sleep, fixture=False, reserve=False, reservation=None, run_url='offline-verification', clock_now=None):
    from product.nz_election.pipeline.sunsets import skip
    if skip('social', now):
        return 'ended'
    if frozen(now):
        return 'frozen'
    windows(day)
    # Offline harnesses explicitly label their run and supply a synthetic transport.
    offline = fixture or (run_url == 'offline-verification' and send is not transport)
    clock_now = clock_now or ((lambda: now) if offline else utc_now)
    paid_send = send
    def send(*args, **kwargs):
        require_collection('social', clock_now())
        return paid_send(*args, **kwargs)
    if date.fromisoformat(day) >= datetime.fromisoformat(now.replace('Z', '+00:00')).astimezone(NZ).date():
        raise ValueError('SOCIAL_DAY_NOT_CLOSED')
    out = Path(out).absolute()
    if out.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    out.parent.mkdir(parents=True, exist_ok=True)
    with (out.parent / ('.' + out.name + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = export.validate_bundle(out) if out.exists() else {}
        ledger = old.get('social/credits', {}).get('data', [])
        prior = next((r for r in old.get('status', {}).get('data', []) if r['dataset'] == 'social'), {})
        budget_day = datetime.fromisoformat(now.replace('Z', '+00:00')).astimezone(NZ).date().isoformat()
        budget_spent = not reservation and CAP - sum(r['reserved'] for r in ledger if r['day'] == budget_day) < RESERVATION
        if reservation:
            run = next((r for r in ledger if r['id'] == reservation), None)
            if not run or run['closed'] or run['requests'] or run['day'] != budget_day:
                raise ValueError('SOCIAL_INVALID_RESERVATION')
        else:
            run = dict(id='run-' + os.urandom(12).hex(), source_ref=[], observed_at=now, day=budget_day, reserved=0, spent=0, cap=CAP, requests=0, allocation=0, closed=False)
            if not budget_spent:
                ledger.append(run)
        sha = code_sha()
        error, record = None, None
        def save(*, restore_status=False):
            with tempfile.TemporaryDirectory(prefix='.social-', dir=out.parent) as tmp:
                stage = Path(tmp) / 'data'
                shutil.copytree(out, stage) if out.exists() else stage.mkdir()
                env = lambda data: export.envelope(data, [], run_url, sha, inputs={'questions': export.digest(export.canonical(QUESTIONS).encode())}, method=QUESTION_VERSION, generated=now)
                if not budget_spent:
                    export.pair(stage, 'social/credits', env(ledger))
                if record is not None:
                    records = [r for r in old.get('social/daily', {}).get('data', []) if r['day'] != day] + [record]
                    export.pair(stage, 'social/daily', env(sorted(records, key=lambda r: r['day'])))
                success = now if record is not None else prior.get('last_success_at')
                last_day = max((r['day'] for r in old.get('social/daily', {}).get('data', [])), default=None)
                if error == 'SOCIAL_CREDIT_CAP':
                    message = "Day's collection cap was already spent; " if budget_spent else 'Collection limit reached; '
                    message += ('showing data through ' + last_day) if last_day else 'no earlier sample is published.'
                else:
                    message = ('Offline verification; synthetic data, not live data.' if fixture else 'Time-stratified X sample; not a complete count.') if record else 'Previous data retained; collection pending or unavailable.'
                if record is not None:
                    message += f" {len(record['provenance']['windows'])} of 24 hours sampled."
                # A skipped collection is not a handled failure for publication or readers.
                status_error = None if budget_spent and error == 'SOCIAL_CREDIT_CAP' else error
                status = dict(id='status-social', source_ref=[], observed_at=now, dataset='social', state=('stale' if error or record is None else 'fresh') if success else 'unavailable', last_attempt_at=now, last_success_at=success, last_good_run_url=run_url if record else prior.get('last_good_run_url'), error_code=status_error, message=message)
                statuses = [r for r in old.get('status', {}).get('data', []) if r['dataset'] != 'social'] + [status]
                status_env = old.get('status', export.envelope([], [], run_url, sha)) if restore_status else export.envelope(statuses, [], run_url, sha)
                export.pair(stage, 'status', status_env)
                export.merged_licences(stage)
                export.inventory(stage, run_url, sha, now)
                export.validate_bundle(stage)
                replace_directory(stage, out)
        diagnostic = dict(window=None, attempt=None, http_status=None, code=None)
        try:
            if reserve or budget_spent:
                hourly_queries(day, diagnostic)
                if budget_spent:
                    error = 'SOCIAL_CREDIT_CAP'
                    save()
                    return 'budget-spent'
            else:
                posts, provenance, limited = collect(day, ledger, run, key=x_key, send=send, sleep=sleep, now=clock_now, checkpoint=save, diagnostic=diagnostic)
                if limited and not provenance:
                    error = 'SOCIAL_CREDIT_CAP'
                else:
                    classified, exclusions = classify(posts, key=jev_key, send=send, diagnostic=diagnostic, enforce_bound=True, now=clock_now)
                    require_collection('social', clock_now())
                    # Judge the complete sample, not a prefix containing one odd post.
                    sent = len(posts) - exclusions['duplicate'] - exclusions['unsupported']
                    if exclusions['classification'] * 10 > sent:
                        diagnostic.update(diagnostic['last_exclusion'])
                        raise ValueError('SOCIAL_CLASSIFICATION_FAILED')
                    record = aggregate(day, posts, classified, exclusions, provenance, now)
                    record['provenance']['fixture'] = fixture
        except SunsetReached:
            run['closed'] = True
            save(restore_status=True)
            ended('social')
            return 'ended'
        except Exception as exc:
            code = diagnostic['code'] or diagnostic_code(exc, 'SOCIAL_UPSTREAM_FAILED')
            diagnostic['code'] = code
            print_diagnostic(diagnostic)
            error = 'SOCIAL_UPSTREAM_FAILED'
        else:
            if reserve:
                remaining = CAP - sum(r['reserved'] for r in ledger if r['day'] == budget_day)
                run['allocation'] = run['reserved'] = remaining // RESERVATION * RESERVATION
                if not run['reserved']:
                    error = 'SOCIAL_CREDIT_CAP'
                    run['closed'] = True
                save()
                return run['id'] if not error else error
        run['closed'] = True
        if frozen(clock_now()):
            record, error = None, 'SOCIAL_FROZEN'
        save()
        return error or 'ok'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--day')
    parser.add_argument('--now')
    parser.add_argument('--fixtures', action='store_true')
    parser.add_argument('--reserve', action='store_true')
    parser.add_argument('--reservation')
    parser.add_argument('--check-freeze', action='store_true')
    args = parser.parse_args()
    now = args.now or utc_now()
    from product.nz_election.pipeline.sunsets import skip
    if skip('social', now):
        return 'ended'
    if frozen(now):
        print('Social publication frozen until 19:00 NZDT on 7 November 2026.')
        return
    if args.check_freeze:
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write('allowed=true\n')
        return
    if not args.out:
        parser.error('--out is required')
    day = args.day or (datetime.fromisoformat(now.replace('Z', '+00:00')).astimezone(NZ).date() - timedelta(days=1)).isoformat()
    run_url = ('https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']) if os.environ.get('GITHUB_RUN_ID') else 'offline-verification'
    try:
        result = refresh_social(args.out, day, now=now, x_key=os.environ.get('X_UPSTREAM_KEY', ''), jev_key=os.environ.get('TYPESAFE_API_KEY', ''), send=fixture_send() if args.fixtures else transport, sleep=(lambda _: None) if args.fixtures else clock.sleep, fixture=args.fixtures, reserve=args.reserve, reservation=args.reservation, run_url=run_url, clock_now=(lambda: now) if args.now or args.fixtures else utc_now)
    except Exception:
        raise SystemExit('FAIL social: validation or storage failure') from None
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write('validated=true\n')
            if result.startswith('run-'):
                f.write('reservation=' + result + '\n')
    if result == 'ended':
        return
    if result not in {'ok', 'frozen', 'budget-spent'} and not result.startswith('run-'):
        raise SystemExit('FAIL social: ' + result)
    print('PASS social')


if __name__ == '__main__':
    main()
