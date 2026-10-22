#!/usr/bin/env bash
# Expected: PASS model rotation: 240 classified, pinned model recorded
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from product.nz_election.pipeline import export, social

upstream = social.fixture_send()
requested = []
def send(method, url, headers, payload):
    status, raw = upstream(method, url, headers, payload)
    if method == 'POST':
        model = json.loads(payload)['model']
        requested.append(model)
        body = json.loads(raw)
        body['model'] = 'jev-1.14.0' if model == 'jev-latest' else model
        raw = json.dumps(body).encode()
    return status, raw

with TemporaryDirectory() as tmp:
    out = Path(tmp) / 'data'
    args = dict(now='2026-10-22T03:00:00Z', fixture=True)
    reservation = social.refresh_social(out, '2026-10-21', reserve=True, **args)
    result = social.refresh_social(out, '2026-10-21', reservation=reservation,
                                   send=send, sleep=lambda _: None, **args)
    if result != 'ok':
        print(f'FAIL model rotation: refresh returned {result}')
        raise SystemExit(1)
    row = export.validate_bundle(out)['social/daily']['data'][0]
    ok = (requested == ['jev-1.13.0'] * 240
          and row['model_versions'] == ['jev-1.13.0']
          and row['sample']['eligible'] == 240
          and row['sample']['exclusions']['classification'] == 0)
    print(f"{'PASS' if ok else 'FAIL'} model rotation: {row['sample']['eligible']} classified, pinned model recorded")
    raise SystemExit(0 if ok else 1)
PY
