# M1 refresh, publication and recovery

## Hand-refreshed fact snapshots

`snapshots/*.json` are committed research snapshots, not scheduled feeds. Load one
offline with `pipeline.snapshots.load('leaders')` (or another filename stem).
The envelope records its schema and UTC retrieval time; every record carries its
own source URL, retrieval time and licence statement. Omitted fields are not claims
of zero or false. Consumers must omit absent fields and empty modules.

To refresh one, fetch its `source_url` again by hand (for a pinned Wikipedia revision,
follow the article to its latest revision and record the new revision URL), check the dated source table
or statement, update only the supported records and UTC retrieval times, then review
the diff against the source. Wikipedia candidates exclude withdrawn/retiring sections.
Join EC list ranks only after reviewing party and electorate identity and an exact,
unique candidate-name match within that party's committed EC list; never use fuzzy
matching or carry over an old Wikipedia rank. Parties outside `party-map.json` keep
their source `party` label and omit `party_id`; they are not the `others` aggregate.
Unknown MP status is omitted. Enrolment uses the electorate's own roll, not the
general table's combined total including Māori-roll voters living in that area.
Historical shares are decimal strings at the source's published precision; general
election seats exclude later by-elections. `hexmap` uses square tiles with x east,
y south and a separate Māori column; its original arrangement is informed by the
committed Stats NZ geometry, not copied from a published cartogram.

Photos must come from Commons or an official source with explicit CC0, CC BY,
CC BY-SA, public-domain or NZ Crown reuse terms. Preserve the file-page URL,
author, licence name and URL, and describe the crop/conversion. Retain share-alike
terms on derivatives. Crop to a 320-pixel square, inspect the result, and keep each
file below 40,000 bytes and all portraits below 2,000,000 bytes. Candidate portraits
are limited to verified sitting electorate MPs. A public webpage alone does not
license its photos. EC copyright is recorded as stated, not relabelled open data;
news quotations are short attributed excerpts, not an assertion of an open licence.

Run `uv run --with pytest pytest -q product/nz_election`, stage only the reviewed
snapshot/code/image/runbook files, then run `bin/lint` and review the staged diff.
Commit locally. This refresh procedure does not change publication workflows.

Run `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`.
This verifies immutable captures and labels every output run `offline-verification`. It never fetches.
The current capture contains missing Others observations: incomplete windows withhold seats.
The latest coherent fixture window ends 18 July 2026. Do not impute missing Others for a nicer picture.

Build with `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`.
For first deployment pass a nonexistent data directory. The first data run is expected by
19 October 2026. The hourly workflow bootstraps the data branch on its first publication.
Pages builds the product after metrics and before the blog. Product output never targets the blog root.

Run `uv run product/nz_election/pipeline/verify.py all`, then the root pytest suite and `bin/lint`.
The optional `--data` and `--site` verifier arguments validate supplied exports and route presence.
For browser checks run `uv run --with playwright python product/nz_election/tests/screenshots.py
--site site --out artifacts/nz-election/screenshots`. Missing Chromium fails `CHROMIUM_REQUIRED`.
Do not install a browser locally. Inspect the baseline images and separately labelled state images.

## Failure and recovery

A parsed source drift or expected validation error retains all last-good poll-family bytes.
Status becomes stale, or unavailable when there has never been a good bundle. Status acquisition
is null because it records an operational event. A new build also marks acquisition older than
three hours overdue; an already open page cannot update its age without JavaScript.
Unknown errors abort without swapping. A failed build leaves the previous product directory intact.

Writes stage on the destination filesystem and exchange directories atomically (macOS or Linux).
Local refreshes serialize with an adjacent flock file. Read a stable copy of an acquired snapshot;
Git publication pins the data commit before building. Do not read a changing refresh directory in
another process. A symlink or unallowlisted file is rejected as data, never executed.

`publish.publish` uses the same algorithm for local bare repositories in tests and the GitHub
remote in Actions. Only the publication job has contents write permission. It validates the
downloaded bundle before touching git, stages explicit allowlisted paths, merges other dataset
status entries and regenerates the manifest. The typed result record is the validated status
JSON inside the bundle; `validated=true` gates artifact upload and the publication job.
Unexpected failures never emit that output. Handled failures exit nonzero but upload their
validated bundle, and publication reports failure only after pushing the status.

Capture replacement and mapping review are supervisor tasks. Keep raw capture bytes unchanged;
review source revisions, removals and incompatible party vectors before approving new mappings.
Poll IDs remain independent of mutable shares and revision IDs. Corrections retain prior row history.

## Failed refreshes and missing data

Inspect the refresh and publication Action summaries: state, error code, attempted revision
(null if acquisition failed), last-good acquisition/run, committed SHA, attempts and outcome.
Diagnostics are fixed codes, never upstream HTML or credentials. HTTP 429 and selected 5xx,
transport errors and API maxlag retry serially up to three attempts. Other HTTP failures stop
immediately. Retry-After seconds or HTTP dates are honoured up to 60 seconds; larger waits
fail with RETRY_AFTER_EXCESSIVE. Each request uses a 20-second timeout and reads at most
2 MiB plus one overflow sentinel byte. Redirects are rejected, including same-host redirects.
Only fetch.py opens HTTP connections; it never follows article citations.

A missing data ref is normal before first publication. The hourly job starts with no previous
bundle; publication creates an orphan containing only product/nz_election/data/. A failed first
fetch still publishes status, CSV, manifest and licences with unavailable state. Pages resolves
the data ref read-only and pins the exact commit in a separate checkout. Empty resolution means
six no-data routes; a failed resolution stops the build. No code from that checkout runs.
If an existing branch lacks a valid bundle, validation stops instead of treating it as absent.
Runner loss, permission errors and failed deployment cannot update public status. Inspect Actions
and the page's build/acquisition times; the previous Pages deployment remains live on build failure.

## Publication retries

The publication job shares non-cancelling group nz-election-data-publication with future writers.
It rereads the tip before each attempt and uses --force-with-lease against that tip, committing
on its fetched parent. This preserves the existing code's lease rule rather than the plan's
plain-push wording. Bootstrap uses a lease expecting absence, so simultaneous bootstraps retry.
Only a changed remote ref permits another attempt, up to three. Unchanged output skips a commit;
older acquisitions cannot replace newer successful data. A newer failure still updates attempt
status. Retry the hourly workflow after investigating PUBLICATION_FAILED or exhausted retries;
never push product data locally. No separate daily writer or ownership registry ships in M1.

## Rollback

Dispatch Publish the blog on main with optional code_sha and data_sha inputs. Use reviewed trusted
commits, each exactly 40 lowercase hex characters. Blank code uses the triggering main commit;
blank data resolves the current data tip. Validation runs before either input is used as a ref.
No ref or branch is rewritten. Pages records git rev-parse HEAD from both actual checkouts in
build-manifest.json and its CSV, together with the run URL and whether polls are available.
The workflow stamps both build-manifest siblings after building, so rollback to the increment 2
skeleton also records actual checkouts even though that builder predates the SHA environment
contract. Inspect those records, the downloads page and screenshots after deployment.

## Pages minutes measurement

All deployment triggers share group pages with cancel-in-progress false. An active deployment
finishes; pending builds can coalesce. workflow_run accepts completed hourly runs on main from
the same repository regardless of conclusion, since failure status also needs deployment.
A GITHUB_TOKEN data push alone is not expected to trigger Pages.
For several days after merge, record hourly and Pages run URLs, run counts and job durations,
including coalesced runs, in the supervisor's daily post. Sum actual durations and extrapolate
using the observed cadence. The public repository's standard hosted runners are not billed;
720 to 2,160 monthly Pages minutes is a duration estimate, not cost. Do not reduce cadence without
a recorded supervisor decision. The supervisor performs the first live dispatch and deployment
check; this increment's tests and local verification are fully offline.

## Export conventions

Every dataset has an envelope, per-row source references, observations, JSON and CSV.
Nested CSV fields use canonical JSON in `*_json` columns; scalar null is empty, booleans are
`true` or `false`, integers are decimal strings. Poll percentages equal shares divided by scale;
the original total is the sum of every share divided by scale, with missing shares still unknown.
No published total is renormalized. Manifest counts are payload records, including one for seats.
Both manifest files have null size/hash because self-reference is excluded. Other files are hashed.
Build records and normalized official validation data are separate from the immutable poll inventory.
Use `--data-sha <40-character commit>` for immutable source-download links; no commit is invented
for fixture runs. EC source-family restrictions remain separate from CC BY-SA poll adaptations.

Output ownership is an allowlist inside any directory named `site`: only its immediate
`nz-election` child may be replaced. The site root, blog siblings and nested destinations
are rejected before reading data or staging output. Resolved paths enforce the same rule
through parent symlinks. Standalone verification outputs outside a site tree remain allowed.
Publication uses a lease on the fetched data SHA and compares the remote ref after rejection;
only a moved ref is retried. Latest attempt status merges separately from last-good data.
The leased push commits directly on the fetched parent; it cannot rewrite newer history.

Successful poll bundles are ordered lexicographically by `polls.fetched_at`, then
`averages.generated_at`. Acquisition time remains primary: a newer generation cannot
reintroduce an older acquisition. For unchanged captures, a later successful generation
advances the daily series. Exact ties retain the repository's bytes and last-good run.
The generation time comes from the retained derived envelope, never the latest attempt or
page build time. Attempt status merges independently, so a later failure still reports its
error while preserving the newest successful bundle and its last-good reference.
Download summaries render retrieval times in Pacific/Auckland with NZST/NZDT; the labelled
raw-record disclosure and downloadable manifests preserve stored UTC timestamps.

Operational instants must be exactly `YYYY-MM-DDTHH:MM:SSZ`, with valid calendar
values. Validators and producers reject naive, offset and fractional timestamps with
`INVALID_TIMESTAMP`; no implicit conversion occurs at the data-branch boundary.
Publication compares these canonical strings for both success and attempt order.
Missing acquisition and last-success values remain null where the schema permits them.
Poll observation, fieldwork and averaging-window dates remain date-only.

## X proof of concept

`NZ election social daily` runs at 13:40 UTC, 02:40 NZDT. In Actions, choose
**Run workflow**, branch `main`, optionally a closed NZ `day` (`YYYY-MM-DD`).
Blank means the previous NZ day. A run lasts about two hours. The supervisor
runs the first live collection after merge; fixtures are offline verification.

Secrets: `X_UPSTREAM_KEY` and `TYPESAFE_API_KEY`, stored as repository Actions
secrets and in SSM under `/unattended/prd`. Only the collection step receives
them. They never enter files, command arguments or diagnostics. The adapters
use twitterapi.io advanced search and TypeSafe System One directly. The HTTP
contract is documented at https://docs.typesafe.ai/api; only the two upstream
files named in the brief were inspected.

The cap is 7,800 X credits per **collection NZ day**, across manual reruns and
historical sample dates. `data/social/credits.json` and its CSV sibling contain
one run record: `day`, `reserved`, `spent`, `cap`, `requests`, `allocation`,
`closed`, plus envelope row metadata. Each request reserves 315 (20 times 15,
plus the 15 minimum); successful calls spend max(15, 15 times returned posts).
Failed/unknown calls conservatively spend 315. Duplicates still cost credits.
Reservations are never refunded. The workflow preallocates the remaining whole
315-credit units and publishes that ledger under the existing data lease before
any request. The collection job then claims that reservation with `publish.py
--claim` before receiving permission to collect. The lease atomically marks it
closed and charges the full reserved allowance as conservative spend. A retried
job must claim again and is rejected before any paid request. Result publication
can add request counts but never refund that conservative spend. Distinct runs
are additive ledger records; conflicting completed reports are rejected rather
than merged with max. Each call consumes one unit. Cancellation therefore cannot erase
spending authority or enable a fresh allowance on rerun. An abandoned reservation
may block the rest of that day's collection; wait for the next NZ day. Never
hand-edit the ledger. The entire workflow is serialised, and reservation and
result publication also share the existing publication concurrency group.

One page per hourly window, no pagination; at most three attempts per window,
within the reserved total. Requests are separated by 330 seconds, including
retries: fewer than 240 possible returned posts in any rolling hour. A retry
can exhaust the budget before all windows complete. Collection checks its NZ
budget date before and after pacing; crossing midnight stops before another
request. Cap/failure retains the
last-good daily aggregates and publishes status; no prior success is unavailable.
An already-spent budget day exits 0 with status only: no requests, new sample or ledger changes.
A cap reached during collection remains fatal with `SOCIAL_CREDIT_CAP`.
A sample older than 36 hours after its last NZ day closed is hidden on the page.
The existing hourly Pages rebuild consumes the updated data branch; this workflow
does not directly deploy Pages.

`social.py --check-freeze` omits its `allowed` output from midnight on 7 November
2026 until 19:00 NZDT. Reservation, collection and publication check this guard,
including delayed jobs; the collector also checks before each request and after
classification. `publish.py --family social` checks again immediately before a
push. No paid call is made when a run starts during the freeze. An existing page
remains unchanged because election builds and Pages deployment both fail closed
from 23:30 NZDT on 6 November to 19:00 NZDT on 7 November. The extra half-hour
allows a margin before the statutory freeze for the ten-minute deploy timeout.
The deploy guard runs immediately before the Pages action, independent of the
artifact's build time or rollback code. `deployment_guard.py --now <UTC instant>`
and `build.py --now <UTC instant>` support deterministic freeze checks. No build
is produced during the freeze, so post-midnight observations cannot be served
by another rebuild or a delayed deployment during that window.

`data/social/daily.json` contains only daily aggregate counts, ordered attitude
counts (null below 30 evaluable posts), summed probabilities as exact decimal
strings (fixed-point, never exponent notation), model versions, sample concentration in parts per million, question
version, query, epoch windows and retrieval times. IDs, text and author identities
exist only in process memory. Only English is classified in this pilot; replies
and quotes are not separately analysed, official accounts are not separated, and
no author weighting is applied. These limitations are printed on the page. The
leader-to-party criteria are dated 17 October 2026, from the research memo. Relevance
and evaluability each require probability at least 0.8. Preserve ambiguous subjects;
never distribute one post's attitude among all parties it mentions.

Run offline with `social.py --fixtures --out <bundle> --day 2026-10-16` after
`refresh.py --fixtures`. Use `--now` for deterministic time and freeze tests.
The model registry currently accepts `jev-1.13.0`, plus the repo-owned synthetic
versions `jev-fixture-1` and `jev-test-1`. Unknown returned models fail closed with
a sanitized error; adding a version requires review. No upstream model string
outside this closed registry can be stored or rendered.

Capture the populated social page, not only its unavailable state, using a fresh
fixture output directory (move aside previous fixture output before repeating):

```sh
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data
uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16
uv run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election
uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots
```

No live response is a permissible fixture. The research memo's data-rights and
release review remain necessary before live publication; this proof of concept
does not establish permission to redistribute X content or validated NZ accuracy.

## Feed home verification (H-a)

The feed is `/`; poll history and the explorer are `/polls/`. Existing poll IDs,
source IDs and coalition hashes resolve on `/polls/`. Navigation includes both routes.
The static countdown uses the build timestamp in Pacific/Auckland. It cannot update
while publication is frozen under s197; the publication guards remain in force.

For a fresh worktree-local demonstration directory, run:

```sh
uv run product/nz_election/tests/prepare_home.py
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election --now 2026-10-17T01:00:00Z
uv run product/nz_election/pipeline/verify.py home --data artifacts/nz-election/data --site site
uv run product/nz_election/tests/screenshots.py
```

The preparation uses the captured coherent window ending 18 July and synthetic social
examples dated 16 October. This is offline verification, not current polling or live
social data. It does not impute Others. Use a fresh data directory for each preparation;
repeat social collection deliberately encounters the credit-cap contract.

The host screenshot contract is `PASS screenshots: 79 routes, 296 images`: 158 baseline,
9 narrow, 33 design states, 13 populated map/detail, 4 home extras, 79 route OG cards.
Inspect Home at 390 by 844 and 1280 by 800, Polls, Night, one electorate, and home-row
keyboard focus. The fold limit remains 780 px and every visible target remains at least
44 px. The jump list follows the seat strip, using supervisor decision 4 to limit hero
height. Source actions are disclosed under the shared seat note; no source is removed.
H-b renders candidates before the historical summary and boundary information. Changed
boundaries explicitly say that the 2023 holder is not comparable; no incumbency is inferred.
Night uses the shared build-time countdown and honest results availability. The static
countdown cannot update during the s197 publication freeze.

The build writes `og-manifest.json` with one unique route key, title, description, HTML
path and PNG path for each of the 79 registered routes. Root is `home`; nested paths use
`--`, for example `social--poc`. The build does not run a browser. Absolute `og:image`
and `twitter:image` URLs point to the PNGs generated by the host or Pages workflow.

Run the complete H-b checks after the preparation and build above:

```sh
uv run product/nz_election/pipeline/verify.py home-routes --data artifacts/nz-election/data --site site
uv run product/nz_election/pipeline/verify.py all --data artifacts/nz-election/data --site site
uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots
uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/og --og-only
uv run product/nz_election/tests/coalitions_browser.py --site site
```

Expected browser lines: `PASS screenshots: 79 routes, 296 images`,
`PASS screenshots: 0 routes, 79 images`, `PASS coalition browser`. The total is
158 + 9 + 33 + 13 + 4 + 79 = 296 manifest records; artifact copies are not counted.
The OG-only run writes all 79 PNGs under `site/nz-election/og/` and records image hashes
in its screenshot manifest. Inspect Night and an electorate at 390 by 844 and 1280 by
800, plus home, polls and electorate OG cards at their native 1200 by 630 size.
Keep measured fold geometry from harness output for the supervisor; never relax the
780 px source-note check or 44 px target check.

Pages installs Playwright with Chromium only after verification, renders `--og-only`,
and fails if any registered page references a missing PNG or wrong dimensions before
upload. Existing build and deployment freeze guards retain their order and strength.
Deployment completion still requires a successful Pages run; local checks cannot prove it.
