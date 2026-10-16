# nz-election-2 fix 2: two Important findings from the second fresh review

Your fix at 2daec23 on change/nz-election-2 (PR #10) passed CI and cleared six of the first
review's items. A second fresh review (state/jobs/review-nz-election-2-2/last.md, also a PR #10
comment) found two Important items; both are confirmed by the supervisor against the code. Fix
both in this worktree, commit, do not push. Existing tests stay as they are; add a regression
test for each item in test_increment_two_regressions.py or a new file.

Read first: the review, product/nz_election/pipeline/publish.py lines 48 to 62,
product/nz_election/pipeline/build.py lines 55 to 60 and 226 to 250, export.py lines 10 to 40
(DERIVED, the status row shape, generated_at), intent/nz-election/spec.md line 257 and the
"Provenance and downloads" section.

The invariant and where it is enforced are named; you choose the shape. Check the change
against export.py's validators and every consumer of any field you touch.

1. publish.py:52 decides keep_data by `previous.last_success_at > proposed.last_success_at`,
   strictly. Two builds from the same unchanged capture share last_success_at even when their
   averages differ (the window moves with the build date). So: an 18 Oct success is in the
   repository; a 19 Oct attempt fails and its bundle still holds a 17 Oct build of the same
   capture; equality makes keep_data false, the 17 Oct files overwrite the 18 Oct files and
   last_good_run_url points at the older run. Invariant: the data files in the repository
   never move backwards in successful-generation order, independent of attempt chronology
   (item 3 of the previous fix stands: status always reports the latest attempt). The polls
   envelope already carries generated_at (export.py DERIVED); decide whether that, the
   build-manifest built_at, or a field on the status row is the ordering key, and whether a
   tie on acquisition time is broken by generation time or generation time alone is enough.
   State the rule in a comment at the comparison and in runbook.md. Regression: the review's
   case with equal last_success_at: result is not a replacement of the newer bundle, and the
   data files and last_good_run_url still match the 18 Oct build; the status row shows the
   19 Oct attempt and its failure.

2. build.py:244 renders `Retrieved (UTC)` with the raw fetched_at string. Spec line 257:
   timestamps are stored in UTC and rendered in Pacific/Auckland with the NZST or NZDT
   suffix; local_time() at build.py:55 already does this and other pages use it. Render the
   retrieval time through local_time; the full manifest record in the details block and the
   downloadable manifest keep UTC. Check the other `(UTC)` labels in build.py templates for
   the same drift. Regression: the rendered downloads page contains the Auckland-rendered
   time for the fixture catalogue and not the bare `Z` string in the summary field.

Definition of done: the eight commands of state/jobs/nz-election-2/prompt.md with their
expected outputs, pytest count above 207, bin/lint ok, `git status --short` empty. If
playwright cannot be resolved offline, paste the error and the supervisor runs the screenshots
on the host. Final message under 30 lines: per item what you changed and the test that proves
it, the eight outputs, departures, open questions.
