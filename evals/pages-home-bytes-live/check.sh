#!/usr/bin/env bash
# Build the site from the data branch at the commit that broke Pages and run the deploy gate.
set -euo pipefail
root=$(git rev-parse --show-toplevel)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$root" fetch -q origin data
mkdir -p "$tmp/data"
git -C "$root" archive d7b8db903ba4e354f995afc9bd53d12f9d992139 | tar -x -C "$tmp/data"
cd "$root"
uv run product/nz_election/pipeline/build.py --data "$tmp/data/product/nz_election/data" --out "$tmp/site/nz-election" >/dev/null
uv run product/nz_election/pipeline/verify.py all --site "$tmp/site/nz-election" | tail -1
echo "PASS home under budget on data d7b8db903ba4e354f995afc9bd53d12f9d992139"
