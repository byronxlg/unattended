# Fix round 1 on change/nz-election-7 (PR #30)

Same worktree, same branch, on top of 176944f. Commit here; never push; do not commit last.md.
Six items: four from the supervisor review and two from the fresh review (both on PR #30).
Protected tests are the ones on main at the base commit 29bf079: `git diff 29bf079..HEAD --stat --
product/nz_election/tests` shows what this branch already moved. Tests this branch added or changed
(176944f) are yours and move with the fix. Nothing may end weaker than main.

## Item 1: the home markets module fits about one mobile screen

At 390 the module is about 16,000 px tall (about 10,600 at 1280). Invariant: the home module shows
the answer at a glance, roughly one 390x844 screen; the full contract list, if published at all,
belongs off the home (a markets route or nothing; your choice, say which). Pick what the home shows
(for example the leading priced contracts per event) and say why in last.md.

## Item 2: placeholder and unpriced contracts are not shown to readers

29 "Not available" rows render, mostly Polymarket placeholders ("Person A", "Person B" with no
price). Invariant: a contract without a price, or a placeholder outcome, never renders on a page;
it may stay in normalized data. If an event has no priced contract, the module says so in one line.

## Item 3: money is rounded and carries its unit

Volume and liquidity print as raw floats ("13118.4606556"). Invariant: every money figure is
rounded and labelled with its unit (USD), like the rest of the site.

## Item 4 (nit): one rules link per event, not per contract

54 per-row "Resolution criteria" disclosures. One link to each market's rules per event satisfies
plan-m2.

## Item 5: a failed live refresh is not reported as fresh

daily_sources.py:58 catches Gamma acquisition and validation failures and returns committed
captures, so daily_refresh.py:102-109 records `fresh`, advances success metadata and exits 0.
Invariant: a failed refresh keeps the last-good bytes and timestamps, publishes an explicit failure
status (stale, with the error code), keeps the original success time, advances the attempt time,
and the workflow ends non-zero. Committed captures are fixtures for tests, never a silent live
fallback. Cover a failure after a good run and a first-run failure.

## Item 6: malformed market timestamps reach the market error contract

export.py:140 validates market rows after the generic timestamp check at line 122, so an empty,
null, wrong-type, float, huge or odd-string `observed_at` gives `INVALID_TIMESTAMP:
envelope.data[0].observed_at` in export but `INVALID_MARKET` in the parser. Invariant: malformed
market input gets the same contract error in both paths. Extend the parity tests to timestamps and
the other required market fields.

## The harness check

The harness passed on a 16,000 px module. Add a check to tests/screenshots.py (or the build tests)
that would have failed on 176944f: the home markets module height at 390 under a stated bound, and
no unpriced or placeholder row on any page. Say in last.md that you ran it against 176944f's build
and it failed, then passes now.

## Done

- `uv run --with pytest pytest -q` from the repo root: all pass, give the count.
- `bin/lint`: ok.
- The screenshot harness on a populated build: PASS, give the route and image counts.
- Screenshots of the home markets module at 390 and 1280 that you looked at; in last.md give its
  height at each width and what it shows.
