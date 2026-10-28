**Verdict: request changes.**

- **Important: unrelated operational state rollback** at `state/phase.md:1`, `state/next-run-after:1`, and `state/ledger.jsonl:486` (base). The supplied diff removes completed-job records, rolls back supervisor instructions, changes the next-run timestamp, and deletes two job briefs. Remove these unrelated changes, including corresponding journal/state-note deletions, from the PR.
- **Nits:** none.

The sunset fix itself looks correct:

- `product/nz_election/tools/check_workflow_history.py:403`: `stamp < sunset` excludes recovery at or after sunset without rounding. Earlier successes remain eligible.
- Other boundaries retain their existing comparisons, including inclusive two-hour recovery and strictly later-than-failure ordering.
- `collection_sunset` recognises only supported scripts with exactly one recognised argument; unsupported guards remain strict.
- `product/nz_election/tests/test_workflow_history_sunsets.py:120`: cases invoke the real `history.main`, mocking only the history response. Assertions distinguish unrecovered failures, coverage gaps, and valid recovery. The exact-sunset cases target the reported old defect directly.

Static review only, limited to the requested diff and `REVIEW.md`. Execution against `498932c` was not verified.