# M1 offline build and publication helpers

Run `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`.
This verifies immutable captures and labels every output run `offline-verification`. It never fetches.
The current capture contains missing Others observations: incomplete windows withhold seats.
The latest coherent fixture window ends 18 July 2026. Do not impute missing Others for a nicer picture.

Build with `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`.
For first deployment pass a nonexistent data directory. The first data run is expected by
19 October 2026; the hourly workflow and data-branch bootstrap belong to increment 3.
The Pages step runs after the blog. Product output never targets the blog root.

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

`publish.publish` accepts only a local bare git repository with an existing data ref. It is an
offline test transport, not a command for publishing production data. It stages only allowlisted
files, merges other dataset status entries, regenerates the manifest and retries non-fast-forward
pushes at most three times. A newer acquisition or attempt prevents an older writer replacing it.
The next increment must add the Actions transport, ownership registry for new source families,
orphan bootstrap and workflow reporting. No network helper or HTTP retry policy ships here.

Capture replacement and mapping review are supervisor tasks. Keep raw capture bytes unchanged;
review source revisions, removals and incompatible party vectors before approving new mappings.
Poll IDs remain independent of mutable shares and revision IDs. Corrections retain prior row history.

For rollback in increment 3, rebuild trusted pinned code and data SHAs through Pages. Never force
push the data branch. Record the build run, both SHAs and screenshot manifest. Measure actual
Pages durations after deployment; the public-repository minute estimates are duration, not cost.

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
