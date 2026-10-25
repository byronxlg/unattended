Verdict: **request changes**.

Critical: None.

Important:
- `product/nz_election/web/night-live.mjs:10,42-45`: The browser learns the cutoff only from a successful JSON response. Until then, `Date.parse(undefined)` is `NaN`, so polling continues after cutoff, including on tab resume. An offline probe made another request after resuming 20 minutes past cutoff and still displayed “Showing the dated packaged snapshot”. A first visit after cutoff also fetches once. Embed the shared Python cutoff in the generated page and initialize the client before its first tick.

Nit: None.

Read-only probe output (`node --input-type=module -e`, `python3 -B -c`):

```text
Known deadline: calls=1, ended=true
Offline then resume: calls=2, ended=false
First visit after cutoff: calls=1, ended=true
Cutoff -1s: guard=open, chain=True
Cutoff +0s: guard=NIGHT_CLOSED, chain=False, watchdog=1
Cutoff +1s: guard=NIGHT_CLOSED, chain=False, watchdog=1
```

The workflow/watchdog use the shared Python constant. Ended copy respects the absent-text rule. `test_result_states.py:64` moves the contract without weakening it: exact dictionary equality remains, adds both required fields, and retains rejection of settling an absent feed.

No files changed; no pytest run.