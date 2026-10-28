Verdict: **request changes**.

- **Important**: [advance_acceptance.py:28](/Users/byron/repos/unattended/.worktrees/nz-election-advance-acceptance/product/nz_election/pipeline/advance_acceptance.py:28) still accepts visually hidden sentences using the site’s own `.chart-data` class. `styles.css:376` clips this content to a 1px box; `home_graphics.py:32` uses it for hidden content. Wrapping either route’s count paragraph in `<div class="chart-data">` passes acceptance. Handle this hiding mechanism and add both-route regressions.

Read-only in-memory probes using `.venv/bin/python -B -c` produced:

```text
index.html inline ADVANCE_NOT_PUBLISHED
index.html chart-data PASS
vote/index.html inline ADVANCE_NOT_PUBLISHED
vote/index.html chart-data PASS
```

These isolate `check()` with mocked filesystem and bundle validation. Inline hiding is fixed; stylesheet hiding remains.

No additional findings in the full diff. Default verification remains opt-in, gap comparison rejects substituted counts, and runbook commands match the CLI.

Attempted targeted pytest via `uv run --offline --no-sync --with pytest pytest -q -p no:cacheprovider`; blocked before collection:

```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open file .../sdists-v9/.git:
Operation not permitted (os error 1)
```

No files changed.