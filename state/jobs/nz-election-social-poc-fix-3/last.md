Committed **`a794765`**, not pushed or amended.

- Identical publication retries succeed without changing the ledger.
- Zero-request handled stops publish; conflicting spend reports remain rejected.
- Budget date is rechecked after checkpointing, immediately before transport.

Verification:
- **342 tests passed** in 176.77s.
- Three new regression tests failed on `0642382` and now pass.
- Fixture pipeline: **78 routes**, **PASS social**, **PASS all**.
- Lint: **lint ok (349 text files)**.

Only `publish.py`, `social.py`, and the new test file changed. Existing tests, wording, and workflows remain unchanged. Evidence is in untracked [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-social-poc/last.md).