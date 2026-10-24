# Fix: publish.py temporary checkout cleanup flake

Branch `change/nz-election-publish-cleanup` in `.worktrees/nz-election-publish-cleanup`, from main.

Read first: `AGENTS.md`, `product/nz_election/pipeline/publish.py` (the `tempfile.TemporaryDirectory(prefix='nz-publish-')`
block near line 62) and its tests.

Symptom: CI on PR #69 (2026-10-23 17:1xZ) failed once in a publish test that the PR did not touch: the
TemporaryDirectory cleanup raised because `<tmp>/.git` was "not empty" while being removed. The rerun passed. Likely a
git background writer in the throwaway checkout (auto gc / maintenance / detached processes) racing `shutil.rmtree`.

Goal: the throwaway checkout can no longer race its own cleanup. Prefer removing the cause (configure the checkout so
git does no background or automatic work: e.g. `gc.auto 0`, `maintenance.auto false`, `gc.autoDetach false`, set
right after `git init`), and only then consider tolerant cleanup; if you add tolerant cleanup, it must not hide a
failure of the publication itself.

Constraints: this is a fix job; tests on main at the base sha are not edited. Add a test that the checkout config
disables automatic gc/maintenance (or whatever your fix relies on). No other behaviour changes.

Definition of done, in last.md (uncommitted):
- `uv run --with pytest pytest -q product/nz_election/tests -k publish` passes; run it 5 times in a loop and report 5 of 5.
- `uv run --with pytest pytest -q product` all pass (name any Chromium-only sandbox failures).
- `bin/lint` prints `lint ok`.
Commit on the branch; never push; do not commit last.md.
