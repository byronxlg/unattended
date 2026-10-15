# Landscape sweep: fleet operations for small live projects from one machine, 2026-10-16 (Codex research job research-fleet-ops-d1)

Method: read the selection criteria and prior sweep, then searched live web sources, preferring project repositories, official documentation, and changelogs.
Snapshot: all stars and prices below were observed on 2026-10-16; stars are “from page,” sometimes rounded, and indexed pages may lag.
Limitations: `gh api` failed with “error connecting to api.github.com”; exact last-push dates were not found. Dated releases are labelled separately; gaps are research inferences, not proof of absence.

## A. Dead-man switches and scheduled-job monitors

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Healthchecks](https://github.com/healthchecks/healthchecks) | 10.4k, from page; push not found. [Changelog](https://raw.githubusercontent.com/healthchecks/healthchecks/master/CHANGELOG.md): v4.4 dated 2026-08-31, followed by unreleased changes. | Receives job pings; checks intervals or cron schedules with grace periods; dashboard and notifications. | BSD-3-Clause; self-hosting has no licence fee. [Instructions](https://healthchecks.io/docs/self_hosted/) document Python/Django, SQLite for development, and a separate alert process. [Hosted pricing](https://healthchecks.io/pricing/): 20 jobs free, 100 for $20/month. | Strong existing answer to missed jobs. Runbook ownership, local scheduler discovery, and output validity still require integration. Hosting it on the monitored Mac shares the Mac’s failure domain. |
| [Cronitor](https://cronitor.io/docs/cron-job-monitoring) | Service stars and backend push: not found. | Scheduled-job and heartbeat monitoring, start/completion/failure telemetry, duration thresholds. [Custom metrics](https://cronitor.io/docs/custom-metrics) support rolling-window aggregates and percentile assertions. | Commercial hosted service; open SDKs. [Pricing](https://cronitor.io/pricing/): five monitors free; Business $2/monitor/month plus $5/user/month. | Much of the proposed telemetry already exists commercially. A local product would need to win on installation, ownership of evidence, or runbook integration. |
| [Dead Man’s Snitch](https://deadmanssnitch.com/plans) | Service stars and backend push: not found. | Scheduled check-ins, missed-check notifications, API and Field Agent; higher plans add integrations and smart alerts. | Commercial. Page lists one free snitch; three for $5/month; 100 for $19/month. On-premise hosting requires contacting the vendor. | Simple heartbeat monitoring is occupied. No public, free local fleet registry was established from the reviewed material. |
| [cronlint](https://github.com/zbcdo/cronlint) | 1, from page; push and dated activity not found. | Zero-dependency cron expression parser/linter. [Site](https://cronlint.org/) lists impossible dates, DST ambiguity, uneven steps, JSON diagnostics, and crontab stdin support. | MIT; small JS CLI, free. | Finds schedule mistakes before execution, but does not observe execution, understand launchd declarations, or verify fresh output. |

Launchd-aware discovery is covered under D. A heartbeat endpoint alone is not a distinct product opportunity here.

## B. Runbook-as-code and fleet registries

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Backstage](https://github.com/backstage/backstage) | 34.6k, from page; push and latest dated activity not found. | Developer portal and software catalogue. Its [descriptor format](https://github.com/backstage/backstage/blob/master/docs/features/software-catalog/descriptor-format.md) models ownership, lifecycle, relationships, links, and status. | Apache-2.0; software free, deployment and maintenance required. | Ownership and lifecycle catalogues are established. Byron’s markdown frontmatter, review-age policy, and Mac observations would need adapters and rules; a portal is a larger operating commitment than a directory reader. |
| [Locus](https://github.com/Nano-Nimbus/locus) | 0, from page; push not found. Changelog places lint/index work under “Unreleased.” | Markdown knowledge system with `locus lint` and deterministic `locus index`; checks Open Knowledge Format frontmatter and index drift, with CI exit codes. | MIT; Python/uv installation documented. Lint/index do not import its agent SDK. | Direct counterexample to “nobody checks markdown registries.” Its documented rules target knowledge structure, not project/tier/owner/review-age policy joined to runtime health. Small observed adoption does not establish reliability. |

The remaining distinction appears to be the connection between documents and observations. Required-field validation or generating an index alone would be easy to substitute with an existing linter and a short script.

## C. Local-first status and health rollup

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Gatus](https://github.com/TwiN/gatus) | 12.3k, from page; push not found. Release page shows v5.37.0 on 24 September; year not exposed in the retrieved date. | [README](https://raw.githubusercontent.com/TwiN/gatus/master/README.md) documents YAML-configured endpoint conditions, status pages, notifications, pushed external checks, and missing-heartbeat alerts. Supports binary installation. | Apache-2.0; self-hosted software free; managed service optional. | Very close substitute for a fleet dashboard. Local file/process/git checks can feed external endpoints; the remaining work is collectors, runbook mapping, and evidence semantics. |
| [Monit](https://mmonit.com/monit/) | GitHub stars and push: not found; upstream uses Bitbucket. [Release notes](https://mmonit.com/monit/changes/) date 6.0.0 to 2026-06-15. | [Manual](https://mmonit.com/monit/documentation/monit.html) covers processes, file timestamps/content, network protocols, arbitrary program checks, alerts, and an HTTP interface. | AGPL; free local daemon. M/Monit is a separate management product. | Already covers most local probes. GitHub recency and runbook policies need scripts, but that is also a strong argument against building another probe engine. |
| [Uptime Kuma](https://github.com/louislam/uptime-kuma) | 92.5k, from page; push not found. Release page shows a release on 9 October; year not exposed in the retrieved date. | HTTP/TCP/DNS/push monitoring, multiple status pages, Telegram/Slack and other notifications. README lists 20-second intervals. | MIT; free Node application. Non-Docker installation exists, although the reviewed platform list does not explicitly promise macOS support. | Substantial existing dashboard and alerting functionality. No documented runbook-to-launchd reconciliation in the reviewed README; Mac installation deserves verification before adoption. |
| [Upptime](https://github.com/upptime/upptime) | 17.2k, from page; push and latest dated activity not found. | GitHub Actions probes endpoints, records history in git, uses Issues for incidents and Pages for status. | MIT code; history data has a separate Open Database Licence. Advertised as free, subject to GitHub availability and account limits. | Useful external observer with no local daemon, but depends on GitHub and cannot inspect local files/processes without an additional channel. Does not meet a strict local-only requirement. |

A page combining endpoints, file age, process liveness, and notifications is substantially occupied. A possible distinction is showing *why* each project is considered healthy, including the age and limitations of its evidence.

## D. Declared versus observed drift

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [LaunchInspector](https://github.com/vincentbattez/launchs-and-crons-inspector) | 0, from page; push not found. Release page shows v0.3.2 on 18 June; year not exposed in the retrieved date. | Scans cron and user/global launchd files; separates enabled, loaded, running, exit code, and run count. Includes headless `--dump-json`. | MIT; free Swift app. README requires macOS 14+ and documents an unsigned download. | Native scheduler discovery is already implemented. Its documented scope does not reconcile a versioned project registry, GitHub deployment identity, or expected output freshness. |
| [Drift](https://github.com/sunkencity999/drift) | 0, from page; push and dated activity not found. | Python CLI/MCP tool snapshots ports, services, packages, users, and cron into SQLite; compares snapshots. macOS collectors use `launchctl list`, crontab, and LaunchAgents. | MIT; local, user-level operation; no cloud required. | Directly occupies “what changed on this Mac?” Its comparison is observed state against earlier observed state, rather than desired state against current state. Scheduled reports are listed as future work. |
| [Terraform plan](https://github.com/hashicorp/terraform) | 49.9k, from page; push and latest dated activity not found. | [Plan documentation](https://developer.hashicorp.com/terraform/cli/commands/plan) describes reading remote objects and comparing configuration and prior state; refresh-only planning isolates external changes. | Source available; local CLI rather than a mandatory monitoring subscription. Backend/provider costs are separate. | IaC drift is already addressed for resources represented by providers and state. It does not establish that a launchd job produced current output or that a deployed application serves the expected revision. |

A useful distinction would require explicit identity mappings: project → scheduler label → expected executable/configuration → workflow/environment → observed output or deployed revision. Import existing IaC findings rather than attempting a new general-purpose IaC engine.

## E. Operational telemetry across GitHub repositories

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [GitHub Actions metrics](https://docs.github.com/en/actions/concepts/metrics) | Service stars and backend push: not found. | Native repository/organisation views for usage, run times, queue times, and failures. | Hosted GitHub feature; access depends on roles and account capabilities. No separate local installation. | Durations and failure-rate dashboards are occupied. The reviewed page does not describe a local cross-account ledger combining runbook tiers, dependency backlog, deployed revision, and explicit missing-data states. |
| [Labbs/github-actions-exporter](https://github.com/Labbs/github-actions-exporter) | 255, from page; push and latest fully dated activity not found. | Configurable repository/organisation polling; exports workflow status/duration and runner metrics for Prometheus. | MIT; Go software free, metrics storage/dashboard stack additional. | Existing collector to reuse or compete against. Small-fleet use still needs persistence, interpretation, and notification rules. README notes a maintenance-related organisation migration, so current maintenance should be checked before adoption. |
| [gh-dash](https://github.com/dlvhdr/gh-dash) | 12.6k, from page; push and latest dated activity not found. | Terminal dashboard with configurable GitHub views and custom actions. Useful adjacent solution for repository and PR triage. | MIT; free local Go application using GitHub. | A configured PR view can cover much dependency-update triage. The reviewed material does not establish persistent duration baselines, deployment reconciliation, or unattended fleet verdicts. |

Use the existing [detector landscape, section D](landscape-2026-10-15.md#d-deterministic-control-bands-on-engineering-telemetry); this sweep does not repeat it. One correction matters: Cronitor now documents duration thresholds and rolling-window metric assertions. The opportunity cannot be described as “job monitors have no duration analysis.”

## Research or practitioner baselines

- **A dozen heartbeat checks already fit a free service.** Healthchecks lists 20 free jobs. Under Cronitor’s published Business rates, 12 monitors and one user calculate to $29/month. These bound the financial value of replacing basic heartbeat monitoring; “free” alone is a weak distinction. [Healthchecks pricing](https://healthchecks.io/pricing/), [Cronitor pricing](https://cronitor.io/pricing/).
- **A local monitor cannot independently report its host’s death.** This is an architectural inference: loss of the Mac or its network also removes its ability to send a warning. Upptime supplies an external observation point, but introduces GitHub dependence. A fully local product should expose its last observation time and avoid promising host-outage notification. [Upptime architecture](https://github.com/upptime/upptime).
- **Sleep changes schedule semantics.** Apple’s archived guide says `StartCalendarInterval` jobs missed during sleep run on waking, whereas cron jobs do not catch up; powered-off jobs wait for the next scheduled occurrence. A detector needs scheduler-specific rules, timezone awareness, and tested wake behaviour. [Apple scheduling guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html).
- **A scheduler inventory is not execution history.** LaunchInspector documents that launchd run counts are since load and are not last-run timestamps; cron lacks that counter. Completion receipts or application output evidence are necessary to answer “when did useful work last finish?” [LaunchInspector](https://github.com/vincentbattez/launchs-and-crons-inspector).
- **GitHub schedules have reliability limits.** Documentation gives a five-minute minimum interval, warns of delayed or dropped scheduled runs, and says public-repository schedules disable after 60 days without activity. These are important explanations for stale projects, not merely generic failure alerts. [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows), [disabled workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).
- **Small-fleet API collection is plausible without a server stack.** GitHub documents 60 unauthenticated requests/hour and a normal authenticated-user limit of 5,000/hour. Assuming four single-page requests per repository every 15 minutes, 12 repositories require 192 requests/hour before job details, pagination, retries, or backfill. This is a sizing estimate, not a measured collector. [Rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
- **Evidence types must remain separate.** Repository metadata exposes `pushed_at`; workflow jobs expose start/completion times; deployment statuses record reported outcomes. None alone proves the current application revision or fresh business output. Prefer a version endpoint or artifact receipt for that stronger claim. [Repositories API](https://docs.github.com/en/rest/repos/repos), [jobs API](https://docs.github.com/en/rest/actions/workflow-jobs), [deployment statuses](https://docs.github.com/en/rest/deployments/statuses).
- **Dependency staleness needs a definition.** Old Dependabot PRs and unresolved Dependabot security alerts are different populations. The alerts API requires specific read permission; an inaccessible endpoint must become “unknown,” not zero outstanding alerts. [Dependabot API](https://docs.github.com/en/rest/dependabot/alerts).

## Unoccupied niches

These are plausible gaps within the reviewed sources, not established market vacancies.

1. **Runbook-driven evidence coverage:** show which active projects lack a trustworthy freshness check, and which verdicts rely on old observations.
   Backstage models ownership; Locus checks documents; Monit/Gatus check runtime evidence. The reviewed sources do not document their combination over Byron’s existing frontmatter.

2. **Desired-state audit for small Mac workloads:** distinguish missing, disabled, unloaded, legitimately idle, and stale-output jobs, attributed to a project.
   LaunchInspector covers observation and Drift covers historical change. Neither reviewed description establishes policy reconciliation against a versioned fleet registry.

3. **A local repository operations ledger with explicit uncertainty:** combine run attempts, deployment evidence, dependency backlog, and per-project operational expectations.
   GitHub metrics, exporters, and gh-dash cover substantial pieces. The narrower gap is persistent interpretation and a reproducible daily verdict without Prometheus or a monitoring service.

## Candidate products

These are alternatives, not one combined build. Commands below are proposed acceptance interfaces, not commands executed during this research. Footprints are design budgets to verify on the Mac, not measured results.

### 1. Fleetbook: runbooks that explain fleet health

Pitch: read existing markdown runbooks and produce one page showing project health, evidence age, missing coverage, and the next useful investigation link.

| Build days | Shippable increment | Verification command and observable result |
| --- | --- | --- |
| 1–2 | Frontmatter reader, configurable field names, required fields, duplicate IDs, review-age and lifecycle rules. | `uv run fleetbook lint examples/runbooks --as-of 2026-10-16` reports fixture violations with file/field locations and stable exit codes. |
| 3–4 | HTTP, file-age, process-identity, and repository-push collectors; timestamped observations with timeouts. | `uv run fleetbook collect --fixture examples/observations.json --json` reproduces expected observations, including permission and timeout failures. |
| 5–6 | Healthy/violated/unknown/retired evaluation; retain evidence source and observation time. | `uv run fleetbook replay examples/stale-output.jsonl --check` catches a live process with stale output and never converts collection failure into health. |
| 7–9 | Static HTML and text digest; bounded SQLite history; optional Gatus-compatible output. | `uv run fleetbook render --fixture examples/fleet.json --check` verifies deterministic output, escaping, links, and visibly expired observations. |
| 10–12 | Transition deduplication, restart recovery, optional Telegram transport, and a read-only pilot over the dozen projects. | `uv run fleetbook acceptance --offline` verifies alert/recovery transitions, repeat suppression, and storage limits; transport is tested against a local fake endpoint. |

**Day 12:** Byron sees one local page listing roughly 12 projects, with owner/tier, runbook review age, latest evidence, and specific reasons for unhealthy or unknown states. The pilot reports actual coverage rather than assuming every project can be monitored.

**Footprint:** Python with uv, stdlib HTTP/SQLite/process support plus a small YAML dependency; target ≤200 MiB installation including interpreter/environment, ≤50 MiB retained state, ≤80 MiB peak RSS. One bounded collection process per interval; static page needs no application server. Free local operation; chat transport optional.

**Users and blog interest:** solo maintainers and small teams with mixed workloads. Posts can follow the discovery that “process alive,” “last run passed,” and “output useful” disagree, then measure coverage and nuisance alerts.

**Strongest argument against:** Monit or Gatus plus a frontmatter converter may deliver nearly all the value. A separate dashboard is difficult to justify unless the evidence model reduces real investigation work.

### 2. Fleet Audit: declared versus observed Mac jobs

Pitch: a read-only audit that explains why a declared project is absent, disabled, running the wrong command, or producing no recent evidence.

| Build days | Shippable increment | Verification command and observable result |
| --- | --- | --- |
| 1–2 | Registry-to-plist mapping and normalised declared inventory using `plistlib`. | `uv run fleet-audit declared examples/fleet --json` handles XML/binary plists, duplicate labels, missing paths, and supported schedule forms. |
| 3–4 | Observed launchd inventory with explicit domains, disable overrides, PIDs, exit codes, and collector errors. | `uv run fleet-audit observe --fixture examples/launchctl --check` separates unloaded, disabled, idle, running, and inaccessible states. |
| 5–6 | Desired-versus-observed comparison for executable, arguments, working directory, and declared lifecycle. | `uv run fleet-audit diff --fixture examples/drift --check` identifies each seeded discrepancy without treating every idle scheduled job as failed. |
| 7–9 | User-crontab comparison and explicit limits for unsupported schedules; optional output receipts/freshness. | `uv run fleet-audit replay examples/sleep-and-restart.jsonl --check` validates policy around wake, restart, missing receipts, and stale outputs. |
| 10–12 | Project-level report, expiring exceptions, fixture capture/redaction, and real-host read-only pilot. | `uv run fleet-audit acceptance --offline` checks report provenance, exception expiry, redaction, and absence of mutating command paths. |

**Day 12:** Byron runs one command and gets a project-attributed discrepancy report, including “cannot determine,” with evidence and investigation commands. GitHub and IaC expansion remains outside this twelve-day scope.

**Footprint:** Python/uv; stdlib plist, subprocess, JSON, and filesystem handling plus YAML if needed. Target ≤200 MiB installed, ≤20 MiB snapshots, ≤60 MiB RSS; on-demand or hourly execution, no resident server or paid API.

**Users and blog interest:** Mac mini operators, automation-heavy developers, and small labs. Posts can demonstrate failures caused by stale paths, disable overrides, differing launch domains, and mistaken interpretations of idle jobs.

**Strongest argument against:** LaunchInspector already exports much of the inventory, while Drift already records changes. macOS output compatibility and schedule semantics may consume the build window; a comparison layer atop an existing exporter could be the better-sized contribution.

### 3. Repo Watch: an operations ledger for a dozen repositories

Pitch: cache GitHub operational evidence locally and issue one reproducible daily report about failing, neglected, or ambiguously deployed projects.

| Build days | Shippable increment | Verification command and observable result |
| --- | --- | --- |
| 1–2 | Explicit repository/workflow/environment registry and read-only permission diagnostics. | `uv run repowatch doctor --fixture examples/access --check` distinguishes inaccessible, archived, empty, and collectable repositories. |
| 3–4 | Incremental workflow/job collection into SQLite, preserving run attempts and timestamps. | `uv run repowatch ingest --fixture examples/runs --check` proves replay idempotence, pagination, and distinct retries. |
| 5–6 | Failure streaks, duration history, Dependabot PR age and security-alert age as separate metrics. | `uv run repowatch report --fixture examples/fleet --as-of 2026-10-16 --check` reproduces expected metrics and missing-permission states. |
| 7–9 | Deployment-status evidence and optional revision endpoint; deterministic duration bands using the prior sweep’s detector work. | `uv run repowatch replay examples/deploy-and-duration.jsonl --check` catches revision mismatch and refuses statistical verdicts below the configured sample minimum. |
| 10–12 | Daily HTML/text digest, optional Telegram delivery, bounded history, and live pilot. | `uv run repowatch acceptance --offline` verifies rate-limit backoff, partial collection, notification deduplication, and retention. |

**Day 12:** Byron sees a daily table of failure streaks, durations, old dependency work, last reported deployment, and independently observed revision where available. Sparse workflows show insufficient history; backfilled data carries its collection boundary.

**Footprint:** Python/uv with SQLite, stdlib HTTP and a small YAML dependency; optional use of the installed `gh` CLI. Target ≤200 MiB installation, ≤100 MiB retained metadata, ≤80 MiB RSS. Poll every 15–60 minutes; do not download job logs or artifacts. No additional paid service required.

**Users and blog interest:** maintainers with several low-traffic repositories. Posts can show why reruns distort streaks, successful deploy workflows disagree with served revisions, and quiet repositories require different expectations from abandoned ones.

**Strongest argument against:** this overlaps native GitHub metrics, exporters, and the lab’s existing engineering-telemetry candidate family. Low run counts may leave too little data for credible control bands, making explicit deadlines and failure streaks more useful than statistical detection.

## Sources

All sources below were consulted on 2026-10-16. Repository pages supply the reported star counts; release/changelog dates are activity evidence, not substitutes for `pushed_at`.

- Local selection criteria: `intent/README.md`; [prior landscape, detector section D](landscape-2026-10-15.md#d-deterministic-control-bands-on-engineering-telemetry).
- Healthchecks: [repository](https://github.com/healthchecks/healthchecks), [changelog](https://raw.githubusercontent.com/healthchecks/healthchecks/master/CHANGELOG.md), [self-hosting](https://healthchecks.io/docs/self_hosted/), [pricing](https://healthchecks.io/pricing/).
- Cronitor: [job monitoring](https://cronitor.io/docs/cron-job-monitoring), [custom metrics](https://cronitor.io/docs/custom-metrics), [pricing](https://cronitor.io/pricing/).
- Dead Man’s Snitch: [plans](https://deadmanssnitch.com/plans).
- cronlint: [repository](https://github.com/zbcdo/cronlint), [CLI and rule overview](https://cronlint.org/).
- Backstage: [repository](https://github.com/backstage/backstage), [catalogue descriptor specification](https://github.com/backstage/backstage/blob/master/docs/features/software-catalog/descriptor-format.md).
- Locus: [repository](https://github.com/Nano-Nimbus/locus), [changelog](https://raw.githubusercontent.com/Nano-Nimbus/locus/main/CHANGELOG.md).
- Gatus: [repository](https://github.com/TwiN/gatus), [README](https://raw.githubusercontent.com/TwiN/gatus/master/README.md), [releases](https://github.com/TwiN/gatus/releases).
- Monit: [project](https://mmonit.com/monit/), [manual](https://mmonit.com/monit/documentation/monit.html), [release notes](https://mmonit.com/monit/changes/).
- Uptime Kuma: [repository](https://github.com/louislam/uptime-kuma), [releases](https://github.com/louislam/uptime-kuma/releases).
- Upptime: [repository](https://github.com/upptime/upptime).
- LaunchInspector: [repository](https://github.com/vincentbattez/launchs-and-crons-inspector), [releases](https://github.com/vincentbattez/launchs-and-crons-inspector/releases).
- Drift: [repository](https://github.com/sunkencity999/drift).
- Terraform: [repository](https://github.com/hashicorp/terraform), [plan command](https://developer.hashicorp.com/terraform/cli/commands/plan).
- GitHub Actions metrics: [official overview](https://docs.github.com/en/actions/concepts/metrics).
- Actions exporter: [Labbs repository](https://github.com/Labbs/github-actions-exporter).
- gh-dash: [repository](https://github.com/dlvhdr/gh-dash).
- Apple: [Scheduling Timed Jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html).
- GitHub scheduling: [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows), [disabling/enabling workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).
- GitHub collection: [rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [repositories](https://docs.github.com/en/rest/repos/repos), [workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs), [deployment statuses](https://docs.github.com/en/rest/deployments/statuses), [Dependabot alerts](https://docs.github.com/en/rest/dependabot/alerts).