# Remove the Fleet Audit product from main

Worktree `.worktrees/remove-fleet-audit`, branch `change/remove-fleet-audit`. Commit there;
never push. Read `intent/README.md` and `state/phase.md` first: Byron rejected Fleet Audit as
the product on 2026-10-16 (GitHub issue #7), so the product code leaves `main` by PR while
the history, the posts, the intent folder and the lessons stay.

## Goal

Delete `product/fleet_audit/` (and `product/` if nothing is left) and `runbook/fleet/` (the
lab's own declaration for that tool), and make everything that referred to them true again.
Do not touch `intent/`, `posts/`, `state/`, `evals/`, `docs/`, or the "Known agent mistakes"
section of `CLAUDE.md` (history stays). `lab_metrics/` is unrelated and stays.

## Invariant and where it is enforced

After the change, no file outside `intent/`, `posts/`, `state/`, `docs/` and the Known agent
mistakes section of `CLAUDE.md` mentions `fleet_audit`, `product/fleet_audit`, `runbook/fleet`
or the fleet audit commands. Check with:
`rg -n "fleet_audit|fleet-audit|runbook/fleet|Fleet Audit" --glob '!intent/**' --glob '!posts/**' --glob '!state/**' --glob '!docs/**' .`
which must print only the Known agent mistakes lines in `CLAUDE.md`. Expect references in
`CLAUDE.md` (Layout: `product/` line now says what it will hold, the NZ election web app from
phase 4), `AGENTS.md`, `runbook/README.md`, `runbook/updates.md`, `.github/workflows/ci.yml`
(its test guard looks for `product/tests`; keep the guard correct with no product tests
present, root tests must still run) and `tests/test_metrics_integration.py` (read what it
asserts about the workflow before editing; change only what the deletion makes false).
Fix tasks never weaken checks: if a root test exists only to exercise the product, delete
it with the product and say so; do not skip or loosen it.

## Definition of done

From the worktree root: `uv run --with pytest pytest -q` with zero failures (84 or fewer
tests, say how many); `bin/lint` printing `lint ok`; the rg command above printing only the
CLAUDE.md Known agent mistakes lines; `git status --short` empty; `du -sh product` either
absent or under 100 KB. Final message under 15 lines: commit hash, each command and its
output, anything you could not do.
