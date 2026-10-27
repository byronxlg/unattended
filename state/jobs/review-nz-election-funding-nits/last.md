**Verdict: request changes.** Review recommendation only; no approval.

- **Important** - [styles.css:534](product/nz_election/web/styles.css:534): Desktop still misses the page-plan question test. In the supplied 1280 px screenshot, “When did the money arrive?” starts around y=782; its answer falls below 800 px and the chart below that. Reduce vertical space so the pace answer and graphic enter the first screen.
- **Nit** - [funding_page.py:22](product/nz_election/pipeline/funding_page.py:22): `ranking()` duplicates `home_graphics.funding_bars()`, leaving two implementations with different rounding. Consolidate the shared graphic when scope permits.

The three weakest visual points:

1. Desktop pace information remains below the fold.
2. The phone introduction spends substantial space around the biggest-donor link, delaying the ranking.
3. The readable stacked rows produce a roughly 21,000 px page without a party jump list, making later parties laborious to reach.

Data checks passed: all 146 returns retain exact amounts, received dates, EC document links, source and retrieval credit. Summaries round after summing exact cents. Te Tai Tokerau Party correctly remains included under its full [registered name](https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/register-of-political-parties). Phone crops keep donor, amount and date together.

Read-only verification via `.venv/bin/python -c …`:
```text
PASS: 5 pure funding test functions (fixture import omitted; not pytest)
PASS: 146 rows retain exact amounts, dates, document links, EC source and retrieval date
Retrieval timestamps: ['2026-10-20T08:46:30Z']
```

Changed tests check values and provenance, not CSS or serialized markup. Full pytest/Chromium and 82-route build results are supplied supervisor evidence, not independently rerun. Dark-mode and before/reference comparisons remain unverified. No files changed.