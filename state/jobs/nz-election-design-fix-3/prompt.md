Third follow-up on change/nz-election-design (now 33eb475). The host harness still fails on the
invalid-link state, now with the auto-wait:

```text
AssertionError: Locator expected to contain text 'This coalition link is invalid.'
Actual value:
  13 x locator resolved to <p role="status" data-warning=""></p>   unexpected value ""
```

Cause, confirmed from the harness code: check_page (tests/screenshots.py lines 96 to 101)
presses Tab and Enter on the skip link, whose href is "#main". That replaces the URL hash
"#coalition=invalid" while the explorer is still awaiting its data (start() awaits before
restore()), so restore() reads "#main" and writes nothing. The same happens to any state that
is carried in the hash (changed-inputs too). My host probe without the skip-link step shows
the warning text, so the product is correct and the harness clobbers its own input.

Fix in the harness only, authorised as before: make the hash-carried state assertions read the
explorer's warning before the skip-link activation, or re-navigate to the state route after
check_page and then read, whichever keeps check_page's focus check intact for every route.
Asserted strings unchanged, no sleeps, no skipped states, no loosening. Check the
changed-inputs and invalid-count paths get the same treatment where they depend on the hash.
Commit on the branch. Report the fix and the tails of pytest, refresh/build/verify and
bin/lint as before. The host runs the harness after your commit.
