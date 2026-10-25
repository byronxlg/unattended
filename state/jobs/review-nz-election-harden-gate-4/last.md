Verdict: **request changes**

Critical: None.

Important: `product/nz_election/tools/check_workflow_history.py:151` splits unquoted newlines into independent commands without tracking unsupported enclosing shell constructs. This valid Bash body only stores and prints array elements:

```bash
args=(
python3 product/nz_election/pipeline/night_live.py
)
printf "%s\n" "${args[@]}"
```

On committed d406b7f, the detector reports a guard invocation and `active_intervals()` returns `[]` for a pre-night day, incorrectly exempting missing history. Bash exits 0 without invoking Python. An uncalled function containing the same line also falsely declares the guard. Reject unsupported enclosing constructs as guard evidence; a full shell parser is unnecessary.

Nit: None.

Verification: Read-only probes using `.venv/bin/python -B -c` against functions extracted from `git show d406b7f:...`; Bash invocation replaced with a logging stub. Output:

```text
ansi_original commands= []
array_data commands= [['product/nz_election/pipeline/night_live.py']] active= []
function_not_called commands= [['product/nz_election/pipeline/night_live.py']] active= []
Existing test file preserved byte-for-byte prefix: True
```

Fix-3 closes the reported ANSI-C case, but the broader invariant still fails. No main tests were weakened: the only test diff appends 329 lines. No pytest run or files changed. `uv run` was blocked by read-only cache permissions.