# Fix 1 on PR #73: the client renderer still says OPP

Fresh review (request changes, one Important, confirmed by the supervisor): the server strip now
prints TOP, but `product/nz_election/web/coalitions.mjs:119` still renders `p.toUpperCase()`, so
the browser-drawn strip shows "OPP" for The Opportunity Party. With the same seven-party input,
Python renders TOP and JavaScript renders OPP.

1. Make the client lane label use the same abbreviation as build.strip(): opp shows "TOP", every
   other party unchanged. One source of truth if practical (the mapping you added for the
   server, exposed to the client through the data it already reads), otherwise a mirrored
   constant with a parity test that would fail if the two disagree.
2. Extend the Python/JS parity coverage to a party set that includes opp, asserting `<span>TOP</span>`
   and no "OPP" in the client output. It must fail on e9ca98d.

Constraints: tests on main at 170bf94 unchanged; this branch's own tests move with it. Absent-text
rule holds. Commit in this worktree (do not commit last.md), do not push.

Done when: `uv run --with pytest pytest -q product/nz_election` passes (say what skips; the
coalitions browser test needs host Chromium, say if it skipped), `bin/lint` prints ok, and last.md
shows the new parity test failing on e9ca98d and passing on HEAD.
