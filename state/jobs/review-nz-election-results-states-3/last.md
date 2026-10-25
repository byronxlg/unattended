Verdict: **accept**.

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Verified:
- `pipeline/night_page.py:106`: neutral “Latest 2026 results” closes the nav issue; sequence hrefs unchanged.
- `web/night-live.mjs:68`: terminal handovers remove obsolete status copy. Official rendered content contains no provisional-leader or due-date copy.
- `pipeline/night_live.py:121`: official source and XML-derived date guards remain intact. Read-only probes rejected preliminary sources, pre-27-Nov XML clocks and malformed metadata.
- `tests/result_states_browser.py:78`: named-leader and one-scroll assertions remain; both handovers retain polling-stop checks.
- Existing checks remain intact except the explicitly accepted capture-count adjustment at `tests/test_contracts.py:18`.

Question test preceded visual judgement. Available screenshots answer Q1/Q2; Q3 screenshot confirmation relies on the reported host run. Python and Node probes passed. No pytest run; no files changed.