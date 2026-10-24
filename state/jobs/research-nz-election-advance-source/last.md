**Checked 25 October 2026 NZDT. The 2026 statistics URL remains unconfirmed.** No files changed. I read the parser, advance manifest entry and supervisor capture gate.

1. **Publication location and historical pattern**

I found no 2026 advance-statistics link in the official pages inspected. The [elections.nz homepage](https://elections.nz/) directs visitors to the [2026 election overview](https://vote.nz/2026-general-election/about/overview/) (redirects to [this URL without the trailing slash](https://vote.nz/2026-general-election/about/overview)). Neither establishes a statistics endpoint. **This does not prove it is unpublished.** I did not invent or probe a 2026 CSV path.

| Election | Official page and file | Publication schedule | Data |
|---|---|---|---|
| 2023 | [Page](https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics), [CSV](https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/AdvanceVoteCSV) | Updates began Tuesday 3 October, one day after [opening on 2 October](https://elections.nz/democracy-in-nz/historical-events/2023-general-election/key-dates). Daily through election day. Time of day unconfirmed. | Daily counts by election-year column; separate cumulative chart. February 2024 revision includes special votes; excludes overseas votes. |
| 2020 | [Page](https://elections.nz/democracy-in-nz/historical-events/2020-general-election-and-referendums/advance-voting-statistics-for-the-2020-general-election), [CSV endpoint probed](https://elections.nz/democracy-in-nz/historical-events/2020-general-election-and-referendums/advance-voting-statistics-for-the-2020-general-election/AdvanceVoteCSV) | Updates from 2pm weekdays beginning Monday 5 October, two days after Saturday opening. | Daily counts, comparison-year columns and separate cumulative chart; excludes overseas votes. |

The 2020 page exposes a CSV download, but the web tool could not resolve that click. Probing the historical `AdvanceVoteCSV` suffix returned an `application/csv` content-type error, supporting its existence without exposing its bytes. **27 October first publication and a 2026 update hour remain unconfirmed.**

2. **Plain GET, status and archive fallback**

All attempts below were on **25 October 2026 NZDT**:

| Fetch | Observed result |
|---|---|
| Plain `curl` GET of 2023 CSV | `curl: (6) Could not resolve host: elections.nz`. No HTTP response; cannot assess today’s WAF. |
| Web-tool GET of both historical CSV endpoints | Tool reported `(400) Unsupported content-type: application/csv`. This is a tool error, **not an established origin HTTP 400**. |
| Plain `curl` GET of [pinned Wayback `id_` snapshot](https://web.archive.org/web/20240513105727id_/https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/AdvanceVoteCSV) | DNS failure; `HTTP 000`, meaning no HTTP response. Web tool also could not access it. |
| Historical HTML pages and other pages listed here | Web tool returned readable content, but did not expose origin status codes. |

The committed manifest records an **Incapsula HTML challenge at the origin**, followed by acquisition through that Wayback snapshot on **20 October 2026 at 00:50:03Z**. That establishes a previously used historical fallback, not current availability or a timely fallback for 2026 figures.

3. **Parser compatibility**

Likely compatible **if 2026 retains the historical CSV schema**, but no 2026 bytes were available to verify. The committed 2023 CSV uses `Date`, election-year columns, ISO dates (`2023-10-02`), integer daily counts, blanks and a `Totals` row. The parser handles these, plus dates such as `26 October`.

Expected metadata changes: `year=2026`, the actual 2026 count-column name, `kind="daily"` if confirmed, and the earliest supplied observation date as `start`. Inspect pre-opening rows: the 2023 CSV supplies explicit zeros before opening. HTML-only tables would require extraction; changed date formats could require adaptation.

Read-only verification: `PYTHONDONTWRITEBYTECODE=1 python3 -B -c '…advance.parse(…)…'` returned:
`Historical fixture parse: 14 rows; last: {'date': '2023-10-13', 'daily': 260219, 'cumulative': 1640204}`

Additional URLs fetched during discovery: [22 October announcement](https://elections.nz/media-and-news/2026/voting-starts-on-monday), [2026 media kit](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf), [participation statistics](https://elections.nz/stats-and-research/participation-in-voting), [about elections](https://elections.nz/democracy-in-nz/about-elections). None established the missing endpoint or publication hour. Search-result-only URLs were not fetched.

4. **Recommendation, three lines**

Use supervisor capture each morning for now; retry after 2pm if absent, pending confirmation of the 2026 schedule.
Keep the daily workflow consuming reviewed committed captures until the official link, raw GET and schema are verified.
Before first data, omit the module; afterwards retain dated figures with “No newer figure available; latest observation: [date]”, preserving gaps, never zero-filling.