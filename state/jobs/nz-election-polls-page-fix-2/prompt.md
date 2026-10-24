# PR #71 fix-2 (fix job on the open PR; Page plan: intent/nz-election/pages/polls.md)

Two items. Tests on main at 382c962 do not change; this branch's own tests move with it if needed. Nothing weaker.

1. Host screenshot harness on 93696cc (populated build from origin/data) fails:
   `screenshots.py:209 AssertionError: STRIP_HEIGHT`. The last screenshot written before the
   failure was `home-1280x800.png`, so the failing page is home at 1280 or the route after it.
   Reproduce with `uv run --with pytest product/nz_election/tests/screenshots.py --site <build> --out <dir>`,
   name the route, viewport and measured height in last.md, and fix the page (not the check).
   Say whether the same route fails on 382c962 (main); if it does, still fix it here.
2. Fresh review (Important): visual verification incomplete. After item 1, run the full harness to
   PASS and look at polls/ at 390x844 and 1280: both "change since" answers above the 390 fold,
   neutral connectors, single footnote period, seats reachable within one scroll. List the image
   paths in last.md.

Done when: full harness prints PASS for every route, pytest for product/nz_election passes, `bin/lint` ok,
commit in the worktree, no last.md or artifacts committed.
