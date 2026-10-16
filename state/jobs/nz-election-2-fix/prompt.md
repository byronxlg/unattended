# nz-election-2 fix: CI failure and six Important review findings

You built increment 2 at 0e82e89 on change/nz-election-2 (PR #10). CI is red and the fresh
review (PR #10 comment, also state/jobs/review-nz-election-2/last.md) found six Important
items. All six are confirmed by the supervisor. Fix all seven below in this worktree, commit,
do not push. Existing tests stay as they are; add regression tests for each item. The
definition of done from state/jobs/nz-election-2/prompt.md stands, run it again at the end.

Read first: the review comment, product/nz_election/pipeline/{average,build,publish,export}.py,
product/nz_election/web/styles.css, intent/nz-election/spec.md lines 38, 73, 186-196, 240,
259, 400-415, and product/nz_election/AGENTS.md design rules.

For each item the invariant and where it is enforced are named; you choose the shape. Check
your change against export.py's validators and every consumer of the field you touch.

0. CI: `test_concurrent_publishers` fails on ubuntu with
   `remote: error: cannot lock ref 'refs/heads/data': is at <b0067> but expected <bbfe2>` and
   `! [remote rejected] HEAD -> data (incorrect old value provided)`. publish.py:71 recognises a
   lost race only by three substrings; this wording is a fourth and raises PUBLICATION_FAILED.
   Invariant: a push rejected because the remote ref moved is a retry, any other push failure is
   fatal. Decide on a detector that does not depend on git's prose (the rejection marker lines
   `[rejected]` / `[remote rejected]`, or a compare-and-swap with `--force-with-lease=data:<sha>`
   you fetched, which makes the failure mode explicit). Prove it with a test that injects this
   exact stderr.

1. average.py:26 `values()` divides through Decimal at default 28-digit precision, so shares at
   a large scale are rounded before the mean. Invariant (spec line 73, plan line 96): averages
   are exact integer arithmetic, rounding happens only in `display`. export.py:73 already
   requires scale to be a power of ten, so `value * (unit // scale)` is exact; or bound the
   scale in the validator and state why. Regression: the review's case, scale 10**30, one party
   at 5*scale-1, Others 95*scale+1: the published mean must not qualify at 5%.

2. build.py:143 passes every window poll to `threshold_watch`, including reviewed exclusions.
   Invariant: the threshold watch and the missing-coverage note are computed from the same poll
   set as the average, `average['poll_ids']`. Check verify.py:18, which also calls
   threshold_watch, for the same mistake. Regression: an excluded poll at 6% must not keep a
   party in the watch whose only included observation is 9% (or the reverse).

3. publish.py:51 returns `older-run-retained` when the checkout holds a newer successful
   acquisition, which drops a later failed attempt's status. Invariant: status.json always
   reports the latest attempt (last_attempt_at, failure) while the data files stay at the latest
   success. Keep the newer bundle, merge the newer attempt status and last-good references;
   status_of / export.validate_bundle define the status shape, keep them the authority.
   Regression: success at 02:00 in the repository, failed attempt at 03:00 built on a 01:00
   snapshot: published status shows last_attempt_at 03:00 and the failure, data unchanged.

4. build.py:221 rejects `site` but accepts `site/posts`, `site/data`, `site/about`; the
   directory exchange then deletes their contents. Invariant: build only ever replaces its own
   output directory and never deletes anything owned by the blog (everything under site/ that
   is not the product's own route root). Decide whether that is an allowlist (the one path
   pages.yml passes) or a denylist of ancestors and siblings; state it in runbook.md.
   Regression: `--out site/posts` and `--out site` both raise UNSAFE_OUTPUT_PATH, nothing
   deleted.

5. build.py:209 renders File, Licence, Rows, Acquired, Immutable download. Spec line 259
   requires size, hash, licence, observation range, retrieval time and producing run per file.
   The manifest (export.inventory) already carries the fields; render them, link the producing
   run, and print an explicit "Not available" where a value is absent (offline builds). Keep
   the table readable at 390 px: decide between two tables or a details row, screenshots decide.
   Regression: a build test asserting every manifest field appears for every file.

6. styles.css / the polls template: at 390x844 the strip is a bare bar and the parties are six
   bordered tiles below it (artifacts/nz-election/screenshots/earlier-coherent-window-390x844.png).
   Spec line 406: the seat counts sit in the strip at 40 px, no separate headline; spec line 194:
   borders only distinguish rows, controls, thresholds or boundaries, no repeated cards. On the
   phone the small segments cannot hold a 40 px count, so use anchored label lanes: each label
   sits in a lane under the strip at its segment's horizontal position with a visible leader or
   tick to the segment, staggered lanes when neighbours collide, no tile borders. Desktop keeps
   counts in the segments where they fit and falls back to the same lanes where they do not.
   Look at both widths after the change and say what you saw.

Definition of done: the eight commands of state/jobs/nz-election-2/prompt.md with their expected
outputs, pytest count above 199, bin/lint ok, `git status --short` empty. If playwright cannot be
resolved offline, paste the error and the supervisor runs the screenshots on the host.
Final message under 40 lines: per item what you changed and the test that proves it, the eight
outputs, departures, open questions.
