**Verdict: request changes.**

Critical: none found.

Important:

- [night_live.py:182](/Users/byron/repos/unattended/.worktrees/nz-election-m3-live/product/nz_election/pipeline/night_live.py:182): Deployment recovery is lost across runner restarts. If data publication succeeds but Pages fails, the successor receives `unchanged`; its `pending_sha` is empty, so it never retries deployment. Unchanging final results can remain unpublished indefinitely. Persist deployment state or reconcile the data SHA against the deployed SHA.

- [night_live.py:143](/Users/byron/repos/unattended/.worktrees/nz-election-m3-live/product/nz_election/pipeline/night_live.py:143): Successful unchanged acquisitions never update retrieval freshness. Four successful cycles produced `changed, unchanged, unchanged, unchanged`; at 06:15 the published retrieval remained 06:00 and the browser reported stale. This conflates unchanged source data with failed refreshes, contrary to the separate freshness contract. Preserve successful-acquisition status independently of result-change deployment suppression.

Nit: none.

Other checks: shared freeze boundaries passed read-only probes, including midnight and 19:00 NZDT. Hidden/resume polling passed a Node probe. Fix-1 strengthens assertions; reviewed merge-base test edits preserve their behavioral checks. Rehearsal transport is artifact-only and labelled separately. No added credentials or paid service found; workflow permissions match the operations used.

Verification limits: `uv` tests could not start: `Failed to initialize cache … Operation not permitted`. Injected cycle verification printed `PASS injected cycle contract`. PR-body access failed through both CLI and connector; real Actions rehearsal and screenshots remain unverified. No files changed.