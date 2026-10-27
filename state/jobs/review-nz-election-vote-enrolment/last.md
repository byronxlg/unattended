Verdict: **request changes**.

Critical: None.

Important:

- [product/nz_election/pipeline/vote_page.py:43](/Users/byron/repos/unattended/.worktrees/nz-election-vote-enrolment/product/nz_election/pipeline/vote_page.py:43): Missing `source_url` crashes rendering at and after the close with `KeyError: 'source_url'`. Guard the lookup, retain the closed message, and omit the link when absent. Add a regression test. Snapshot validation rejects this input, but the requested sparse-field rendering contract explicitly includes it.

Nit: None.

Python probes (`python3 -B -c`, no pytest) confirmed:

```text
Before close: old=2 closed=0 update=1
At close:     old=0 closed=2 update=0
No at:       old=0 closed=1 update=0
No source_url at close: KeyError 'source_url'
```

Equivalent UTC/NZ timestamps agree; a shifted `at` takes precedence over the date. Both summary locations switch together. Provenance remains intact; new wording makes no additional eligibility claim. Tests check text, source URLs and absence rather than serialized markup.

Limits: brief file absent; inspected the supplied base screenshot only, so changed-page visual verification remains incomplete.