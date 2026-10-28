Two remaining items, ranked. Read-only; executed in-memory renderer probes at all five clocks. No full build or browser run.

1. **Electorate pages miss post-election states. Size: small.**  
   [electorate_pages.py:123](/Users/byron/repos/unattended/product/nz_election/pipeline/electorate_pages.py:123) checks opening time only. Stale, settled and official inputs all render “Who is leading here now?” and “leader provisional”, without freshness/ended/official status. [Line 83](/Users/byron/repos/unattended/product/nz_election/pipeline/electorate_pages.py:83) retains “Who is standing in 2026?” through 27 November. Probes confirmed both.
   
   **Smallest change:** use shared result-state/freshness copy for the local count, label retained results as dated, and switch candidate copy after close. Extend executable electorate tests across all five clocks and preliminary/settled/official inputs.
   
   **Proving command after adding assertions:**  
   `uv run --with pytest pytest -q product/nz_election/tests/test_electorate_page_plan.py product/nz_election/tests/test_sunsets.py`

2. **An empty night page cannot receive the first live capture without reload. Size: small.**  
   [night_page.py:144](/Users/byron/repos/unattended/product/nz_election/pipeline/night_page.py:144) returns before emitting the live target, status element or client script. At every requested clock, rendering an absent night family produced neither `night-snapshot` nor `night-live.mjs`. Readers opening this fallback during initial acquisition failure stay there after publication recovers.
   
   **Smallest change:** emit the live shell/client even without sequences, with explicit waiting/ended copy and the official link. Add a browser case that starts empty, receives unavailable responses, then renders the first complete package without navigation; assert polling stops at cutoff.
   
   **Proving command after adding that case:**  
   `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py`

No operator decision needed for either change.