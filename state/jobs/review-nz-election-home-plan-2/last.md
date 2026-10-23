Verdict: **request changes**.

Critical: None.

Important:
- `product/nz_election/web/styles.css:6`: Removing `.home-picker .home-directory{display:block}` restores the desktop four-column grid for its single link. In `screenshots-before/home-1280x800.png`, “Browse all electorates and candidates” wraps into a narrow stack of broken words. Restore the picker-specific override. This regresses the accepted plan’s readable electorate directory.

Nit: None.

Other requested fixes check out:
- 390×844 question test: governing parties 67 seats, 64 needed; Labour/National unchanged since 17 July; enrolment deadline and voting dates visible.
- Picker targets: supplied host evidence reports 26×26 at 360/390.
- Market test reads rendered Methods HTML and asserts four contracts.
- One directory link remains; Māori markers have a label.
- Methods height and candidate-link targets pass supplied host checks.
- Existing numeric thresholds unchanged; `market_checks.py` unchanged against `de9a7c2`.

Read-only verification using `check_site(..., validate_bundle(...))`:
```text
before: PASS home_checks; built CSS matches HEAD
after: PASS home_checks; built CSS matches HEAD
night: PASS home_checks; built CSS matches HEAD
```

Limitation: PR comments were inaccessible through both `gh` and the connector. Reviewed the first-review items supplied in your prompt. No files changed.