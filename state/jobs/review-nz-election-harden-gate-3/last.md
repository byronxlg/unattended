Verdict: **request changes**.

Critical: None.

Important: [check_workflow_history.py:126](product/nz_election/tools/check_workflow_history.py#L126) mishandles escaped single quotes in Bash `$'…'` strings. This `run: |` body falsely declares the night guard:

```bash
echo $'a\'
python3 product/nz_election/pipeline/night_live.py
#'
```

Direct probes confirmed:
- Bash exits 0 and only echoes the string.
- `workflow_commands()` yields `night_live.py` as an invocation, allowing history to be incorrectly exempted.

Handle this quoting form or conservatively reject it as guard evidence; no full shell parser needed.

Nit: None.

Verification: read both diffs; ran read-only Python/Bash probes, no pytest. Requested newline, comment, continuation, literal/quoted hash, ordinary escaped-double-quote and heredoc cases behaved correctly. Tests from `dc57e78` are unchanged: 300 added lines, zero removed.