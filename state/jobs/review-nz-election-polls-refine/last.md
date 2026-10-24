Verdict: **request changes**.

- **Critical:** None.
- **Important:** `product/nz_election/web/coalitions.mjs:119` still renders `opp` as **OPP**. Confirmed with the same seven-party input: Python renders TOP, JavaScript renders OPP. Apply the same abbreviation mapping to the client renderer. Existing parity coverage omits `opp`.
- **Nit:** None.

Verified directly: new regression passes at HEAD and fails on `170bf94`; label is escaped; aria-label retains the configured name (“Opportunity”); no pre-existing tests changed. CSS inheritance is correctly scoped.

Limitations: pytest blocked by read-only uv cache permissions; local venv lacks pytest. Current-head screenshots unavailable, so visual review remains unverified.