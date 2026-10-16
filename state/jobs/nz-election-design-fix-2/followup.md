Second follow-up on change/nz-election-design (now 980d06e). The host screenshot harness got
past axe (your fix held) and then failed on the invalid-link state:

```text
File "product/nz_election/tests/screenshots.py", line 151, in state_images
    assert 'This coalition link is invalid.' in page.locator('[data-warning]').inner_text()
AssertionError
```

Diagnosis from the host: a probe that builds the same fixture with design_states.fixture, serves
it with the harness Handler, loads PREFIX + 'nz-election/#coalition=invalid' at 390x844 and waits
1000 ms shows `<p data-warning role="status">This coalition link is invalid. It has not been
applied. Reset to start again.</p>` and an empty console. So the copy is right and the state
renders; the harness reads [data-warning] the moment check_page returns and the explorer has
not written it yet. It is a race between the harness's immediate read and the module's hash
handling.

Find out which side moved: git diff main...HEAD -- product/nz_election/web/coalitions.mjs. If
this branch made the explorer apply the hash later than main did (after an await, a fetch, a
layout read, a deferred render), restore the ordering so the warning is written synchronously
on module start as on main; that is the product fix and the preferred one. Only if main had the
same ordering and the race was already latent, the fix is in the harness and I authorise this
one change to it: wait for the explorer's state before reading, with the same asserted text,
for example a Playwright expectation that auto-waits on the locator text, or a wait for a ready
attribute the module already sets. Do not loosen the text, do not skip the state, do not add
sleeps. Check whether the two sibling states (invalid-count, changed-inputs) read the warning
the same way and apply the same treatment.

Commit on the branch. Report: which side moved and the evidence (the diff lines), the fix, and
the tails of:
```text
uv run --with pytest pytest -q product/nz_election/tests   -> all passed, count
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/ds-data && uv run product/nz_election/pipeline/build.py --data /tmp/ds-data --out /tmp/ds-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/ds-data --site /tmp/ds-site  -> PASS all
bin/lint -> lint ok
```
The harness still cannot run in your sandbox; the host runs it after your commit.
