Verdict: **request changes**.

- **Important** [product/nz_election/pipeline/vote_page.py:71](/Users/byron/repos/unattended/.worktrees/nz-election-advance-2026/product/nz_election/pipeline/vote_page.py:71): `advance_line()` omits `source['provenance']`. Both home and vote show the count, source URL, retrieval time and statistical caveat, but neither discloses the hand transcription. Add that disclosure beside the number and assert its presence in both rendered pages.

Other checks:
- [EC voting statistics](https://vote.nz/2026-general-election/about/overview/voting-statistics) confirms 69,034, 106,714 and total 175,748.
- Read-only Python probes: `PASS missing, partial and historical omission`.
- Contradicting headers remain rejected by the preflight logic.
- The moved assertion preserves the missing-capture check using an empty registry; subsequent checks remain intact.

Verification limits: `uv run --no-sync` was blocked by cache permissions; the verifier requires a writable temporary directory. Supervisor-reported 478 tests and 82-route build were not independently rerun. Screenshot comparison remains unverified. No files changed.