Verdict: **request changes**.

Critical: None.

Important:

- `product/nz_election/tools/check_workflow_history.py:179`: Quoted newlines become command separators after `shlex` removes quoting. In a `run: |` block, `echo '\n' python3 product/nz_election/pipeline/night_live.py` (with an actual newline inside the quotes) only echoes text, but declares the night guard. Probe with empty history returned `PASS workflow history`, exit 0. This still violates the incidental-text invariant.
- `product/nz_election/tools/check_workflow_history.py:174`: Shell comment handling consumes command-separating newlines. A block containing `set -e # setup` followed by a real `python3 .../night_live.py` invocation fails to recognize the guard. Probe outside the night window returned `FAIL workflow history`, exit 1. Backslash-continued invocations also go unrecognized.

Nit: None.

Read-only `python3 -B -c` probes passed date-specific cadence, ranges, lists, steps, DOM/DOW OR semantics and UTC boundaries. Confirmed main’s existing test file remains a verbatim prefix; only tests were appended. No pytest run or files changed.