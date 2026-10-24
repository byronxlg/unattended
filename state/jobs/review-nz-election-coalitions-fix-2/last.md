**Verdict: request changes.**

- **Important**: [coalitions.mjs:166](product/nz_election/web/coalitions.mjs:166) restores reader-visible “Seats are unavailable”, conflicting with the stated absent-text rule. This is **not screen-reader-only**: `build.py:283` emits a normal paragraph, `styles.css:1` styles it at 20 px, and `coalitions.mjs:199` reveals its container. `aria-live` adds announcements; it does not hide text. The static absent-text gate misses this runtime insertion. Resolve the copy and regression expectation together.

- **Critical / Nit**: None.

Assertions remain unchanged, including unavailable-state, cleared-picture, and unassigned-count checks. The corrected routes match production: `/unattended/nz-election/coalitions.mjs` resolves `data/averages.json` and `data/seats.json` beside itself via `import.meta.url` at line 143.

Reviewed the requested diff at confirmed HEAD `78a9b94`. No files modified. Browser checks and REVIEW.md pass 4 screenshot assessment were not rerun; `PASS coalition browser` is host-reported and does not establish absent-text compliance.