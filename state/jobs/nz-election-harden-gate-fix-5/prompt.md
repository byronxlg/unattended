Fix-5 on PR #83 (nz-election-harden-gate), same worktree and branch, head dcf467d. Fix job: tests on main at dc57e78
are not edited; this branch's own tests may move.

Fifth fresh review, Important, confirmed: check_workflow_history.py:179 accepts `run: "python3\rproduct/nz_election/pipeline/night_live.py"`.
YAML decodes a carriage return; shlex treats it as whitespace and records the guard; Bash treats it as part of the
command word and never runs the script. History check exits 0.

Invariant (unchanged): the detector may under-recognise a guard, never over-recognise one. Close the class, not the
instance: before tokenising, a run step whose text contains any character outside printable ASCII plus space, tab and
newline (so CR, VT, FF, NUL, non-ASCII, other control characters) yields no guard evidence for that whole step, the
same fail-closed path fix-4 uses. Also make the tokeniser's whitespace set exactly space, tab, newline so shlex and
Bash agree on the remainder.

Tests: regressions for \r, \v, \f, \x00 and a non-ASCII space (U+00A0) between python3 and the script path, each
not guard evidence; they fail with check_workflow_history.py at dcf467d. The real workflows still classify as before.

Done: `uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py` all pass; `bin/lint` prints
`lint ok`. Commit in the worktree, do not push; report in last.md (do not commit it).
