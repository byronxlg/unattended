Verdict: **request changes**.

- **Important**: `product/nz_election/tools/check_workflow_history.py:396` accepts a recovery success exactly at the sunset: `end <= stamp <= query_end` remains true when both bounds equal the deadline. With otherwise adequate coverage, a failure one second before sunset can incorrectly pass using an out-of-window success. Exclude the sunset instant from recovery evidence and add checker tests at deadline −1 second, deadline, and deadline +1 second.
- **Important**: `state/next-run-after:1`, `state/ledger.jsonl:486`, and `docs/journal.md:3743` contain unrelated scheduler changes and history deletions. The diff also deletes both build prompts. Remove these unrelated changes from the PR.

The implementation uses imported shared constants, preserves strict handling of the tested unrecognised guards, and clips expected intervals correctly. New history tests invoke the real `main` with injected clock and runner; static inspection indicates the base fails on the intended missing sunset exemption, not an incompatible API.

Read-only review of the diff and REVIEW.md. Tests not executed; no nit findings.