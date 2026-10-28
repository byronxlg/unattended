Build: the 2026 advance vote count on vote/ and home, from the Electoral Commission's own table.

Page plan: intent/nz-election/pages/vote.md (home: intent/nz-election/pages/home.md). Design: product/nz_election/DESIGN.md.

Goal. The EC publishes informal daily advance-vote counts at
https://vote.nz/2026-general-election/about/overview/voting-statistics (CSV link .../voting-statistics/AdvanceVoteCSV).
Read-only research on 28 Oct 2026 20:08 NZDT (state/jobs/research-nz-election-advance-2026/last.md) read the HTML table:
columns Date, 2020 General Election, 2023 General Election, 2026 General Election; 2026 rows 26 Oct 69,034 and
27 Oct 106,714 (175,748 through 27 Oct); caveat: informal daily counts, subject to revision, excluding overseas votes;
updated daily. The CSV and page are behind Incapsula for curl and headless Chromium on the host, so the first 2026
capture is a transcription of the official table with its source URL, retrieved_at 2026-10-28T07:08:00Z and a
provenance note saying it was transcribed from the EC page, not downloaded.

Read first: product/nz_election/pipeline/advance.py, product/nz_election/tools/advance_preflight.py and their tests,
pipeline/vote_page.py, pipeline/home.py, AGENTS.md.

Do:
1. Commit that capture through the existing advance capture path (fixtures/captures and its manifest), kind daily,
   start 2026-10-26, count column "2026 General Election", with the caveat and provenance. Preflight currently rejects
   the header (no daily/cumulative wording in it): let the capture declare kind explicitly from the page's own semantics
   and have preflight accept that declaration; it must still reject an undeclared, ambiguous header. Tests on main may
   move only where they pin the old rejection of a declared kind; say which.
2. vote/: one dated, sourced line in the advance-voting part: "175,748 advance votes reported through 27 October.
   Informal count, subject to revision; excludes overseas votes." with the EC link and retrieved date, taken from the
   data, never literal. Home: the same figure on the voting-dates line, or nothing if the family is absent. No zero,
   no 2023 substitute, no "not available" text when absent (absent means absent).
3. Tests check data, provenance and absence, not markup or class names.

Constraints: worktree only, commit, never push. No secrets. No new dependencies.

Done when, all shown in your last message:
- uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home" : passed (Chromium launch
  denials in the sandbox listed by name, nothing else failing)
- uv run python product/nz_election/tools/advance_preflight.py on the capture: PASS line
- bin/lint : lint ok
- the vote/ and home lines as rendered text from a fixture build.
