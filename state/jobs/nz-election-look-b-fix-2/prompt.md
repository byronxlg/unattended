Fix round 2 on PR #45 (look-b), same worktree and branch, head 11c0421 on main 4987a93. The fresh
review requested changes; its full text is state/jobs/review-nz-election-look-b/last.md (main checkout,
also on the PR). Fix all four items:

1. Electorate pages: the map renders without the exact-value table and legend (snapshot_views.py:103).
   Every map keeps an accessible equivalent with exact values on every route that shows it.
2. Provenance: the map's Methods target credits only Stats NZ geometry (snapshot_views.py:115); link the
   EC results and Port Waikato snapshot sources and licences that the colours and margins come from.
   Port Waikato party votes reference source-baseline-2023, which resolves to an empty span
   (electorate_pages.py:104): point it at a target that carries provenance, and add a build check that
   every source reference on a page resolves to a non-empty provenance target.
3. Absent means absent (issue #40): an empty-data render still emits the "Closest on unchanged boundaries"
   heading with no rows (home.py:292), and build.py:381 renders "Not reported" for an absent sample size.
   Omit a module whose rows are empty (heading included) and omit the absent value. Extend the absent
   gate to catch an empty module heading, not only banned words, and show it failing on 11c0421.
   Contract that moves: test_average.py:52 pins display(None, 0) == 'Not reported'; it may change to the
   omission behaviour, with an assertion at least as strong (absent yields no text on the page).
4. Nit: Port Waikato says "Nineteen electorates are unchanged" (electorate_pages.py:73); make the boundary
   sentence seat-specific or omit it.

Constraints: no harness check loosened; other tests on main at 4987a93 unchanged; the branch's own tests
move with it. Do not commit last.md.

Done when, in the worktree:
- uv run --with pytest pytest -q product/nz_election  -> all pass
- bin/lint -> lint ok
- the populated build and screenshots.py harness PASS on 79 routes (as in fix-1)
- the new gate/provenance checks fail on 11c0421 and pass on HEAD (say the command and output)
Report in last.md: commits, each item and where, verification output.
