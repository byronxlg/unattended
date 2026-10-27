Verdict: **request changes**.

Critical: None.

Important:

- `product/nz_election/pipeline/snapshots.py:493`: Field-level absence fails validation. A partial record with a verified count but no confirmed names (`candidates: []`) raises `Invalid list top`, preventing rendering. The renderer supports this state, but its test bypasses validation. Permit absent opening ranks for partial records while preserving confirmed-list checks.
- `product/nz_election/pipeline/parties_page.py:121`: The new count lacks the required programmatic source association and source-note treatment. Include the recorded count source, EC copyright notice and retrieval date, with `aria-describedby` linking the count to its note.
- `intent/nz-election/pages/parties.md:57`: Pass 4 remains unverified. Neither required viewport screenshot is present; `last.md:46` confirms capture was blocked. Screenshot-derived answers for Q1 policies, Q2 leader/potential MPs and Q3 governing partners cannot be recorded. The supervisor’s Chromium test pass does not establish this visual gate.

Nit: None.

Checks completed:

- All 17 counts and 78 opening names match the recorded [EC release](https://elections.nz/media-and-news/2026/candidate-and-party-lists-released) and [EC PDF](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf). Counts total 443; display-name transformations match.
- Read-only `python3 -B -c` probes: 48/48 malformed values rejected; 6/6 off-domain URLs rejected; duplicate/skipped ranks, ranks exceeding counts and truncated confirmed lists rejected. Empty renderer input produces neither a candidate block nor placeholder text.
- The four-line test diff comprises two legitimate replacements: `test_parties_page.py:66` retains all previously tested mapped parties while accommodating new unmapped parties; `:70` strengthens exact equality with `source_name`. No base assertion was removed or weakened.
- No files changed; pytest was not run.