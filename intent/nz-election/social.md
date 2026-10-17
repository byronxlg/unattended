# Social analysis and a feed-shaped home: validation (Codex research job research-nz-election-social, 2026-10-17)

Research date: **17 October 2026**. All linked sources were read or attempted on that date. Repository plans, templates and pipeline were reviewed; only the two permitted upstream files were opened in `x402-services`. Neither paid service was called. Costs are estimates; audience appeal and classifier accuracy remain untested.

## 1. What would it show?

The strongest proposition is **what this sample is discussing**, followed by sentiment only if validation supports it. Neither posting volume nor model confidence measures voter support.

### Shared collection and classification

Use one combined query, avoiding separate party searches that multiply billing and distort comparisons:

```text
(#nzpol OR #nzvotes OR #nzelection OR
"Christopher Luxon" OR "Chris Hipkins" OR "David Seymour" OR
"Winston Peters" OR "Chlöe Swarbrick" OR "Chloe Swarbrick" OR
"Marama Davidson" OR "Rawiri Waititi" OR "Debbie Ngarewa-Packer" OR
"Qiulae Wong" OR "Te Pāti Māori" OR "Te Pati Maori" OR
"NZ First" OR "New Zealand First" OR "ACT New Zealand" OR
"Opportunities Party" OR
((National OR Labour OR Greens) (NZ OR "New Zealand" OR Aotearoa)))
-filter:retweets since_time:{start_epoch} until_time:{end_epoch}
```

Call `/twitter/tweet/advanced_search` with `queryType=Latest`. The provider now documents epoch filters, explicitly warning against timestamp-formatted `since:` filters. [Search documentation](https://docs.twitterapi.io/api-reference/endpoint/tweet_advanced_search)

Once daily, retrieve one page from each of the previous NZ day's 24 hourly windows: at most 480 returned posts under the inspected adapter's 20-post page shape. This is a **time-stratified, recency-biased convenience sample**, not a random sample or complete daily count. Record pagination flags; never extrapolate capped windows into platform totals. Verify operators and response limits in the pilot.

Deduplicate IDs and repeated text; retain original posts, replies and quote commentary separately. Do not impose English-only search, but exclude unsupported-language classification transparently. Separate verified party/leader accounts from other authors using a reviewed registry; journalists, campaigners and overseas accounts remain possible contributors.

One Jev request per eligible post, with five keyed questions:

1. `noul`: Is this about current NZ national politics?
2. `choice`: Which party is the primary subject? National, Labour, Green, ACT, NZ First, Te Pāti Māori, Opportunity, other, multiple, none/unclear. Map named leaders through a dated registry.
3. `choice`: Main topic: economy/tax, housing, health, education, crime, Treaty/Māori affairs, climate, immigration, campaign/personality, other/unclear.
4. `noul`: Does the author express an interpretable attitude toward that primary party?
5. `score`: Attitude toward that party, ordered strongly negative, negative, neutral, positive, strongly positive.

Skip sentiment for multiple/unclear subjects, missing context or low evaluability. Never assign one post's negativity to every party it mentions. Preserve probabilities and model version; determinism and claimed calibration do not establish NZ-domain accuracy.

### Four chart candidates

Thresholds below are proposed editorial gates, not statistical guarantees.

| Chart and five-second test | Calculation and sample requirement | Required caption |
|---|---|---|
| **Who dominated this sample?** Horizontal party bars. Reader identifies the most-discussed primary subject. | Relevant posts grouped by primary-party classification; show counts, authors and mixed/unclear separately. Require 100 eligible posts/day overall; suppress percentages for party cells below 20. | “Primary subjects in sampled X posts, not party support or all NZ posts. Search coverage and prolific authors affect the result.” |
| **What is each party being discussed for?** Weekly party-by-topic matrix. Reader spots a contrasting topic. | Cross-tab primary party and main topic; percentages within party. Require 140 posts and 50 authors per party/week, roughly 20 posts/day; suppress cells below 10. | “Topics in this X sample, not voters’ priorities or parties’ policy commitments. Machine classified; ambiguous posts excluded.” |
| **How favourable is the language?** Weekly favourable/neutral/unfavourable bars, initially experimental. Reader understands tone without mistaking it for approval. | Average score probabilities, equalising authors within each party/day; favourable = upper two levels. Require 500 evaluable posts and 100 authors per party/week, roughly 72 posts/day. | “Estimated tone toward the named party among sampled X authors, not voters. Sarcasm, quotations and missing context can change classification.” |
| **What changed in the final campaign week?** Dumbbell chart of party attention shares. Reader identifies the largest sampled change. | Compare 24-30 October with 31 October-6 November using identical queries and coverage. Require 200 primary-subject posts per party in each week, roughly 29/day. | “Change in this sample’s attention share, not electoral swing. Different authors may contribute in each week.” |

Human-check a stratified sample covering parties, Māori language, sarcasm, replies and quotations before publication. Publish precision, confusion tables and abstention rates. Suppress conclusions that reverse when repeat authors or duplicate text are removed.

## 2. Does the volume exist?

**Measured October 2026 daily public-post totals, party breakdowns and unique political authors: not found.** Public evidence supports investigating a sample, not promising daily sentiment for every party.

| Evidence | What it establishes |
|---|---|
| [DataReportal, Digital 2026](https://datareportal.com/reports/digital-2026-new-zealand) | Late-2025 X advertising audience: **678,000**, equivalent to **15.9% of adults**. Advertising reach is not active users, posters or voters; NZ political posting frequency is **not found**. |
| [NZ Social Media Study](https://www.wgtn.ac.nz/policy-hub/projects/completed-projects/new-zealand-election-study-2020) | More than **4,000 Facebook posts over five campaign weeks in 2023**, from parties and leaders. That exceeds **114/day**, calculated, but cannot estimate public X conversation. |
| [Well-being study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9917295/) | Its NZ collection averaged **4,624 tweets/day in 2020**, across topics. Historical collection volume, not a current platform census. |
| [Political Analysis study](https://www.cambridge.org/core/journals/political-analysis/article/ideological-scaling-of-social-media-users-a-dynamic-lexicon-approach/0173A3145A67CB89ACFC8DE09B30C482) | Identified **131 candidate accounts** in the 2014 NZ election; excluded inadequately represented parties. Supports caution about small-party analysis, not a 2026 volume forecast. |

A low-confidence **planning range is 500-5,000 matching posts/day**, not an observed estimate or confidence interval. It deliberately spans an order of magnitude around the historical collection evidence because political share, overseas participation, repost exclusions and current search coverage are unknown. Do not publish this range as a finding about X.

At 480 returns/day, even an unrealistic equal split across seven parties gives only **69 posts each before filtering**. National and Labour are plausible weekly candidates; ACT, Greens and NZ First require measurement. Treat Te Pāti Māori, Opportunity and smaller parties as too thin for daily sentiment until demonstrated otherwise; online prominence need not follow poll share.

A seven-day pilot must measure eligible posts, unique authors, concentration, language and capped windows. It must also distinguish party/leader publishing from public reaction. Hashtag searches alone cannot establish either electorate membership or residence.

## 3. What does it cost?

[Public pricing](https://twitterapi.io/pricing/details) confirms **15 credits per returned tweet**, **15 credits minimum per call**, and **100,000 credits per USD**. Duplicates still cost money. The adapter's comment suggesting a per-request rate should not guide budgeting.

Assumptions: **29 days**, 17 October-14 November inclusive; 480 returns/day; **800 Jev input tokens/post**, including questions; operator-supplied Jev price **USD 0.042/million**, output free. Actual token usage is unmeasured.

| Item | Per day | Through 14 November |
|---|---:|---:|
| Returned posts | 480 | 13,920 |
| Search credits | 7,200 | 208,800 |
| Share of operator-reported 783,103 balance | 0.92% | **26.66%** |
| Search value at public rate | $0.072 | $2.088 |
| Jev input tokens | 384,000 | 11,136,000 |
| Jev cost | $0.0161 | **$0.4677** |

Base upstream total: **about $2.56**. This excludes Actions, engineering and human review. At 200 tweets/hour continuously, search alone would consume **2,088,000 credits**, or **266.63%** of the stated balance.

Propose a hard **7,800-credit daily cap**, including empty calls, duplicates and retries: maximum **226,200 credits, 28.89%** through 14 November. Reserve worst-case page cost before requests; use a persistent ledger across reruns. No automatic top-ups. Other buyers can exhaust the shared balance earlier.

Pace acquisition below **240 returned posts/hour** to respect the operator's ceiling; a full run consequently occupies about two runner-hours. Add a serial daily refresh stage producing one validated social aggregate family, JSON/CSV, method version and status; the existing build renders SVG and HTML.

If the cap prevents completion, retain last-good aggregates and their dates. Show **“Collection limit reached; showing data through {date}”** immediately. Authentication, classification or validation failure behaves similarly; no previous success means unavailable. A normally completed capped sampling plan is labelled sampled, never complete coverage.

## 4. Rules and risks

**Election day is a publishing blocker.** Section 197 restricts statements intended or likely to influence voting; section 197(2A) provides the existing-website exception. Commission guidance permits existing material when voluntarily accessed, unchanged and unadvertised, and says personal political views have no election-day exemption. [Commission social-media guidance](https://elections.nz/guidance-and-rules/advertising-and-campaigning/social-media), [voting-day guidance](https://elections.nz/assets/Candidate-Hub-content/Rules-once-voting-starts.pdf). The current consolidated statutory page could not be retrieved; obtain a current legal check before release.

Do not newly publish sentiment charts or refresh a political-tweet feed on **7 November before 7pm NZDT**. A qualifying frozen page may remain accessible. Freeze election-related publication before midnight, including scheduled rebuilds, embeds and promotional posts; enforce the embargo at deployment time, including delayed runs. Resume after voting closes, subject to any official extension.

Ordinary advertising rules are separate: material encouraging votes for or against parties can be election advertising even unpaid. Editorial exemptions do not automatically cover this newly created site. Obtain a Commission opinion on concrete pages and promotions; apply promoter/authorisation requirements if applicable. [Advertising guidance](https://elections.nz/guidance-and-rules/candidate-hub/candidate-rules/advertising-and-campaigning)

**Data rights are a release blocker.** X's [policy](https://docs.x.com/developer-terms/policy) requires current displayed content, removal compliance and restricted redistribution; content obtained outside X tools has additional republication-consent requirements. Its [agreement](https://docs.x.com/developer-terms/agreement) permits approved analysis but restricts derivatives and third-party access. Confirm that twitterapi.io's supply chain permits this collection, Jev processing, retention and aggregate publication. Inference is distinct from model training, but that does not establish permission to transmit posts to Jev.

No public raw-text archive, author sentiment profiles or inferred voter affiliations. X's [licensing restrictions](https://legal.x.com/data-terms/us/mla.html) specifically address sensitive political profiling. Publish only permitted aggregates; keep raw material out of public Git history and arrange deletion compliance.

**Defamation blocks an unattended quotation feed.** Repeating a candidate allegation can create liability; attribution and “AI classified” disclaimers do not cure it. [NZ defamation guidance](https://defamationupdate.co.nz/legal-guide-publication/) Ship no quotations or allegation summaries without editorial review.

**Bias needs controls plus captions.** Deduplicate, limit author influence, separate official accounts, report concentration and retain unknowns. Do not claim a bot detector: coordinated humans can dominate too. Non-representativeness is a caption; inadequate samples, unstable conclusions and unvalidated classification are suppression conditions.

Methods must disclose queries, windows, truncation, exclusions, author weighting, topic definitions, model/questions/version, validation errors, language gaps, denominators, costs/caps, retention, rights, corrections and election-day handling.

## 5. What exists already?

- **Victoria University NZSMS, 2023:** analysed campaign Facebook communication, including negative campaigning. Stronger precedent for topic/content analysis than voter sentiment because its population is explicit. [University findings](https://www.wgtn.ac.nz/news/2023/10/negative-campaiging-in-the-2023-new-zealand-election)
- **Zavy Pulse, 2017:** sentiment timelines, conversation volume and cross-platform interaction shares, with contextual posts. An engaging historical analogue; predictive validity and a comparable 2023/2026 release were **not found**. [Contemporary walkthrough](https://yournz.wordpress.com/2017/08/21/party-pulse-and-activity-on-social-media/)
- **Curia and Talbot Mills:** public polling and survey-based tracking, not verified public X-sentiment products. Their public material does not establish social-classifier quality. [Curia](https://www.curia.co.nz/), [Talbot Mills](https://talbotmillsresearch.co.nz/)
- **Pulse:** [Webfit Community Pulse 2026](https://poll.webfitnews.co.nz/) describes self-selected community polling. Useful disclosure; not X analysis.
- **Meltwater:** documented mention, keyword and sentiment analytics establish that the dashboard form is commonplace. Public NZ election-specific accuracy, counts and 2023/2026 dashboard: **not found**. [Analytics documentation](https://developer.meltwater.com/guides/listening/analyzing-mentions/)

The [NBC midterms hub](https://www.nbcnews.com/politics/2026-elections/midterms) could not be inspected through available retrieval tools; no browser was available. Its precise layout, card inventory and card-to-detail behaviour are **not verified**.

[NBC's own announcement](https://nbcuniversalnewsgroup.com/nbcnews/2026/03/02/nbc-news-unveils-comprehensive-cross-platform-coverage-for-2026-midterms-beginning-tuesday-with-primary-elections/) confirms results pages, reporting, live digital coverage and streaming analysis. The corresponding forms are result summaries, article teasers, live updates and video entries, but their arrangement on that hub is unknown. Static chart summaries and detail links fit this product; continuous reporting and video production do not.

## 6. The home feed

Reach is the goal. Drop `/vote/`. Use a finite, editorially ordered sequence of chart previews, each with one descriptive sentence and a detail link.

| Order | Preview and description | Destination |
|---|---|---|
| 1 | **Seats:** “What the current poll average means under the stated electorate assumptions.” | New `/polls/#seats` |
| 2 | **Poll trend:** “How published party support has changed.” | New `/polls/#trend` |
| 3 | **Threshold watch:** “Which parties sit near the threshold.” | New `/polls/#thresholds` |
| 4 | **Markets:** “What these specific contracts currently cost.” Increment 7, once available; preserve wording and liquidity. | Proposed `/polls/#markets` |
| 5 | **Electorates:** labelled boundary graphic and search, without unsupported winning-party fills. | Existing `/electorates/` |
| 6 | **Candidates:** roster preview for a reader-selected electorate, with names and affiliations. | Existing `/electorates/<slug>/` |
| 7 | **Conversation topics:** “What sampled X posts discussed this week.” Only after release gates pass. | New `/social/` |

Move existing home detail into `/polls/`, preserving old fragment destinations. Markets are planned, not present in inspected templates. Night and campaign remain placeholders today; promote `/night/` to first position when validated results are available, with preliminary/official status through 27 November.

“Cards” means linked editorial units: preserve draft-2 white ledger, meaningful rules, square corners, quiet typography, party data colours and dominant seat strip. Bend its single-page drill-down into separate detail routes, not its visual grammar. Keep source notes, accessible tables, focus, contrast and reduced motion.

Place downloads and methods in navigation and beside detail charts. Journalists get permitted aggregates, immutable versions and citations; power users get assumptions and tables. Sharing images must retain dates and caveats. Measure referred visits and detail opens; reach improvement remains a hypothesis.

## 7. Verdict

**Build a smaller version:** ship the graphic-led home and conditionally one weekly social-topic chart, withholding daily sentiment and tweet quotations. The feed reuses existing assets, while social sentiment currently lacks demonstrated sample sufficiency, validated classification and established downstream rights. The smallest worthwhile release before 26 October is the home feed plus `/polls/`, with `/social/` added only after an authorised pilot clears those gates.

**What would change the verdict:** a reproducible pilot showing stable, human-validated party sentiment at sufficient author counts.

**Judgement-call alternative:** prioritise shareable poll-and-seat graphics instead of social analysis.

No files changed or paid calls made. Budget arithmetic was checked locally; implementation tests and screenshots were not applicable to this read-only research.