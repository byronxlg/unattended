# look-a2 fix-1: two disclosure gaps from the fresh review (PR #35)

Same branch, same worktree. Fix only these two; commit; do not push.

1. Derived Others is not disclosed where it feeds displayed numbers (product/nz_election/pipeline/build.py:161 area).
   The headline seats, the averages and any chart built from rows whose Others was derived as the
   remainder must say so. Shape: one short footnote line on the affected module ("Others derived as
   100 minus the named parties for N of M polls; see sources") linking to the full list of affected
   polls on the sources/method page. Do not add per-figure inline citations to the main page (Byron,
   issue #34: references are flooding the main page). Invariant: no displayed number from a derived
   input without a visible disclosure on the same page.
2. The stale social band publishes sample counts without provenance or the synthetic-fixture notice
   (product/nz_election/pipeline/social_page.py:68). Fixture data must render its fixture notice and
   the source/input link next to the counts, as the populated page does.

Tests: add a test for each item. Tests on main at 85c3b14 are protected; this branch's own tests move
with it. Nothing weaker.

Done when: `uv run --with pytest pytest -q` passes, `bin/lint` ok, `python3 -m product.nz_election.verify all`
(or the repo's verify entry) PASS, harness PASS on 79 routes. Report the commands and output in last.md
(do not commit last.md).
