# nz-election-night-stop fix-1 (PR #80, fresh review request changes)

One Important item, confirmed by the supervisor reading `product/nz_election/web/night-live.mjs:10`:

`ended()` reads `this.loopEndsAt`, which is set only from a successful package response. Until
then `Date.parse(undefined)` is NaN, so after the cutoff the client still polls: offline then
resume past the cutoff kept fetching and showed "Showing the dated packaged snapshot"; a first
visit after the cutoff fetches once.

Invariant: the browser knows the cutoff before its first tick, from the same shared Python
constant the workflow and watchdog use (no second literal in JS). Past the cutoff the client makes
zero requests, on first visit, on resume and after failures, and shows the ended notice.

Choose the shape (data attribute on the generated night page, or a constructor option fed from
it); a package response may still carry `loop_ended`/`loop_ends_at` but must not be needed.

Done when:
- A regression test in the night browser/unit tests (the review's three probes: known deadline,
  offline then resume past cutoff, first visit after cutoff) asserts zero fetches past the cutoff
  and the ended notice; it fails on 95387fe and passes on HEAD.
- A test asserts the page's embedded cutoff equals the Python constant.
- `uv run --with pytest pytest -q product/nz_election/tests` passes (browser tests with host
  Chromium where available), `bin/lint` ok.
- Tests on main at bd53141 are not edited; this branch's own tests may move. Commit in the
  worktree, do not push; summarise in last.md outside the tree (do not commit last.md).
