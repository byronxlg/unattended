# Eval: a documented date exception survives the next Wikipedia revision

Origin: production incident 2026-10-17T07:00Z. "NZ election hourly" (runs 39011994985 at 07:00Z
and 39029509938 at 11:39Z, and every run between) failed with `FAIL refresh: parse_drift`; the
polls status row went stale with last good 01:20Z (run 38990427608) and the site served that
bundle for the rest of the day. The log and the status row named only `parse_drift`; the reason
and locator took a supervisor reproduction on the host to find: `invalid_dates`, visible
`8–11 Aug 2026` with `data-sort-value="2026-08-12"`, the 1 News–Verian row. That row has a
documented exception in `product/nz_election/config/party-map.json`, but the exception is keyed
to revision 1380524613 (the fixture). Wikipedia moved to 1380694545 at 08:21Z (an unrelated
edit elsewhere on the page) and the exception stopped matching, so a row the lab had already
read and accepted failed the whole refresh.

Invariant: a documented exception describes a row (visible text, pollster, sort value), not a
revision of the page; a row that matches a documented exception parses on every revision that
carries it unchanged. A `parse_drift` outcome names its reason and locator in the Actions log
and in the step summary, so an operator can see the cause without reproducing it on the host.

Check: `evals/polls-date-exception-revision/check.sh` parses the pinned fixture under a revision
id that is not the fixture's and expects the exception row present with fieldwork end
2026-08-11. Expected last line: `PASS exception row parsed on revision 9999999999`.
