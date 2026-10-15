---
schema_version: 1
project: unattended
owner: Byron
tier: standard
lifecycle: active
reviewed: "2026-10-16"
jobs:
  - id: tick
    scheduler: launchd
    host: local
    domain: gui/501
    label: com.unattended.tick
    plist_path: /Users/byron/Library/LaunchAgents/com.unattended.tick.plist
    expected_program: /bin/bash
    expected_arguments: [/bin/bash, /Users/byron/repos/unattended/bin/tick]
    expected_working_directory: /Users/byron/repos/unattended
    expected_schedule:
      interval_seconds: 600
    expected_enabled: true
    output:
      path: /Users/byron/repos/unattended/state/ticks.jsonl
      kind: ticks_jsonl
      max_age_seconds: 1200
    grace_seconds: 1800
---

# Fleet declaration

The lab's one launchd job, declared for `fleet-audit` (`product/fleet_audit`). The frontmatter
is the declaration; this prose is not read by the tool.

`com.unattended.tick` runs `bin/tick` every 600 seconds from the repository root. Each run
appends one receipt line to `state/ticks.jsonl`, whether or not the supervisor ran, so the
receipt is the freshness evidence: a receipt older than 1200 seconds is uncertain, older than
3000 seconds (max age plus grace) is late. RunAtLoad is set in the plist and is observed, not
declared, because the lab makes no promise about it. The declaration is reviewed on the date
in `reviewed`; change the date when any expectation changes.
