**Verdict: request changes.**

**Critical:** None identified.

**Important**

- `product/nz_election/pipeline/night_page.py:42`: No electorate map, search, leader, margin or reporting status is rendered. Question 3 is unanswerable in every state. The runbook acknowledges the capture gap, but it remains an acceptance gap against the page plan.

- `product/nz_election/pipeline/night_page.py:18`: Intermediate illustrative frames omit both reporting coverage and seats, leaving questions 1 and 2 unanswered. The endpoint omits update time. Obtain supported inputs or secure an explicit plan revision; do not invent values.

- `product/nz_election/pipeline/night_page.py:72`: Before election night, a populated build defaults to the 2023 final result and places the countdown and voting link after the entire results table. This contradicts the planned before-results hierarchy. State selection depends on data presence, not election phase.

- `product/nz_election/web/night.mjs:41`: Playback continually changes `#night-clock`, which has `aria-live="polite"` (`night_page.py:77`). At 10x/60x it changes on every 100 ms draw. Announce playback transitions separately from elapsed-time updates.

- `product/nz_election/web/night-parser.mjs:28`: Nested numeric XML produces different errors: `<votes><x>1</x></votes>` yields browser `XML_FIELDS` versus Python `XML_COUNT`. Confirmed with an isolated fields probe. `tests/night_browser.py:137` exercises malformed scalar values, not equivalent malformed complete documents, so its parity claim misses this divergence.

- `product/nz_election/pipeline/m3_checks.py:56`: The new night gate lacks the forbidden-placeholder check. Appending `<p>not available</p>` to valid night markup still returns `True`. Apply the absent-text contract to night content and test rejection.

**Nit:** None.

Verification: `node --test product/nz_election/tests/night_scheduler.test.mjs` reported **1 pass, 0 fail**. Additional clock probes at 1x/10x/60x each returned final frame `2`, elapsed `600`, running `false`. Replay labels persist in the wiring; playback contains no network request. The exact 80-route assertions remain intact.

Limits: `uv run --with pytest pytest -q product` failed initializing its read-only cache. PR #60 retrieval failed through both CLI and connector. No night screenshots were present, and the browser was unavailable, so 390×844 fold placement, graphic comparison, target sizes and visual style remain unverified. No files changed.