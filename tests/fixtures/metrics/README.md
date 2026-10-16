# Metrics evidence
Real records copied verbatim from 0a4b5600849b150ce97fedf5b5947751b08e2334:
ledger lines 1-2 (smoke-0, smoke-1), ticks lines 1-2, mistakes line 1,
and the complete changes.yaml. Expected: two jobs, two ticks, one mistake
class with one repeat, Fleet Audit attempts 11 and five linked PRs.
Synthetic files contain explicitly constructed evidence; test builders add
edge cases. GitHub shapes are synthetic, not authenticated captures.
No future regression, incident-ID or signal contracts are assumed.

Synthetic sample: two overlapping two-hour jobs give peak 2 and mean 4/3;
120 total tokens, latest weekly window 5%; one malformed line and one
non-object line are skipped. Supervisor mean cost is USD 1, turns 2.
The eval passes 50% with 2-hour incident latency. The sample change has
two rework cycles, 6-hour wall time and 1-hour deploy lead time.
GitHub and history JSON supply frozen responses for the full output pipeline.
All other edge cases are explicitly constructed in the named indicator tests.
