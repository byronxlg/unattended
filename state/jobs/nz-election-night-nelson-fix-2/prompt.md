# nz-election-night-nelson fix-2 (PR #132, fresh review request changes)

Same branch, same worktree. Two test items from the fresh review; product code should not need to change.

1. `product/nz_election/tests/night_design_browser.py:81` now asserts only absence plus "2023 final count". Restore a positive browser check: the dated label `Source XML captured at <capture timestamp>.` is visible on night/, with the timestamp derived from the replay source's capture metadata (the manifest or source record the page reads), not a literal string. Keep the absence check for the removed 2024 date.
2. `product/nz_election/tests/test_night_page.py:335` positively pins `2024-11-10T00:00:00`. Replace with a before/after comparison: the source data the renderer reads is unchanged by rendering (deep copy before, compare after), and the rendered page does not show that date. No literal 2024 timestamp in the test.

Constraints: tests on main at the PR's base stay as they are, except the `night_design_browser.py:81` block this branch already moved; the branch's own tests move. `night_deployed.py:284` invariant unchanged. No markup or class-name pins.

Done when, in the worktree:
- `uv run --with pytest --with playwright pytest -q product/nz_election/tests -k 'night or electorate or design'` reports 0 failed (Chromium cases may be sandbox-denied for you; say which).
- `bin/lint` ok.
- Commit on the branch; do not push. Report the commit sha and the two changed assertions in last.md.
