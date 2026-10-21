# night-page fix-2 (PR #60)

CI is red and the fresh review requests changes. One round, these items. Tests on main at b523eda
are protected; tests this branch added (test_night_page.py, night_browser.py,
night_scheduler.test.mjs) move with the fixes, never weaker.

1. CI: `tests/night_browser.py:155` looks for a host-only Chromium path and fails on the Actions
   runner (`next(...)` StopIteration, run 39583749324). Make it use Playwright's own Chromium when
   the host path is absent, and add a step to `.github/workflows/ci.yml` before the tests that
   installs it, the same command pages.yml:128 uses
   (`uv run --with 'playwright>=1.51,<2' python -m playwright install --with-deps chromium`).
   Do not skip the browser tests when Chromium is missing.
2. Before-results hierarchy (pages/night.md "Page order"): state follows the election phase, not
   data presence. Before 19:00 NZDT 7 Nov the countdown line and the vote/ link come first, above
   the fold at 390; the 2023 final result or the replay sits below, labelled. Use the build time
   (or --now) to choose.
3. Question 2 on every frame: the endpoint shows its update time; intermediate replay frames show
   the reporting share and seats only where the archive supplies them. Where it does not, say what
   the frame is (for example "Replay frame 2 of 9, 21:30; seats published only in the final
   archive") in words that pass ABSENT_TEXT. Invent nothing.
4. Accessibility: `#night-clock` must not be an aria-live region that changes every draw. Announce
   play, pause, rate change and end in a separate polite live region; the elapsed clock is not live.
5. Parser parity: nested element inside a numeric field (`<votes><x>1</x></votes>`) gives XML_COUNT
   in both Python and night-parser.mjs. Add it, and whole malformed documents, to the parity cases.
6. Gate: `m3_checks.py` night check applies the forbidden-placeholder (absent-text) contract to
   night content; a test shows it rejects valid night markup plus `<p>not available</p>`.

Not in this round: the electorate map, search and table (question 3) wait for the electorate
detail data job; keep the runbook note.

Done when: `uv run --with pytest pytest -q` passes on the host, `bin/lint` ok, verify all PASS,
night_browser.py PASS, and the night/ page at 390x844 with --now before 7 Nov shows the countdown
and vote/ link above the fold (screenshot path in last.md). Commit in the worktree; do not push.
