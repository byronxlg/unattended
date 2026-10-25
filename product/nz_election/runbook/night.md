# Night data

Build offline with `uv run product/nz_election/pipeline/daily_refresh.py --out /tmp/night-data`.
Check with `uv run product/nz_election/tests/night_smoke.py /tmp/night-data` and
`uv run product/nz_election/pipeline/verify.py night`. The archive/replay page uses these packaged snapshots. The live Actions path is documented below.

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

The page provides paused replay controls and no-JS national tables. The browser XML parser
implements the archive contract. Live operation uses the validated Actions acquisition and
same-origin packaged JSON described below. Browser CORS evidence and deployed rehearsals are
recorded separately; local fixture proofs make no live availability claim.

Verification with `verify.py night --data <directory>` checks that supplied bundle and fails with
`MISSING_NIGHT_FAMILY` if its night index is absent. Without `--data`, verification builds fixtures.
Snapshot modes are constrained by capture references and derivation: demo captures stay Recorded demo,
archive captures stay Final snapshot, and derived 2023 steps retain the illustrative label.
A zero valid-party-vote total requires zero party percentages and seats (`XML_TOTAL` otherwise).
Empty and whitespace-only count elements use `XML_COUNT`, as do other malformed count tokens.

The aggregate `all` gate retains its optional-family contract: an absent night family is omitted
from its checks and produces no PASS night line. The explicit `night` gate requires the family.

Final snapshots are compared with the parsed committed archive XML, including party votes, seats,
statistics, source timestamp and reference version. Claimed input hashes must match the verified
XML and its three reference captures. This independent check raises `NIGHT_CAPTURE_MISMATCH` for
synthetic or altered final rows, even if replay metadata was removed and package hashes regenerated.
Keep those immutable captures available when validating retained packages.
Summed electorate seats cannot exceed that archive's electorate registry (`XML_TOTAL`); with
nonnegative seat counts, this also bounds every individual party's electorate seats.
The CLI prints `FAIL night: MISSING_NIGHT_FAMILY` and exits nonzero without a traceback when an
explicit night check receives an empty directory. Other validation errors use the same FAIL format.


## Packaged page rehearsal

Build with `uv run product/nz_election/pipeline/build.py --data <data> --out <site>/nz-election`.
Open `/unattended/nz-election/night/?sequence=illustrative-2023` (the documented
`2023-illustrative` alias also works). Select 60x and Play: the middle step is at five seconds,
the endpoint at ten. Pause preserves elapsed time; Reset returns to the start, paused, retaining
button focus and the selected speed. The mode label stays visible in every frame. The endpoint
has 2,851,211 valid party votes and House 122. These are source-reported seats, not an allocation.

`?sequence=mediademo` selects the recorded demo. `?sequence=2017`, `2020`, and `2023` select
single final snapshots, without playback controls. Without a query or JavaScript, the page
renders the 2023 final snapshot table. Unknown queries keep that labelled static default.
Every frame is packaged into inert HTML templates at build time. Playback makes no requests;
source downloads are explicit links. Static HTML keeps the usable final table if scripts fail.

Run `uv run product/nz_election/tests/night_browser.py` for browser XML parity, replay controls,
request assertions and the exact 60-image night registry. The full screenshot harness adds the
same 30 states at 390x844 and 1280x800. It requires a host that permits Chromium to launch.

The replay includes provisional electorate leaders and margins from the captured 2023 candidate
results, with a leader-coloured map and searchable table. Intermediate illustrative snapshots contain no
seats or voting-place coverage. Synthetic steps have no observed update time, including the
endpoint. Do not manufacture these fields from scaled votes, map historical electorates onto
2026 boundaries, or describe this rehearsal as a live election. The 2026 final-results date is
separate from the explicitly historical/demo snapshots. An absent family renders the countdown,
voting link and official results link before polls close; after polls close it keeps the official
results link. Phase uses the build timestamp (CLI `--now`), with the boundary at
2026-11-07T06:00:00Z, 19:00 NZDT. Even with archives packaged, countdown and voting actions
precede the results until that boundary.

Each illustrative frame states its ordinal and elapsed time. Intermediate frames explain that
coverage and seats are published only in the final archive. The endpoint shows that archive's
source update date/time from its derivation basis, explicitly labelled as the final archive's
clock, not an observed replay time. The elapsed counter has no live announcements; a separate
polite region announces play, pause, speed, reset and completion.

CI installs Playwright Chromium before tests. The browser harness uses a local Mac headless
binary when present, otherwise Playwright's default browser resolver; a missing installation
still fails the tests. Screenshot states use the deterministic build time 2026-11-05T00:00:00Z
and check countdown/vote bounds at 390x844 before recording the existing named images.

## Packaged electorate leaders and seat calculation (increment 4)

The 2026 media captures are read offline after manifest hash validation. Detail paths are
`eNN/eNN.xml` for electorate IDs 1 through 71, with two-digit padding. No browser request is
made: these captures have no CORS permission. Live transport is now the Actions path below. The package
includes the six captured details; other electorate rows say not yet reported. A zero-place,
zero-vote detail is never a leader or final count, including when its XML says `final="true"`.

The illustrative replay derives 2023 leaders and margins from captured per-electorate candidate
CSV totals, using party and electorate IDs to join candidate references. Intermediate margins
are scaled final margins, not historical observations. Port Waikato's deferred contest remains
unreported in this replay. Historic names and boundaries remain intact; links identify today's
related electorate pages without transferring historic votes. Grey hexagons have no reported
leader. Reported ties show margin 0 and every tied candidate by name. The map is non-interactive;
Table links are the accessible selection route, at least 24 px wide and 44 px high. The searchable
table supplies names, provisional leaders, vote margins and reporting status without requiring a
map or JavaScript.

Source-reported seats remain distinct from the application calculation. The final 2023
calculation uses the golden candidate/list inputs: proportional entitlement 120, overhang 2,
vacancies 0, occupied House 122. Incomplete inputs and unresolved allocation ties suppress the
waterfall. Unchecked list capacity suppresses vacancies and occupied House. No compatible dated
preliminary/official captures are supplied, so production has no change comparison or specials
component. Labelled synthetic pairs exercise that optional view in the proof harness.

Run `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py waterfall` and the full
night browser harness before release. The latter registers 30 states at both 390x844 and
1280x800, including map, table, selected leader, seat calculation and comparison cases.

## Live operation through Actions (increment 5)

The transport amendment supersedes the earlier browser-feed instructions. Production acquires
`https://media.election.net.nz/xml/` in Actions, never in a browser. That origin has no CORS
header. The browser reads only same-origin `night-live.json`, generated from the validated night
family using the existing page renderer. Archives and explicit replay queries do not poll.

Predeploy this code by 5 November. Two annual cron entries request starts at **7 November
06:02 and 06:07 UTC**. Independently, `bin/tick` checks from 06:10 UTC and dispatches
once if no night-live run has been created since 06:00 UTC and none is pending.
A failed run counts as an attempt; the watchdog does not retry it. GitHub cron may drift.
The whole watchdog subprocess (including uv startup, eligibility and dispatch) has a 60-second
wall-clock limit. On timeout its process group is killed, a line is logged and tick continues.
A nonblocking OS lock at `state/night-start.lock` serializes check and dispatch across ticks.
The worker inherits the locked file description, so killing the wrapper alone cannot admit
another attempt while its worker remains alive. Timeout cleanup kills the worker group before
the wrapper closes its lock; the lock releases when its last holder exits.
Do not delete the lock file while ticks run.
After a successful dispatch, `state/night-start-2026.dispatched` suppresses further watchdog
attempts for the entire remaining 2026 live window, covering run-list visibility lag. The marker
is intentionally retained; manual recovery uses the explicit dispatch command below.
Failed or timed-out dispatches do not write a success marker; a later tick rechecks GitHub.
The shared window guard is checked again immediately before invoking the dispatch command.
For manual recovery during the live window:

```sh
gh workflow run nz-election-night-live.yml --ref main
gh run list --workflow nz-election-night-live.yml
```

The injected-clock guard rejects production before 7 November 06:00 UTC, including manual dispatch.
Scheduled runs are never rehearsals and exit successfully without work outside the 2026
live window: 7 November 06:00 UTC inclusive to 8 November 06:00 UTC exclusive.
The shared injected-clock guard also bounds the watchdog and production loop.
The single non-cancelling workflow job loops for about five hours, then queues
its successor before exiting; the job timeout is 350 minutes. A complete cycle fetches
`electorates.xml`, `parties.xml`, `candidates.xml` serially, validates the references, fetches
`election.xml` and all `e01/e01.xml` through `e71/e71.xml`, then rechecks all three references.
The committed 2026 electorate registry anchors the 64 general and seven Maori seats. A changed
reference set or any failed file discards that pending cycle. A later cycle starts from a fresh
reference set. Counts remain source counts; 0 of 0 places with `final="true"` is never final
and never supplies a leader.

Each cycle is bounded to about 20 minutes plus the final bounded request; the next cycle starts
no sooner than five minutes after the previous start. HTTP requests have 20-second timeouts,
three attempts and bounded Retry-After handling. Publication uses the existing leased data-ref
publisher, owning only night. A single Git commit contains references, national results, all
71 details, JSON/CSV siblings and manifest. Other families survive lease retries. Daily captured
night data cannot replace a newer Actions source vector. Every successful production cycle publishes
its new retrieval time, even when raw XML and result counts are unchanged. The loop still reports
`changed` or `unchanged` for the result bytes; that distinction no longer suppresses freshness.
Failed acquisition keeps the previous retrieval time. Rehearsal still saves only changed demo bundles.

Each new freshness commit dispatches `pages.yml`, using its existing non-cancelling concurrency group.
This deliberately uses a full site build/deployment for unchanged counts too: the existing static
Pages service has no independent same-origin JSON write endpoint. Reusing the complete validated
artifact workflow preserves atomic exports and provenance without adding hosting or credentials.
At a steady five-minute cadence, budget 12 Pages runs per hour; slow builds reduce that cadence. Budget
approximately `60 + 12 * P` Actions runner-minutes per wall-clock hour, where `P` is the combined
build and deploy job time per Pages run. For example, a measured `P=3` would cost about 96 runner-minutes
per hour (60 for the looping acquisition job plus 36 for Pages). This is a planning example, not a
measured run time. Record actual job durations during the real Actions rehearsal.
The [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
exempt custom Actions builds from the soft ten-builds-per-hour limit.

Before acquisition, including the first cycle of each successor, the runner reads the data-branch
SHA through the GitHub API and compares it with `data.data_sha` in the HTTPS-served
`/unattended/nz-election/build-manifest.json` (cache-busted, bounded read). A mismatch or unavailable
manifest triggers a pinned deployment of the published data, even if counts never change again or
the upstream feed is now unavailable. No data ref means there is nothing to recover yet. A recovery
uses that cycle's slot, so it cannot double the deployment rate, and never fabricates a retrieval time.
A successful matching Pages run confirms that SHA within the runner; a fresh runner consults the
served manifest again. Failed/timed-out deployment is never confirmed and retries on the next cycle.
The data ref and served manifest are durable evidence; no in-memory pending flag is needed after a crash.
The runner waits for its specific Pages run, bounded to ten minutes. Repeated failure needs operator
investigation in the Pages run log. Check the deployed build manifest for actual code and data SHAs,
then open `/unattended/nz-election/night/` without a replay query.
The page polls at most once per 60 seconds, stops requests while hidden, rejects obsolete responses,
and backs off on failed requests. Staleness is 15 minutes from the **complete cycle retrieval**,
not the XML's local source clock. Each detail retains its own source timestamp. Failed acquisition
keeps the last complete family; failed browser fetch keeps the displayed snapshot and official link.
Exports say **Packaged by the site**, with upstream URLs, source clocks, Actions retrieval, run URL
and code SHA. The stored raw XML lets validation reparse every result before accepting a package.

### Rehearse before polling day

After this commit is merged, use the same workflow with its rehearsal input:

```sh
gh workflow run nz-election-night-live.yml --ref main -f rehearsal=true
gh run list --workflow nz-election-night-live.yml
gh run download RUN_ID -n night-rehearsal -D artifacts/night-rehearsal
```

Rehearsal uses mediademo (its own 72-electorate registry, including e72/e72.xml) for about ten minutes, writes only the `night-rehearsal` artifact,
and neither publishes nor chains a successor. Inspect the artifact's complete bundles with
`verify.py night --data <bundle>` and compare source timestamps across cycles. It is explicitly
Recorded demo, never live results. Record run URL, code SHA, artifact hashes and observed change
in the supervisor report. A pre-merge local test is not this real Actions rehearsal.

Offline proofs inject clocks and transport. They use the manifest-checked 2026 zero-state files
and the two recorded demo national observations. Only six 2026 details were captured; remaining
details in the test transport are **synthetic unreported zeros** built from each reference set.
They are not added to the capture manifest or represented as official captures. Browser proof
images use labelled 2023 final counts to exercise populated seat answers, separately from zero-state
parser proofs. Run `tests/night_live_browser.py` with `PYTHONPATH=.` for the 16 added screenshots,
or the full screenshot harness for the exact expanded state registry.

### Stop, diagnose and roll back

1. Disable the night workflow (`gh workflow disable nz-election-night-live.yml`) to block cron,
   watchdog and successor starts, then cancel the current run and any queued runs. Cancellation is an explicit operator action; concurrency
   never cancels runs automatically.
2. Check `night/index.json`, its source timestamps and the last Pages deployment. A failed cycle
   leaves the last complete snapshot intact. Check upstream HTTP failures, reference changes,
   parser errors and Actions logs. Never patch a single detail into the data branch.
3. For a pinned rollback, dispatch Pages with the trusted 40-character `code_sha` and `data_sha`.
   The current workflow's guard runs before a rollback checkout and again in the deploy job.
   All collection/publication/deployment paths use the same 6 November 23:30 through 7 November
   19:00 NZDT freeze, including queued jobs. No rollback bypass exists.
4. To resume, enable the workflow and dispatch it again within the live window. Do not enable a
   second feed or browser XML transport. Keep the reviewed preliminary root; there is no guessed
   official-feed switch. For 27 November, capture and validate compatible official results through
   the established daily capture workflow, keeping the preliminary baseline and its date. Stop
   the preliminary live loop before publishing that transition. Only evidence-supported official
   changes and specials components may appear.

A failed renderer/browser launch is an acceptance gap, not permission to skip screenshots.
The supervisor must inspect fresh, selected, hidden/resumed, stale, fallback, changed-reference,
pre-close and post-close images at 390x844 and 1280x800 before release.


## Deployed acceptance

Run the three separate modes for the 30 October and 6 November acceptance records:

```sh
uv run --with playwright python product/nz_election/tests/night_deployed.py --probe
uv run --with playwright python product/nz_election/tests/night_deployed.py --rehearse --speed 60
uv run --with playwright python product/nz_election/tests/night_deployed.py --faults
```

The default product root is `https://byronxlg.com/unattended/nz-election/`.
`--origin https://another-host.example` preserves that prefix; `--base-url` overrides the
complete product root, for example `http://127.0.0.1:8000/unattended/nz-election/` served by
`python -m http.server 8000 --directory <served>`. Build into `<served>/unattended/nz-election`
for this ordinary static server (do not name the server directory `site`, a reserved build path).
No credentials are required.

Each invocation writes `artifacts/nz-election/deployed/<mode>-<UTC stamp>/record.json` even
on failure. Keep artifacts untracked. The last stdout line is `PASS deployed-<mode>` or
`FAIL deployed-<mode>: <check>`; failure exits nonzero. INCONCLUSIVE checks also prevent PASS and exit nonzero. Read `checks` for reasons,
`requests`, `failed_requests` and `night_data_responses` for transport evidence, `phases`
for actual wall seconds, and `screenshots` for paths relative to the record directory.
`code_sha` and `data_sha` require an HTTP 200 build manifest with both SHAs containing exactly
40 hexadecimal characters. Missing, malformed or unavailable provenance fails acceptance. Browser/version, origin and UTC bounds identify
what was tested. Inspect the start/middle/end phone and desktop screenshots before acceptance.

Probe never intercepts requests or changes time/security. It records the dated fallback and
all observed same-origin night JSON responses, using the existing envelope/row validators or
the deployed NightLive package validator. Before polls close, zero page data requests is expected
and accepted only with a visible countdown and vote link and no unexpected page errors.
`probe_phase` records before/after close using the deployed module's OPEN schedule and the
host's Python UTC clock, without executing the module. The page's `Date.now()` value is recorded
as informational `page_now_ms` only and cannot decide the phase. From close, a completed, successful, validated
night JSON response requested after opening is required; zero or pending responses fail.
Unexpected page errors fail every mode and are listed in `unexpected_page_errors`; expected
CORS diagnostics and injected fault HTTP errors remain separately recorded. The four ordinary in-page
CORS fetches validate readable HTTP 200 XML through the existing reference and election parsers.
A blocked fetch passes only with a URL-specific browser CORS diagnostic and an independent
host read returning a non-empty, valid upstream body. Host reads use the existing bounded feed
fetcher and never substitute bytes into the browser. DNS, TLS, timeout, unreachable or empty
upstream responses are INCONCLUSIVE with reasons; missing CORS diagnostics also remain
INCONCLUSIVE. Invalid readable responses fail acceptance.
A local base URL still probes the real official URLs; only the offline pytest fixture substitutes
local feed URLs. Replay uses real elapsed time, pauses at the middle frame for screenshots,
resumes to the golden endpoint, resets, and selects all three final archives. Its console errors
and official-feed requests must be empty.

Faults alone installs a simulated post-close clock and intercepts packaged JSON. Its initial
package is explicitly labelled offline fixture data, validated through the existing night
pipeline and retained beneath the record directory in `fault-fixture/`. It then tests HTTP failure and an unchanged package aging past 15 minutes, retaining
the exact last-good HTML and showing Stale. This is client resilience evidence, never evidence
of a real published live cycle or an Actions acquisition rehearsal.
