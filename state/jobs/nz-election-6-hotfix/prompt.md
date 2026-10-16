Hotfix for a production incident. Worktree .worktrees/nz-election-6-hotfix, branch
change/nz-election-6-hotfix from main 47f229e. Commit there, do not push.

Incident: since increment 6 merged (379d93a), every Pages run fails at "Verify election pages"
(runs 38972492825 and 38972584106):
```text
uv run product/nz_election/pipeline/verify.py all --data _nz-election-data/product/nz_election/data --site site
ValueError: VERIFY_FAILED: supplied daily families
```
The data branch holds only the hourly polls family. No workflow publishes the daily families
(candidates, baseline-2023, enrolment, electorate-polls, geography) until increment 7 lands the
daily workflow. verify.py main() (lines 211 to 216) requires every daily family in the supplied
bundle whenever the check is candidates, electorates or all. The build step before it succeeded,
so build.py already renders the no-data state for absent families; the verifier contradicts it.

Invariant to restore: the Pages build deploys whenever the published data validates; a family
that has never been published renders its documented empty state, and the verifier checks only
the families the supplied bundle contains. Where that invariant is enforced today: build.py for
rendering (read how it treats a missing family), export.validate_bundle for the bundle, and the
verifier's supplied-bundle block. Choose the shape; the tests say what must hold:

1. verify.py all --data <polls-only bundle> --site <built site> passes, and the site's electorate
   routes exist and show the no-data state for candidates and baselines (whatever wording
   electorate.html already uses for a missing family; do not invent new copy).
2. verify.py all --data <bundle with every family> keeps every existing requirement (coverage,
   72 baselines) unchanged.
3. A bundle that contains the candidates family but fails coverage still fails. Weaken nothing.

Read first: product/nz_election/pipeline/verify.py, build.py (missing-family handling),
export.py (FAMILIES, NEW_FIELDS, validate_bundle), .github/workflows/pages.yml lines 90 to 125,
tests/test_electorates.py and tests/test_contracts.py (patterns for controlled bundles).

Rules: fix job, so existing tests are not edited; add tests only (a polls-only bundle case for
the verifier and a build case). No product copy changes, no workflow changes. No emojis, no em
dashes.

Definition of done, run on the host with expected output:
```text
uv run --with pytest pytest -q product/nz_election/tests        -> all passed, 0 failed, count 344 plus your additions
uv run product/nz_election/pipeline/verify.py all                -> PASS all
uv run product/nz_election/pipeline/refresh.py --out /tmp/polls-only && uv run product/nz_election/pipeline/build.py --data /tmp/polls-only --out /tmp/site-po && uv run product/nz_election/pipeline/verify.py all --data /tmp/polls-only --site /tmp/site-po  -> PASS all
bin/lint                                                         -> lint ok
```
If refresh.py's flags differ, use the real ones and say so. Report: the shape you chose, the
diff stat, the four command tails, and what you could not run in the sandbox.
