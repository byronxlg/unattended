# Fix 2 for PR #118 (advance publication acceptance)

Second fresh review (request changes), confirmed by its in-memory probe:

1. Important: `product/nz_election/pipeline/advance_acceptance.py:28` still accepts text hidden by the site's
   own stylesheet. `styles.css:376` clips `.chart-data` to a 1px box (used for hidden content, e.g.
   `home_graphics.py:32`). Wrapping either route's count paragraph in `<div class="chart-data">` yields PASS.
   Invariant: the count and date sentence counts only when a sighted reader can see it on both home and
   vote/. Fix-1 handled inline hiding; this round must cover every class in `styles.css` that hides or clips
   content (grep it for clip, clip-path, 1px, display:none, visibility, sr-only, visually-hidden, hidden), not
   only `.chart-data`. Choose the mechanism (a class list derived from or checked against styles.css, or a
   rendered check); say in last.md which classes you found and why the list cannot silently drift (for
   example a test that fails if styles.css gains a hiding rule the checker does not know).
   Add behavioural regressions on both routes for each hiding class found, rejected with the existing
   not-published code; the visible case still passes.

Constraints: fix job; tests on main at the PR's base sha are untouched; this branch's own tests may move with
the fix. Commit in the worktree, do not push.

Done when: the pytest command from your build round's last.md passes, the new cases fail with
advance_acceptance.py at 65fbef1, and `bin/lint` prints `lint ok`. Write commands and output in last.md.
