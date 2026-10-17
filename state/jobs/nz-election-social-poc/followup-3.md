Fix round 1 on change/nz-election-social-poc (1271c0e, PR #24). The fresh review found five
Important items and the host harness found a sixth. This is a fix job: existing tests and
assertions stay exactly as they are; add new tests that fail on 1271c0e for each defect and pass
after. Nothing gets weaker to pass. Read the review verbatim first (it is on PR #24 as the
second comment; the same text is below) and REVIEW.md.

For each item I name the invariant and where it is enforced; you choose the shape.

1. Upstream text in permitted fields (social.py:182). Invariant: no string taken from an
   upstream response body reaches data/, a page, a log line or a step output unless it passes
   through a closed enumeration this repo owns (party names, attitude classes, topics, a model
   registry) or is a validated number or date. The Jev model field today is a permissive regex,
   so echoed text or an identifier shaped like `jev-fictional-post-id-123456789` is persisted
   and rendered. Replace with a trusted registry of model versions; anything else is rejected and
   recorded as a sanitized error. Extend the validator and test_validator_rejects_identifiers to
   cover sensitive content inside permitted fields, not only added fields.

2. The s197 freeze at deployment time (.github/workflows/nz-election-social-daily.yml:132 and
   .github/workflows/pages.yml:143). Invariant: from 2026-11-07 00:00 NZDT until 19:00 NZDT
   nothing on social/poc/ changes and no social aggregate observed after the freeze start is
   served, whichever workflow builds or deploys, including a delayed or re-run pages.yml run.
   Today the freeze stops the social publication only; the hourly pages.yml can deploy a
   pre-midnight social update after midnight or rebuild the social page inside the window.
   Enforce it where the site is built or deployed (the build can render the route from the
   last pre-freeze state when the build time is inside the window, and pages.yml can pass the
   check), keep the change to pages.yml minimal and prove it with a test that uses --now.

3. Reservation replay on retry (workflow line 87, social.py:353). Invariant: a credit is never
   spent twice against one reservation and the ledger records every spend. Today a retried
   collection after runner loss downloads the original unused reservation and reuses it, and
   publication merges counters with max, so the replay the review ran spent 14,400 and the
   ledger says 7,200. Claim consumption durably before collection (the reservation becomes
   consumed in the published ledger before any paid request), and make publication additive and
   refuse a merge that would hide a spend.

4. Budget day rollover (social.py:352). Invariant: the sum of reservations whose spend happened
   on one NZ day never exceeds 7,800. Today the day is fixed at collection start, so a manual
   run crossing NZ midnight spends against yesterday's reservation while another run today gets
   a fresh allowance. Stop at the day boundary or acquire today's durable allowance before
   continuing.

5. Decimal serialization (social.py:234, validator at line 300). Invariant: every probability sum
   the collector writes passes its own validator. str(Decimal) can produce 1E-8, the validator
   rejects scientific notation, and the final save sits outside the collection exception
   handler, so valid upstream probabilities can block publication after paid collection.
   Serialize fixed-point and test fractional upstream responses including very small values.

6. Populated page fails the harness. On the host, after `social.py --fixtures --out <data>
   --day 2026-10-16` and a build, `tests/screenshots.py` stops at social/poc/ with
   `AssertionError: MISSING_SOURCE: figure {}` from design_checks.py line 27: a figure on the
   populated page has no aria-describedby. Every other route's figures carry it (read
   build.py and electorate_pages for the shared shape). Fix the markup in social_page.py, no
   change to design_checks.py or screenshots.py. The harness invocation in the runbook social
   section must list the social fixtures step before the build so the populated state is what
   gets captured and reviewed.

Definition of done, in the worktree, output in last.md (keep last.md untracked):
- `uv run --with pytest pytest -q product/nz_election` all passed, count stated; the new tests
  named, each shown to fail on 1271c0e (one line each, e.g. by running them against a stash or
  by stating the assertion that fires there).
- `uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data` then
  `uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16`
  then build to /tmp/sp-site/nz-election then `verify.py --data /tmp/sp-data --site /tmp/sp-site all`:
  PASS social, PASS all, 78 routes.
- `uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots`:
  if Chromium is blocked in your sandbox, say so and state the exact command; the host runs it.
- `bin/lint` ok; the secret-name scan clean outside runbook, workflow and social.py.
- No live X or Jev request. One commit, message in the imperative.

The review, verbatim:
- **Important** [social.py:182](product/nz_election/pipeline/social.py:182): Upstream `model` is persisted and rendered after only a permissive regex check. `jev-fictional-post-id-123456789` passes validation; similarly shaped echoed text or identifiers can reach JSON, CSV and screenshots. `test_validator_rejects_identifiers` checks added fields, not sensitive content inside permitted fields. Use a trusted model-version registry. Transport/classification exceptions otherwise suppress upstream diagnostics; the stored static query is explicitly required by the brief.

- **Important** [.github/workflows/nz-election-social-daily.yml:132](.github/workflows/nz-election-social-daily.yml:132): The freeze stops data publication, but does not guard Pages deployment. The existing hourly-triggered [.github/workflows/pages.yml:143](.github/workflows/pages.yml:143) can deploy a pre-midnight social update after midnight, or rebuild the social page during the embargo. The memo explicitly requires enforcement at deployment time, including delayed runs; documenting this as an operational requirement does not enforce it.

- **Important** [.github/workflows/nz-election-social-daily.yml:87](.github/workflows/nz-election-social-daily.yml:87): Collection downloads the original, unused reservation snapshot on each job attempt. Retrying collection after runner loss can reuse that allowance because [social.py:353](product/nz_election/pipeline/social.py:353) checks only the downloaded copy. Publication merges counters using `max`, concealing repeated spending. An in-memory replay spent **14,400 credits**, while that merge records **7,200**. Claim consumption durably before collection; workflow serialization alone does not prevent sequential replay.

- **Important** [social.py:352](product/nz_election/pipeline/social.py:352): The budget day is fixed at collection start, with no rollover check before subsequent requests. A manual run crossing NZ midnight spends against yesterday’s reservation; another run today receives a fresh allowance. Together they can exceed today’s 7,800-credit cap. Stop at the day boundary or acquire today’s durable allowance before continuing.

- **Important** [social.py:234](product/nz_election/pipeline/social.py:234): Probability sums use `str(Decimal)`, but validation at line 300 rejects scientific notation. A valid sum of `0.00000001` becomes `1E-8` and fails `INVALID_SOCIAL_PROBABILITY`. Final saving occurs outside the collection exception handler, so valid upstream probabilities can prevent publication after paid collection. Serialize fixed-point decimals and test fractional upstream responses.

The modified existing assertions retain or strengthen coverage: registered route sets and uniqueness are checked, the hourly/daily race remains, and social publication extends the family union. Secrets are scoped to the collection step; no environment-printing step was found. Handled failures retain aggregates and publish status/ledger updates. No unrelated route removal or family ownership expansion was found. Read-only probes confirmed the model, replay and decimal findings. Full tests were not rerun: `uv` required forbidden cache writes, and the existing virtual environment lacks pytest.

The populated page provides the Proof of concept title, sample size, dates and candid method limitations. Both source notes now use `div.source-note` with links inside `p.source-actions`. The supplied desktop and phone screenshots show a legible empty state with truthful unavailable copy, but provide no evidence for populated chart layout, contrast or touch targets. Those populated screenshots remain necessary.

Important findings: 5