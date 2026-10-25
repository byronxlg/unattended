Verdict: **accept**

- Critical: none.
- Important: none.
- Nit: none.

`night_page.py:139` embeds the shared `night_live.CLOSE`; `night-live.mjs:70` supplies it before the first tick.

Read-only Node probes confirmed zero requests at/after cutoff for first visits, offline, HTTP failures, malformed responses, tab resume and pending requests. All seven scenarios reproduced late requests on `95387fe`. Before-cutoff backoff passed.

The five new tests target the old implementation’s failures. No existing check was weakened. No pytest run; no files changed.