**Verdict: request changes.**

Critical: none.

Important:

- `product/nz_election/pipeline/route_cards.py:65`: Item 4 remains incomplete. Probing `night/` on 28 November still returns “Official results due 27 November.” `night_page.py:131,159` also call `sentence()` without the build clock, preserving future-tense copy for settled results. Apply date-aware wording to HTML, share metadata and live packages.
- `product/nz_election/pipeline/social.py:630`: The sunset check also blocks `--check-freeze`, used by the publication job at `.github/workflows/nz-election-social-daily.yml:163`. A completed bundle queued across sunset cannot publish its sample or final credit ledger, and cannot trigger Pages. Probe output changes from `allowed=true` to `skipped=true`. Separate collection eligibility from publication freeze checks.
- `product/nz_election/pipeline/result_sources.py:37`: Reaching midnight on 27 November unconditionally asserts “Official results are published,” even with no official data. The scheduled date does not establish publication. Use neutral past-date wording until publication is evidenced.

Nit: none.

Items 1-3 appear fixed. Read-only `python3 -B -c` probes confirmed:

```text
All four windows: before=True, at=False
night alias=True
transport/classify/collect: SunsetReached SOCIAL_CLOSED
retry crossing: SOCIAL_CLOSED calls=1
home/vote past copy: before=False, at=True
```

Freeze boundaries remain unchanged. Main-test edits match changed contracts. No pytest run or files changed. Existing screenshots were inspected but predate the copy fix.