# Night data

Build offline with `uv run product/nz_election/pipeline/daily_refresh.py --out /tmp/night-data`.
Check with `uv run product/nz_election/tests/night_smoke.py /tmp/night-data` and
`uv run product/nz_election/pipeline/verify.py night`. No page or live feed is enabled by this job.

`night/index.json` enumerates sequences, snapshot dependencies, reference versions and SHA-256
hashes of every dependency and CSV sibling. All files use the existing provenance envelope.
References include each archive's parties, candidates and electorate registry. They are not
joined to the 2026 registry. Every JSON has a lossless CSV sibling; nested values use JSON columns.
The outer data manifest inventories the index as well as its dependencies. Publication validates
all bytes before atomic directory exchange. A failed family refresh retains all last-good bytes;
a valid replacement removes obsolete night files. Daily publication compares acquisition vectors
through `night/index`, independently of other families.

The 2017, 2020 and 2023 archives are labelled `Final snapshot`. Each has one snapshot, without
invented elapsed times. The feed's `updated` string is preserved as `source_updated_local`.
No UTC conversion is asserted: the XML supplies no offset, and the captured 2023 final archive
actually says 2024-11-10. Acquisition timestamps remain in source metadata, generation timestamps
in the envelope. An observation timestamp is omitted where its timezone is unverified.

The two demo captures are labelled `Recorded demo`: simulated results, not an election.
Their source clock reads 14:22:32 and 14:23:02 on 20 October 2026. Both manifest retrieval times
are 01:23:09Z; do not infer a retrieval interval from those identical values. Keep source order,
including any future simulation reset; decreasing counts need not mean corrupt demo data.
The committed national feeds contain no electorate detail paths or leader/margin results.
Those fields are absent. No detail URL was guessed or fetched.

`Illustrative replay based on 2023 final results` uses three steps, at elapsed seconds 0, 300
and 600. Each party's intermediate votes are floor(final votes * numerator / 10), with numerators
1, 5 and 10. Every step records this derivation and its final-snapshot dependency. Synthetic steps
have no source update timestamp. Intermediate steps omit reporting statistics and seats because
vote scaling does not support those claims. The final step preserves the final counts: 2,851,211
valid party votes and source-reported House 122. Reported seats remain distinct from allocator output.

The parser accepts bounded UTF-8 XML only (2,000,000 bytes), rejecting entities and DTDs before
parsing. `XML_DOCUMENT` covers malformed document inputs; `XML_COUNT` covers all malformed integer
count tokens, including booleans, decimals, Unicode digits and values over nine digits.
`XML_PERCENT`, `XML_FIELDS`, `XML_REFERENCE`, `XML_TIMESTAMP` and `XML_TOTAL` identify other contract
failures. Duplicate and unknown reference IDs fail. Party ID 0 is the observed unaffiliated sentinel
in candidate files; electorate ID 0 is the observed list-only sentinel. Preserve the 2020 candidate
569's supplied party 0/list rank 1 without treating it as a registered party list.
Party percentages are checked against summed valid party votes using the supplied decimal precision;
`total_votes_cast` includes other votes and is never the party-share denominator. Source fields for
special votes remain raw statistics, not evidence for a preliminary-to-final specials component.

The page job owns replay controls, no-JS rendering and screenshots. Client XML parsing/parity and
live-feed checks belong with the client implementation; this data-only job adds no client script.
Before live use, establish timezone evidence, check HTTPS availability and browser CORS separately,
and capture validated references before accepting results. This package makes no live availability claim.
