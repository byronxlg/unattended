Committed `8742598`; not amended or pushed.

Added the runtime guard and boundary tests, restored `"New Zealand First"`, updated the intent and caption, and confirmed query provenance. Tests on `main` remain untouched.

Verification:

- `uv run --with pytest pytest -q product/nz_election/tests`
  `372 passed in 174.01s (0:02:54)`
- `evals/social-query-length/check.sh`
  `PASS query length 495 of 512`
- `evals/pages-verify-polls-only/check.sh`
  `PASS all`
- `bin/lint`
  `lint ok (375 text files)`

`last.md` contains exact outputs and remains uncommitted. Open questions: none.