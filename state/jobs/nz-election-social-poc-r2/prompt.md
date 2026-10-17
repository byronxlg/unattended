# Follow-up 2: source-note links fail the 44 px target check; last.md is committed

The host ran your definition of done from this worktree at 8faba3e. Tests 331 passed, the
fixture pipeline printed PASS social and PASS all (78 routes), lint ok, no key names outside the
three files. The screenshot harness failed on the social page:

```text
  File ".../tests/screenshots.py", line 95, in check_page
    assert all(height >= 44 for height in targets), 'SMALL_TARGET'
AssertionError: SMALL_TARGET
```

The invariant, enforced at `tests/screenshots.py:94-95`: every `a` outside an svg, `summary`,
`button` and `input` that renders is at least 44 px tall at 390 and 1280. Measured on the host
with the site served under `/unattended/`: the four links in `#source-social` and its attitude
copy (`twitterapi.io`, `Inputs`, `method`, `data run`) are 16 px (37 px when `data run` wraps).
Cause: `styles.css` line 23 sets `.source-note a{display:inline;min-height:0;padding:0}` and
restores the 44 px target only for `.source-note .source-actions a`. Every other route puts the
source note's links in a `<p class="source-actions">` inside the note; see `build.py:82-91`
(`source_note`) and `electorate_pages.py:32-41`. Your note in `social_page.py:34-40` is a single
`<p class="source-note">` with the links inline in the prose.

Do, in this worktree, on the same branch, a new commit (not amended):

1. Render the social source note in the shared shape: a `div.source-note` with the prose in a
   `p` without links, and the links in a `p.source-actions` (reuse `build.source_note` if its
   envelope fits the social family; otherwise mirror its markup). Both copies (`source-social`,
   `source-social-attitude`) get the fix. No CSS change: the stylesheet already handles this
   shape, and a rule that lowers the 44 px floor is a reject.
2. `last.md` at the worktree root is tracked in 8faba3e. Remove it from the branch
   (`git rm --cached last.md`, commit) and keep writing it on disk; it stays untracked. The PR
   must not carry it.
3. Re-run the definition of done from the original brief. The screenshot harness will stop at
   Chromium launch in the sandbox; before it does, confirm your markup against the invariant by
   reading the three stylesheet rules named above. Say in last.md what you changed and that the
   host must run the harness.

Nothing else moves. No test edits. No live X or Jev request.
