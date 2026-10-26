Committed `f728f4d`. Never pushed.

- `vote_page.py`: shorter deadlines, shared credits, resolved descriptions.
- `styles.css`: stacked help labels and answers.
- Updated `DESIGN.md` and stack-only credit tests.
- Report: [last.md](last.md), uncommitted.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py
3 failed, 144 passed in 36.24s

bin/lint
lint ok (1163 text files)
```

Failures: Chromium launch denied for `test_phone_rendered_type_and_targets[map]`, `[trend]`, `[header]`.

Screenshots at 390/1280 were also blocked by that sandbox denial. Visual review remains outstanding.