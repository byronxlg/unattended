Committed `196720e`. Not pushed.

- Fixed caption punctuation in `parties_page.py`; credit/licence links retained. Shared CSS unchanged.
- Added regression test; updated one pinned caption expectation.
- Parent-branch regression: `2 failed` as expected.
- Required pytest command: `1 failed, 330 passed, 2549 deselected`.
- Sole failure: `test_picker_chips_share_top_at_360`, Chromium blocked by sandbox permission denial.
- `bin/lint`: `lint ok (1088 text files)`.

Screenshots and browser target-size verification remain blocked. Details in `last.md`; report and artifacts are uncommitted.