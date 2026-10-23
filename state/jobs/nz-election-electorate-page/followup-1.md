Fix round 1 on PR #67 (this branch; tests on main at e32e60e are protected, this branch's own tests move with it).

Supervisor looked at wellington-north, te-tai-tonga, port-waikato at 390x844 and 1280x800 on a build from data d7b8db9. Fix:

1. The provenance line "Data to 20 October 2026. Sources and method" renders twice in a row under the locator on every electorate page. One line only. Add a check (test or content check) that fails on de641c1's output for a repeated adjacent provenance line on an electorate page.
2. Candidate names display in the EC sheet form "APPLEBY, Michael". Readers expect "Michael Appleby". Display the reconciled snapshot name (records[].matched[].snapshot_name) or an equivalent given-then-family form with the EC's case restored; keep the EC form only where the source record is shown. Sort order unchanged (family name).
3. Nit: snapshot_views.py:130 Methods text still describes square tiles on detail pages, which this change removes. Make it true.

Not changing: incumbency stays from candidates-2026 with its explicit source flag (the reconciliation snapshot carries no incumbency field; accepted on the PR).

Done when: pytest for the electorate tests passes, `verify.py all` PASS on a populated build, bin/lint ok, the new check fails on de641c1 and passes on HEAD. Commit in the worktree; do not commit last.md.
