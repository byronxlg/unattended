# Spike verification, 2026-10-16 02:40 NZ

Three spike jobs ran in parallel (workspace-write, throwaway worktrees), all rc 0, 282 to 411
seconds each, Codex weekly window at 6 percent after them. Each final message is copied verbatim
into spike-<slug>.md in this directory; the longer reports the jobs wrote are spike-<slug>-report.md
and spike-pr-evidence-squash-transcript.txt; receipt-self.json is the lab's first build receipt.

The supervisor ran each spike's proving command in its worktree:

```text
.worktrees/spike-fleet-audit    uv run --with pytest pytest -q spike/   17 passed in 0.06s
.worktrees/spike-pr-evidence    uv run --with pytest pytest -q spike/   11 passed in 0.01s
.worktrees/spike-skill-contract uv run --with pytest pytest -q spike/   11 passed in 5.63s
```

## Did each spike answer its question

- fleet-audit: yes. `launchctl print gui/501/<label>` parses into the record for all 454 labels
  on the host, one structural failure (com.apple.networkserviceproxy) handled as warnings, not
  a crash. Only 8 of 454 carry a timer schedule, which is the shape of the problem rather than a
  parser gap: most launchd agents are on-demand, and the audit is about the timed few. The five
  real fixtures pass. New fact: a service can be disabled in the override table and still loaded.
  Not shown yet: an interpretation (healthy, late, failing) of the host's real timed jobs.
- pr-evidence: no for the small receipt alone, yes with writer attestations. The squash
  scenario in /tmp confirmed the draft's claim: walking main after a squash finds 0 of 3
  original commits, so a saved commit snapshot is required, and even then exactness rests on the
  wrapper attesting it was the only writer. GitHub was reachable from the sandbox this time.
- skill-contract: technically yes, practically no. The one real finding on tts (the helper
  accepts --help but does not list it) is a documentation mismatch an ordinary helper test
  would catch. Codex's own verdict: the evidence does not justify a standalone product.

## What went wrong

All three jobs ended with "Unable to create .git/worktrees/<name>/index.lock: Operation not
permitted": the workspace-write sandbox covers the worktree but not the main repo's .git that
the worktree's commits go through. Nothing was lost (the files were on disk, the supervisor
committed them on the spike branches) but it is a lab tooling bug, not a Codex mistake:
bin/codex-run now passes `--add-dir <root>/.git` and `--add-dir ~/.cache/uv` for workspace-write
jobs. The uv cache was the other sandbox collision; each spike worked around it differently.

## Spike 2 (fleet-audit interpretation), 02:50 NZ

Job spike-fleet-audit-2, rc 0, 356 seconds, weekly window 7 percent after it. Proving command in
the same worktree: `uv run --with pytest pytest -q spike/` printed `62 passed in 0.07s`.

Pass criterion from the provisional decision: at least one true finding a person would act on, and
no wrong verdict against the plist and the service's own evidence. Result: pass.

- True findings: org.nixos.skhd and org.nixos.yabai, both KeepAlive, loaded, no PID, state
  `spawn scheduled`, last exit `78: EX_CONFIG`. The supervisor re-ran `launchctl print
  gui/501/org.nixos.skhd` and `plutil -p` on its plist: same state, exit code and KeepAlive true.
  A person would reconcile the two installations (nix and Homebrew) of each window manager.
- Also checked: com.koekeishiya.yabai is `disabled` in `launchctl print-disabled gui/501`, and
  com.google.keystone.agent.plist is an empty dictionary. Both verdicts match.
- The six cannot_determine verdicts are honest: the policy gives freshness contracts only to the
  ticks, and an mtime cannot show supervisor completion. Codex's reading of bin/tick is right
  (a skip can exit 0 before the receipt append; the result field is inside the receipt). The
  intent takes this as a requirement: receipts are read as JSONL, not statted, when declared.
- Policy error found by the spike: 20 minutes plus 30 grace was implemented as a 50 minute
  threshold on the receipt mtime. The intent fixes the contract: max age and grace are separate
  fields with defined meanings, and a 45 minute supervisor run must not read as late.
