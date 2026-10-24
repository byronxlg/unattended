Verdict: **accept**.

- Critical: none.
- Important: none.
- Nit: none.

No remaining route or staging reference to `coalitions.mjs`; Night retains its allocator dependency. Fragment aliases and replacement invariants remain intact. Server strip, TOP, and majority assertions are preserved. `SCRIPT_ALLOWLIST` is narrowed. No data-family, workflow, or page-copy changes found.

Direct read-only probes:
```text
PASS read-only probes: empty-page aliases, retired-script rejection, TOP/majority/overhang, landmark rejection
```

Full pytest/build verification was unavailable: uv cache access is blocked, and the existing virtualenv lacks pytest. No files changed.