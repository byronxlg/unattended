# Follow-up 3: PR #88 CI red on a moved contract

CI on PR #88 fails in `product/nz_election/tests/test_coalitions.py`:
- `test_script_allowlist` (line 132) pins `SCRIPT_ALLOWLIST` to four names.
- `test_static_content_preserved` (line 154) pins the built `*.mjs` set to six names.

Your branch registers `home-live.mjs` in `pipeline/scripts.py`, so both contracts move with the
registered set (this is a build round's contract, not a weakened check). Authorized: add
`'home-live.mjs'` to exactly those two expected sets. Nothing else in that file changes; no other
test on main at 3ee6372 is edited; no product code changes unless a test shows it is needed.

Done when, from the worktree:
`uv run --with pytest pytest -q product/nz_election/tests/test_coalitions.py product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py`
reports 0 failed, and `bin/lint` prints `lint ok`. Commit on the branch; do not push; do not commit last.md or artifacts/.
