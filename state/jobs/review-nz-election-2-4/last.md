No findings in `33b906b..61d405e`. No approval issued.

- All operational timestamp fields used by this increment are covered. Stem-specific validation prevents date-only status/manifest observations from reaching consumers.
- The regex plus `datetime.fromisoformat` guarantees valid, timezone-aware UTC instants. Values are rejected, never silently rewritten.
- Real fixture metadata and normalized poll/average rows remain valid. Publication comments and runbook match the implementation.
- All 23 tests would fail against `33b906b`, by diff analysis. Some fail because older validation raises a different error. The rendering test actually switches `TZ` and calls `tzset()`; its naive-input rejection distinguishes the old implementation.
- Changes are limited to timestamp validation, consumers/producers, documentation and the new tests.

Read-only `python3 -B -c` reproductions printed:
```text
PASS: 10 generated_at cases accepted by old code, rejected by HEAD
Fixture time keys: captured_at, timestamp
PASS: fixture manifest and real normalized polls/averages accepted
PASS: Auckland summer/winter rendering under both host TZ settings
PASS: generic date allowance cannot bypass status instant validation
```

`git diff 33b906b..61d405e --stat -- '*test*'`:
```text
 product/nz_election/tests/test_timestamp_canon.py | 133 ++++++++++++++++++++++
 1 file changed, 133 insertions(+)
```

Full suite not rerun in the read-only sandbox; host results supplied by the supervisor remain the full verification evidence.

Important findings: 0