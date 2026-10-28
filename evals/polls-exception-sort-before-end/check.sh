#!/usr/bin/env bash
# Optional ref checks the same fixture and config with that ref's parser, offline.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - "${1:-}" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

from product.nz_election.pipeline import poll_parser
from product.nz_election.pipeline.models import ParseDrift

if sys.argv[1]:
    path = 'product/nz_election/pipeline/poll_parser.py'
    source = subprocess.check_output(['git', 'show', f'{sys.argv[1]}:{path}'], text=True)
    poll_parser = ModuleType('product.nz_election.pipeline.eval_parser')
    poll_parser.__package__ = 'product.nz_election.pipeline'
    exec(compile(source, path, 'exec'), poll_parser.__dict__)
mapping = json.loads(Path('product/nz_election/config/party-map.json').read_text())
text = Path('evals/polls-exception-sort-before-end/row.wikitext').read_text()
for revision in ('1382442932', '9999999999'):
    try:
        result = poll_parser.parse_polls(text, revision, mapping, {})
    except ParseDrift as exc:
        print(f'FAIL parse_drift {exc.reason} {exc.public_locator}')
        raise SystemExit(1)
    row, = result.polls
    assert row['pollster'] == 'reid-research'
    assert (row['fieldwork_start'], row['fieldwork_end']) == ('2026-10-20', '2026-10-26')
    diagnostic, = result.diagnostics['date_exceptions']
    exception, = [e for e in mapping['date_exceptions'] if e['sort'] == '2026-10-01']
    assert diagnostic == dict(exception, locator=row['source_ref'], kind='documented-exception')
print('Fieldwork: 2026-10-20 to 2026-10-26 (offline verification)')
print('PASS')
PY
