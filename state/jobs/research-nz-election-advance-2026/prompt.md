# Research: is the 2026 advance-voting statistics file published yet

Read-only research, web live. No files change.

## Context
Advance voting opened Mon 26 Oct 2026 NZDT. The supervisor tried on 27 Oct: plain curl to elections.nz gets an
Incapsula bot wall; a browser found no 2026 voting statistics page or CSV link. In 2023 updates began on day 2.
Earlier research: state/jobs/research-nz-election-advance-source/last.md. Ingest code:
product/nz_election/pipeline/advance.py (2023 AdvanceVoteCSV shape), tools/advance_preflight.py.

## Answer, with evidence (URL, what you fetched, status code, time)
1. Is a 2026 advance-voting count published anywhere official today (elections.nz pages, the EC media releases,
   the EC's social accounts quoted by NZ media, media.election.net.nz)? Exact URL and the latest figure and date.
2. If an official file exists: its URL, columns, daily or cumulative, and whether advance_preflight.py and
   advance.py would accept it as written (run them read-only on a downloaded copy in /tmp if you can).
3. If only a figure in a media release or news story exists: the exact sentence, its source URL and date, so the
   supervisor can decide whether to show it as a dated, sourced figure.
4. Three lines: what the supervisor should capture today and from where, and what vote/ and home should say
   until the official file appears.

Definition of done: a short report with the four answers and every URL touched; say plainly what you could not
confirm.
