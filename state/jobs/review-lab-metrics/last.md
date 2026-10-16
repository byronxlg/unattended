Timestamp comparisons can misclassify post-merge fixes, and the integration test breaks on normal ledger updates. The timestamp defect was reproduced; the full pytest command was blocked by read-only sandbox restrictions on uv's cache.

Full review comments:

- [P2] Compare parsed timestamps instead of ISO strings - /Users/byron/repos/unattended/.worktrees/lab-metrics/lab_metrics/compute.py:284-285
  When a fix starts within the same second as a merge but includes fractional seconds, this string comparison incorrectly excludes it. For example, a merge at `06:00:00Z` followed by a fix at `06:00:00.500Z` produces a 0% change failure rate because `.` sorts before `Z`. Compare parsed datetimes, or normalize timestamps to fixed precision, consistently across chronological comparisons and sorting.

- [P2] Keep fixed metric expectations independent of live state - /Users/byron/repos/unattended/.worktrees/lab-metrics/tests/test_metrics_integration.py:27-28
  This test collects the repository's mutable `state/` files but asserts today's exact totals. Recording the first implementation attempt for `lab-metrics`, for example, adds another eligible change and changes the mean rework from 17, failing CI without any metrics regression. Assert fixed numerical expectations against the frozen fixtures; keep the real-state integration test focused on runtime and output invariants.