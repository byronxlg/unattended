Fourth follow-up on change/nz-election-design, host harness run 2026-10-17 00:21Z to 00:34Z on
your 9b593cd. fix-3 held: all state images passed the hash-carried checks. The harness then
failed in state_images on an electorate state fixture with an axe violation, a product defect:

landmark-unique (moderate): two <div class="scroll" tabindex="0" role="region"
aria-label="Reported local shares"> on one page, `.local-poll:nth-child(2) > .scroll` and
`.local-poll:nth-child(3) > .scroll`. Source: electorate_pages.py line 88 passes the constant
'Reported local shares' to table() for every local poll, so an electorate with two local polls
has two landmarks with the same accessible name.

Invariant: every landmark on a page has a unique accessible name; enforced by the axe assertion
in tests/screenshots.py check_page (landmark-unique). Choose the shape yourself (the pollster and
measure, or the heading, are natural candidates); keep the sighted table caption readable, keep
the source pairing (aria-describedby) as it is, and check build.py for any other table() caller
that can repeat a label on one page (home, polls, coalitions, candidates). Product fix only; do
not edit tests or weaken the axe check. Run pytest, refresh/build/verify, bin/lint; a
test_electorates assertion that two local polls on one electorate yield distinct region labels
is welcome if you add it as a new test, not by editing an existing one. Commit on the branch, do
not push, reply with the commit hash and the verification tails, and list any check you could
not run in the sandbox as a claim.
