#!/usr/bin/env bash
# Expected: last line "PASS all". Runs the product pipeline against a polls-only bundle.
set -euo pipefail
cd "$(dirname "$0")/../.."
tmp=$(mktemp -d)
uv run product/nz_election/pipeline/refresh.py --fixtures --out "$tmp/data"
uv run product/nz_election/pipeline/build.py --data "$tmp/data" --out "$tmp/site/nz-election"
uv run product/nz_election/pipeline/verify.py all --data "$tmp/data" --site "$tmp/site"
