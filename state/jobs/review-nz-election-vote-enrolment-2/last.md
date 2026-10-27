Verdict: **accept**.

- Critical: none.
- Important: none.
- Nit: none.

Checked `vote_page.py:23-48,87`: missing/null/empty source links are omitted; closed guidance remains. Missing `at` uses the date fallback; no label is required. Both summary locations switch at the same instant. No new claims beyond the snapshot.

Python probes (`python3 -B -c`, pytest not run):
```text
PASS 192 sparse/source/at/label/boundary probes; before-close HTML identical to base
PASS both summary locations switch at 2026-10-25T11:00:00Z
PASS every single-record and empty-record page
```

`test_vote_page_enrolment.py:25-66` checks text, sourced URLs and absence without locking markup.

Limits: brief and first-review files absent; used your supplied context. Screenshots not assessed. No files changed.