"""Bounded, serial acquisition from approved Wikipedia and Gamma API endpoints."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.client import HTTPException
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from . import export

TITLE = 'Opinion polling for the 2026 New Zealand general election'
USER_AGENT = 'unattended-lab/0.1 (https://github.com/byronxlg/unattended)'
URL = 'https://en.wikipedia.org/w/api.php?' + urlencode(dict(
    action='query', prop='revisions', titles=TITLE, rvprop='ids|timestamp|content',
    rvslots='main', format='json', formatversion=2, maxlag=5))
LIMIT = 2 * 1024 * 1024
MAX_DELAY = 60


class FetchError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A redirect must never expand the source host allowlist.
        return None


def http(request, *, timeout):
    from .deployment_guard import require_publication_allowed
    require_publication_allowed()
    return build_opener(NoRedirect()).open(request, timeout=timeout)


def delay(headers, attempt, now):
    value = headers.get('Retry-After')
    if value is None:
        return 2 ** attempt
    try:
        if value.isascii() and value.isdecimal():
            seconds = int(value) if len(value) < 10 else MAX_DELAY + 1
        else:
            instant = parsedate_to_datetime(value)
            if instant.tzinfo is None:
                raise ValueError
            seconds = max(0, (instant - now()).total_seconds())
    except (ValueError, TypeError, OverflowError, AttributeError):
        raise FetchError('INVALID_RETRY_AFTER') from None
    if seconds > MAX_DELAY:
        raise FetchError('RETRY_AFTER_EXCESSIVE')
    return seconds


def decode(raw, title=TITLE):
    try:
        # Oversized integer tokens remain invalid revision values without hitting Python's digit limit.
        body = json.loads(raw, parse_int=lambda value: int(value) if len(value) < 21 else value)
        if isinstance(body, dict) and body.get('error', {}).get('code') == 'maxlag':
            raise FetchError('MAXLAG')
        pages = body['query']['pages']
        if not isinstance(pages, list) or len(pages) != 1:
            raise FetchError('WRONG_PAGE')
        page = pages[0]
        if page['title'] != title or type(page['ns']) is not int or page['ns'] != 0 or 'missing' in page:
            raise FetchError('WRONG_PAGE')
        revisions = page['revisions']
        if not isinstance(revisions, list) or len(revisions) != 1:
            raise FetchError('INVALID_REVISION')
        revision = revisions[0]
        if not isinstance(revision, dict) or type(revision.get('revid')) is not int or not 0 < revision['revid'] < 2 ** 63:
            raise FetchError('INVALID_REVISION')
        stamp = export.timestamp(revision.get('timestamp'), 'revision.timestamp')
        slot = revision['slots']['main']
        if slot['contentmodel'] != 'wikitext' or not isinstance(slot['content'], str) or not slot['content'].strip():
            raise FetchError('INVALID_CONTENT')
        return dict(revision=str(revision['revid']), timestamp=stamp, wikitext=slot['content'])
    except FetchError:
        raise
    except ValueError as exc:
        code = 'INVALID_TIMESTAMP' if str(exc).startswith('INVALID_TIMESTAMP') else 'INVALID_RESPONSE'
        raise FetchError(code) from None
    except (KeyError, TypeError, AttributeError, IndexError):
        raise FetchError('INVALID_RESPONSE') from None


CANDIDATE_TITLE = 'Candidates in the 2026 New Zealand general election by electorate'
CANDIDATE_URL = 'https://en.wikipedia.org/w/api.php?' + urlencode(dict(
    action='query', prop='revisions', titles=CANDIDATE_TITLE, rvprop='ids|timestamp|content',
    rvslots='main', format='json', formatversion=2, maxlag=5))


def gamma_url(slug):
    from .markets import events
    if slug not in {e['slug'] for e in events()}:
        raise FetchError('UNAPPROVED_SOURCE')
    return 'https://gamma-api.polymarket.com/events?' + urlencode({'slug': slug})


def acquire(transport=http, *, sleep=time.sleep, now=lambda: datetime.now(timezone.utc), url=URL):
    from .markets import events
    gamma_urls = {gamma_url(e['slug']) for e in events()}
    if url not in {URL, CANDIDATE_URL} | gamma_urls:
        raise FetchError('UNAPPROVED_SOURCE')
    for attempt in range(3):
        headers = {}
        try:
            with transport(Request(url, headers={'User-Agent': USER_AGENT}), timeout=20) as response:
                headers = response.headers
                status = response.status
                if status != 200:
                    raise HTTPError(url, status, 'HTTP failure', headers, None)
                length = headers.get('Content-Length')
                if length is not None and length.isdecimal() and (len(length) > 10 or int(length) > LIMIT):
                    raise FetchError('RESPONSE_TOO_LARGE')
                raw = response.read(LIMIT + 1)
                if len(raw) > LIMIT:
                    raise FetchError('RESPONSE_TOO_LARGE')
                result = dict(raw=raw) if url in gamma_urls else decode(raw, CANDIDATE_TITLE if url == CANDIDATE_URL else TITLE)
                result['fetched_at'] = export.timestamp(now().isoformat(timespec='seconds').replace('+00:00', 'Z'))
                return result
        except HTTPError as exc:
            headers = exc.headers or {}
            exc.close()
            if exc.code not in {429, 500, 502, 503, 504}:
                raise FetchError('HTTP_REJECTED') from None
            error = 'HTTP_RETRIES_EXHAUSTED'
        except (URLError, TimeoutError, OSError, HTTPException):
            error = 'HTTP_RETRIES_EXHAUSTED'
        except FetchError as exc:
            if exc.code != 'MAXLAG':
                raise
            error = 'MAXLAG_RETRIES_EXHAUSTED'
        if attempt == 2:
            raise FetchError(error)
        sleep(delay(headers, attempt, now))


NIGHT_ROOTS = ('https://media.election.net.nz/xml/', 'https://mediademo.electionresults.govt.nz/xml/')


def night_xml(root, path, *, transport=http, sleep=time.sleep, now=lambda: datetime.now(timezone.utc)):
    """Only reviewed EC paths; no redirects, bounded bodies, serial caller."""
    import re
    if root not in NIGHT_ROOTS or not re.fullmatch(r'(?:electorates|parties|candidates|election)\.xml|e(0[1-9]|[1-6][0-9]|7[012])/e\1\.xml', path):
        raise FetchError('UNAPPROVED_SOURCE')
    if root == NIGHT_ROOTS[0] and path == 'e72/e72.xml':
        raise FetchError('UNAPPROVED_SOURCE')
    url = root + path
    for attempt in range(3):
        headers = {}
        try:
            with transport(Request(url, headers={'User-Agent': USER_AGENT}), timeout=20) as response:
                headers = response.headers
                if response.status != 200:
                    raise HTTPError(url, response.status, 'EC fetch failed', headers, None)
                raw = response.read(LIMIT + 1)
                if len(raw) > 2_000_000:
                    raise FetchError('RESPONSE_TOO_LARGE')
                return raw
        except HTTPError as exc:
            headers = exc.headers or {}
            exc.close()
            if exc.code not in {429, 500, 502, 503, 504}:
                raise FetchError('HTTP_REJECTED') from None
        except (URLError, TimeoutError, OSError, HTTPException):
            pass
        if attempt == 2:
            raise FetchError('HTTP_RETRIES_EXHAUSTED')
        sleep(delay(headers, attempt, now))


def deployed_data_sha(transport=http):
    """Read durable Pages evidence; unavailable or malformed evidence never confirms a deploy."""
    import re
    url = 'https://byronxlg.github.io/unattended/nz-election/build-manifest.json'
    request = Request(url + '?reconcile=' + str(time.time_ns()), headers={'Cache-Control': 'no-cache', 'User-Agent': USER_AGENT})
    try:
        with transport(request, timeout=20) as response:
            if response.status != 200:
                return None
            raw = response.read(LIMIT + 1)
            if len(raw) > LIMIT:
                return None
            sha = json.loads(raw)['data']['data_sha']
            return sha if isinstance(sha, str) and re.fullmatch(r'[0-9a-f]{40}', sha) else None
    except (ValueError, KeyError, TypeError, URLError, OSError, HTTPException):
        return None
