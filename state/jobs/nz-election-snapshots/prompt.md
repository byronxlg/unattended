# nz-election-snapshots: fetch the static facts once, as sourced snapshots

Byron, issue #40 (Telegram 2026-10-19 04:46Z): "you have codex so don't need to make pipelines for
absolutely everything sometimes you could just ask codex to go get the data to make it more
interesting". And: "there is a real problem with it saying data not available. In that case just
don't show it. I want this to look great."

Goal: the facts that are static or slow-moving get fetched by you, now, from the web, into committed
snapshot files with a source and licence per record, plus a small loader and tests. No scheduled
pipeline, no workflow change. Rendering is the next job (a visual round that consumes these files);
this job adds data and a loader only, so it can run alongside other work. Do not edit templates,
styles, pages.yml or existing tests.

Read first: `AGENTS.md`, `product/nz_election/AGENTS.md`, `product/nz_election/config/sources.json`,
`product/nz_election/config/ec-party-lists-2026.json`, `product/nz_election/config/electorates.json`,
`product/nz_election/config/party-colours.json`, `product/nz_election/geography.md`, and the issue
text: `gh issue view 40`.

## What to fetch (in priority order; stop at the time limit with what is done committed)

1. `snapshots/leaders.json`: leader of each party polling over 1 percent or holding seats (name,
   party id as in party-map.json, role, electorate if any, a photo). Photos only from Wikimedia
   Commons or official sources with a licence that permits reuse (CC0, CC BY, CC BY-SA, public
   domain, NZ Crown copyright with reuse terms); record file page URL, author, licence name and
   URL. Download each to `product/nz_election/web/people/<slug>.webp` (or .jpg), cropped square
   head and shoulders, 320 px, under 40 KB each. No licensable photo: no photo field (absent, not
   null text).
2. `snapshots/candidates-2026.json`: for each electorate in electorates.json, the 2026 candidates
   (name, party, list rank where the EC party lists give one, sitting MP flag), from the Electoral
   Commission candidate list for 2026 (vote.nz / elections.nz) or Wikipedia's electorate articles,
   source per record. Photos only for sitting electorate MPs, same licence rule, same folder.
3. `snapshots/enrolment.json`: enrolled electors by electorate, latest Electoral Commission
   enrolment statistics, with the as-at date.
4. `snapshots/port-waikato-2023.json`: the 25 November 2023 Port Waikato by-election candidate
   results (official EC results), so the electorate has a 2023 holder and margin like the others.
5. `snapshots/history.json`: party vote share and seats for the major parties at every general
   election 1996 to 2023 (EC official results), for context charts.
6. `snapshots/hexmap.json`: a hex (or tile) layout for all electorates, general and Maori, one
   cell per electorate slug from electorates.json, arranged so a NZ reader recognises it (north up,
   Auckland cluster, Maori electorates as a separate group). Cite any published layout you adapt
   (and its licence); a layout you derive from the committed geometry centroids is fine, say so.
7. `snapshots/positions.json`: each party's stated pre-election coalition position, a short quote
   (under 30 words) with URL and date.

Every file: `{"schema": "<name>-v1", "retrieved_at": "<UTC>", "records": [...]}`, every record with
`source_url`, `retrieved_at`, and `licence` where content is copied (photos, quotes). Facts that
you cannot source are left out of the record entirely; the file never contains the words "not
available", "unavailable", "pending" or "missing". Put the snapshots under
`product/nz_election/snapshots/`.

## Code

- `product/nz_election/pipeline/snapshots.py`: `load(name)` returning validated records; raises
  on a record without `source_url` or a photo without licence fields; checks slugs and party ids
  against the committed config.
- `product/nz_election/tests/test_snapshots.py`: every snapshot loads; every photo file referenced
  exists, is under 40 KB and has licence fields; every electorate slug in electorates.json has a
  hexmap cell and no cell is duplicated; no banned word in any snapshot; Port Waikato has a winner
  and a margin. Tests run offline against the committed files.
- A short section in `product/nz_election/runbook.md`: these are snapshots, how to refresh one by
  hand (rerun the fetch, review the diff), and the licence rule.

## Constraints

- No API keys, no raw social posts, no personal data beyond what candidates publish as candidates.
- Repo size: all new images together under 2 MB.
- Commit in the worktree, do not push. Do not commit last.md.

## Done when

`uv run --with pytest pytest -q product/nz_election` passes (676 before plus yours), `bin/lint` says
`lint ok`, and last.md lists the commit, each snapshot with its record count and sources, what you
could not source and why, and the total image bytes.
