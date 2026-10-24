Committed `deecb15`. Not pushed.

- Added actionable messages for tied allocations and no qualifying parties.
- Updated only the authorized assertion; added the shared `ABSENT_TEXT` gate before it.
- Preserved all other assertions.

Verification:
- Browser harness: `CHROMIUM_REQUIRED` launch denial.
- Browser mutation run: same launch denial; new wording restored.
- Supplemental Node mutation: `ABSENT_TEXT: coalition runtime data-live: unavailable`.
- Absent-presentation tests: `11 passed in 4.68s`.
- Lint: `lint ok (829 text files)`.

Host browser verification remains outstanding. Updated `last.md`, left uncommitted.