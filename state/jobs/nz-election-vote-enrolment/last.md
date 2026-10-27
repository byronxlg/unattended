Committed `06a1a8b`; not pushed.

- Updated `vote_page.py`: before-close copy unchanged; afterward, “The enrolment close has passed.” with the cited EC link.
- Added `test_vote_page_enrolment.py`. Regression tests fail on `1406aff`.
- [last.md](last.md) quotes both built answers; left uncommitted.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py
3 failed, 132 passed in 32.26s

bin/lint
lint ok (1145 text files)
```

Failures: `test_phone_rendered_type_and_targets[map]`, `[trend]`, `[header]`. Chromium launch denied by sandbox. Required screenshots were also blocked.

Open questions: none.