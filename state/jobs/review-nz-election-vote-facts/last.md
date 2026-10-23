Verdict: **request changes**.

Critical: none.

Important:
- [product/nz_election/pipeline/snapshots.py:251](/Users/byron/repos/unattended/.worktrees/nz-election-vote-facts/product/nz_election/pipeline/snapshots.py:251): malformed offsets pass validation. Replacing enrolment’s `at` with `2026-10-26T00:00:00+12:60` still loads. Python normalizes it to `+13:00`, bypassing the offset check, and the loader returns the malformed string unchanged. Validate offset components before parsing and add a regression expecting `voting_date_invalid`.

Nit: none.

Source checks found no date mismatches:

| Record | Snapshot matches EC wording |
|---|---|
| Enrolment closes | Midnight ending 25 October. [Source](https://vote.nz/enrolling/enrol-or-update/enrol-or-update-online) |
| Advance opens | 26 October. [Source](https://vote.nz/2026-general-election/about/overview/key-dates) |
| Advance closes | 6 November, “Advance voting ends”. Direct fetch returned 429; search-indexed content from the exact URL confirmed it. [Source](https://elections.nz/guidance-and-rules/for-third-party-promoters/new-standard-page-2) |
| Election day | 7 November, 9am-7pm. [Source](https://vote.nz/2026-general-election/about/overview/key-dates) |
| Telephone registration | Noon, 7 November, NZ time; previous users must register again. [Source](https://vote.nz/2026-general-election/voting-in-the-election/cant-get-to-a-voting-place/telephone-dictation-voting) |

All 20 records have EC-domain provenance. Non-EC, suffix-spoofed and userinfo-spoofed URLs were rejected. All stored instants correctly use Auckland `+13:00`.

No copied paragraphs or invented gap-fill found in the reviewed content. The terms summary accurately reflects the [EC restrictions](https://vote.nz/privacy-and-security/your-online-information-and-using-our-websites). Loader and new tests contain no network operations; no existing test was modified.

Read-only in-memory probes via `PYTHONDONTWRITEBYTECODE=1 python3 -c …` produced:
```text
valid records: 20
malformed rejection probes: 112
INVALID OFFSET ACCEPTED: 2026-10-26T00:00:00+12:60
All stored instant offsets match Pacific/Auckland
```

Both `uv run --with pytest pytest -q product` and `bin/lint` were blocked:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Operation not permitted (os error 1)
```

Read the [PR body](https://github.com/byronxlg/unattended/pull/53) through web access after `gh` failed. Its reported test passes were not independently reproduced. No files changed.