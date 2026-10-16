# nz-election-4 fix: one Important finding and one documentation nit from the fresh review

Branch change/nz-election-4 at 7dca242 (PR #12). Commit on the branch, do not push. Fix job
rules: no existing test changes; add regression tests; nothing weakens a check.

## Important: stale unassigned text on an unresolved allocation

product/nz_election/web/coalitions.mjs:153 `draw()`: when `scenario()` returns no seats (no
eligible party, or a tie that needs a recorded lot result), the function returns before
`[data-unassigned]` is rewritten, so the electorate count shown is the previous scenario's.
Reproduction from the review: votes `{a:239, b:1, others:0}`, zero electorate wins, then give
`b` one electorate: unassigned goes 71 to 70, the text still says 71.

Invariant: every visible number on the page describes the current state. `[data-unassigned]`
depends only on the counts, not on the seat allocation, so it must be correct whether or not
seats are available. Choose the shape (compute it before the early return, or have
`scenario()` return the unassigned count alongside the error). Check that the Python twin
(pipeline/coalitions.py) reports the same unassigned count for the no-seats case if it reports
one at all, so parity stays byte-exact; do not change what the Python twin emits unless the
JS twin needs it to agree.

Regression test: add a browser check in tests/coalitions_browser.py (host-run) that drives the
no-seats path and asserts the unassigned text, and a Python or runner test if the scenario
output changes. Existing tests untouched.

## Nit: say precisely what validate_scripts enforces

pipeline/scripts.py is a filename allowlist (two named same-origin modules under PREFIX, type
module, no inline content, no other script). The supervisor's review brief described it as
a hash allowlist; that was the brief's error, not yours. Make the module docstring and the
enforcer row in product/nz_election/coalitions.md state exactly what is checked and where the
module bytes come from (build.py copies product/nz_election/web/*.mjs from the code checkout,
reviewed by PR). No hashing of modules is required.

## Definition of done

```
uv run --with pytest pytest -q                       # all pass, count >= 252 plus new tests
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election
uv run product/nz_election/pipeline/verify.py all    # PASS all
bin/lint                                             # lint ok
git diff 7dca242 --stat -- '*test*'                  # only additions, no existing test changed
```
Chromium does not start in your sandbox: the supervisor runs coalitions_browser.py and
screenshots.py on the host. Report the commit, the test count, and the exact lines changed in
coalitions.mjs.
