# Follow-up 1: electorate-design (PR #98)

The fresh review asks for one change (state/jobs/review-nz-election-electorate-design/last.md):

`product/nz_election/tests/test_electorate_page_plan.py` (this branch's own test, it moves with the branch) pins markup: exact class strings, class order (`race-candidates module`, line 58), generated SVG inclusion and `<polygon>` counts. The lab rule (CLAUDE.md, Design loop): tests check data, provenance, absence and accessibility, never markup, class names or byte counts.

Rewrite those assertions as semantic checks:
- candidate content: the electorate's candidates appear by name with party, from the snapshot data;
- action order: the page's questions answer in the page-plan order (intent/nz-election/pages/electorate.md), read from heading or landmark text, not classes;
- selected-seat identity: the map marks exactly the page's own electorate as selected through an accessible name or aria attribute, not a polygon count;
- accessible links: map links have accessible names and resolve to existing routes.

Do not edit tests that exist on main at the base of this branch. No product code change is needed; if one is, say why. Commit in the worktree, do not push.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_electorate_page_plan.py product/nz_election/tests/test_design.py` passes, `rg -n 'class=|polygon|race-candidates' product/nz_election/tests/test_electorate_page_plan.py` prints nothing, and `bin/lint` is ok. Report the commands and their output in last.md.
