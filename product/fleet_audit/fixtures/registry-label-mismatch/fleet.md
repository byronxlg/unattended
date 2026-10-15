---
schema_version: 1
project: example
owner: Fixture owner
reviewed: '2026-10-16'
jobs:
- id: tick
  label: different.label
  plist_path: /fleet-fixtures/com.unattended.tick.plist
  expected_program: /bin/bash
  expected_arguments:
  - /bin/bash
  - /Users/byron/repos/unattended/bin/tick
---
Synthetic declaration.
