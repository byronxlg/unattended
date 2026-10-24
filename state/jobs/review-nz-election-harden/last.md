Verdict: **request changes**.

Critical: None.

Important:

- `product/nz_election/tools/harden.py:65`: Missing evals disappear from discovery. Filtering out `social-retry-budget/check.sh` produced `PASS harden`, exit 0, with seven evals. Validate discovery against a required inventory.
- `product/nz_election/tools/harden.py:57`: Eval output is unchecked. An injected eval returning `SKIP unavailable dependency` with exit 0 produced `PASS harden`. Reject explicit SKIP/FAIL results.
- `product/nz_election/tools/harden.py:86`: Omitting `--history` produces the same `PASS harden` without checking workflow history. Require history for milestone PASS; distinguish local partial verification.
- `product/nz_election/tools/check_workflow_history.py:60`: One success plus 23 failures produces PASS. This does not establish “every scheduled workflow green 3 days running” (`intent/nz-election/schedule.md:24`). Require a documented recovery and hourly coverage policy. Exactly 24 runs need not be mandatory because schedules are best effort, but one success cannot establish hourly health; 18 observed runs need explicit acceptance criteria.

Nit: None.

Verification: `python3 -B -c '<in-memory injected-runner probes>'`; no pytest, network calls, or file changes. Output confirmed all four false-PASS paths above. Eval exit 9, missing verifier family, verifier FAIL, and missing workflow day correctly failed. No direct credential printing or modifications to existing checks found.