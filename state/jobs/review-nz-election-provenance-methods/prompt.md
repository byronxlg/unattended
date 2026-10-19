Fresh-context review of nz-election-provenance-methods, read-only. Worktree .worktrees/nz-election-provenance-methods,
branch change/nz-election-provenance-methods, head 7224985 on main 4a36c80. PR #41 (`gh pr view 41`).
Diff: git diff 4a36c80..7224985. Judge against REVIEW.md, intent/nz-election/design-principles.md (principle 5:
compact footnotes on the page, full records on anchored Methods sections) and the brief
state/jobs/nz-election-provenance-methods/prompt.md (main checkout). The engineer's account
(state/jobs/nz-election-provenance-methods/last.md) is a claim to check. Context: issue #40 (`gh issue view 40`)
asks that provenance blocks leave electorate and party pages, one "Sources and method" link per module.

Check: (1) every record that left a page is reachable on Methods at an anchor the page links to; no source or
licence attribution lost from the site; (2) every fragment ID that existed on main still resolves; (3) the new
provenance check would fail on 4a36c80 and is not weaker than what it replaces; (4) no test on main at 4a36c80
weakened, no harness check loosened; (5) no "Not available"-style text added.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
