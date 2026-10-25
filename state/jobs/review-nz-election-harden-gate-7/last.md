Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/tools/check_workflow_history.py:236`: Multiline quoted YAML values are not consumed completely. A step name containing `run: python3 product/nz_election/pipeline/night_live.py` counts as guard evidence even when the actual `run` is `echo checking`. Ruby’s YAML parser confirmed this is name text; the detector yielded the guard and removed the active interval.
- `product/nz_election/tools/check_workflow_history.py:245`: A step with `if: false` still contributes guard evidence. Probe returned the night guard and an empty active interval although the step never executes.
- `product/nz_election/tools/check_workflow_history.py:260`: `python3 product/nz_election/pipeline/night_live.py --help` counts as guard evidence. Execution probe printed `--help exit: 0 guard calls: []`; detection nevertheless removed the active interval.

Nit: None.

Fix-6’s folded-scalar probe returned no guard evidence. No main tests weakened: the original test file is an exact prefix, with 456 added lines and zero deletions.

Verified with read-only `python3 -B -c` and `ruby -e` probes. `uv run` was blocked by its cache write requirement. No pytest run; no files changed.