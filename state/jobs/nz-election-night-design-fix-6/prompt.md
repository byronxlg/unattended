# PR #94 fix-6: CI red on main's disclosure gate

CI run 40307082449 on 51c94ce... (branch head) failed 3 tests, all on main's contracts:

- product/nz_election/tests/test_disclosures.py::test_non_home_disclosures_hold_tables:
  `PROSE_DISCLOSURE: night/index.html:23: details requires a table` (pipeline/disclosure_checks.py:33).
  The night page now renders a `<details>` with prose. Invariant (design-principles.md, enforced by
  disclosure_checks.py): on non-home routes a disclosure holds a table; prose is shown open, not
  collapsed. Choose the shape: render the content open, or make it a table if it is tabular.
- product/nz_election/tests/test_verify_required.py:30 and :53: `FAIL all: CAMPAIGN_DATA`. Likely the
  same build failure surfacing through verify; confirm, and fix the cause if it is separate.

Also: main moved (PR #97 hexmap merged 2fa5be9, touches pipeline/home_graphics.py and the shared hex
map). Merge origin/main into the branch (no rebase, no force-push), resolve so night/ uses the
hex-native layout from main.

Constraints: fix job. Do not edit tests on main at 2fa5be9. Nothing weakens a check.

Done when, in the worktree:
`uv run --with pytest pytest -q product/nz_election/tests/test_disclosures.py product/nz_election/tests/test_verify_required.py product/nz_election/tests/test_night_page.py product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py`
passes (browser tests may skip in the sandbox; say which), `bin/lint` ok, committed on the branch.
Write last.md with the commit, the test output tail and what changed.
