Fresh-context review of PR #99 (nz-election-vote-design), read-only. Worktree .worktrees/nz-election-vote-design,
branch change/nz-election-vote-design, head 995ac4b. Diff: git diff origin/main...995ac4b. Judge against REVIEW.md
(pass 4 included). Brief: state/jobs/nz-election-vote-design/prompt.md; page plan intent/nz-election/pages/vote.md;
design product/nz_election/DESIGN.md.

Claimed: presentation only (vote_page.py, home.py shared prose modules, styles.css, DESIGN.md); no tests or contracts
changed; content parity across phases (before, advance, election, after) and absence variants. Check: no words, links,
dates or provenance lost in any phase; absent data stays absent; page-plan question order holds; shared modules in home.py
do not change other pages' content; no test pins markup; DESIGN.md matches what the CSS does; accessibility (headings,
targets, contrast tokens).

Supervisor host screenshots of vote/ on an origin/data build at 2026-10-26T21:00Z are at /tmp/vd-shots/vote-390.png and
vote-1280.png (read them if you can). Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
