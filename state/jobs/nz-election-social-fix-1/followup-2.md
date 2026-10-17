# Follow-up 2: fresh review of PR #25, two Important items

Same branch, same rules (fix job: no edits to pre-existing tests; new tests welcome; nothing
weakened). Commit on the branch, do not amend or push. Rewrite `last.md` with exact outputs and
leave it uncommitted.

1. Runtime length guard (`product/nz_election/pipeline/social.py`). The branch shortened the
   query but nothing in the code stops a longer one reaching the paid endpoint. Validate every
   fully composed query (the base phrases plus any window or operator suffix, exactly as sent)
   against the upstream limit of 512 characters before any credit reservation and before any
   transport call. Over the limit: raise a locally defined, allowlisted code
   `SOCIAL_QUERY_TOO_LONG` (add it to `DIAGNOSTIC_CODES`) so the run fails at the diagnostic
   print with zero paid requests and zero reserved credits. The limit is one named constant.
   Boundary tests in `test_social_diagnostics.py`: a 512 character query sends; 513 sends
   nothing, reserves nothing, and the diagnostic code is the new one.

2. Coverage of the dropped phrases. Restore `"New Zealand First"` (the party's full name; every
   other party keeps its full name, so dropping it would bias the comparison). Keep
   `"Opportunities Party"` (it matches both with and without "The"); do not restore
   `"Opportunity Party"`. Expected eval length: run `evals/social-query-length/check.sh` and
   report the number; it must stay at or under 512 with the guard's constant.
   In `social_page.py` add one sentence to the "How this sample was made" caption, after the
   sentence on the hourly windows: "The search matches each party's name and common short form
   as quoted phrases; the exact phrase list is recorded in each day's provenance." Confirm the
   provenance actually carries the query (the reviewer says it does); if it does not, say so in
   last.md instead of changing the sentence. Update `intent/nz-election/social.md` to match.
   Check `grep -rn "Opportunit\|Zealand First" product/nz_election/tests` first: if a
   pre-existing test pins the phrase list, do not edit it; report the conflict and stop.

Definition of done: `uv run --with pytest pytest -q product/nz_election/tests` all passed,
`evals/social-query-length/check.sh` PASS with the number, `evals/pages-verify-polls-only/check.sh`
PASS all, `bin/lint` ok, screenshots unaffected (caption text only).
