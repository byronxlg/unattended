# Follow-up 1 on PR #84 (advance preflight): fresh review request changes

Fix job on your own branch `change/nz-election-advance-preflight`. Tests on `main` at the base sha are
protected: do not weaken or edit them. Tests this branch added move with it. Commit in the worktree,
do not push. Do not commit last.md.

Three Important findings from the fresh review (full text on PR #84):

1. `product/nz_election/tools/advance_preflight.py:49`: ambiguous column semantics default to daily.
   `Date,Total votes` with 10, 30 drafts `daily` (cumulative 40). Invariant: the draft names daily or
   cumulative only on explicit evidence (header wording, or values that can only be one); otherwise it
   fails `INVALID_ADVANCE` with a message saying which evidence is missing. A warning is not enough.
2. `product/nz_election/pipeline/advance.py:50`: malformed quoting passes (`2026-10-26,10,broken"quote`;
   a total row `Total,1"0`). Invariant: CSV syntax is validated by one shared reader used by both the
   preflight and the pipeline, before any field or row is ignored; preflight stops duplicating the
   header/CSV validation.
3. `product/nz_election/runbook/advance.md:36`: no recovery path for a legitimate shorter correction.
   Document a reviewed supersession procedure that keeps captures immutable and says how the manifest
   records it. Docs only unless the loader needs a small, tested hook to honour it; if it does, say so.

Definition of done:
- A regression test per finding 1 and 2 that fails on the current HEAD before your change and passes
  after (say so in last.md with the failing output).
- `uv run --with pytest pytest -q product/nz_election/tests` subset you touched passes (name it).
- `bin/lint` prints `lint ok`.
- last.md: what changed, the commands and their output.
