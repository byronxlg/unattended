1. **Scheduled shutdown still looks like failure on secondary surfaces. Size: small.**

   **Evidence:** [build.py:280](/Users/byron/repos/unattended/product/nz_election/pipeline/build.py:280) emits “Update overdue” on `/polls/` after hourly collection intentionally ends. [market_panel.py:60](/Users/byron/repos/unattended/product/nz_election/pipeline/market_panel.py:60) similarly emits “Update overdue or failed” after daily collection ends. These remain outside the completed home-banner fix.

   **Smallest change:** use the shared collection deadlines to show “Scheduled updates ended” with the retained observation date. Preserve genuine failure information separately. Add executable renderer assertions for the five requested clocks, including a healthy final collection and a genuinely failed one.

   **Exact proving command after adding assertions:**
   ```sh
   uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_polls_plan.py product/nz_election/tests/test_markets.py
   ```

Read-only in-memory renderer probes confirmed:
```text
7 Nov 06:00Z: polls_overdue=True
7 Nov 10:00Z: polls_overdue=True
8 Nov 06:01Z: polls_overdue=True
14 Nov 00:00Z: polls_overdue=True
27 Nov 00:00Z: polls_overdue=True
27 Nov: market_ended_as_failure=True
```
No files changed. No full build or browser run. No operator decision needed.