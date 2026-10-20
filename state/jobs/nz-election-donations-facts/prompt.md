# Campaign data: EC donations over $20,000 as a sourced snapshot (no page)

Data half of M3 increment 3 (`intent/nz-election/plan-m3.md`, "Increment 3" and "Supervisor capture gates"), fetched once by Codex per issue #40. No route, no rendering, no daily family yet; the campaign page waits for its page plan.

Read first: `AGENTS.md`, `intent/nz-election/plan-m3.md` (increment 3 paragraph: the donation row fields and rules), `product/nz_election/snapshots/` with its loader and tests (follow the same record shape: source URL, retrieved_at, licence or terms note, per-record provenance; `voting.json` from PR #53 is the nearest example).

Goal: `product/nz_election/snapshots/donations.json`, fetched by you from https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-exceeding-20000/ and the 2026 returns it links (the 2026 calendar year and any late-2025 returns the page lists for this term), holding one record per disclosed donation: party, donor name as published, exact NZD amount as published (string or integer cents, not float), date received, date disclosed by the party, document URL and a locator (row, or page for a PDF). A date the EC does not publish is omitted from that record, never replaced by retrieval time. Corrections or amended returns are kept with a link to what they replace. EC copyright or reuse terms as stated. If a return is a scanned PDF you cannot read reliably, list it in last.md with its URL and skip it; do not guess values.

A loader next to the existing snapshot loaders that validates the file and fails loudly with a named error: amount at or above the published threshold and exact, dates parse and received is not after disclosed, every record has a document URL on an EC domain and retrieved_at, no duplicate (party, donor, amount, received) without a correction link.

Constraints: no change to routes, page rendering, client code, workflows or the site harness; tests on main at the base sha are untouched except contracts that enumerate the snapshot set, which move with it. No secrets. Web access is for EC pages only.

Done when:
- `uv run --with pytest pytest -q product` passes, with new tests for the loader (valid file loads; below-threshold amount, received after disclosed, non-EC URL, float amount, unlinked duplicate each fail with their named error).
- `bin/lint` prints ok.
- last.md gives the record count per party, the total per party, every return skipped and why, and `git diff --stat main` shows only snapshots, the loader and tests.
Commit in the worktree; do not push.
