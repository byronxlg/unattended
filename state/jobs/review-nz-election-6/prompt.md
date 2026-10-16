Fresh-context review of the build commit on branch change/nz-election-6 (NZ election increment 6:
candidates, 2023 baselines, enrolment, electorate polls and 71 electorate detail pages). Worktree
.worktrees/nz-election-6, read-only. Follow REVIEW.md. Important or Nit, at most five nits, nothing
bin/lint reports. Do not approve.

Scope: `git diff 3f49469..7241c10 -- product ':!product/nz_election/fixtures'` (pipeline, web,
tests, config; about 1,400 lines). 3f49469 is the supervisor's inputs commit (captures, manifest,
config/ec-party-lists-2026.json); do not review the captures themselves. The build brief is
state/jobs/nz-election-6/prompt.md on main; its "Invariants" section names nine invariants and the
test that enforces each. Plan: intent/nz-election/plan-m2.md ("Data contracts and family
boundaries", "Candidates, baselines and electorate pages", "Supervisor decisions" 5 to 8 and 10).

Check, in this order:
1. Each of the nine invariants: find the enforcing test, confirm it tests the invariant rather than
   the happy path, then look for a code path the test misses. Especially: candidates.py creating a
   row from Wikipedia or Wikidata alone; any join by surname, similarity or row position; baseline.py
   adding an explicit electorate total row to voting-place sums or double counting; Port Waikato
   (deferred 2023 contest) rendered as zero instead of absent; Māngere (file 21 absent in this
   worktree) crashing a build or validator instead of yielding "no candidate baseline".
2. Successor comparisons: old electorates listed separately, never summed; unresolved shown.
3. Enrolment: the report says electorate values are null, national totals only. Is that what the
   capture actually contains, or a parser gap? Read fixtures/ec-2026/wayback-enrolment-general.html
   (1546 lines) enough to say which.
4. Date-only observations: an explicit schema extension, with canonical instant validation untouched
   elsewhere (export.py envelope and validators, test_timestamp_canon.py).
5. Hourly families and outputs unchanged (refresh.py, daily_refresh.py, decision 6).
6. electorate.html and styles.css: the missing-data state, the unresolved state, keyboard reachability
   of the map links, no inline event handlers; whether export.py or publish.py could emit a route
   with user-influenced or unescaped text.
7. config/electorate-aliases.json: every mapping an exact NFC match to the registry name; none
   fuzzy. propose-mappings: confirm the build never reads the proposal file.
8. Sandbox run if the read-only sandbox allows: `uv run --with pytest pytest -q` (expected: only
   test_required_baseline_captures fails, on file 21); `uv run product/nz_election/pipeline/verify.py all`.
   Say what you could not run.

Report: the diff you read, each check with its evidence (file:line, commands and output), Important
findings with a reproduction, nits, and "Important findings: N" as the last line.
