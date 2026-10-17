Committed **`5705910`** locally; not pushed. **Incomplete, not ready to merge.**

Added `social.py`, `social_page.py`, synthetic tests and the daily workflow; updated bundle validation, publishing, routes, styling and runbook.

Stopped under `AGENTS.md`’s “If a test is wrong, say so and stop” rule:
- Three existing tests require 77 routes; the requested route produces 78.
- Two existing tests assume hourly/daily refresh produces every registered family.
- Existing tests were not edited. My new build test also has an incorrect output path.

Commands run and final output:

```text
uv run --with pytest pytest -q product/nz_election/tests
5 failed, 293 passed in 129.78s
uv run --with pytest pytest -q product/nz_election/tests/test_social.py
1 failed, 32 passed in 1.63s
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data
PASS refresh: polls bundle
uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16
PASS social
uv run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election
PASS build: 78 routes
uv run product/nz_election/pipeline/verify.py all --data /tmp/sp-data --site /tmp/sp-site
PASS all
uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots
AssertionError: screenshot harness requires 77 routes
bin/lint
lint ok (346 text files)
rg -n "X_UPSTREAM_KEY|TYPESAFE_API_KEY" --glob '!**/runbook.md' --glob '!.github/**' --glob '!**/social.py' product .github
No matches (exit 1)
```

Daily record fields: `id, source_ref, observed_at, day, sample, party_counts, attitude, topic_counts, model_versions, question_version, provenance, probability_sums`. Ledger fields: `id, source_ref, observed_at, day, reserved, spent, cap, requests, allocation, closed`.

Implemented question text, verbatim; **no live Jev requests were made**:
1. “Is this about current NZ national politics?”
2. “Which party is the primary subject?”
3. “Main topic:”
4. “Does the author express an interpretable attitude toward that primary party?”
5. “Attitude toward that party, ordered strongly negative, negative, neutral, positive, strongly positive.”

Unverified: screenshots, live upstreams and Actions execution. `verify.py all` does not yet include a dedicated social check. Resolving the existing test contracts is required before continuing.