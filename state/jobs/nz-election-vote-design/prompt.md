# Build: vote/ on the shared design system (design-backlog item 2, part 1)

Goal: bring the `vote/` page onto `product/nz_election/DESIGN.md` (tokens, page anatomy, components) the way night/ (PR #94) and the electorate pages (PR #98, in review) were. Advance voting is open (26 Oct to 6 Nov), so vote/ is the page most readers arrive at now.

Page plan: intent/nz-election/pages/vote.md. It sets what the page answers and in what order; DESIGN.md sets how it looks. Keep every question, answer, source and absence rule the plan and the current page have; this is a presentation change.

Read first: product/nz_election/DESIGN.md, intent/nz-election/pages/vote.md, the current vote page module and its template, snapshots/voting.json and its loader, the night/ page as merged on main (6fda184) as an example of the shared components, REVIEW.md pass 4.

Constraints:
- Data: only what voting.json and existing snapshots hold; no new upstream fetches. Never render "not available" style text: absent means absent (existing absent-text gates stay green).
- Dates and times in NZ time, as the page does now; the phase logic (before advance, advance open, election day, after) stays.
- Mobile first: at 390 the reader sees where and when to vote and the enrolment link above the fold; no sideways scroll at 360.
- Tests check data, provenance, absence and accessibility. Do not pin class names, markup order by class, SVG element counts or byte sizes. Tests on main at the base sha are protected; contracts that move with the registered set (route lists, heading sets) may move with a sentence in last.md saying why.
- Commit in the worktree, never push.

Definition of done (report each command and its output in last.md):
1. `uv run --with pytest pytest -q product/nz_election/tests` passes (Chromium tests included if present on the host).
2. `bin/lint` prints ok.
3. A build from fixtures passes `verify.py all`.
4. Screenshots of vote/ at 390 and 1280 in each phase the page has (use `--now` clocks before 26 Oct, 30 Oct, 7 Nov 10:00 NZDT, 8 Nov), saved under artifacts/ (untracked), and one sentence per screenshot on what the reader sees first.
