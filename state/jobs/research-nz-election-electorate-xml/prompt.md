# Research: EC electorate detail XML paths (read-only, web live)

Goal: the supervisor must capture electorate detail XML files before M3 increment 4 (electorate
leaders on night/, `intent/nz-election/plan-m3.md` increment 4; `intent/nz-election/pages/night.md`
question 3 "Who is ahead in my electorate?"). The national files are known
(`https://electionresults.govt.nz/electionresults_2023/xml/{election,parties,candidates,electorates}.xml`,
same quartet at `https://mediademo.electionresults.govt.nz/xml/`), but the per-electorate detail
path is not: `e1.xml`, `e01.xml`, `electorate-1.xml`, `electorates/e1.xml` all return 404 on both roots.

Read first: `product/nz_election/fixtures/manifest.json` (existing EC captures and their notes),
`product/nz_election/fixtures/ec-mediademo-xml/electorates.xml`, `intent/nz-election/plan-m3.md`
"Supervisor capture gates" and increment 5.

Find, with a citation for every claim (EC media kit or XML documentation, the mediademo site,
archived 2017/2020/2023 media pages on web.archive.org):
1. The exact URL rule for an electorate detail file on the 2023 root, the mediademo root, and the
   expected 2026 preliminary and official roots, with one URL per root you confirmed returns 200
   (HEAD or GET; say which, and the status you saw).
2. What a detail file contains (candidate votes, party votes, voting places counted, update time)
   and its element names, from one fetched file.
3. Whether the 2026 media kit or XML spec is published yet, its URL, and anything it says about
   HTTPS, CORS, rate limits or terms of use.
4. Anything that changes the increment 5 assumptions in plan-m3.md (serial polling, 30 s floor).

Constraints: read-only, no files written, no more than about 40 requests to electionresults.govt.nz.
Done: `last.md` answers 1 to 4 in order, each with URLs, and lists what you could not confirm.
