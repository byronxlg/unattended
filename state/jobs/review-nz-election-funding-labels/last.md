Verdict: **accept**.

No Important or Nit findings.

- `product/nz_election/pipeline/home_graphics.py:457`: rounds summed integer cents half up, matching `whole_money` and the headline.
- Exact cumulative amounts remain in the table equivalent; per-return rows retain cents.
- `funding_page.py:134` is the only caller of `funding_steps`.

Verification: supervisor reports 11 tests passed, lint OK, and the expected rendered labels. Independent probes were blocked by read-only sandbox restrictions on uv’s cache. Screenshots were not independently reviewed.

No approval issued.