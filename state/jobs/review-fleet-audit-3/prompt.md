Fresh-context review of branch change/fleet-audit-3 against main, for PR #3 (Fleet Audit
increment 3: verdicts and freshness). Follow REVIEW.md in the repository root: three passes in
order (bugs and logic errors; security; compliance with intent/fleet-audit/spec.md sections
"Receipt and freshness semantics", "Verdict decision order", "CLI and report contract",
supervisor decisions 1, 3, 4, 5 and 6, and plan.md "Increment 3: verdicts and freshness",
"Ordered verdict engine", "Receipt algorithm and contract", "Snapshot and fixture format").
Severity Important or Nit, at most five nits, do not report what bin/lint reports. Do not
approve; the supervisor decides. Decision 4 replaces the spec body's completed/failed
predicate for ticks_jsonl: judge receipts.py against the decision, not the body.

Focus for this diff:
- receipts.py and files.py tail_regular: any read beyond the final 64 KiB; any backward
  search past the final physical line after a malformed or blank line; exactly one terminal
  newline removed; a partial first line in the region ever parsed as the receipt; a changed
  file (size, inode, device, mtime between before and after, or path replaced) ever yielding
  data instead of uncertainty; a nonregular file (directory, FIFO, socket) reaching parse;
  any retry loop; any text from the receipt becoming a path, a command argument or an
  environment value anywhere in the package.
- normalize_tick against decision 4: ran false with error null or "skipped:..." is completed;
  ran true with rc 0 (int or decimal string) and error null is completed; ran true with
  nonzero rc or non-null error is failed; ran false with non-null error not beginning
  "skipped:" is failed; everything else unestablished. Boolean rc must be rejected; a
  missing supervisor mapping must not be completed; `result` is never interpreted.
- verdicts.py rules 2 to 14: any rule where an Unknown, Unsupported or Absent value satisfies
  a predicate; any order where a later rule can win over an earlier one; age boundaries
  (A<=M fresh, M<A<=M+G cannot_determine, A>M+G late, equality never late, negative age
  cannot_determine); rule 11 firing on a running job (it must not: rule 6 first); rule 12 on
  a stale failed receipt (must be late via rule 11); rule 13 ever matching with a collection
  error anywhere in the job; a job without a contract ever healthy_idle; mtime evidence ever
  satisfying rule 13 without mtime_sufficient true.
- reports.py exit_code: precedence 3, 1, 2, 0 per the spec; expected_enabled false disabled
  exits 0, null or true exits 2 or 1; running with ancillary uncertainty exits 2; drift
  findings (none yet computed) would exit 1; empty fleet exits 2.
- cli.py run_audit and snapshot.py replay: any live clock, subprocess or host-path read on
  the --fixture path; domain mismatch exits 3; a snapshot whose stats or receipts index
  omits a declared path fails as invalid input rather than falling back to the host.
- capture.py: still no filesystem write; receipt tail bytes captured only for ticks_jsonl
  contracts; nothing from the environment in stats.json or receipts/index.json.
- Fixtures: the three real lines match state/ticks.jsonl at d0dd7de (hashes exclude the LF,
  as provenance.json says); every synthetic snapshot says so; expected.json values match the
  spec's decision table (the supervisor accepted the table in PR #3's body); no environment
  value anywhere under fixtures/verdicts.
- Tests: tests/conftest.py unchanged; increment 1 and 2 tests unchanged except the rule-count
  assertion in test_observer.py (1 to 14); every test the plan's increment 3 names is present
  and asserts what its name says; no test spawns a process.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
