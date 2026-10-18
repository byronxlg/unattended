# Fix round 1 on change/nz-election-home (PR #29)

Same worktree, same branch, on top of 7e27c97. Commit here; never push. Three items: two from the
supervisor review and one from the fresh review (both on PR #29). Protected tests are the ones on
main at the base commit bb0690d: `git diff bb0690d..HEAD --stat -- product/nz_election/tests` shows
what this branch already moved. Lines this branch changed or added (test_home.py, the lines 7e27c97
changed in test_design.py and the others in that stat) are yours and move with the fix. Nothing may
end weaker than main.

## Item 1: the seat-strip legend is not overlapped at 360 and 390

On the home at 390x844 the seat strip's box outlines run down through the legend labels ("GRN 1|5"
is crossed by a vertical rule; empty outline boxes hang under NZF and Others). Invariant: no seat
box or rule paints over a legend label at 360, 390 and 1280. Fix in CSS or markup, your choice.
Verify: screenshots of the home at 360, 390 and 1280 that you look at, and say in last.md what you
saw in the legend region at each width.

## Item 2: the harness counts electorate entries, not every li in the directory

tests/screenshots.py:341 asserts `.electorate-directory li` == 71, which also counts the "Local polls
not matched" list, so the harness fails on populated artifacts (78). Pre-existing on main, explicitly
authorized here. Invariant: exactly 71 electorate entries in the directory; count those (build.py:413
gives them `id="electorate-<slug>"`, so `li[id^="electorate-"]` or equivalent), keep the 71, do not
drop or loosen the check.

## Item 3: /polls/ keeps the byte budgets main enforced on the explorer

Fresh review: test_design.py:112 (test_real_first_view_budget) now measures home only and checks
only that the explorer assets are present on /polls/; the transfer-byte and reserved-font budgets no
longer cover the explorer page. Invariant: moving the explorer page must not weaken main's checks.
Enforce the same CSS, FIRST_VIEW_GZIP_BYTES (< 100,000) and RESERVED_FONT_BUDGET (total + 45,000 <
100,000) assertions on both home and polls/index.html, with failure messages that name the page.
Verify: a test (or a temporary local probe described in last.md) shows an oversized explorer
dependency fails the polls assertion.

## Done

- `uv run --with pytest pytest -q` from the repo root: all pass, give the count.
- `bin/lint`: ok.
- The screenshot harness on a populated build: PASS, give the route and image counts.
- last.md: per item, what changed, where, and the verification output.
