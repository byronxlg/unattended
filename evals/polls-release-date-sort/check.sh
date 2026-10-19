#!/usr/bin/env bash
# Offline verification with an in-memory row, never a fixture rewrite.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
import json
from pathlib import Path
from product.nz_election.pipeline.fixtures import captures
from product.nz_election.pipeline.models import ParseDrift
from product.nz_election.pipeline.poll_parser import parse_polls

root = Path('product/nz_election')
wikitext = captures()['wikipedia/polls-2026.wikitext'].decode()
mapping = json.loads((root / 'config/party-map.json').read_text())
identities = json.loads((root / 'config/poll-identities.json').read_text())
row = """|-
| data-sort-value="2026-10-20" |'''9–19 Oct 2026'''
|[https://www.thepost.co.nz/politics/361101225/ The Post/Freshwater Strategy]
| 1,458 || 27.6 || 28.7 || 14.3 || 9 || 11.8 || 2.0 || 5.4 || – || –
"""
anchor = '|-\n| data-sort-value="2026-10-14"'
assert wikitext.count(anchor) == 1
wikitext = wikitext.replace(anchor, row + anchor, 1)
try:
    result = parse_polls(wikitext, '1381086195', mapping, identities)
except ParseDrift as exc:
    print(f'FAIL parse_drift {exc.reason} {exc.public_locator}')
    raise SystemExit(1)
rows = [p for p in result.polls if p['pollster'] == 'freshwater'
        and p['fieldwork_start'] == '2026-10-09' and p['fieldwork_end'] == '2026-10-19']
assert len(result.polls) == 44 and len(rows) == 1
assert any(d['locator'] == rows[0]['source_ref'] and d['sort'] == '2026-10-20'
           and d['source'].endswith('1381086195') and d['reason']
           for d in result.diagnostics['date_exceptions'])
print('Fieldwork: 2026-10-09 to 2026-10-19 (offline verification)')
print('PASS release-date row parsed')
PY
