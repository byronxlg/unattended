Verdict: **request changes**.

Critical: None.

Important:

- `product/nz_election/pipeline/advance.py:75-89`: Malformed descriptors bypass handled failure retention. Probes produced `KeyError` for missing `kind`, `TypeError` for null `start`, and `AttributeError` for null `advance`. Since daily refresh catches only `ValueError`, these abort the whole refresh without publishing failure status or unrelated successful families. Validate descriptors and raise `INVALID_ADVANCE`.

- `product/nz_election/pipeline/m3_checks.py:20-30`: Absence enforcement is incomplete. With no backing rows, the checker accepts `<h3>Advance voting</h3>`, an empty `<figure>`, and “No campaign totals are available here yet.” These contradict the explicit heading/chart/placeholder prohibition. Add structural checks and negative tests.

- `product/nz_election/pipeline/campaign_page.py:9`: One observation outside the hardcoded voting window silently hides the entire valid series. A descriptor-backed series containing October 25’s supplied zero and October 26’s count passes normalization but renders nothing. The committed 2023 capture demonstrates pre-opening zero rows. Preserve valid observations rather than rejecting the module wholesale.

Nit: None.

Checked read-only: supplied production and populated bundles validate; production has no advance module; daily/cumulative gaps and tie rejection behave correctly. Existing contract assertions remain intact and cover the expanded family. Publication mapping is scoped to advance. Figure markup, licence, and archive provenance are present.

Full tests and screenshots were not rerun; visual acceptance remains unverified.