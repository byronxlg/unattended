# Follow-up 1: campaign-past (PR #135), fresh review findings

The fresh review requested changes; confirmed. `test_campaign_past.py` is this branch's own test and moves freely. Tests on main at the base sha stay unchanged. Touch only `product/nz_election/pipeline/campaign_page.py` and `product/nz_election/tests/test_campaign_past.py`.

1. Important, `campaign_page.py:46`: after close, empty eligible rows produce a sentence claiming the retained record has no 2026 observations. A validated series holding only 24 and 25 October observations (outside the displayed voting window) gets that false claim. The sentence must be true of what it describes: scope it to the displayed window, or say the record holds observations outside it. A truly empty record keeps its current sentence. Both must pass `ABSENT_TEXT` and the presence gates.
2. Nit, `test_campaign_past.py:72`: the byte comparison from `'<table'` pins markup. Compare the extracted dates, counts and provenance instead.

Add a case with a series of only 24 and 25 October 2026 rows after close that fails on HEAD ff6ca3e.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_m3_presence.py product/nz_election/tests/test_campaign_verify.py product/nz_election/tests/test_campaign_past.py` passes, the new case fails at ff6ca3e, pre-close output unchanged, one commit, no push.
