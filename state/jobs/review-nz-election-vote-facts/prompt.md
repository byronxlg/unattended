Fresh-context review of nz-election-vote-facts, read-only. Worktree .worktrees/nz-election-vote-facts,
branch change/nz-election-vote-facts, head eda2d3b on main d55b42e. PR #53 (`gh pr view 53`).
Diff: git diff d55b42e..eda2d3b. Judge against REVIEW.md, the brief state/jobs/nz-election-vote-facts/prompt.md
(main checkout) and the page plan intent/nz-election/pages/vote.md. The PR body is a claim to check.

Check: (1) spot-check at least five dates in snapshots/voting.json against their source URLs where reachable
(enrolment close, advance open, advance close, election day hours, telephone dictation registration); report
any mismatch with the source's wording; (2) every record has an EC-domain source and the loader rejects a
non-EC or spoofed domain; (3) no EC paragraphs copied verbatim beyond short factual phrases, given the EC terms;
(4) instants are correct Pacific/Auckland offsets (NZDT +13:00 from 27 Sep 2026); (5) the loader and tests are
offline and fail on malformed input; (6) no test on main weakened; (7) nothing invented to fill a gap.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
