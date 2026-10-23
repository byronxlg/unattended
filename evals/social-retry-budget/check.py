"""Offline retry at zero-based window 5, with a full reserved allocation."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path.cwd()))
from product.nz_election.pipeline import export, social

DAY, NOW = '2026-10-23', '2026-10-24T03:00:00Z'
upstream = social.fixture_send()
starts = [a for a, _ in social.windows(DAY)]
attempts = {}


def send(method, url, headers, payload):
    if method == 'GET':
        query = parse_qs(urlsplit(url).query)['query'][0]
        start = int(query.split('since_time:')[1].split()[0])
        window = starts.index(start)
        attempts[window] = attempts.get(window, 0) + 1
        if window == 5 and attempts[window] == 1:
            return 503, b'private upstream error'
    return upstream(method, url, headers, payload)


with TemporaryDirectory() as tmp:
    out = Path(tmp) / 'data'
    reservation = social.refresh_social(out, DAY, now=NOW, reserve=True, fixture=True)
    result = social.refresh_social(out, DAY, now=NOW, reservation=reservation,
                                   send=send, sleep=lambda _: None, fixture=True)
    envs = export.validate_bundle(out)
    rows = envs.get('social/daily', {}).get('data', [])
    hours = len(rows[0]['provenance']['windows']) if rows else 0
    run = envs['social/credits']['data'][0]
    status = envs['status']['data'][0]
    ok = (result == 'ok' and hours == 23 and run['spent'] == 7560
          and run['reserved'] == 7560 and run['requests'] == 24 and run['closed']
          and attempts == {i: 2 if i == 5 else 1 for i in range(23)}
          and rows[0]['sample']['eligible'] == 230
          and '23 of 24 hours sampled' in status['message']
          and status['error_code'] is None)
    print(f"{'PASS' if ok else 'FAIL'} retry budget: result={result}; {hours} of 24 hours sampled; requests={run['requests']}; reserved={run['reserved']}; spent={run['spent']}")
    raise SystemExit(0 if ok else 1)
