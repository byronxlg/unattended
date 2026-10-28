Two remaining gaps, ranked. Read-only; no files changed. Traced all five requested clocks; ran Python and Node in-memory probes, not a full build.

1. **Home results lack stale/ended status. Size: small.**  
   At 7 Nov 10:00Z, failed refreshes leave “Live preliminary results” without a stale warning. At 8 Nov 06:01Z, a populated home retains that label. Fresh builds with an unsettled capture also retain it through 14/27 Nov. Evidence: [home-live.mjs:7](/Users/byron/repos/unattended/product/nz_election/web/home-live.mjs:7) supplies no status callback; [line 25](/Users/byron/repos/unattended/product/nz_election/web/home-live.mjs:25) preserves populated results at cutoff; [home.py:205](/Users/byron/repos/unattended/product/nz_election/pipeline/home.py:205) uses the clock-independent fallback in [result_states.py:38](/Users/byron/repos/unattended/product/nz_election/pipeline/result_states.py:38).  
   **Smallest change:** retain counts but render shared freshness/ended status in both static home and client; initialize freshness from the rendered capture. Extend populated DOM tests, which currently explicitly expect unchanged HTML after cutoff ([test:65](/Users/byron/repos/unattended/product/nz_election/tests/home_handover_dom.mjs:65)).  
   **Proving command after adding those assertions:** `uv run --with pytest pytest -q product/nz_election/tests/test_home_handover.py product/nz_election/tests/test_sunsets.py`  
   **Fresh Node probe output:** `10:00Z failed feed: Live preliminary results.` / `after stop: Live preliminary results.`

2. **Workflow-history acceptance ignores collection sunsets. Size: small.**  
   Its text-derived active windows recognize freeze/night guards, but ignore `sunsets.py hourly/daily/social`: [check_workflow_history.py:258](/Users/byron/repos/unattended/product/nz_election/tools/check_workflow_history.py:258). Consequently, week-after acceptance demands hourly executions after collection has ended; green no-op runs satisfy it, while disabling expired schedules causes false failures.  
   **Smallest change:** apply shared sunset deadlines to history windows. Add executable interval/history cases for each cutoff, including no runs after sunset and missing runs before it. This is separate from the in-flight Actions boundary drill.  
   **Proving command after adding those cases:** `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py`  
   **Fresh Python probe output:** hourly remained required for the entire `2026-11-14T06:00Z` to `2026-11-27T06:00Z` interval.

No new operator decision required for either fix.