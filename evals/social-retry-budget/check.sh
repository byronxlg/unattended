#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
cd "${1:-$script_dir/../..}"
uv run python "$script_dir/check.py"
