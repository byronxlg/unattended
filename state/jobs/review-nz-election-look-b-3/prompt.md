Second fresh-context review of look-b, read-only. Worktree .worktrees/nz-election-look-b, branch
change/nz-election-look-b, head bb29173 on main 4987a93. PR #45 (`gh pr view 45 --comments`)
holds the first fresh design review (request changes: map table on electorates, map provenance and
empty source target, empty-module and Not reported absence with a gate, Port Waikato sentence) and
the supervisor reviews. Fix commit: git show bb29173. Judge against REVIEW.md and
intent/nz-election/design-principles.md. The engineer's account (.worktrees/nz-election-look-b/last.md)
is claims to check.

Host harness on bb29173: PASS 79 routes 296 images; screenshots in
.worktrees/nz-election-look-b/artifacts/lookb-r2-screenshots/ (home, electorates--port-waikato,
electorates--nelson at 390 and 1280 at least). Built site: /tmp/look-b/after/nz-election.

Check: (1) the four first-review items are fixed on every route they apply to (all 71 electorate
maps, Port Waikato, home closest-seat module, polls tables with absent samples); (2) the new gates
(EMPTY_PROVENANCE, EMPTY_MODULE, Not reported) would fail on 11c0421 and are not trivially
satisfiable; (3) the fix weakened no test on main at 4987a93 beyond the one permitted
test_average.py assertion; (4) nothing new regressed in the screenshots.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
