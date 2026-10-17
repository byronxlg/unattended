Correct stop: the brief asked for the singular-day wording while forbidding assertion edits,
and test_social.py:179 pins "over 1 days". That conflict is mine. Drop item 3 entirely: the
wording and its assertion move together in the refinement round after the first real day,
not in this fix job. Nothing in tests/ changes except new tests.

Proceed with items 1 and 2 of followup-4.md exactly as written (publication retry idempotent,
zero-request handled stop publishes, lowering or hiding a spend still refused; budget date
rechecked immediately before transport). Same definition of done as followup-4.md: all tests
passed with the count, each new test named and shown failing on 0642382, the fixture
pipeline ending PASS all, bin/lint ending lint ok, one commit touching only publish.py,
social.py and new or extended tests, not pushed, last.md untracked.
