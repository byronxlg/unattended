Verdict: **request changes**.

**Critical:** None found.

**Important:**

- [snapshots.py:110](/Users/byron/repos/unattended/.worktrees/nz-election-snapshots/product/nz_election/pipeline/snapshots.py:110): Record licences are checked only for nonempty text. In-memory mutations setting `licence: "nonsense"` on leaders and copied coalition quotes both load without error. Photo licence validation works, but record-level validation does not meet the requested bad-licence rejection check. Validate source-specific licence statements and add negative tests.

**Nit:** None.

Five numeric spot-checks matched their cited sources:

| Record | Snapshot and source |
|---|---|
| National 2023 | **38.08%**, 1,085,851 votes, 48 seats. [EC](https://electionresults.govt.nz/electionresults_2023/) |
| Port Waikato, Andrew Bayly | **14,296 votes**, margin 11,432. [EC](https://elections.nz/media-and-news/2023/port-waikato) |
| Botany enrolment | **52,737**, general roll, 30 September 2026. [EC](https://elections.nz/stats-and-research/enrolment-statistics/enrolment-by-general-electorate?name=Botany) |
| Banks Peninsula enrolment | **61,384**, same roll/date. [EC](https://elections.nz/stats-and-research/enrolment-statistics/enrolment-by-general-electorate?name=Banks+Peninsula) |
| Antonia Modkova | **ACT list rank 13**. [EC PDF](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf) |

All 678 records carry source URL, retrieval timestamp and licence. Eight portrait file pages matched author/licence metadata; Debbie’s page was unreachable, although its [parent image](https://commons.wikimedia.org/wiki/File:Debbie_Ngarewa-Packer,_Makoto_Osawa,_and_Rawiri_Waititi_August_2025.jpg) corroborates the attribution and CC BY 4.0. All portraits include derivative notes, measure 320×320, and total 98,262 bytes.

No raw social posts, social handles, keys or extraneous personal data found. No existing tests changed. All 332 supplied ranks match party/name/rank in committed EC lists after spelling normalization; no inferred ranks or gap-filling substitutions found.

Offline in-memory probes: all seven snapshots load; missing source, unknown party and prohibited photo licence each raise `ValueError`. Loader and new tests contain no network acquisition.

Verification limitation: `uv run --with pytest pytest -q product/nz_election` and `bin/lint` both stopped before execution:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
```
No files changed.