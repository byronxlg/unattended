Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/pipeline/social.py:492`: Paid-call guard defaults to the fixed start timestamp when `clock_now` is omitted. A read-only mocked probe crossed the sunset and reached the paid classifier at `2026-11-14T11:00:00Z`. Default to a live clock; restrict fixed clocks to offline execution. Direct `collect`, `classify`, and `transport` also lack sunset enforcement.

- `product/nz_election/pipeline/social.py:567`: Crossing the sunset with a live clock prevents spending but becomes `SOCIAL_UPSTREAM_FAILED`, saves a failure status, and makes the CLI exit nonzero. Probe confirmed this result. Hourly/daily loader cutoff exceptions likewise enter ordinary failure handling. Treat sunset termination as a clean skip, preserving required credit accounting without a failure row.

- `product/nz_election/pipeline/sunsets.py:31`: Night cutoff ownership remains in `night_live.py:25`; its consumers bypass `sunsets.py`. This does not meet the requested single shared module contract. Define the night cutoff in `sunsets.py` and import it throughout.

- `product/nz_election/pipeline/home.py:149`, `product/nz_election/pipeline/vote_page.py:71`: Post-election copy indefinitely says official results are “due 27 November,” including after that date or official publication. The 27 November probe reproduced this. Update these sections and the vote share description by result/date phase.

Nit: None.

Verification: Read-only inspection and `python3 -B -c` probes; no pytest. All four deadline predicates allowed one second before and rejected exactly at cutoff. Freeze boundaries remained intact. The three base-test edits change only the specified contracts.