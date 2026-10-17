#!/usr/bin/env bash
# Expected: last line "PASS query length <n> of 512". Composes every hourly query of a sample day
# the way collect() does and checks the upstream's 512 character limit.
set -euo pipefail
cd "$(dirname "$0")/../.."
uv run python - <<'PY'
from product.nz_election.pipeline import social
longest = max(len(query) for _, _, query in social.hourly_queries('2026-11-07'))
print(('PASS' if longest <= social.MAX_QUERY_LENGTH else 'FAIL') + f' query length {longest} of {social.MAX_QUERY_LENGTH}')
raise SystemExit(0 if longest <= social.MAX_QUERY_LENGTH else 1)
PY
