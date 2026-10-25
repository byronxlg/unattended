Fix round 3 on PR #83 (change/nz-election-harden-gate, head 191c461). The third fresh review found one Important:

product/nz_election/tools/check_workflow_history.py:126 mishandles Bash ANSI-C quoting `$'...'`, where `\'` is an
escaped quote inside the string. This run body falsely declares the night guard:

    echo $'a\'
    python3 product/nz_election/pipeline/night_live.py
    #'

Bash exits 0 and only echoes; workflow_commands() yields night_live.py as an invocation, so history is wrongly exempted.

Invariant: guard and invocation evidence is only taken from text the checker is sure Bash executes as a command. Either
parse `$'...'` with its backslash escapes, or conservatively treat any line containing `$'` (and the rest of that run body
after it) as not evidence. No full shell parser needed; the conservative option is fine.

Constraints: tests on main at f5becd4 are protected; this branch's own tests may move with the fix. Add a regression
test with the case above that fails on 191c461. Commit in the worktree, do not push.

Done when:
  uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py   -> all pass
  the new test fails with check_workflow_history.py at 191c461
  bin/lint                                                                    -> lint ok
Write last.md: commit sha, the commands and their last lines.
