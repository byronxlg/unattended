# nz-election-2 fix 3: timestamp canon, two Important findings from the third fresh review

Your fix at 33b906b on change/nz-election-2 (PR #10) passed CI and the host run. A third fresh
review (state/jobs/review-nz-election-2-3/last.md, also a PR #10 comment) found two Important
items. The supervisor confirms both and reads them as one root cause. Fix in this worktree,
commit, do not push. Existing tests stay as they are; add regression tests in
test_generation_provenance.py or a new file.

Root cause: export.py's validators accept any string datetime.fromisoformat parses for the
operational timestamps (fetched_at, generated_at, last_attempt_at, last_success_at, and any
other instant in an envelope, manifest or status row), including naive values, other offsets
and fractional seconds. publish.py:63 compares last_attempt_at as strings and success_order
parses and compares; build.py:56 local_time renders. All of them assume the one form
refresh.py utc_now() emits (YYYY-MM-DDTHH:MM:SSZ). Data on the data branch is the trust
boundary: it may come from an older or newer pipeline version or a hand edit.

Invariant: every operational timestamp that enters the pipeline through validate_envelope or
validate_bundle is a UTC instant in exactly one canonical form, so that string order equals
instant order and rendering is host-independent. Enforce it at the validator with a clear
error code (see the error contract in AGENTS.md), and make the producers unable to emit
anything else. Poll observation and fieldwork fields are dates, not instants; they stay
date-only. Once the validator enforces the canon, decide whether publish.py compares strings
or parsed values; either is sound, but say which in the comment at the comparison and keep
runbook.md true.

Reproductions to turn into tests (each must fail on 33b906b):
1. Repository attempt 2026-10-17T01:00:00Z, incoming failed attempt
   2026-10-17T01:00:00.100000Z or any non-canonical form: today publish returns
   older-run-retained and loses the newer failure. After the fix the value is rejected at
   validation (or, if you choose to canonicalise instead of reject, the newer failure wins and
   the status row reports it).
2. generated_at 2026-10-17T01:00:00 (naive) passes validate_envelope today; after the fix it
   does not. local_time on a canonical value renders the same on a UTC host and an Auckland
   host (test with TZ set both ways or by asserting against a fixed expected string).

Read first: the review, export.py lines 47 to 90 and 147 to 200, refresh.py utc_now and every
place it builds a status row, publish.py success_order and the keep_data/keep_status block,
build.py local_time and observation_label, product/nz_election/runbook.md around line 68.

Definition of done: the eight commands of state/jobs/nz-election-2/prompt.md with their
expected outputs, pytest count above 209, bin/lint ok, `git status --short` empty. The
screenshots command may fail offline on Playwright; paste the error and the supervisor runs
it on the host. Final message under 30 lines: what you changed, the tests that prove it,
the eight outputs, departures, open questions.
