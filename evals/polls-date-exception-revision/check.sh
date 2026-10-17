#!/usr/bin/env bash
# Expected: last line "PASS exception row parsed on revision 9999999999". Parses the pinned 2026
# fixture under a revision id that is not the fixture's, as the hourly refresh does after any
# Wikipedia edit, and expects the documented 1 News-Verian exception row to parse.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
import json
from pathlib import Path
from product.nz_election.pipeline.poll_parser import parse_polls
from product.nz_election.pipeline.models import ParseDrift
root = Path('product/nz_election')
wikitext = (root / 'fixtures/wikipedia/polls-2026.wikitext').read_text()
mapping = json.loads((root / 'config/party-map.json').read_text())
identities = json.loads((root / 'config/poll-identities.json').read_text()) if (root / 'config/poll-identities.json').exists() else {}
revision = '9999999999'
try:
    result = parse_polls(wikitext, revision, mapping, identities)
except ParseDrift as exc:
    print(f'FAIL parse_drift {exc.reason} {exc.locator!r} on revision {revision}')
    raise SystemExit(1)
rows = [p for p in result.polls if p['fieldwork_end'] == '2026-08-11' and p['fieldwork_start'] == '2026-08-08']
ok = bool(rows) and bool(result.diagnostics.get('date_exceptions'))
print(('PASS' if ok else 'FAIL') + f' exception row parsed on revision {revision}')
raise SystemExit(0 if ok else 1)
PY
