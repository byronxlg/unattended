Fix-4 on PR #83 (fourth fresh review, request changes). Head d406b7f.

Finding (confirmed): check_workflow_history.py:151 splits unquoted newlines into commands without tracking enclosing
shell constructs. A night_live.py path inside a bash array literal `args=( ... )`, an uncalled function body, and
similar constructs count as a guard invocation, so active_intervals() returns [] and missing history is exempted.

This is the fourth round of the same class: guard evidence read from shell text. Stop adding cases. Invariant:
the detector fails closed. A run body is guard evidence only when the invocation is a top-level simple command
(nesting depth zero: not inside ( ), { }, an array literal, a function definition, $( ), backticks, a heredoc, an
if/for/while/case body, or after && / || / | in a way you cannot prove executes). Any construct the detector does not
fully understand makes that step NOT guard evidence. A false negative (a real guard treated as absent) is acceptable
and must surface as the existing history failure, never as an exemption. Check the repo's real workflows still
classify as they do today (the hourly and night-live workflows on main), and say in last.md if any real guard is
now treated as absent.

Tests: append regressions for the array literal, the uncalled function, and at least two other enclosing constructs
(subshell, if-body or heredoc); each must fail with check_workflow_history.py at d406b7f. Tests on main at f5becd4 are
protected; this branch's own tests may move only if the fail-closed rule changes their expected outcome, and say which.

Done: uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py passes; the new regressions fail on
d406b7f's check_workflow_history.py; bin/lint ok. Commit in the worktree, do not push, do not commit last.md.
