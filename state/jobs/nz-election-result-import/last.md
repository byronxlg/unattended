Committed `3309ff2`; not pushed.

Added dispatch-only result imports, leased night rollback, refusal checks, tests, and exact runbook commands.

Verification:
- Required suite: `1 failed, 133 passed`. Existing browser test blocked by Chromium sandbox permission denial.
- Import/history checks: `108 passed`.
- Final contract checks: `9 passed`.
- Lint: `lint ok (1059 text files)`.
- YAML parse: exit 0 using repository environment.

Commands, outputs, refusal codes, and outstanding verification are in [last.md](last.md), uncommitted. Full acceptance still requires the browser check on an unrestricted runner.