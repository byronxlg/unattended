**Verdict: request changes.**

- **Important: weakened count-retention coverage**, `product/nz_election/tests/home_handover_dom.mjs:85`. The replacement accepts either 120 seats or zero in every populated scenario. It also searches raw HTML, while status assertions inspect a detached mock object. The browser checks retain only the house total; party counts and reporting percentage could disappear unnoticed. Compare scenario-specific visible counts before/after cutoff and against source data, allowing status text to change.

- **Important: unrelated state rollback**, `state/next-run-after:1`, `state/ledger.jsonl:486`, `docs/journal.md:3744` (deleted base lines). The specified diff changes scheduling state, removes completed-job records and deletes both job prompts. These changes exceed the home-status fix and should be excluded.

The implementation shares `result_states.live_status` between home and night, seeds client freshness from rendered `retrieved_at`, and preserves populated content at cutoff. Post-cutoff ticks delegate to `NightLive`; tests assert no further requests, but its unchanged internals are outside the permitted diff.

Read-only static review of the diff and `REVIEW.md` only. No tests or screenshot review performed.