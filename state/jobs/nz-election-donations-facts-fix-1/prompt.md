Follow-up 1 (supervisor review of db83ff9). Same branch, same thread, build round.

The snapshot is careful, but the skips bias it: 52 of 146 returns are dropped, 23 of them National's (15 of 38 kept) against 7 of ACT's (42 of 49 kept). A page that sums this file would show ACT at three times National, which is an artefact of which PDFs your fetcher could read, not of the returns. Your included records already take donor, amount and dates from the EC index table, not from the PDF (last.md says so). So the brief's skip rule for unreadable scans should not apply to rows whose facts are on the index.

1. Source of record is the EC index row. Include every 2026 return listed on the index (146 expected) with its index facts. Add a per-record boolean `document_checked` (true where you read the PDF and it agreed with the index, false where it was image-only or timed out) and keep `document_url` for all. Skip a return only when its index row itself lacks a party, donor or amount, and list those in `skipped_returns` with the reason.
2. A `party_id` on each record that maps the published label to the party ids the product already uses (grep the existing parties snapshot or pipeline for the id set; "Opportunity Party" and "The Opportunities Party" are one party if the EC means TOP, check the index). Keep `party` as published. The loader fails with a named error on an unknown party_id.
3. Loader: also fail when `len(records) + len(skipped_returns) != listed_return_count`.
4. Tests on main at f4668e4 stay untouched; this branch's own test_donations_snapshot.py moves with the change.

Done when: `uv run --with pytest pytest -q product` passes; `bin/lint` says lint ok; last.md gives records per party_id with totals, the document_checked false count per party, and every skipped return; `git diff --stat main` shows only snapshots, the loader and tests. Commit on the branch, do not push, do not commit last.md.
