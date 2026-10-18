**Verdict: accept.**

No Important or Nit findings in `bb0690d...085ffbd`.

- H-a is implemented; night/detail restructuring and per-route OG delivery remain deferred to H-b.
- `/polls/` preserves the fragment inventory. Explorer asset resolution and coalition hashes remain valid from that route.
- Home source associations and missing-family states hold.
- Watch selection uses unchanged boundaries, includes East Cape, excludes tied/missing results, and introduces neither incumbency inference nor ratings.
- No pre-existing check was weakened. Both routes retain transfer/font budgets; route and screenshot counts track the expanded inventory. The scoped electorate selector still requires 71 entries.
- Social rendering uses aggregates, with suppression retained; no raw posts or handles found.

Read-only verification with `.venv/bin/python -B -c` reported:

- `PASS in-memory populated/absent provenance`
- `PASS missing-family presentation`
- `PASS countdown, tied/missing results, East Cape`
- Transfer/font budgets: home **11,833**, polls **31,362** gzip bytes.
- `PASS supplied-site home verifier`

Limits: PR comments were inaccessible through `gh`. Pytest was unavailable in the local environment. The artifacts bundle failed validation with `INVALID_SOCIAL_FIELDS`; presentation probes used existing site data without claiming bundle validity. That site's manifest identifies `ca77770`, so inspected screenshots are supporting evidence, not independent verification of `085ffbd`. Chromium was not launched; the current host harness result remains supervisor-provided.