Verdict: **request changes**.

Critical: None.

Important: [check_workflow_history.py:179](/Users/byron/repos/unattended/.worktrees/nz-election-harden-gate/product/nz_election/tools/check_workflow_history.py:179) permits false guard evidence. This valid YAML reproduces it:

```yaml
- run: "python3\rproduct/nz_election/pipeline/night_live.py"
```

YAML decoding produces a carriage return. `shlex` treats it as whitespace and recognises the guard; Bash treats it as part of the command name and never invokes the script. Read-only probe output:

```text
detected: [['product/nz_election/pipeline/night_live.py']]
bash exit: 1
PASS Example 2026-10-24: not scheduled (cron or active-window guard)
PASS workflow history
history exit: 0
```

Reject decoded carriage returns or match Bash whitespace rules.

Nit: None.

Confirmed main’s existing test file is preserved verbatim. Fix-4 enclosing constructs were rejected; optional and required SKIP probes behaved correctly. No pytest run or files changed.