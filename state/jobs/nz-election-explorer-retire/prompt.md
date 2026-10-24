# nz-election-explorer-retire: retire the dead coalition explorer client path

Page plan: intent/nz-election/pages/polls.md

## Goal
Since PR #71 (170bf94) no route renders the interactive coalition explorer: polls/ keeps only
anchor spans (`polls_page.py:88` aliases) and no page loads `coalitions.mjs`. So
`product/nz_election/tests/coalitions_browser.py` times out waiting for `#coalition-explorer
fieldset` on main, and the client strip in `web/coalitions.mjs` is dead code shipped to the site.
The accepted page plan for polls/ does not list the explorer, so it does not come back. Retire the
dead path; keep every live behaviour and every old fragment.

## Read first
`intent/nz-election/pages/polls.md`, `AGENTS.md`, `product/nz_election/pipeline/build.py`
(around 276-300 and 635), `pipeline/scripts.py` (SCRIPT_ALLOWLIST), `pipeline/home_checks.py:24-28`,
`pipeline/landmark_checks.py:12`, `pipeline/verify.py:143`, `pipeline/polls_page.py:88`,
`tests/coalitions_browser.py`, `tests/coalitions_runner.mjs`, `tools/render_coalition.mjs`,
`tests/test_coalitions.py`, `tests/test_polls_refine.py`, `runbook.md:311`, `coalitions.md`.

## Constraints
- Old URL fragments on polls/ stay resolvable (`coalition-explorer`, `coalition-title`,
  `source-history`, `source-average` and the rest of the aliases). The harness BROKEN_FRAGMENT check
  must still pass.
- The server-rendered seat strip and its labels (TOP for The Opportunity Party, build.strip) stay,
  with their tests. The allocator (`allocator.mjs`) stays if any route still loads it; check before
  removing anything.
- Verify checks that require the explorer (`verify.py:143`, home_checks legacy inventory,
  landmark_checks) are retargeted to what the page actually renders now, not deleted without a
  replacement: each retired check names the invariant that replaces it, or says in the PR body why
  the invariant no longer exists.
- Tests that pin the client explorer move with the retired code (this is a build round, not a fix
  round); tests on main that pin server output do not weaken.
- No changes to data families, workflows or page copy.

## Done when
- `rg -n 'coalitions\.mjs' product/nz_election` returns only history notes (coalitions.md, design
  docs) or nothing; no built route references it; it is not copied into the stage.
- `uv run --with pytest pytest -q product/nz_election` passes (Chromium may be missing in your
  sandbox; say which tests you could not run).
- `bin/lint` prints ok.
- A build from fixtures passes `verify.py all`.
- Commit on change/nz-election-explorer-retire; do not commit last.md. Report the files removed,
  each retargeted check and its replacement invariant, and the test counts.
