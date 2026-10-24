# polls/ fix-1 (PR #71), on this build thread

Page plan: intent/nz-election/pages/polls.md. Fix job on an open PR. Tests on main at the base sha are
protected; this branch's own tests move with the change. Nothing weaker.

Three lists, one round:

1. Supervisor (host screenshots 390/1280 on an origin/data build):
   - Trend label leader lines run from each series' last point down to the stacked labels, so ACT,
     Opportunity and Te Pati Maori read as falling to zero after 24 Oct. Labels must not look like data:
     visually separate connectors from observations and averages (gap plus short neutral tick, or the
     label at the series value). The helper is pipeline/home_charts.py:133; if you change it, home's
     trend must still pass its own checks. Add a check that fails on 280b2c2.
   - 'Wikipedia contributors.' passed to footnote() gives a double period (polls_page.py:59 and :73,
     and any other caller): fix at the call or in footnote(), with a test.
2. Fresh review (Important): question 2 fails at 390x844: only National's change is readable above the
   fold; Labour's change and the trend are below. Put a readable change summary for the leading parties
   (at least National and Labour, points and since-date) above the 390 fold, or compact the layout.
   screenshots.py:323 only checks that the trend starts above 844 px; make the check assert the change
   answers are in the first viewport, failing on 280b2c2.
3. Host harness on 280b2c2 stopped with NO_JS_CONTENT_MISMATCH (screenshots.py:592, route not printed).
   Make the assertion name the route and width, find which route differs between JS and no-JS, and fix
   the page so the static text equals the hydrated text (do not relax the assertion). Say whether main
   at the base sha has the same failure.

Done: `uv run --with pytest pytest -q product` (Chromium denials allowed, say which), live-data build
`PASS build`, `verify.py all` PASS all, `bin/lint` ok, the new checks shown failing on 280b2c2 and passing
on HEAD. Commit; do not commit last.md. The supervisor reruns the harness on the host.
