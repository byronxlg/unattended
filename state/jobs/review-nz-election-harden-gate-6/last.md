Verdict: **request changes**

Critical: None.

Important: [check_workflow_history.py:233](/Users/byron/repos/unattended/.worktrees/nz-election-harden-gate/product/nz_election/tools/check_workflow_history.py:233) replaces every folded-scalar newline with a space, falsely joining separate commands:

```yaml
      - run: >-
          python3

          product/nz_election/pipeline/night_live.py
```

Ruby’s YAML parser decodes this as `python3\nproduct/nz_election/pipeline/night_live.py`. Bash exits with `Permission denied`; the guard never executes. The detector nevertheless returns the guard invocation and `active_intervals(...) == []` before election night, exempting missing history. Reject unsupported folding cases conservatively or preserve YAML’s command boundaries.

Nit: None.

Read-only probes confirmed the character rejection. No tests from main were weakened: the sole test-file diff adds 420 lines without deletions. Pytest was not run.