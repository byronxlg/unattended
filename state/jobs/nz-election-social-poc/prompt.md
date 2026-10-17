# nz-election-social-poc: a proof of concept of X sentiment and party analysis

You are building in `.worktrees/nz-election-social-poc` on branch `change/nz-election-social-poc`,
branched from `main` after the design PR (#21) merged. Read `AGENTS.md` and
`product/nz_election/AGENTS.md` first; their rules bind. Commit in the worktree, never push.

## Goal

Byron (the lab owner) asked for tweet sentiment classification and party categorisation, and then
said: proof of concept every new thing early and refine. So this change is the smallest real
thing: real posts through the real X upstream, classified by the real Jev upstream, aggregated,
and shown on one page clearly labelled as a proof of concept with its sample size and date range.
Refinement comes after we have looked at what it shows. It is not the sentiment feature; do not
build what the memo calls the full plan.

Read first, in this order:

1. `intent/nz-election/social.md`, the research memo (sections 1, 3 and 4 are the constraints:
   the combined query, the hourly-window sampling, the five Jev questions, the 7,800 credit daily
   cap, the s197 freeze, aggregates only, no quotations).
2. `intent/nz-election/spec.md` and `intent/nz-election/design.md` for routes, data families,
   source notes, captions and the design system you render into.
3. `product/nz_election/pipeline/daily_refresh.py`, `publish.py`, `export.py`, `build.py` and
   `.github/workflows/nz-election-hourly.yml`: the data branch, the lease algorithm, the bundle
   validation and the unavailable states are already built; reuse them.
4. Upstream shapes, read-only, only these two files, nothing else in that repository (no .env,
   config or tests): `/Users/byron/repos/x402-services/src/services/x-intel/upstream.ts`
   (twitterapi.io request and response shape) and
   `/Users/byron/repos/x402-services/src/services/jev/index.ts` (TypeSafe System One request
   shape and limits, POST https://api.typesafe.ai/v1/systemone).

## What to build

- `product/nz_election/pipeline/social.py`: `collect` (one `advanced_search` page per hourly
  window of the previous NZ day, `queryType=Latest`, epoch `since_time`/`until_time`, the memo's
  combined query, bounded retries, response size limit), `classify` (one System One request per
  eligible post with the memo's five questions; keep probabilities and the model version),
  `aggregate` (counts and shares only), and a `main` taking `--out <data dir>`, `--day <NZ date>`,
  `--now`. Transport and sleep are injected; tests never open a socket. Keys are read from the
  environment (`X_UPSTREAM_KEY`, `TYPESAFE_API_KEY`) inside `main` only, passed to the clients
  in memory, never logged, never written, never in an exception message.
- The credit ledger: `data/social/credits.json` in the data bundle, one record per run with
  reserved, spent and the cap. Reserve the worst-case page cost (20 posts at 15 credits, plus the
  15 minimum) before each request; stop collecting when the next reservation would pass 7,800
  for that NZ day, including empty calls, duplicates and retries; write the status "Collection
  limit reached; showing data through {date}" into the family status when that happens.
- Output family `social` under `data/social/`: a daily aggregate record per NZ day with sample
  size (posts returned, posts eligible after dedup and the `noul` gate, unique authors as a
  number, the top author's share as a number, windows that hit the page limit), party share of
  primary subject (counts per party), attitude distribution per party (five ordered classes,
  counts; withhold a party's attitude row below 30 eligible posts and say so), topic counts, the
  model version, question text version, and provenance (query text, windows, retrieval times).
  Never write a post id, text, handle, author id, URL or anything that identifies a post or
  author to disk, to `data/`, to a log, to a test fixture taken from the live upstream, or to a
  screenshot. Synthetic fixtures for tests are written by you, with obviously fictional content.
  Validate the family in `export.py` the same way the other families are validated.
- `.github/workflows/nz-election-social-daily.yml`: once a day at 13:40Z (02:40 NZDT, after the
  NZ day closes) and `workflow_dispatch` with a `day` input for a manual run; the two keys come
  from Actions secrets into the step environment only; `permissions: {}` at the top like the
  hourly workflow; the publish stage reuses `publish.py` with the family set so it takes the same
  lease on the data branch; a run on 2026-11-07 that would publish before 19:00 NZDT exits before
  collecting (the s197 freeze from the memo, enforced in the workflow and in `social.py`). A
  workflow that prints its environment or any secret-bearing variable is a reject.
- The page: route `social/poc/` from `config/routes.json`, title "Proof of concept: what X says
  about the parties", built by `build.py` from the `social` family. Above the fold: the label
  "Proof of concept", the sample size and the date range in one sentence ("N posts sampled from
  X over D days, 17 to 19 October 2026, one page per hour, not a complete count"), then one chart
  of primary-party share of posts and one of attitude by party (ordered classes as a stacked
  bar, withheld rows labelled), then topics, then the caption the memo requires (sampling method,
  dedup, author concentration number, classification model and version, unvalidated on NZ text,
  CC and X terms line). The page is in the nav only under a "Proof of concept" label. Unavailable
  state when the family is absent or stale (more than 36 hours since the last day): the page
  says so and shows nothing else. No quotations, no post text, no handles on the page, ever.
  Follow `design.md` for the chart (the design system's chart primitives, party colours from
  `config/party-colours.json`, the source note template with a true calculation sentence:
  "Posts sampled and classified by this site; counts only").
- Runbook: a section in `product/nz_election/runbook.md` naming both secrets (names only), where
  they live (Actions secrets and SSM `/unattended/prd`), the cap, how to run the workflow by
  hand, what the ledger shows and how to read the freeze.
- Tests: deterministic, injected transport with synthetic fixtures; cover the cap (a run that
  would exceed it stops and records the status), dedup, the `noul` gate, the attitude
  withholding threshold, the freeze window, the validator rejecting a record carrying a post
  id or handle field, and a build with and without the family. Do not edit existing tests.

## Constraints

- Standard library only at runtime. No new dependencies.
- One page per hourly window, 24 windows a day, never more; pacing under 240 returned posts an
  hour.
- Aggregates only in the tree, in `data/` and on the page. Counts under 5 in any cell are
  shown as "under 5".
- The caption never claims platform totals, representativeness or a bot detector.
- No emojis, no em dashes. Humble language in the page copy.

## Definition of done

```sh
uv run --with pytest pytest -q product/nz_election/tests            # green, nothing weakened
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data && uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16 && uv run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/sp-data --site /tmp/sp-site
# expected: PASS social, then PASS all; /tmp/sp-site/nz-election/social/poc/index.html contains "Proof of concept" and no "@" handle
uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots   # may fail at Chromium launch in the sandbox; say so and give the host command
bin/lint                                                             # lint ok
rg -n "X_UPSTREAM_KEY|TYPESAFE_API_KEY" --glob '!**/runbook.md' --glob '!.github/**' --glob '!**/social.py' product .github   # expected: no matches outside those three
```

Your final message: the commit, the exact commands you ran with their last lines, the shape of
the `social` family record (field names), the questions you sent Jev verbatim, and anything you
could not verify. The supervisor dispatches the workflow by hand after the PR merges; the first
real day of data is what we look at together.
