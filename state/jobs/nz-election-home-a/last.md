Committed `9950c56` on `change/nz-election-home`. Not pushed.

Changed home rendering, shared seat partials, social rendering, navigation, CSS, verifier/tests, screenshot harness, runbook and intent docs.

Pins moved (paths under `product/nz_election/`):

| Pin | Old → new | File:line |
|---|---|---|
| Navigation | Root “Polls and seats” → “Home”; polls at `/polls/` | `config/routes.json:4` |
| Routes | 7 primary / 78 total → 8 / 79 | `pipeline/build.py:472`, `:531` |
| Exact route sets | 78 → 79 | `tests/test_build.py:40`, `test_design.py:86`, `test_electorates.py:118` |
| Poll fragments | Root → `/polls/`, every published ID preserved | `tests/test_home.py:52` |
| Explorer URLs/assets | Root → `/polls/` | `tests/coalitions_browser.py:56`, `design_states.py:40`, `test_design.py:112` |
| Screenshot routes/narrow subset | 78/8 → 79/9 | `tests/screenshots.py:285`, `:315` |
| Root screenshot name | `polls` → `home` | `tests/screenshots.py:323` |
| Images | 215 → 219; home extras 3 → 4 | `tests/screenshots.py:229`, `:393` |

Verification:

- `uv run product/nz_election/pipeline/verify.py home`: `PASS home`
- `uv run product/nz_election/pipeline/verify.py all`: ends `PASS all`
- `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election --now 2026-10-17T01:00:00Z`: `PASS build: 79 routes`
- `uv run --with pytest pytest -q product/nz_election`: `389 passed in 192.57s (0:03:12)`
- `uv run --with pytest pytest -q`: `473 passed in 192.31s (0:03:12)`
- `bin/lint`: `lint ok (396 text files)`

Plan notes: recovered the missing accepted plan from `6f283b4`. Jump links and the fieldwork-range line follow the strip to reduce fold pressure; checks remain unchanged.

Host review remains: `uv run product/nz_election/tests/screenshots.py`, expected `PASS screenshots: 79 routes, 219 images`. Sandbox launch returned `CHROMIUM_REQUIRED` with permission denied (1100); no screenshots were reviewed. Populated artifacts remain untracked for the supervisor’s 390×844 and 1280×800 review.