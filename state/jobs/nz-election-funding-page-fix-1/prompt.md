Follow-up 1 on PR #105 (fresh review request changes). Same worktree and branch; commit, do not push.

1. Important: pipeline/funding_page.py:106, the home feed summary publishes ACT's amount and return count with no
   source. Give it the same dated EC credit the funding page uses (source link to the EC returns index and the
   retrieved date from donations.json), using the existing credit component in DESIGN.md. Add a test that the home
   summary carries a source URL and retrieved date taken from the data (not a literal), and that it fails on 1e6cdc5.
2. Nit: styles.css:533, top-ten table at 1280: give the donor column the room; party, amount and date stay on one
   line (nowrap, tabular numbers). No markup pins in tests.
3. Nit: styles.css:522, phone bar labels: the amount is primary; the return count secondary (smaller, muted token).

Main's tests at origin/main are untouched; this branch's own tests may move with the change. Verify:
uv run --with pytest pytest -q product/nz_election/tests -k "funding or home or design" (Chromium launches may be
sandbox-denied; list them), and bin/lint (expect "lint ok"). Report the commit sha.
