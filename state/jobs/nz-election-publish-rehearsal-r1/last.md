Committed `9ac171a`. No push.

Seven files add the isolated rehearsal workflow, shared orchestration, recovery tests, and runbook instructions. Fixed the staged relative-path bug.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py
72 passed in 53.75s

bin/lint
lint ok (1119 text files)
```

- Two new tests fail against `origin/main` as expected.
- Workflow YAML parses using uv/PyYAML.
- Local CLI: `PASS publication rehearsal`.

Actions proof remains for supervisor dispatch after merge. Details in [last.md](last.md); report and artifacts remain uncommitted.