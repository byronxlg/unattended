# Follow-up 1: nz-election-backlog-nits (PR #119)

The fresh review found one Important, confirmed by the supervisor:

`product/nz_election/pipeline/funding_page.py:54` `headline()`, which `feed()` uses for the home
funding summary, still computes the leading party's total, rounding and return count itself
(`groups()`, `total()`, `whole_money()`), not from `funding_totals()`. The new test in
`product/nz_election/tests/test_funding_totals.py:32` compares `funding_bars()` with `ranking()`,
which is the same renderer twice, so it does not exercise the home summary.

Invariant: the home summary sentence and the funding/ ranking show the same leading party, the
same rounded total and the same return count, because both come from `funding_totals()`.

Do:
1. Route `headline()` (and anything else on the home summary that states a total or count) through
   `funding_totals()`. You choose the shape.
2. Change the branch's own test (it moves with the branch) so it renders the actual home summary
   via `feed()` (or `headline()` on loaded records) and the funding ranking, and asserts the leader,
   the displayed total and the count agree. Compare data values, not markup or class names.
3. Show the new test failing with `funding_page.py` at 80235df and passing at HEAD.

Constraints: tests on main at the base sha are not edited. Visible output of home and funding/
should be unchanged on the real snapshot (if it changes, say exactly what and why).

Done when, from the worktree:
`uv run --with pytest --with playwright pytest -q -k 'funding or design or home_graphics' product/nz_election/tests`
passes (Chromium cases may be sandbox-denied; list them), `bin/lint` prints ok, and you have
committed. Report the fail-at-80235df evidence in last.md.
