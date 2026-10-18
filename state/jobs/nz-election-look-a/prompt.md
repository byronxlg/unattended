# nz-election-look-a: the 538 look, site-wide (L-a)

Goal: restyle the NZ election site in the visual form of FiveThirtyEight's 2024 forecast page, per
`intent/nz-election/look-538.md` section L-a (copied into this worktree, uncommitted: commit it
as your first commit). Byron asked for this today (issue #32); UI is the priority. L-b (the
simulation) is NOT in scope: no probabilities, no "N out of 100" anywhere.

Read first: `intent/nz-election/look-538.md`, `intent/nz-election/design.md` (Tokens, Budgets and
checks), `intent/nz-election/home.md`, `product/nz_election/AGENTS.md`, `AGENTS.md`,
`product/nz_election/web/styles.css`, `product/nz_election/web/templates/base.html` and
`home.html`, `product/nz_election/tests/test_design.py`, `design_checks.py`, `screenshots.py`.

Constraints:
- Fonts: Libre Franklin 400/700 and one OFL mono, self-hosted woff2 subsets (Latin plus Latin
  Extended-A; check that the macron vowels render), OFL licence text committed beside them, no
  third-party font host. Fetch the font files with the network if the sandbox allows; if it does
  not, stop and say so in the final message with the exact files and URLs needed (the supervisor
  will supply them), do not substitute a system stack silently.
- No 538 or ABC marks, mascot, illustrations or copy. The home topline uses seats from the
  existing allocator, coloured by bloc, with the provenance note kept directly under it. Bloc
  membership comes from the existing coalitions config; a party with no statement is grey.
- Sticky section nav works without script; 44 px targets; reduced motion honoured.
- This is a build round: tests that pin the old font stack, token values, heading text or CSS
  budget figure move to the new values in the same commit, never weaker. The first-view 100 KB
  budget includes the fonts and does not move. CSS raw budget may move from 12 KB to at most
  16 KB; state the measured size. Contrast, axe and viewport checks keep their strength.
- Route set stays 79; no new data families.

Definition of done, in the worktree:
- `uv run product/nz_election/pipeline/verify.py all` ends with `PASS all`.
- The build prints `PASS build: 79 routes`.
- `uv run --with pytest pytest -q product/nz_election` passes; quote the summary line.
- `bin/lint` prints `lint ok`.
- Screenshots are host-run: name the commands (full harness, expected `PASS screenshots: 79
  routes, <N> images` with N derived; `--og-only`; `coalitions_browser.py`). The supervisor
  looks at home, polls/, one electorate page and night/ at 360, 390 and 1280.
- Final message: files changed, each pin moved (old to new with file:line), font files with sizes
  and licences, first-view bytes measured, CSS bytes, commands run with their output lines, any
  departure with the reason. Do not commit last.md.
