# Follow-up 1: keep the party's real name in the query

Supervisor review of bc917a6: the diagnostics item is accepted as is. One correction on the
query item.

The party is "The Opportunities Party" (TOP). Your commit kept the phrase "Opportunity Party"
and dropped "The Opportunities Party". A quoted phrase search for "Opportunity Party" will not
match tweets that say "Opportunities Party", so the surviving term is the one that does not
match the party's name. Dropping "New Zealand First" in favour of "NZ First" is fine.

Do:

1. In `product/nz_election/pipeline/social.py` `QUERY`, replace `"Opportunity Party"` with
   `"Opportunities Party"` (no leading "The": the phrase still matches the full name and saves
   four characters). Same edit to the query block in `intent/nz-election/social.md`.
2. Your own new test `test_query_keeps_hashtags_leaders_and_parties` in
   `test_social_diagnostics.py` pins `'Opportunity Party'`; move that one term to
   `'Opportunities Party'`. No other test changes. `PARTIES` and the leader mapping stay as they
   are (the classifier label is `Opportunity`, that is separate from the search phrase).
3. Rerun the four commands from the brief. Expected: product tests 367 passed,
   `PASS query length 472 of 512`, `PASS all`, lint ok.
4. One more commit on this branch with a humble message; do not amend, do not push, do not
   commit `last.md`. Rewrite `last.md` with the new measured length and the exact output lines.
