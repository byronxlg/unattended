# Fix brief: nz-election increment 6, three Important items from the fresh review

Same worktree `.worktrees/nz-election-6`, branch change/nz-election-6, your commit 7241c10 is pushed
as https://github.com/byronxlg/unattended/pull/14. Commit on top; never push, never rebase. The
supervisor's host run of 7241c10: verify all PASS, build 77 routes, screenshots PASS 77 routes,
pytest 336 passed and 1 failed (test_required_baseline_captures, file 21), lint ok.

Three Important findings, each confirmed by the supervisor reading the code. For each, the
invariant and where it is enforced; you choose the shape, then check your diff against the
enforcer and add a test that fails on 7241c10 and passes after.

1. Publish must let a bundle that gains sources advance. `pipeline/publish.py` around line 96
   forces keep_data when the source-id set differs between the published and incoming envelope
   (a rule inherited from the polls era; `test_contracts.py` around 144 covers only regressed
   timestamps). Consequence: once `ec-2023/candidate-votes-by-voting-place-21.csv` is captured, or
   a reviewed Wikipedia or Wikidata mapping lands, the baseline-2023 and candidates families can
   never publish. Invariant: published data never regresses (no source's fetched_at goes
   backwards, no source disappears); a bundle that keeps every published source at or after its
   published fetched_at and adds sources advances. Enforce in publish.py; prove with a test that
   takes the current baseline envelope, advances generated_at, adds file 21 to its sources and
   asserts the data is published, plus one that drops a source and asserts it is kept.
2. The missing-baseline check must not depend on Māngere staying missing. `verify.py` line 188
   and `tests/test_electorates.py` line 85 require "No candidate baseline" on the Māngere page.
   Invariant 5 of the build brief: a missing candidate-vote file yields "no candidate baseline"
   for that electorate and the page still renders. Use a controlled missing input (as the
   Te Tai Tonga check already does with `detail(row, {})`, or a fixture root with one file
   withheld) so the check passes both before and after file 21 arrives. The assertion stays as
   strong: a missing capture must still produce the message, and a present capture must not.
   Keep `test_required_baseline_captures` exactly as it is.
3. Repeated reviewed claims must preserve conflicts, not crash, and never replace official
   provenance. `pipeline/candidates.py` line 104 builds `dict(value=row[field], **field_sources[field][0])`
   while line 113 stores claims (which carry `value`) as the field sources, so a second mapping
   on the same field raises TypeError and aborts the daily refresh; a first agreeing mapping
   also overwrites the EC provenance. Invariants 1 and 3 of the brief, enforced by
   `test_official_spine_and_explicit_joins` and `test_conflicts_preserved`: official name and
   party keep their EC provenance whatever the mappings say; every claim is kept with its
   provenance; disagreement renders Unresolved. Extend `test_conflicts_preserved` with two
   mappings on one field (first agreeing, then differing) and assert the conflict lists all
   three claims with provenance and the official provenance survives.

Constraints: product code and tests only in these three areas; no capture, manifest, config or
registry edits; no assertion removed unless replaced by a stronger one on the same invariant
(say which in your report); stdlib only.

Definition of done (print the exact lines):
```
uv run product/nz_election/pipeline/verify.py all               # ends PASS all
uv run product/nz_election/pipeline/daily_refresh.py --out artifacts/nz-election/data   # PASS refresh: daily bundles
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election   # PASS build: 77 routes
uv run --with pytest pytest -q      # only test_required_baseline_captures fails; report the count (expect about 340)
bin/lint
```
Final report: the diff summary (files, insertions, deletions), the three fixes and the test that
proves each, any assertion changed and why it is not weaker, the verification output quoted.
