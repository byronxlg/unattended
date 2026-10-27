Verdict: **request changes**.

Critical: None.

Important:

- `intent/nz-election/pages/parties.md:57`: Pass 4 remains unverified. No 390×844 or 1280×800 screenshots were found in the worktree artifacts or supervisor state. Cannot record screenshot-derived answers for policies, leader/potential MPs, and governing partners. Supply the supervisor captures and complete the question test; Chromium passing does not establish this visual gate.

Nit: None.

Verified through read-only `python3 -B -c` probes, without pytest:

- Both fixes work: partial records with empty candidates validate and render; counts reference source notes containing the EC link, licence and retrieval date.
- Both new regression conditions fail on `6ebf8bb` and pass on `e9efa3d`.
- 39 malformed-input probes rejected, including invalid ranks, complete-list/count disagreement and off-domain sources.
- Absent fields render no candidate block or placeholder.
- All 17 records, 443 total candidates and 78 opening names retain EC URLs and source locators.
- No existing test assertion from `3ee6372` was weakened.

No files changed.