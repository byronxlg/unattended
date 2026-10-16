# Research brief: who reads an NZ election site, and what each audience needs first

## Who you are and where this goes

You are the researcher in the unattended lab (read AGENTS.md). The product is live at
https://byronxlg.com/unattended/nz-election/ : a static site about the 2026 New Zealand general
election (election day 7 November, advance voting from 26 October, official results 27 November).
Byron, the lab's owner, wrote on 2026-10-16: "do some more research on what people want to see
and make some pages targeting different audiences and tailor the ui to them." This job is that
research. Your sandbox is read-only, so you cannot write files: your final message IS the
deliverable. The supervisor copies it verbatim into intent/nz-election/audiences.md, so write a
complete, self-contained markdown document with the title on the first line and nothing before
or after it.

Read first: intent/nz-election/intent.md, intent/nz-election/spec.md (the sections on routes,
data families and the election-night mode), intent/nz-election/design.md (draft 2: the home
sentence, the four forms, the source note, the twelve states), product/nz_election/web/templates/
(what each route shows today). Do not repeat their content; build on it.

## Questions, in order

1. Who reads an NZ election site in the last three weeks, on election night, and in the week
   after? Candidate audiences to test, not a list to accept: first-time and young voters,
   undecided voters comparing parties, voters in a swing electorate, readers who follow polls
   closely, journalists and researchers who want the data, overseas New Zealanders, election-night
   watchers on a phone. Drop any the evidence does not support; add any it does.
2. For each audience: the one question they arrive with, the first thing they look for, the
   device and moment (commute, couch, newsroom, polling booth queue), and what would make them
   leave in five seconds.
3. Evidence: Electoral Commission FAQs and its most-visited pages, Google Trends for NZ election
   queries in October and November 2023 (and 2020 if 2023 is thin), how the 2023 coverage was
   structured (RNZ, NZ Herald, Stuff, 1News, Interest.co.nz, The Spinoff, Wikipedia's opinion
   polling page), and what the existing dashboards (name them with URLs) serve and miss.
   Every claim carries its source URL and the date you read it. Never invent a figure or a URL;
   if unknown write "not found". Depth over breadth.
4. The page plan: for each audience you keep, the page or view it needs (new route, a new entry
   point on an existing route, or a UI tailoring such as default tab, ordering, copy, density),
   what data it needs that the site already has, what it needs that the site lacks and where that
   would come from (source URL, licence, update cadence), and the five-second test for it.
   Mark each item: build before 26 October (advance voting), before 7 November, or after.
5. What should NOT be built, and why (the strongest candidates you rejected).

## Document format

1. Title: "# Audiences for the NZ election site, 2026-10-17 (Codex research job research-nz-election-audiences)"
2. "## Summary" of ten lines at most: the audiences kept, the two or three pages or tailorings
   with the best evidence, and the one surprise.
3. "## Audiences": one subsection per audience answering question 2 with its evidence.
4. "## Evidence": the sources table (source, what it showed, URL, date read).
5. "## Page plan": a table (audience, page or tailoring, data have, data need and source,
   five-second test, build-by).
6. "## Not building".
7. "## Open questions for Byron": at most three, each answerable in one word.

Constraints: the site stays static on Pages fed by scheduled Actions jobs, no bundler, phone
first, everything verifiable by commands and screenshots. Under 2,500 words. No emojis, no em
dashes, humble language: a thing is true when a source shows it.
