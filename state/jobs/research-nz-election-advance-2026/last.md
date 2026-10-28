**Yes: an official statistics page and CSV download link are published on vote.nz.** Checked **28 October 2026, 20:07-20:09 NZDT**. No files changed.

1. **Latest official count:** [Voting statistics](https://vote.nz/2026-general-election/about/overview/voting-statistics) reports **175,748 through 27 October**: 69,034 on 26 October and 106,714 on 27 October. The 28 October row is blank. These are informal daily counts, subject to revision, excluding overseas votes. Updates are scheduled daily from 27 October.

2. **File and compatibility:** The page links [AdvanceVoteCSV](https://vote.nz/2026-general-election/about/overview/voting-statistics/AdvanceVoteCSV). The web fetch encountered `application/csv` but could not expose its bytes. Thus **the link exists; actual CSV columns and parser acceptance remain unverified**.
   - HTML columns: `Date`, `2020 General Election`, `2023 General Election`, `2026 General Election`; observations are **daily**, with a separate total.
   - `advance.py` accepts those observations with `kind="daily"`, `start="2026-10-26"` and `count_column="2026 General Election"`.
   - **Preflight rejects that header** because it requires explicit daily/cumulative wording within the count header, even though the page supplies the semantics.
   - Read-only verification used `PYTHONDONTWRITEBYTECODE=1 python3 -B -c '…'` on an **in-memory HTML transcription, not downloaded CSV**. Output:
     ```text
     advance.parse: [{'date': '2026-10-26', 'daily': 69034, 'cumulative': 69034}, {'date': '2026-10-27', 'daily': 106714, 'cumulative': 175748}]
     advance_preflight.inspect: INVALID_ADVANCE: missing daily or cumulative evidence in count header
     ```
   - `uv run --no-project --offline --no-sync` failed because its cache required a prohibited write. No `/tmp` download was possible.

3. **Media fallback is unnecessary and already stale.** [Newswire, 28 October, 08:21](https://newswire.nz/a/K3wAHXluj5s6E1CSU5rsvlipogO/coalition_holds_its_ground_as_national_slips_below_30_but_overhang_arithmetic_not_the_kingmaker_label_may_decide_who_governs.html) says: “The Electoral Commission recorded 68,944 votes on the first day, 4.7% more than on the equivalent day in 2023.” The official table now gives **69,034**.

Fetch ledger, covering every directly requested URL; search-result-only URLs excluded:

| URL | Fetch result and time, NZDT |
|---|---|
| [Statistics page](https://vote.nz/2026-general-election/about/overview/voting-statistics) | 20:08: readable HTML via web; origin status undisclosed. Curl: DNS failure, `HTTP 000`. |
| [CSV](https://vote.nz/2026-general-election/about/overview/voting-statistics/AdvanceVoteCSV) | 20:08: web tool reported `(400) Unsupported content-type: application/csv`, **not a confirmed origin 400**. Curl: DNS failure, `HTTP 000`. |
| [EC 2026 news path](https://elections.nz/media-and-news/2026/) → [homepage](https://elections.nz/) | 20:07: web redirected and returned HTML; status undisclosed. |
| [EC news index](https://elections.nz/media-and-news) | 20:07: readable HTML, no count in displayed summaries; status undisclosed. Curl: DNS failure, `HTTP 000`. |
| [EasyVote announcement](https://elections.nz/media-and-news/2026/more-easyvote-emails-on-their-way) | 20:07: web open failed; search text concerns emailed slips, not votes; status unknown. |
| [Media election results](https://media.election.net.nz/) | 20:07: HTML announces election-night results; no advance count shown. Status undisclosed; curl DNS failure, `HTTP 000`. |
| [Newswire article](https://newswire.nz/a/K3wAHXluj5s6E1CSU5rsvlipogO/coalition_holds_its_ground_as_national_slips_below_30_but_overhang_arithmetic_not_the_kingmaker_label_may_decide_who_governs.html) | 20:07: readable HTML; status undisclosed. |

No browser was available. Social posts were not independently confirmed; RNZ search access was robots-blocked. Exact origin HTTP statuses and CSV bytes remain unconfirmed.

4. **Supervisor actions, three lines:**  
Capture today’s official vote.nz table, revision caveat, timestamp and linked CSV bytes when accessible; resolve the preflight header mismatch before ingestion.  
`vote/`: “175,748 advance votes reported through 27 October. Preliminary; excludes overseas votes.” Link the official page.  
Home: show the same dated, sourced figure after review; until captured, say “Advance voting is open” without a count, zero or historical substitute.