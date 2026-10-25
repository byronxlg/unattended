Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/pipeline/night_live.py:129`: Official validation requires dates and a label, but no recorded evidence of official publication. A read-only probe retimestamped the preliminary fixture and obtained `Official results`, with identical party results and all 71 electorates unreported. Require dated official-publication evidence tied to the capture; test rejection of relabelled preliminary data.
- `product/nz_election/pipeline/night_page.py:138` and `product/nz_election/web/night-live.mjs:67`: A preliminary page receiving an official package retains “Preliminary; official results due 27 November” outside the replaced snapshot. Update the surrounding state copy during handover and test the actual DOM transition.
- `product/nz_election/tests/result_states_browser.py:65`: The question-three acceptance check only verifies that searching returns one row. Both fixtures have no reported electorate leaders, so they cannot demonstrate “Who is ahead in my electorate?” Use populated leader data and verify the answer within one scroll.

Nit: None.

Question test before visual judgement: phone screenshots answer Q1 (National 63 against 62 required; official parties tied at 61) and Q2 (100% reporting, dated update). Q3 remains unproven.

Verification: read-only Python and Node probes; no pytest or edits. Terminal-state probes each made exactly one request despite subsequent ticks. Absent-feed rendering omits results without “not available”. Existing checks were not weakened.