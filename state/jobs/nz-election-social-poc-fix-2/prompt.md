Fix round 2 on change/nz-election-social-poc (0642382, PR #24). The second fresh review (the
fourth comment on PR #24; same text in state/jobs/review-nz-election-social-poc-2/last.md,
read it verbatim) found two Important items I confirm and one I have accepted as is (the
pages.yml guard-to-deploy gap: leave pages.yml alone). Fix job: existing tests and assertions
stay exactly as they are; add a new test that fails on 0642382 for each item and passes after.
Nothing gets weaker to pass. Invariants and where they are enforced; you choose the shape.

1. Publication retry (publish.py:112). Invariant: publishing the same completed report twice
   is idempotent (the second publication leaves the ledger unchanged and succeeds), a handled
   stop before the first paid request publishes its sanitized status with zero requests, and
   a report that would lower a recorded spend or hide one is still refused. Today the first
   publication stores the conservative figure (7,560 for a 7,200 report), so the identical
   retry differs from the stored row and fails SOCIAL_LEDGER_CONFLICT, and requests == 0 is
   rejected outright. The daily workflow retries publication on a lost push; that path must
   not fail. Tests: identical report published twice; zero-request handled stop published;
   a conflicting lower report still refused.

2. Midnight check before transport (social.py:137). Invariant: no paid request is sent when
   the NZ budget date at the moment of send differs from the reservation's day. Today the
   check precedes checkpoint(), which does filesystem publication and validation; a slow
   checkpoint can cross midnight before send(). Recheck immediately before transport. Test:
   an injected checkpoint that advances the clock past 11:00Z (NZ midnight) must stop the
   run with no request sent; the reviewer reproduced a paid request at 2026-10-17T11:00:01Z
   charged to 17 October.

3. Nit: social_page.py:25 says "over 1 days" for a single record. Singular for one day.

Definition of done, in the worktree, output in last.md (keep last.md untracked):
- `uv run --with pytest pytest -q product/nz_election` all passed, count stated; the new
  tests named, each shown failing on 0642382 (one line each).
- `uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data && uv run
  product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16 && uv
  run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election
  && uv run product/nz_election/pipeline/verify.py --data /tmp/sp-data --site /tmp/sp-site all`
  ending PASS all (move any previous /tmp/sp-data aside first).
- `bin/lint` ending lint ok.
- `git diff 0642382 --stat` touching only publish.py, social.py, social_page.py and new or
  extended tests; one commit, not pushed, no amend.
