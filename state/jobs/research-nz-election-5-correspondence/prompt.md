# Research: draft config/electorate-correspondence.json and config/party-colours.json evidence

Read-only. Worktree .worktrees/nz-election-5 (branch change/nz-election-5 at e68f964) holds the
increment 5 captures under product/nz_election/fixtures/ with 12 new manifest entries. You
produce two JSON documents in your report; the supervisor reviews and commits them. Do not
guess: every relationship and every colour carries an evidence locator a reviewer can open.

## Read first
- intent/nz-election/plan-m2.md, section "Before increment 5" and the increment 5 and 6 items
  (what the correspondence config and the colour evidence are for; no population weighting).
- product/nz_election/fixtures/representation-commission/schedule-b.pdf is one page; its text is
  at /Users/byron/unattended-captures/m2/representation-commission/schedule-b.txt and the full
  report text (pdftotext of report-2025.pdf, 75 KB) at
  /Users/byron/unattended-captures/m2/representation-commission/report-2025.txt. If those paths
  are unreadable in your sandbox say so and stop; do not reconstruct from memory.
- product/nz_election/fixtures/stats-nz/{general,maori}-2025.geojson: the 2025 names and stable
  IDs (GED2025_V1_00, MED2025_V1_00) are in feature properties. 64 general, 7 Maori.
- product/nz_election/fixtures/ec-2023/: the 2023 election files list the 2020-boundary
  electorates (65 general, 7 Maori) with the EC's electorate numbers.

## Document 1: electorate correspondence (2020 boundaries to 2025 boundaries)
One entry per 2025 electorate and one per abolished 2020 electorate. Fields: new_id (2025 code
or null), new_name, old_ids (2023 EC electorate numbers), old_names, relationship (one of
unchanged, boundary_changed, renamed, created, abolished; renamed means same seat with a new
name per the report, created means a new seat formed mainly from named predecessors), note
(one sentence from the report: what moved, in the report's words), evidence (schedule B line
for unchanged/changed; report section heading and page for everything else), reviewer
"supervisor (Claude), unattended lab" and review_date "2026-10-17" left for the supervisor to
confirm. Totals must reconcile: 71 new seats, 72 old seats, every old seat appears at least
once. Flag any entry where the report is ambiguous rather than resolving it yourself.

## Document 2: party colour evidence
For each of nat, lab, grn, act, nzf, tpm, opp read product/nz_election/fixtures/party-identity/
<code>.html and list candidate brand colours with locators: meta theme-color, CSS custom
properties, inline styles, class names that carry a hex value, in that order of preference.
For each party give the colour you would recommend as the primary and why, the locator (file,
line or byte offset, the attribute or selector), and whether the HTML alone shows visible
identity evidence or only references external CSS (then say which URL would need capturing).
Compare with the M1 colours in the product (grep for the party codes in the CSS or templates
under product/nz_election/) and state agree or differ per party.

## Output
Your report: the two JSON documents in fenced blocks, then a short list of ambiguities and of
anything you could not read. No file writes.
