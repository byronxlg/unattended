# Audiences for the NZ election site, 2026-10-17 (Codex research job research-nz-election-audiences)

## Summary

Keep task-based audiences: voting-help seekers, policy comparers, local-contest readers, poll followers, overseas voters, election-night watchers, post-election checkers, and data users.
Young and first-time voters belong within voting help; age alone does not justify a separate site.
Prioritise three changes: a concise `/vote/` gateway, candidates-first electorate pages, and a results-first `/night/` view that remains useful after polling day.
Give policy comparers a clearly labelled exit to established comparison tools.
Retain downloads as a specialist entry point, with immutable versions and explicit reuse terms.
The surprise: the Herald published its 2023 polling model and source code. “Nobody publishes methods” is not a defensible differentiator. [S9]
These are evidence-backed design hypotheses, not measured segments of this site's visitors.

## Audiences

All sources below were read or attempted on **2026-10-17**. Device, moment and five-second abandonment descriptions are hypotheses for testing; the sources establish information needs, not those behaviours.

### 1. People preparing to vote

**Arrival question:** “What do I need to do before I can vote?”

**First thing:** enrolment deadline, official voting-place finder, and a short explanation of the two votes. Include obvious links for accessible formats, language help and assisted voting.

**Device and moment:** phone before leaving home, during a commute or in a polling-place queue.

**Five-second exit:** a seat chart where practical instructions should be, unexplained MMP terminology, or inaccessible controls.

The Commission's 2023 survey found that 18% sought additional voting information, rising to 26% among 18-29-year-olds. Among information seekers, 48% searched online and 29% used the Commission website. This supports a practical gateway, not an exclusively youthful identity. [S1] Current official guidance supplies the actionable destination. [S4]

### 2. Undecided voters comparing policies

**Arrival question:** “Which parties offer what I want?”

**First thing:** an issue-based comparison destination, visibly separate from polling popularity.

**Device and moment:** phone during a conversation; laptop when comparing several issues.

**Five-second exit:** being offered a coalition calculator as an answer to a policy question.

Vote Compass's 2023 reporting explicitly discussed undecided respondents and their policy priorities, while acknowledging self-selection. Policy.nz offers policy and candidate comparison. These establish a real task, but do not measure its prevalence among this site's visitors. [S6, S7]

### 3. Readers following their electorate

**Arrival question:** “Who is standing here, and how competitive is this contest?”

**First thing:** electorate search, correct roll, candidate names, then dated local evidence.

**Device and moment:** phone from a shared local link; couch browsing before voting and checking the count.

**Five-second exit:** a map that requires geographic knowledge, hidden Māori electorates, or an old result presented as comparable with changed boundaries.

The Spinoff explicitly organised 2023 coverage around tight-race electorate profiles; Stuff provided national and electorate results with separate general and Māori directories. [S8, S10] Keep the broader local audience; “swing electorate” is a subset, not a classification justified by old margins alone.

### 4. Poll followers

**Arrival question:** “Has support actually changed, and what does that imply for seats?”

**First thing:** dated observations, trend, inclusion rules and assumptions behind the seat calculation.

**Device and moment:** phone after a poll headline; desktop for inspecting history.

**Five-second exit:** an undated average, concealed exclusions, or calculated seats described as a prediction.

Wikipedia separates polling observations and references; Interest.co.nz interpreted polling averages through coalition arithmetic. [S12, S13] Existing calculators already address scenarios, so another calculator alone is weak differentiation. [S14]

### 5. Overseas New Zealanders

**Arrival question:** “How do I cast my vote from here before the deadline?”

**First thing:** official overseas instructions, opening date and deadline explicitly in New Zealand time.

**Device and moment:** phone abroad, then a computer when handling voting papers.

**Five-second exit:** domestic-only instructions or a date without a time zone.

The Commission maintains a dedicated overseas process and FAQ. Overseas voting opens **21 October**, earlier than domestic advance voting. [S5] Keep this as a distinct entry point within voting help, not a separate polling dashboard.

### 6. Election-night watchers

**Arrival question:** “What is the current result, and how complete is it?”

**First thing:** party seats, majority requirement, count status and update time together.

**Device and moment:** phone beside television coverage on the couch.

**Five-second exit:** replay mistaken for live results, stale numbers without explanation, or commentary preceding the count.

Stuff's 2023 results dashboard combined party totals, Parliament composition and electorate navigation. The Spinoff paired results tracking with reporting and later analysis. [S8, S10] That supports a compact numerical companion; the phone-and-television setting remains a hypothesis.

### 7. Readers returning after election night

**Arrival question:** “Is this settled, and what could still change?”

**First thing:** preliminary versus official status, next official milestone and changes since election night.

**Device and moment:** phone the next morning or during the following week's commute.

**Five-second exit:** a frozen “live” badge, no explanation of specials, or a claim that seat arithmetic confirms a government.

The Commission's 2023 official release reported changed party-seat totals and four changed electorate outcomes, and now carries an amendment notice. [S15] This warrants an explicit post-election state, including the week before official results exist.

### 8. Journalists, researchers and data-checkers

**Arrival question:** “Can I reproduce and cite this number?”

**First thing:** downloadable rows, definitions, observation dates, version, method and licence.

**Device and moment:** desktop in a newsroom or research workflow, throughout all three periods.

**Five-second exit:** chart-only data, mutable downloads without versions, or ambiguous reuse rights.

The Commission publishes statistical CSVs and identifies media and researchers among elections.nz's audiences. [S2, S16] The Herald's reproducible model supports demand for inspectable methods, though demand for this project's particular exports remains unmeasured. [S9]

## Evidence

Publication architecture shows what publishers serve, not how often readers use it. No interviews, site analytics or usability sessions were available.

| Source | What it showed | URL | Date read |
|---|---|---|---|
| S1. Commission voter survey, pp. 34-37 | Information-seeking differences and channels; stronger evidence than invented personas. | [Survey][S1] | 2026-10-17 |
| S2. Commission election report, p. 35 | Election-day pageviews: 1,182,373 for vote.nz and 152,112 for elections.nz. These are site totals, not unique readers or page rankings. Most-visited individual pages: **not found**; also checked the annual report. | [Election report][S2]; [annual report][S18] | 2026-10-17 |
| S3. Google Year in Search | “How to vote” leads the 2023 NZ trending how-to list; “How to register to vote” also appears. Annual trending searches are not absolute volumes or monthly rankings. | [Google's report][S3] | 2026-10-17 |
| Google Trends, NZ | Attempted October-November comparisons for election results, where to vote and how to vote in 2023 and 2020. Both unavailable through the research tool. Monthly series, peaks and related-query rankings: **not found**. | [2023 query][T23]; [2020 query][T20] | 2026-10-17 |
| S4. Commission voting guidance | Practical instructions and assistance destinations; does not answer party-policy preferences. | [What to do][S4]; [accessible formats][S19] | 2026-10-17 |
| S5. Commission overseas guidance | Separate process, dates and FAQ; supports a distinct gateway. | [Overseas voting][S5]; [FAQ][S20] | 2026-10-17 |
| S6. 1News, 2023 | Coverage combined polls, debates and Vote Compass; issue comparison served a different task from horse-race coverage. Survey participants were self-selecting. | [Vote Compass reporting][S6]; [2023 hub][S21] | 2026-10-17 |
| S7. Policy.nz | Current tool organises policies, candidates and parties, including alignment and favourites. Complements seat calculations; does not replace a count dashboard. | [2026 guide][S7] | 2026-10-17 |
| S8. The Spinoff, 2023 | Policy explainers and local profiles before voting; results and party-event reporting on the night; analysis the next morning. No reusable export identified on this coverage page. | [Coverage plan][S8] | 2026-10-17 |
| S9. NZ Herald polling model | Published method and GPL3 source code; challenges the brief's blanket claim that competing methods are closed. Not a simple voter-help interface. | [Model documentation][S9] | 2026-10-17 |
| NZ Herald results map | Served national and electorate results. Reusable exports on the inspected page: **not found**. | [Map entry][S22] | 2026-10-17 |
| S10. Stuff results dashboard | National seats and votes, counting status and electorate directories. Downloadable underlying rows: **not found** in retrieved content. | [2023 dashboard][S10] | 2026-10-17 |
| S11. RNZ, 2023 | Indexed coverage includes outcome reporting and policy/poll analysis. Direct access was restricted; historical dashboard interactions and exports: **not found**. | [Outcome report][S11]; [analysis][S23] | 2026-10-17 |
| S12. Wikipedia polling page | Chronological tables, pollsters and citations; useful reference, not practical voting help. | [2023 polling][S12] | 2026-10-17 |
| S13. Interest.co.nz, 2023 | Interpreted final polls and its average through possible parliamentary combinations. Reusable export on the article: **not found**. | [Final-polls analysis][S13] | 2026-10-17 |
| S14. NZ Polls calculator | Existing poll-average starting point and coalition arithmetic; shows scenario tools are already available. | [Calculator][S14] | 2026-10-17 |
| S15-16. Official results and statistics | Changes after election night and downloadable statistics. Existing official downloads mean “open data” alone is also insufficient differentiation. | [Release][S15]; [statistics][S16] | 2026-10-17 |

Repository review covered the requested intent, specification, draft-2 design and all templates. “Data have” below means the repository's existing data/rendering capability, not independently verified freshness. The builder currently renders night and campaign placeholders. The live homepage could not be retrieved; no live visual audit is claimed.

## Page plan

All routes are relative to `/unattended/nz-election/`. These are proposed changes, not implemented work.

| Audience | Page or tailoring | Data have | Data need and source | Five-second test | Build-by |
|---|---|---|---|---|---|
| Voting-help seekers | New `/vote/`; direct navigation entry. Deadline and official actions first; accessible-format and language links beside them. | Candidate and electorate destinations. | Reviewed dates and official links from [S4, S17, S19]. EC copyright; no open licence asserted. Original short summaries, not copied guidance. Review daily through voting. | Reader identifies enrolment deadline and official voting-place destination. | **Before 26 October**, preferably 20 October |
| Policy comparers | `/vote/#compare`: “Compare policies” external link; distinguish it from “Explore seat combinations”. | Party names and existing explorer. | Current Policy.nz and 1News links [S6, S7]. No policy ingestion or reuse licence needed for this link-only scope; verify destinations weekly. | Reader finds policy comparison without interpreting a poll. | **Before 26 October** |
| Local-contest readers | Existing directory: search and roll choice before map. Existing detail: candidates before outline; boundary warning beside historical comparison. Shareable Māori-directory entry. | Registry, candidates, boundaries, historical results and local polls where available. | No new family. Continue reviewed candidate captures and hourly poll checks under existing contracts. EC copyright, boundaries CC BY 4.0, Wikipedia-derived fields CC BY-SA 4.0. | Reader names candidates and recognises whether the historical comparison is valid. | **Before 26 October** |
| Poll followers | Existing home: direct “Latest polls” and “Explore combinations” anchors; dense table remains below the first answer. | Poll rows, average, assumptions, allocator and provenance. | No new source; existing hourly pipeline. Wikipedia-derived data retain CC BY-SA 4.0 and revision links. | Reader identifies fieldwork date and distinguishes observation from calculation. | **Before 26 October** |
| Overseas voters | `/vote/#overseas`, directly shareable; NZ-time deadlines and official paper-handling link first. | General navigation and local candidates. | Overseas instructions [S5, S20]; EC copyright, link and independently summarise. Review daily; do not process voting papers. | Reader finds the official action and knows which time zone governs it. | **Before 26 October**, specifically before **21 October** |
| Night watchers | Existing `/night/`: compact results summary before detailed waterfall; one electorate selectable by ordinary link. | Allocator and electorate registry; night feed remains planned. | Validated EC XML and reference IDs, using the [media kit][S24] and existing source contract. EC copyright; no open licence found. Browser checks no faster than 30 seconds, only after CORS verification. | Reader states result, completeness and freshness; identifies replay immediately. | **Before 7 November** |
| Post-election checkers | Same `/night/`, changing to “Results so far”; next milestone and change-since-night table. Keep saved night snapshot. | Planned night snapshot structure and allocator. | Official milestones [S17], later validated official results. EC copyright; daily packaged status checks, event-driven result replacement. Exact 2026 final-feed availability remains unconfirmed. | Reader knows whether results are official and when to return. | **Before 7 November** for transition; **after** for populated changes |
| Data users | Existing `/downloads/`: dataset-first ordering, schema/version links and copyable citation; expose immutable snapshot links beside charts. | JSON/CSV catalogue, manifest and provenance. | No new family. Preserve each family's licence and update cadence; live exports explicitly identify browser acquisition. | Reader can locate the exact dataset version behind a number. | **Before 26 October**; night exports **before 7 November** |

Keep static HTML and scheduled Actions publishing. Live browser fetching follows the existing specification; if unavailable, show a dated packaged snapshot and official-results link, not an implied real-time service.

Implementation acceptance: fixture-backed command checks for routes, links, dates, licence/provenance retention and phase transitions; existing `uv run --with pytest pytest -q` and `bin/lint`; inspected screenshots at **390×844** and **1280×800**, including keyboard focus, unavailable data and post-election states. Five-second judgements from screenshots are provisional until tested with readers. No implementation tests were run for this read-only research.

## Not building

- **A separate youth dashboard.** The survey supports additional help, not a different political-information hierarchy. Avoid equating youth with inexperience. [S1]
- **A home-grown policy matcher.** Established tools already serve this; the repository prohibits Policy.nz derivatives. Linking is useful without a new editorial operation. [S7]
- **A “swing seats” forecast from old margins.** Existing boundary qualifications prevent treating historical contests as current predictions. Retain local context without invented certainty.
- **A parallel voting-place database or eligibility engine.** Link to official operational guidance; the site lacks a verified maintenance contract for these services. [S4, S5]
- **A government-formation predictor.** Numerical majorities cannot establish negotiated agreements. Show scenarios and official-result status.
- **A newsroom, live blog or demographic microsites.** Existing publishers supply reporting; this site's strongest proposed contribution is traceable, compact numerical answers. Access needs belong throughout the interface, with official assistance links. [S8, S19]
- **More donations, markets or pollster rankings as the first answer.** This research found weaker audience evidence for prioritising them over voting help, local candidates and result status.

## Open questions for Byron

1. Primary success measure: **usefulness** or **reach**?
2. Can someone review voting-help links daily: **yes** or **no**?
3. Can someone own result updates after 4 November: **yes** or **no**?

[S1]: https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf
[S2]: https://elections.nz/assets/2023-General-Election/Report-on-the-2023-General-Election.pdf
[S3]: https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/
[S4]: https://vote.nz/2026-general-election/voting-in-the-election/what-to-do
[S5]: https://vote.nz/2026-general-election/overseas/vote-from-overseas
[S6]: https://www.1news.co.nz/2023/09/15/vote-compass-reveals-top-issues-on-the-minds-of-kiwis/
[S7]: https://policy.nz/2026
[S8]: https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night
[S9]: https://nzherald.github.io/nzh-poll-of-polls/
[S10]: https://interactives.stuff.co.nz/2023/election-2023-results-live/
[S11]: https://www.rnz.co.nz/news/election-2023/500185/election-2023-labour-s-chris-hipkins-concedes-congratulates-national-on-results
[S12]: https://en.wikipedia.org/wiki/Opinion_polling_for_the_2023_New_Zealand_general_election
[S13]: https://www.interest.co.nz/public-policy/124713/new-zealand-first-would-be-parliament%E2%80%99s-fourth-largest-party-according-one-new
[S14]: https://nzpolls.com/coalition-calculator/
[S15]: https://elections.nz/media-and-news/2023/official-results-for-the-2023-general-election
[S16]: https://www.electionresults.govt.nz/electionresults_2023/statistics/index.html
[S17]: https://vote.nz/2026-general-election/about/overview/key-dates
[S18]: https://elections.nz/assets/pagecomponent-file-files/Electoral-Commission-annual-report-2023-24.pdf
[S19]: https://vote.nz/2026-general-election/resources/information-in-accessible-formats
[S20]: https://vote.nz/2026-general-election/overseas/common-questions
[S21]: https://www.1news.co.nz/tags/vote2023/
[S22]: https://www.nzherald.co.nz/bay-of-plenty-times/news/track-nz-election-2023-live-results-with-the-nz-heralds-interactive-map/5VEXGNXHLZGOHMK2AQIOKZ7TOM/
[S23]: https://www.rnz.co.nz/podcast/focusonpolitics/2023/polls-and-fiscal-holes-put-major-parties-on-notice/
[S24]: https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf
[T23]: https://trends.google.com/trends/explore?date=2023-10-01%202023-11-30&geo=NZ&q=election%20results,where%20to%20vote,how%20to%20vote
[T20]: https://trends.google.com/trends/explore?date=2020-10-01%202020-11-30&geo=NZ&q=election%20results,where%20to%20vote,how%20to%20vote