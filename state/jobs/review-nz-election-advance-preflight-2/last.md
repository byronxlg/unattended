Verdict: **request changes**

Critical: None.

Important:

- [product/nz_election/tools/advance_preflight.py:49](/Users/byron/repos/unattended/.worktrees/nz-election-advance-preflight/product/nz_election/tools/advance_preflight.py:49): Missing-evidence errors echo raw file content through `repr(column)`, propagated by the CLI at line 90. Probe output: `INVALID_ADVANCE: missing daily or cumulative evidence in count header 'Votes PRIVATE_CAPTURE_MARKER'`. Remove the header value from the diagnostic and update the new test that expects it.

Nit: None.

The three requested fixes otherwise hold: explicit semantic evidence is required; both consumers validate quoting through the shared reader before filtering; the runbook documents shorter-capture supersession while retaining old captures.

No tests from main were weakened: the test diff contains only additions.

Read-only probes using `python3 -B -c` produced:

```text
Malformed probes: 38 rejections, all INVALID_ADVANCE
Generic headers: 3 rejected
Explicit headers: 5 correct
```

`uv run` was blocked by sandbox temporary-file restrictions. No pytest run; no files changed.