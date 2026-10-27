Verdict: **accept** as a review recommendation, not approval. Reviewed `origin/main...3dcc564`; no Important findings.

The earlier finding is resolved: `funding_page.py:57-61,114` gives the home summary the EC link, licence and snapshot retrieval date. The regression test varies both date and source URL.

Confirmed: question order, exact declared-return totals, all 146 document links, party anchors, unchecked returns retained, absence handling, and accessible chart equivalents. Route contracts consistently move to 82 without weakening assertions. New tests check facts, provenance and behaviour.

Three weakest visual points, ranked Nit:

- **Nit** `product/nz_election/web/styles.css:533`: Desktop timeline begins below the initial viewport, making the pace-of-arrival answer slower to find.
- **Nit** `product/nz_election/web/styles.css:529-530`: Phone tables require horizontal scrolling to compare donors with amounts and dates.
- **Nit** `product/nz_election/web/styles.css:519-521`: The phone ranking occupies nearly the entire first screen; the biggest-donor answer gets little visual invitation below it.

Read from the screenshots: ACT leads with **NZD 2,394,410.40 across 49 returns**; National follows with 38. Desktop identifies Rank Group Limited’s NZD 250,000 return. The 390 header stays within two navigation rows.

Verification: read-only Python assertions returned:
```text
PASS: 146 document links, party anchors, exact totals, provenance, absence, dated home EC credit
```
Host fix-1 log reports `158 passed, 2919 deselected`. Local pytest could not run: `.venv` lacks pytest. Inspected both supplied screenshots and fix-1 versions; 360, dark mode and full-page visual checks were not independently repeated. No files changed.