# Follow-up 1: polls refinement, rescoped (supervisor error)

You were right to stop. Item 2 was my error: I saw "two NAT blocks" and "OPP 7" on a stale local
server (another build, logged in state/mistakes.jsonl 09:40Z), not on 170bf94. The National
entitlement plus overhang segment is the intended design (styles.css .overhang, pinned by
test_increment_two_regressions.py:200). Drop item 2 entirely: no strip change, no
one-segment-per-party check.

Do these two:

1. build.strip() (build.py:244) prints `p.upper()`, so The Opportunity Party reads "OPP" wherever
   that strip is still drawn (legacy seat module, home social/OG card). Show the reader
   abbreviation instead: "TOP" for opp, every other party unchanged (NAT, LAB, GRN, ACT, NZF, TPM
   stay as the pinned test at test_increment_two_regressions.py:192 expects). One mapping, in the
   place party ids become display labels (party-colours.json or the label helper; your call).
   Add a test that a strip with opp renders `<span>TOP</span>` and no "OPP"; it must fail on
   170bf94. The parser keeps reading the OPP column.
2. The "since <date>" `<time>` in the polls/ change summary renders 13px mono (styles.css global
   `time` rule) inside a 16px sentence. Make it the sentence's size and face there only; other
   `time` uses keep their style.

Constraints: tests on main at 170bf94 unchanged; your new tests are yours. Absent-text rule holds.
Commit in this worktree (do not commit last.md), do not push.

Done when: `uv run --with pytest pytest -q product/nz_election` passes (say what skips),
`bin/lint` prints ok, the new TOP test output on 170bf94 (fail) and HEAD (pass) is in last.md.
