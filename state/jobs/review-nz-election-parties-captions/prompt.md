Fresh-context review of PR #89 (nz-election-parties-captions), read-only. Worktree .worktrees/nz-election-parties-captions,
branch change/nz-election-parties-captions, head 3b513a4 on main 6366d90. Diff: git diff origin/main...3b513a4.
Judge against REVIEW.md, including pass 4 (the question test) against intent/nz-election/pages/parties.md.

The change: party source captions (leader photo author, licence, changes) render as sentences, so an empty field leaves
no orphan separator or period. Check: no caption on parties/ can render a leading, trailing or doubled separator or
period for any combination of empty fields; licence text that already ends in a period is not doubled; the pinned
assertion moved in test_parties_refine.py still checks the visible parts exactly (not weakened, only the format);
test_parties_captions.py would fail on main 6366d90; nothing else on parties/ changed.
Supervisor host run on 3b513a4: pytest -k parties 79 passed, bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
