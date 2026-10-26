Fresh-context review of PR #94 (nz-election-night-design), read-only. Worktree .worktrees/nz-election-night-design,
branch change/nz-election-night-design, head 18ab8ef on main 51c94ce. Diff: git diff 51c94ce...18ab8ef.
Judge against REVIEW.md, including pass 4 against intent/nz-election/pages/night.md and product/nz_election/DESIGN.md.

The change: night/ moved onto the shared design system: seat hemicycle with bloc totals, minimal-majority cards,
shared hex-map geometry and tones from home_graphics.py, title-case candidate display names (source records
unchanged), ribbon and timeline removed live once results arrive, sticky electorate column, replay hook order.
Check: seat totals, bloc grouping and majority figure come from the data and agree with the parser (House 122,
62 for a majority on the 2023 replay); display-name transform never changes matching or parity checks; the
s197 freeze notice, the before-results order (countdown and vote/ link first, per pages/night.md) and the aria-live
region survive; live removal of pre-night content cannot remove results; the updated assertions (test_night_page,
test_night_review, test_waterfall, night_scheduler.test.mjs) moved presentation only and nothing that checked data,
provenance, absence or accessibility was weakened; no horizontal overflow at 360/390 (long names, tables, cards).
Supervisor host run: origin/data build PASS build: 81 routes; screenshots night and home at 390 and 1280 at
/tmp/nd/shots/{night,home}-{390,1280}.png (read them). Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
