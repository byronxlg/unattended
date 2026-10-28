Verdict: **accept** as a review recommendation, not approval. No Important findings.

- **Nit** `product/nz_election/tests/funding_browser.py:53`: repeated donors use `.first()`, so visibility checks can repeatedly inspect the same return. Match document URLs or complete rows. The separate multiplicity test does verify all documents exist.
- **Nit** `product/nz_election/tests/funding_browser.py:49`: add keyboard activation and print-media checks. Current coverage verifies fragment loading and mouse closing, but not those two behaviours.

All 146 returns remain in nine groups. Native links expose groups without JavaScript, including incoming `parties/` fragments. Hidden tables leave the accessibility tree until selected; persistent, labelled heading links and visible focus styles make this approach acceptable. The print override reveals every group. Tests primarily assert data and behaviour, not class names.

Inspected all three supplied screenshots: no visible desktop overlap. Read directly: ACT leads with NZD 2,394,410 across 49 returns; largest donation NZD 250,000 to National; 19 of 146 returns received since 13 September.

Three weakest visual points:
- `funding_page.py:139`: party jump list duplicates the immediately following heading links.
- `styles.css:566`: tall mobile donation rows still dominate page length.
- `styles.css:551`: desktop timing chart remains mostly below the 800 px fold.

Read-only verification using `PYTHONDONTWRITEBYTECODE=1 python3 -B -c '…'` checked generated links and exact document multiplicities:
```text
PASS: 146 returns across 9 fragment-linked groups; exact document multiplicities preserved
```

Relied on supplied host evidence for 78 passing tests and the 82-route build. Dark mode, before/reference comparisons, and assistive-technology operation were not independently verified. No files changed.