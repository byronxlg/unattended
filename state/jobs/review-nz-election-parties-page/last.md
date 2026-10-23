**Verdict: request changes.**

Critical: none found.

Important:

- `product/nz_election/web/parties.css:1`: The picker inherits `nav { flex-wrap:wrap }` from shared CSS. `white-space:nowrap` only prevents text wrapping; the seven chips still wrap into multiple rows at phone width. Set `flex-wrap:nowrap` to meet the accepted one-row picker plan.
- `product/nz_election/pipeline/snapshots.py:447`: New validators accept malformed provenance. In-memory probes accepted an unrelated `example.com` list source, an invented licence, a null source locator, copied policy-text fields, and a Policy.nz URL with an empty party slug. Enforce the source and links-only contracts and add rejection tests.
- `product/nz_election/pipeline/home_charts.py:114`: Changing label spacing from 22 to 44 alters existing chart geometry beyond adding party links. With the supplied averages, chart height changes from **290 px at the merge base to 378 px**. Preserve existing geometry or obtain an explicit scope change.

Nit: none.

Verified: all edited pre-existing checks retain their assertions while updating route inventories. List ranks match the [EC PDF](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf). Six party-page tests passed when invoked directly, including unchecked donation totals and absent-line omission. `check_absent_text(page(...))` returned `PASS ABSENT_TEXT empty` and `PASS ABSENT_TEXT populated`. `.venv/bin/python bin/lint` returned `lint ok (619 text files)`.

Review limits: the requested brief and screenshots are absent; GitHub access failed, so the PR body remains unchecked. Screenshot question answers, fold placement, keyboard interaction and rendered accessibility remain unverified. `uv run --offline --with pytest pytest ...` failed because the read-only sandbox denied cache access. No files changed.