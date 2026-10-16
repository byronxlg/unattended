Follow-up on your design-system commit 91ebf33 (same worktree, same branch). The host screenshot
harness ran and failed on axe before any route image was judged:

```text
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
AssertionError: AXE_VIOLATIONS: aria-prohibited-attr (serious, wcag412):
  "aria-label attribute cannot be used on a div with no valid role attribute."
  nodes:
   <div class="segment overhang" style="width:5.51%" aria-label="Overhang"></div>
     target: #main > figure > .strip[role="img"] > .overhang.segment      (build.py line 184)
   <div class="segment overhang" aria-label="Overhang" style="width: 5.51%;"></div>
     target: div[data-picture] > figure > .strip[role="img"] > .overhang.segment   (coalitions.mjs line 142)
```

The strip itself is role="img" with its own aria-label and aria-describedby, so children are
already out of the accessibility tree; a label on a child div is both prohibited and dead. The
invariant: every segment inside the strip is presentational, and the overhang stays described
to assistive tech through the strip label or the seats table (your choice, but check
design.md draft 2 and the seats table copy before choosing). Do not add a role that makes the
segment focusable or announced twice.

Fix both places (server-rendered and the client-side re-render) so they stay identical, keep
the existing tests untouched, add or adjust nothing in tests unless an assertion asserts the
old attribute (then say which and why). Commit on the branch. Report the diff summary and
these tails:

```text
uv run --with pytest pytest -q product/nz_election/tests   -> all passed, count
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/ds-data && uv run product/nz_election/pipeline/build.py --data /tmp/ds-data --out /tmp/ds-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/ds-data --site /tmp/ds-site  -> PASS all
rg -n 'aria-label' product/nz_election/web/coalitions.mjs product/nz_election/pipeline/build.py  -> no segment or overhang line
```
The screenshot harness still cannot run in your sandbox; the host runs it after your commit.
