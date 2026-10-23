**Verdict: request changes.**

**Critical:** None identified.

**Important**

- `product/nz_election/pipeline/route_checks.py:42`: The whole PR weakens the base check requiring the night publication-freeze notice. It now compares against the new renderer, which omits that notice. The unchanged `test_home_routes.py:33` still tests the unused old renderer, so it passes without protecting the published page. Preserve the original requirement in the active rendering path and gate.

- `last.md:81`: Required browser and visual acceptance remains incomplete. No 390×844 or 1280×800 screenshots exist; the implementation report records Chromium launch failures. Run the browser harness and inspect both viewport sizes before acceptance.

The six fix-2 changes otherwise look substantive: Chromium installation and mandatory browser-test invocation; phase ordering with boundary coverage; explicit archive/frame labels; transition-only announcements; complete-document XML parity cases; and the shared `ABSENT_TEXT` gate. Electorate detail is explicitly deferred by the brief.

Verification:
- `node --test product/nz_election/tests/night_scheduler.test.mjs`: **1 pass, 0 fail, 0 skipped**.
- Read-only phase probe: `PASS phase boundary: 8 cases`.
- Placeholder probe: `ABSENT_TEXT: night: not available`.
- Focused pytest and `bin/lint`: blocked by read-only uv cache permissions.

**Nit:** None. No files changed.