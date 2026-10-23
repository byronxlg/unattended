Committed `b7ac47e` on `change/nz-election-m3-live`.

Fixed a harness timestamp race: one synchronous fetch can occur 1 ms before the assertion’s timestamp. The harness now pauses the clock, preserves exact-one-fetch checks, and prints resume calls on failure. Host call values remain unknown.

Verification:
- Requested pytest: **49 passed, 2 errors**, both Chromium startup permission failures.
- Fix-2 regressions plus synchronous resume test: **3 passed**.
- Standalone browser: blocked by `MachPortRendezvous` permission denial.
- `bin/lint`: **lint ok (645 text files)**.

Evidence in `last.md`. Report and artifacts uncommitted; nothing pushed. Host browser rerun required.