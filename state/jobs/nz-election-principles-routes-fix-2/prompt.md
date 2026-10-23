# Fix-2: host harness HOME_MARKET_HEIGHT (principles-routes, bd1de2f)

Fix-1 cleared the landmark-unique failure. The host harness (`screenshots.py --site site` on the
populated build from `site/build_review.py`, Chromium) now stops at:

```
market_checks.py:36 check_browser
AssertionError: HOME_MARKET_HEIGHT: 957 > 844
```

Cause: `market_panel.py:72` turned the "Amounts and observation details" `<details>` into an open
`<div>`, so every per-contract volume, liquidity and observed line now shows inside `#markets` at
390 px. The 844 px budget (main at c6d8ff3) stays. Principle 3 in
`intent/nz-election/design-principles.md` sends provenance to Methods: keep the amounts and
observation lines reachable (a link from the module's source-actions to where they are listed in
full, on the markets detail or methods route) rather than inline in the home module. Choose the
place; keep the `source-markets` note, the attribution and the rules links in the module.

Audit the same pattern elsewhere before you finish: any other disclosure this branch opened inside a
module that has a height, row or byte budget (home byte and font budgets, polls budgets,
HOME_MARKET_ROW_BUDGET, the seat module). Add a no-Chromium check that fails on bd1de2f: the home
`#markets` section contains no per-contract volume/liquidity lines (or an equivalent structural
proxy you can justify for the height). Report it failing on bd1de2f and passing on HEAD.

Tests on main at c6d8ff3 stay as they are except where this change's registered set moves them;
this branch's own tests move with it. Nothing weaker.

Done when: `uv run --with pytest pytest -q product` passes, `verify all` PASS all, `bin/lint` ok,
the new check's fail/pass output in last.md; commit in the worktree, do not push, last.md not
committed.
