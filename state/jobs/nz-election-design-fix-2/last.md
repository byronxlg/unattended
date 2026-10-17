Committed `33eb475` on `change/nz-election-design`. Not pushed; worktree clean.

The race was latent. `git diff main...HEAD -- coalitions.mjs` changes only `picture()` (`@@ -89,39 +89,61 @@`). `start()` and module startup match main byte for byte: main line 138 awaits data loading before `restore()` at line 186.

Changed only `tests/screenshots.py`: invalid-link, invalid-count, and changed-inputs now use auto-waiting `expect(...).to_contain_text(...)`, preserving all three asserted strings. No sleeps or skipped states.

Requested command tails:

```text
uv run --with pytest pytest -q product/nz_election/tests
287 passed in 141.89s (0:02:21)

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS build: 77 routes
PASS all

bin/lint
lint ok (313 text files)
```

Screenshot harness not run in the sandbox. Host verification remains pending.