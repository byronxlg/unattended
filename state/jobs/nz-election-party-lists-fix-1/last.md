Committed `e9efa3d`; no push.

- Partial records with empty candidate lists now validate.
- Counts include linked EC source notes, licence, retrieval date and `aria-describedby`.
- Both regression tests failed on `6ebf8bb`. Protected tests unchanged.

Verification:
- Pytest: `1 failed, 116 passed`. Only `test_picker_chips_share_top_at_360` failed: sandbox denied Chromium launch.
- Campaign: `PASS campaign`.
- Lint: `lint ok (1087 text files)`.

`last.md` remains uncommitted. Screenshots assigned to supervisor.