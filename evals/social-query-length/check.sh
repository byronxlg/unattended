#!/usr/bin/env bash
# Expected: last line "PASS query length <n> of 512". Composes every hourly query of a sample day
# the way collect() does and checks the upstream's 512 character limit.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
from product.nz_election.pipeline import social
longest = max(len(social.QUERY + f' since_time:{s} until_time:{e}') for s, e in social.windows('2026-11-07'))
print(('PASS' if longest <= 512 else 'FAIL') + f' query length {longest} of 512')
raise SystemExit(0 if longest <= 512 else 1)
PY
