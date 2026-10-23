Second fresh-context review of nz-election-vote-page, read-only. Worktree .worktrees/nz-election-vote-page,
branch change/nz-election-vote-page, head 3360258 (fix-1 on 3228381). PR #57 (`gh pr view 57 --comments`) has the
first review and the supervisor's notes. Diff: git diff main...3360258. Judge against REVIEW.md (question test in
pass 4 first), intent/nz-election/pages/vote.md and the brief state/jobs/nz-election-vote-page/prompt.md.

Check first the two items fix-1 addressed: (a) the answer-3 harness check now fails when answer 3 is hidden,
clipped or outside the viewport, not only on its bottom coordinate (find the fixture that proves it fails);
(b) answer-3 guidance text is rendered from snapshots/voting.json, not hardcoded in vote_page.py. Then a full pass:
nothing on main at the base sha weakened, no invented facts, no "not available" text, EC domains only for official
links, NZ-midnight transition at 26 Oct tested both sides.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
