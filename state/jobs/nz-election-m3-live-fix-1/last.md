Committed `727561e`; not pushed.

Evidence confirms the handler calls fetch immediately on resume. Fixed the harness to await that specific request, preserving assertions for zero hidden requests and exactly one resume fetch.

- Required suite: **44 passed, 2 errors**, both Chromium sandbox launch failures.
- Synchronous-handler regression passes.
- Lint passes.

Host browser rerun remains required. `last.md` and artifacts remain uncommitted.