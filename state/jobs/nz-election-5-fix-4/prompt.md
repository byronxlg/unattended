# Follow-up 4: nz-election increment 5, third fresh review findings

Same worktree `.worktrees/nz-election-5`, HEAD ec78040, on PR #13 (CI green on ec78040). The
third fresh-context review, scoped to fix 3, found two items in `tests/svg_budget.py`, both
confirmed as Important by the supervisor. Item 1 of fix 3 (registry binding) passed every probe
and is not in scope. Read first: `AGENTS.md`, `tests/svg_budget.py`,
`tests/test_contracts.py` (the svg budget tests), `intent/nz-election/plan-m2.md` line 172.

## 1. Important: CSS string, escape and comment parsing

Invariant (plan-m2 line 172, decision 7): the page budget counts every SVG the rendered page
needs; a reference that a browser would resolve must be counted. Two reviewer probes with a
six-byte SVG asset return 0 instead of 6:

    <style>x{background:url("../maps/a\"b.svg")}</style>
    <style>x{background:url("../maps/map.svg?x=/*")} /* real comment */</style>

The `url(...)` regex mishandles escaped quotes, and the comment stripper consumes quoted
content through the next comment terminator. Tokenise CSS strings, escapes and comments
together (a small hand-written scanner is fine; no new dependency). Regression tests, additions
only: both probes count 6; a real comment containing `url(x.svg)` still counts 0; the existing
CSS tests keep passing.

## 2. Important: SVG data URIs

Invariant as above. `url("data:image/svg+xml,...")` returns 0 although the browser renders an
SVG of arbitrary size. Either count the decoded bytes (percent-encoded and base64 forms) or
reject the form with a clear assertion so an author cannot use it unbudgeted. Choose, say
which, and cover both encodings in the tests. Non-SVG data URIs (png, woff) are not SVG budget
and must not crash the scanner.

## Constraints

- Tests: additions only. Existing assertions stay. Budget constants unchanged.
- Product code and fixtures untouched; this fix is confined to tests/svg_budget.py and tests.
- Commit in the worktree; do not push.

## Definition of done

From the worktree:

    uv run --with pytest pytest -q product/nz_election/tests    # all pass, count up from 222
    git diff ec78040 --stat                                     # tests/ only, no removed lines
    uv run product/nz_election/pipeline/verify.py all           # PASS all

Report: commit hash, test count, which tests you added, the data URI decision, and the
electorates page byte total (expected 284,316, unchanged).
