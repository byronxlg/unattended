Verdict: **request changes**.

Critical: None.

Important:

- `product/nz_election/tools/check_workflow_history.py:129` - Cadence combines hours from all schedules without their date restrictions. With July hourly cron `17 * * 7 *` and November daily cron `0 0 * 11 *`, a healthy November day fails: `success gap 11 hours exceeds 3 hours`. Conversely, `0 0-10 * * *` passes with only its final run, hiding ten missing hourly runs. Derive cadence and active intervals from schedules applicable to the evaluated dates.

- `product/nz_election/tools/check_workflow_history.py:114` - Guard detection matches arbitrary source text. Adding only `# See product/nz_election/pipeline/night_live.py` to a daily workflow makes missing runs pass outside the night window, indefinitely after CLOSE. Probe returned `PASS workflow history` with zero history queries. Recognize actual guarded execution rather than comments or incidental path mentions.

Nit: None.

Verification: read-only `python3 -B -c` probes with injected workflow text/history; no pytest or subprocess checks executed. Used Python directly because uv required a prohibited cache write.

Confirmed: missing annual runs retain `cron did not fire; no runs`; tested ranges, lists, steps, weekdays and UTC/NZ boundaries behaved as expected. Existing main tests remain an unchanged prefix; additions only.

Release acceptance remains explicitly opt-in: omitting `--require` permits optional SKIPs and `PASS harden`; supplying `--require night,waterfall` forwards it unchanged and rejects those SKIPs. No separate date-triggered release mode exists.