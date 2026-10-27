**Verdict: request changes**

Critical: None.

Important:

- `product/nz_election/pipeline/home.py:179`: Server handover still compares against a literal timestamp instead of the shared cutoff. An in-memory probe shifting the shared cutoff produced `post_election=False` but `night_summary=True`. Use the shared predicate so the hero and voting dates cannot diverge.
- `product/nz_election/web/home-live.mjs:24`: The stop guard prevents cached pages from completing handover. Opening a pre-election page after 8 November 06:00Z changes the dates but leaves the poll hero indefinitely. Probe output: `requests=0 hero=poll hero`. A page already showing the waiting summary also retains “counting is under way” indefinitely. Retire obsolete content independently of the request cutoff.

Nit: None.

Verification, read-only; no pytest:

- In-memory Node probe: **1,783 gzip bytes**, zero requests before handover, exactly one at handover despite repeated ticks, no additional requests after stop.
- The moved assertions enforce exactly one module and `< 2048` gzip bytes. Against `3ee6372`, the only other existing test changes are the intended absent-feed handover expectations in `test_home_plan.py`; no unrelated weakening found.
- No prohibited absent-state wording introduced.
- Question test, supplied 390px screenshots: before handover, “Government 67, three above 64”; “Labour and National unchanged”; election day 7 November. After handover, “Voting closed at 7pm” and “counting is under way”; winner and reporting percentage cannot be read from this empty-feed screenshot. Populated-results visual verification remains unproven by the supplied images.