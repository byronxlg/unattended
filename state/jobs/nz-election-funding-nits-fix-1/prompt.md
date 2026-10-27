Follow-up 1 on PR #109 (fresh review request changes). Same worktree and branch; commit, do not push.

1. Important: funding/ at 1280x800 fails the page-plan question test (intent/nz-election/pages/funding.md): the
   heading "When did the money arrive?" starts near y=782, so its answer sentence and the pace graphic are below the
   first screen. Reduce vertical space above it (intro, biggest-donor link block, ranking spacing; styles.css near
   :534 and the page markup) so the pace answer sentence and the top of its graphic are visible at 1280x800. Keep
   DESIGN.md tokens; do not shrink text below the 16 px reading floor. At 390 the order stays as the plan sets it.
2. Nit (if it fits the same edit): at 390, tighten the space around the biggest-donor link so the ranking starts
   sooner.

Do not consolidate ranking() with home_graphics.funding_bars() in this round. Tests check data and behaviour, not
markup, class names or pixel positions; no new layout pins. Main's tests at origin/main are untouched; this
branch's own tests may move with the change.
Verify: uv run --with pytest pytest -q product/nz_election/tests -k "funding or home or design" (Chromium launches
may be sandbox-denied; list them) and bin/lint (expect "lint ok"). Report the commit sha and, if you could measure
it, the y of the pace answer at 1280x800.
