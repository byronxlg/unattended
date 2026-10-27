Verdict: **accept**.

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Rehearsal publication uses a local bare repository and explicit `rehearsal-data` ref. No reachable rehearsal path dispatches production Pages. The successor dispatch is pinned and bounded to one generation.

Production workflows, freeze guard and 8 November cutoff are unchanged. No data validation, provenance, absence or accessibility checks were loosened. Added integration tests exercise actual publication and recovery, including preservation of a seeded production ref.

Read-only Python probes, without pytest:
```text
PASS old/new deployment trace: closed
PASS old/new deployment trace: served
PASS old/new deployment trace: failed
PASS old/new deployment trace: success
PASS bounded successor and malformed-generation probes
PASS production workflows, freeze guard and sunset constants unchanged
```

Remote Actions dispatch and artifact transfer remain unverified here. No files changed.