Verdict: **request changes**

Critical: None.

Important:
- [test_electorate_page_plan.py:21](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-design/product/nz_election/tests/test_electorate_page_plan.py:21): Tests still pin markup: exact class strings, generated SVG inclusion, and `<polygon>` counts. Line 58 additionally pins class order (`race-candidates module`). Replace these with semantic checks of candidate content, action order, selected-seat identity and accessible links. The documented layout change justifies updating expectations, but not replacing old markup locks with new ones.

Nit: None.

Read-only probes confirmed home/night/electorate map links = **71/0/1**, correct source IDs, one h1 per detail page, all six portraits attributed through Methods, and absent Policy.nz links omitted. Enrolment remains an unconditional hard-coded link, as before this PR.

No pytest run or files changed. Visual assessment relies on the supervisor’s reported inspection; I did not independently inspect electorate screenshots.