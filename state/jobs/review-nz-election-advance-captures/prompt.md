Fresh-context review of PR #116 (nz-election-advance-captures), read-only. Worktree .worktrees/nz-election-advance-captures,
branch change/nz-election-advance-captures, base origin/main. Diff: git diff origin/main...HEAD -- product/
(fixtures/manifest.json bytes fields, runbook/advance.md, tests/test_advance_2026.py, tests/test_contracts.py). Judge against REVIEW.md.

Goal of the change: registering the next daily 2026 advance transcription (a new capture file plus its manifest entry)
must not require editing any test. Check: the replaced count pin in test_contracts.py is not weaker than what it replaced
(registered set equals files on disk, digests and byte lengths); the 2026 advance assertions still pin the original
26 and 27 Oct figures exactly; nothing lets an unregistered or mis-hashed capture pass; the runbook steps for a daily
transcription are complete and true. Supervisor host evidence: pytest test_advance_2026.py test_contracts.py 40 passed;
Codex reported 168 passed with a third capture registered on a throwaway copy, tests unchanged.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
