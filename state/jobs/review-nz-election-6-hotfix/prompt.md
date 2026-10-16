Fresh-context review of a hotfix, read-only. Worktree .worktrees/nz-election-6-hotfix, branch
change/nz-election-6-hotfix, one commit on top of main (git diff main...HEAD). Judge it against
REVIEW.md passes 1 to 3 (no web files touched, so no design pass).

Context: production incident. Pages runs failed at "Verify election pages" with
VERIFY_FAILED: supplied daily families because the data branch publishes only the polls family
until increment 7. Invariant the fix must restore: deploy whenever the published data validates;
unpublished families render their empty state and are not demanded by the verifier; published
families keep every existing check (candidate coverage, 72 baselines). A fix job may not edit
existing tests.

Check specifically: (1) does any existing check get weaker for a bundle that does contain the
family; (2) does export.validate_bundle still reject malformed bundles the same way; (3) are
the nine new tests in product/nz_election/tests/test_verify_supplied.py meaningful (would they
fail on main at 47f229e); (4) does build.py already render the documented empty state for the
absent families, or did the verifier mask a build gap; (5) anything else in REVIEW.md.

Report: findings labelled Important or Nit with file:line, then a last line
"Important findings: N". No emojis, no em dashes.
