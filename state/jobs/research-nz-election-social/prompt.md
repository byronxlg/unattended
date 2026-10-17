# Research brief: validate a tweet sentiment and party analysis feature, and a feed-shaped home

## Who you are and where this goes

You are the researcher in the unattended lab (read AGENTS.md). The product is live at
https://byronxlg.com/unattended/nz-election/ : a static site about the 2026 New Zealand general
election (election day 7 November, advance voting from 26 October, official results 27 November),
built by scheduled GitHub Actions jobs, no server. Your sandbox is read-only: your final message
IS the deliverable. The supervisor copies it verbatim into intent/nz-election/social.md, so write
a complete, self-contained markdown document, title on the first line, nothing before or after.

Byron, the lab's owner, wrote on Telegram 2026-10-16 23:49Z to 23:57Z (issue #20):

> I have another idea. Tweet sentiment classification and party categorisation analysis. A
> potential structure for the app could be to have a feed like home page with charts and
> description which opens into a page that goes into mor detail. Don't strictly go off what I
> say, that is an idea for making it interesting for users, validate it
> This could be a good inspiration: https://www.nbcnews.com/politics/2026-elections/midterms
> Reach. But we don't need to help people vote if that's what you were getting at. We're more
> displaying info and analysis
> The demographics would be more like, general users / power users / journalists etc
> Just going off how you provide downloads, that would not be useful to general users but
> general users would want to see graphics

So: the success measure is reach, not usefulness to voters; the /vote/ gateway proposed in
intent/nz-election/audiences.md is dropped; audiences are general users (want graphics), power
users and journalists (want data and downloads). "Validate it" means tell him honestly whether
this feature earns its place, with evidence.

Read first: intent/nz-election/intent.md, intent/nz-election/spec.md (routes, data families,
election-night mode), intent/nz-election/design.md (draft 2), intent/nz-election/audiences.md,
product/nz_election/web/templates/ (what each route shows today), product/nz_election/pipeline/
(how data refreshes: one scheduled job writes JSON, build renders static HTML; any new data
family must fit that). Do not repeat their content; build on it.

## The two upstreams (facts from the operator, do not look for keys and never print one)

- Tweets: twitterapi.io (search, user, tweet, user tweets). Read only
  /Users/byron/repos/x402-services/src/services/x-intel/upstream.ts for the request and response
  shape. The account has 783,103 prepaid credits at 2026-10-17; public pricing is about 15 credits
  per tweet returned on search (verify on https://twitterapi.io and cite). Other buyers share the
  balance: a few hundred tweets an hour is the ceiling, never a firehose.
- Classification: Jev, TypeSafe AI's System One (POST https://api.typesafe.ai/v1/systemone): a
  state (text or JSON under 8,000 characters) and up to five typed questions, calibrated numbers
  back. `choice` picks one of named options with a probability each (party or topic
  categorisation), `score` places the state on an ordered scale (sentiment), `noul` is a yes/no
  with a probability. Deterministic for the same input. USD 0.042 per million input tokens,
  output free. Read only /Users/byron/repos/x402-services/src/services/jev/index.ts for the
  request shape and limits. Open nothing else in that repo (no .env, no config, no tests).

Keys exist as GitHub Actions secrets on this repo, so a scheduled workflow can call both. You
cannot call them in this job; estimate from public evidence and say so.

## Questions, in order

1. What would it show? Design three to five concrete charts a general reader would stop for
   (examples to test, not accept: party mention volume per day, sentiment per party over the
   campaign, what topics each party's mentions are about, leaders compared, the swing in the
   final week). For each: the exact query or classification that produces it, the sample it
   needs per day, what a careful caption must say about what X sentiment is and is not (a
   sample of X users, not voters), and the five-second test.
2. Does the volume exist? Estimate the daily count of public tweets about NZ parties and leaders
   in October 2026 (hashtags such as #nzpol, party and leader names, the accounts that post
   them). Use public evidence: 2023 campaign studies, academic work on NZ political Twitter, X
   usage in NZ (share of adults, posting activity), any public counts. Every figure carries its
   source URL and the date you read it; if unknown write "not found". State clearly whether the
   sample is big enough per party per day to chart without noise, and which parties would be
   too thin.
3. What does it cost? Credits per day for the query plan in 1, Jev tokens per day, the total
   to 14 November, and the share of the 783,103 credits. Propose a daily cap and what the
   workflow does when the cap is hit (last good data stays, chip says so).
4. Rules and risks: the Electoral Act 1993 on election day (section 197 and the advertising
   rules: can a site publish a sentiment chart or a feed of political tweets on 7 November
   before 7pm; cite the Electoral Commission's guidance), X's terms on displaying tweet text
   and on derived analysis, bots and coordinated posting, defamation (quoting tweets about
   named candidates), what a methods page must disclose. Say which risks are blockers and which
   are captions.
5. What exists already? Who did X or social sentiment for the 2023 NZ election or does it for
   2026 (universities, media, Curia, Talbot Mills, Pulse, Meltwater-style dashboards), with URLs,
   what they showed, and whether it was any good. NBC's 2026 midterms hub (the URL above): what
   its shape is (feed of cards opening into detail pages?), what each card type is, and which of
   those forms fit a static site with daily data.
6. The shape: given reach as the goal and three audiences (general users want graphics, power
   users and journalists want data and downloads), propose the home page as a feed of chart
   cards with one-line descriptions, each opening a detail route. List the cards in order with
   what the site already has (polls, seats, electorates, candidates, markets from increment 7)
   and what the social feature would add, the detail route each card opens, and how downloads
   and the methods page serve the other two audiences without cluttering the feed. Keep the
   design system (design.md) intact; say where it bends.
7. Verdict: build it, build a smaller version, or do not build it, with the reason in three
   sentences, the smallest version that is worth shipping before 26 October, and the one thing
   that would make you change the verdict. Then the alternative Byron should be offered in the
   judgement-call line (one clause).

## Rules

- Evidence over opinion: sources with URLs and dates; no invented figures or URLs.
- Humble language, no emojis, no em dashes. Under 2,500 words.
- Never print or hint at a key or token value. If you see one anywhere, say "a key is present at
  <path>" and nothing more.
