Fresh-context review of PR #87 (nz-election-party-lists), read-only. Worktree .worktrees/nz-election-party-lists,
branch change/nz-election-party-lists, head 6ebf8bb. Diff: git diff origin/main...6ebf8bb.
Judge against REVIEW.md, including pass 4 (the question test) against intent/nz-election/pages/parties.md.

The change adds EC party list sizes and the confirmed top five list candidates to the party snapshot, its validator
in pipeline/snapshots.py, the parties renderer and tests. Check: every list size and name traces to an EC source URL
recorded in the snapshot; an unconfirmed field renders nothing (no "not available" text); the validator rejects
malformed ranks, counts that disagree with the candidate list, and off-domain sources; no test on main at the base sha
was weakened (test_parties_page.py changed four lines; say whether each move is legitimate).
Supervisor host run on 6ebf8bb: test_parties*.py and test_snapshots*.py 111 passed incl. Chromium. Do not run pytest;
read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
