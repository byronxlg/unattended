Changed: `lab_metrics/`, `bin/metrics`, tests/fixtures, Python metadata, CI/Pages workflows, `CLAUDE.md`, plan checklist.
Departure: normalized records use dictionaries inside dataclass source/snapshot contracts. No open questions.

1. `uv run --with pytest pytest -q`: `81 passed in 0.51s`; product tests excluded.
2. `bin/metrics`: `metrics: 56 indicators, 12 unavailable, 0 skipped`
   `bin/metrics --json - | head -c 300`:
```text
{
  "diagnostics": {
    "calculation": {},
    "skipped": 0,
    "sources": {
      "changes": {
        "available": true,
        "reason": "",
        "skipped": 0,
        "warnings": {}
      },
      "checks:1": {
        "available": true,
        "reason": "",
        "skipped": 0,
        
```
3. `bin/metrics --json - > /tmp/a.json && bin/metrics --json - > /tmp/b.json && cmp /tmp/a.json /tmp/b.json && echo identical`: `identical`
4. `bin/blog build`: `built 2 posts into site/`; `rg -c "<h2>" site/metrics/index.html`: `12`
5. `rg -n "urllib|http\.client|requests" lab_metrics tests bin/metrics`: no output.
6. `bin/lint`: `lint ok (177 text files)`
7. `git status --short`: empty. `git log --oneline main..HEAD`:
```text
403e1a4 Complete metrics verification and preserve invalid timestamp exclusions
0d88555 Verify live metrics and harden untrusted evidence boundaries
2ecf88f Generate metrics in Pages and enable independent root test collection
99d1f7c Render deterministic metrics documents and expose atomic CLI output
43e925b Calculate all specified indicators and cost cohorts
f4329bd Implement defensive local readers and bounded GitHub collection
3ac84b0 Add metrics package and provenance-labelled fixtures
```