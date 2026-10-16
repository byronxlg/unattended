Fresh-context review of branch change/nz-election-1 against main, for PR #9 (NZ election
increment 1: fixtures, MMP allocator in Python and JS, Wikipedia poll parser), first round,
HEAD 281e6d8. You are in the worktree .worktrees/nz-election-1, read-only.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with intent/nz-election/spec.md sections "Poll method and assumptions",
"Allocator contract", "Required 2023 golden fixture", "Testing and acceptance", and with
intent/nz-election/plan.md including its supervisor decisions). The plan is absent in this
checkout: read it with `git show 62d3ff6:intent/nz-election/plan.md`. Severity Important
or Nit, at most five nits, do not report what bin/lint reports. Do not approve.

Patterns to look for, not single instances:
- Allocator (pipeline/allocator.py and web/allocator.mjs): any path where the two
  implementations can disagree (eligibility, tie detection, exhausted lists, overhang,
  nonListWinners, validation order), any float or string comparison where exact arithmetic is
  required, any input shape that raises something other than INVALID_INPUT.
- Poll parser (pipeline/poll_parser.py): any wikitext construct the bounded scanner mishandles
  silently instead of failing parse_drift (nested templates, refs with attributes, rowspan or
  colspan, header renames, event rows), any way a poll id changes between revisions for the
  same poll, and whether the date exception in config is narrow enough (revision, pollster,
  visible and sort dates all required).
- Fixture loader (pipeline/fixtures.py): BOM, CRLF and banner handling; a national total row
  summed with electorate rows; name-based joins where structural ids were required.
- Tests: do the 24 product tests prove the spec, or restate the implementation.

Running checks: try `uv run --with pytest pytest -q` from the worktree root; if the sandbox
cannot run it, say so and review by reading. The supervisor's run at 281e6d8 stands: 108
passed, bin/lint ok. Node is installed; the parity test ran.

Already found by the supervisor, do not re-report: loader error-code assertions inside
test_2023_official_result; the departures section in product/nz_election/AGENTS.md.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
