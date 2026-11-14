#!/usr/bin/env bash
# Expected: last line "PASS post-close build verifies". Builds the fixture bundle at
# 2026-11-08T06:01Z and runs the Pages acceptance (verify.py all) on it.
set -euo pipefail
cd "$(dirname "$0")/../.."
if uv run --with pytest pytest -q product/nz_election/tests/test_post_close_verify.py >/dev/null 2>&1; then
  echo 'PASS post-close build verifies'
else
  echo 'FAIL post-close build rejected by verify.py all'
  exit 1
fi
