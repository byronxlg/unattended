**Verdict: accept.**

- **Critical:** none.
- **Important:** none.
- **Nit:** none.

Checked all 146 records against the [EC index](https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-exceeding-20000), including ten complete party/donor/amount/date/URL spot-checks. No dropped or duplicated rows; all five amendments retain original-return locators.

Party mappings agree with the config; `nzof` and `tttp` have explicit rationale. Both TOP names correctly map to `opp`, supported by the [EC name-change notice](https://elections.nz/media-and-news/2026/name-changes-for-two-parties).

The 145 unchecked documents remain included. The sole checked document agrees with its PDF. Alajamber’s contradiction is preserved and narrowly pinned. No invented gap-fill, copied source prose, stored PDFs, or weakened existing tests found. [PR #55’s](https://github.com/byronxlg/unattended/pull/55) substantive claims match the reviewed files.

Verification:
```text
In-memory probes across both loaders:
PASS 554 malformed-input/exception/inclusion probes
PASS 146 sequential locators, unique IDs and document URLs
Total cents: 765781722

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python bin/lint
lint ok (563 text files)
```

`uv run --with pytest pytest -q product` could not start: uv cache access denied by the read-only sandbox. Full-suite results remain independently unverified.

No files changed. Open source question: EC clarification of Alajamber’s dates.