Committed `3360258`; not pushed.

- Strengthened answer-3 visibility, viewport bounds and text checks.
- Rendered guidance from snapshot summaries.
- Hidden fixture fails; visible fixture passes. Snapshot correction tests pass.

Verification:
- `uv run --with pytest pytest -q product`: **1466 passed**
- `bin/lint`: **lint ok (576 text files)**

Evidence recorded in uncommitted `last.md`. No open questions.