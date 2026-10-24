# Research: the 2026 advance-voting statistics source

Read-only research, web live. No files change.

## Goal
Advance voting for the 2026 NZ general election opens Mon 26 Oct NZDT. `product/nz_election/pipeline/advance.py`
ingests national advance observations from committed captures (`fixtures.captures`), modelled on the
2023 `AdvanceVoteCSV`. plan-m3.md says the 2026 URL is unconfirmed and must be discovered from the
official page, not inferred. Find it before the first day's figures publish (expected 27 Oct NZ).

## Read first
- `product/nz_election/pipeline/advance.py`, `product/nz_election/fixtures/manifest.json` (advance entries)
- `intent/nz-election/plan-m3.md` "Supervisor capture gates" (advance paragraph)

## Answer, with evidence (URL, what you fetched, status code, date)
1. The official elections.nz page where 2026 advance-voting statistics will be (or are) published, and the
   exact file or table URL if it exists yet. If not yet published, the 2023 and 2020 pattern (page and file
   URLs, first publication day relative to opening, update time of day, daily vs cumulative columns).
2. Whether that origin answers a plain HTTPS GET from a non-browser client (status, any bot wall or WAF
   page), and whether a Wayback `id_` snapshot path works as a fallback.
3. Whether the 2026 format is likely to parse with `advance.py` as written (columns, kind daily or
   cumulative, date format); list any difference.
4. A recommendation in three lines: fetch in the daily workflow, or supervisor capture by hand each
   morning, and what the page should say on days with no figure.

Definition of done: a short report with the four answers and every URL you touched; say plainly what you
could not confirm.
