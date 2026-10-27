**Verdict: request changes.** Review only, not approval.

- **Important:** [funding_page.py:106](product/nz_election/pipeline/funding_page.py:106) adds ACT’s amount and return count to the home feed without an EC source line or retrieval date. Its only link opens funding/, requiring another click to reach the source. Add a dated EC credit beside this summary, as REVIEW.md requires for published numbers.

Three weakest visual points, all **Nit**, from the supplied screenshots:

1. [styles.css:533](product/nz_election/web/styles.css:533): desktop columns crowd the top-ten table. Long donor names wrap while party, amount and date compete for space.
2. [styles.css:522](product/nz_election/web/styles.css:522): phone bar labels give exact amounts and parenthesised counts similar emphasis, making comparison slower than the bars suggest.
3. [base.html:22](product/nz_election/web/templates/base.html:22): the phone masthead consumes roughly 158 px before the answer. It stays within two rows, but remains visually heavy.

The core implementation checks out: plan order preserved; declared-return caveat explicit; all 146 document links independently verified in the full list; unchecked returns retained; empty input omits data modules. Route counts, inventories and navigation expectations move consistently without weakening assertions. New tests primarily check data, provenance and behaviour.

Screenshot answers: ACT leads with **NZD 2,394,410.40, 49 returns**; National follows with **NZD 2,291,751.20, 38**. Desktop shows a largest return of **NZD 250,000**, Rank Group Limited to National.

Verification: read-only Python probe printed `PASS: 146 return document links in full list`. Local pytest attempt failed with `No module named pytest`; no suite rerun claimed. Supplied screenshots do not show the cumulative chart or full list. Full-page, dark-mode and 360 px visual verification remain open pending host evidence.