Verdict: **request changes**.

Critical: None.

Important:
- `product/nz_election/pipeline/electorate_pages.py:182` and `web/electorate.css:14`: Actions follow the entire single-column candidate list at 390 px. Nelson has seven cards; Wellington North has eight. Enrolment therefore falls below the first screen, violating the page plan. Preserve candidate-first order while meeting the phone visibility requirement.
- `product/nz_election/pipeline/home_graphics.py:314`: With empty candidate lists, the selected map link targets the omitted `#candidates-title`. Read-only probe confirmed `link=True, target=False`. Give it a valid destination when candidates are absent.

Nit:
- `intent/nz-election/plan.md:318`: Still records actions before candidates, contradicting the final implementation and accepted page order.

Read-only probes passed rendering and question order across 71 pages, plus omission of missing Policy.nz links. The rewritten page-plan tests use semantic checks; remaining modified markup assertions were inherited from main.

No pytest run or files changed. Visual review remains incomplete: electorate screenshots and the first-review report were absent from this worktree.