# Page plan template

Byron, Telegram 2026-10-20 01:41Z: "You need to fix the process. Make sure research and planning
is done before making the ui. Start with what will a user be interested in seeing and work back."

Every page (or shared surface, `site.md` for chrome and navigation) gets a page plan at
`intent/<slug>/pages/<page>.md` before any UI build brief for it is dispatched. Order is fixed:
readers and their questions, then answers, then data, then layout. Visual style (`design-principles.md`,
`look-538.md`) is applied last and never decides what is on the page. `bin/lint` checks the
sections below; `bin/codex-run` refuses a UI build brief that does not name an accepted plan.

Copy from here down.

---

# <page>: page plan

status: draft
route: `/unattended/nz-election/<route>/`
research job: `state/jobs/<id>/last.md`

## Readers and their questions

Who arrives on this page, from where (search, share, the home, election night), and the questions
they bring, ranked by how many readers have them and how much they matter on the day they visit.
One line each, in the reader's words, with the evidence for the rank (search data, the EC voter
survey, what NZ outlets and reference sites lead with, Byron's issues). At most seven.

1. <question in the reader's words> - <who, when> - evidence: <url>, <url>
2. ...

## Answers

For each question above, in the same order: the answer in one sentence as the reader would read
it today, and the fastest form that gives it (one number, a chart, a map, a table, a link out).
If the honest answer is "nobody knows yet", say what the page shows instead.

## Data, worked back

For each answer: the data it needs, and one of: have it (file under `data/`), fetch once now
(Codex one-off, sourced and dated), pipeline (scheduled job, existing or new), or drop the
question (absent data is never rendered). Licence and refresh cadence beside each.

## Page order

The page top to bottom at 390 px, in question rank: what is above the fold (the top one to three
answers), then the rest. A text wireframe is enough. Anything on the page that answers no ranked
question is listed here with the reason it stays, or it goes.

## Not shown

What readers might expect and this page deliberately leaves out, with the reason (another page
answers it, the data does not exist, another publisher does it better, it belongs on the
sources page).

## Question test

The acceptance test for the build: a reviewer given only the 390x844 screenshot answers questions
1 to 3 within five seconds each, and the 1280x800 screenshot answers every ranked question without
scrolling past an unrelated section. The fresh review runs it and logs the answers it read off.
