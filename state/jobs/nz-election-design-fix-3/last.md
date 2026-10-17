Committed `9b593cd` on `change/nz-election-design`. Not pushed; worktree clean.

Harness-only fix: after `check_page` finishes, invalid-link and changed-inputs re-navigate to their fixture URLs before the unchanged auto-waiting assertions. Every route retains the skip-link focus check. Invalid-count has no hash dependency and remains unchanged. No sleeps or skipped states.

Diff: `tests/screenshots.py`, 3 insertions.

Verification tails:

```text
pytest -q product/nz_election/tests
287 passed in 148.96s (0:02:28)

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (313 text files)
```

Screenshot harness not run in the sandbox. Host verification remains pending.