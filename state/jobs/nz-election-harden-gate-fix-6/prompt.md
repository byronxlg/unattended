Fix round 6 on PR #83 (nz-election-harden-gate), same worktree and branch, head e04e72b. Tests on main at dc57e78 are
protected; this branch's own tests move with it. Commit, do not push.

Sixth fresh review, Important (check_workflow_history.py:233): a folded block scalar (`run: >-` or `>`) is joined with
spaces, so `python3`, blank line, `product/nz_election/pipeline/night_live.py` counts as the guard although YAML
decodes a newline there and bash runs two commands. Invariant, unchanged: the detector may under-recognise a guard,
never over-recognise one.

Fix it fail-closed and simply: do not reconstruct YAML folding yourself. Use the decoded string the YAML loader
returns for the run value, or, if the detector reads raw text, treat any folded block scalar as not guard evidence.
Add a regression for the case above (and `>` with a blank line) that fails on e04e72b. Real workflows in
.github/workflows must still classify as they do now.

Done when: uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py passes; the new regressions fail
with check_workflow_history.py at e04e72b; bin/lint prints lint ok. Report the commands and outputs in last.md
(uncommitted).
