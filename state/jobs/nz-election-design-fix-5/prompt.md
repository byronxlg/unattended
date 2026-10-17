Fifth follow-up on change/nz-election-design, after the fresh-context review of PR #21 on your
bed5452 (CI green, host harness PASS all 77 routes, 202 images). The review found eight
Important items and two nits; its full text is at the end of this brief. Carry every Important
item in one round; the two nits as stated. Reply with the commit hash, the verification tails,
and for each finding one line: what you changed, or why it is already true, or "deferred" with
the reason. Commit on the branch, do not push.

Decisions on the findings:

1. build.py:251 empty 30-day window. Invariant: build never raises for any bundle verify.py
   accepts; enforced by the home-page tests and by the daily workflow. Compute the window range
   only for a nonempty window and render the unavailable form otherwise; add one regression
   test (polls older than 30 days, build renders). Confirm with the reviewer's comparison: the
   73378ab fixture that rendered 22521 characters must render on your HEAD.

2. Weakened checks. test_coalitions.py:149 and test_increment_two_regressions.py:184 must be
   at least as strong as at 73378ab, expressed against the new markup: full strip and table
   equality (rows, columns, values), numerical anchors and connector checks for the new
   geometry. Editing those two assertions back to full strength is the one test edit allowed
   in this round; no other existing test changes, no assertion anywhere becomes weaker. New
   tests are welcome.

3. coalitions.mjs:89 vs build.py:186 parity. Invariant: the client-rendered coalition strip is
   DOM-equal and accessibility-equal to the server-rendered one for the same inputs (names,
   captions, columns including per-party base and overhang, disclosure structure, precision).
   Add the parity check with an overhang fixture (the existing node or Playwright path the
   tests already use; choose). If parity cannot be reached in this round, say exactly which
   attribute still differs and why.

4. electorate_pages.py:18 source labels. Invariant: each source link carries its own
   publisher and licence as recorded in the bundle (the Representation Commission report is
   not "Stats NZ"); the source note shows the original-source links and licences in the
   visible paragraph, per the accepted source-note grammar in design.md. Fix the label
   derivation per source, not per dataset, and move the links out of the disclosure.

5. styles.css:3 link line boxes. Merge-blocking design defect: prose links are inline-block
   44 px with vertical padding, so the source note is triple-spaced at every width and on the
   OG card. Fix as the reviewer says: no interactive padding inside .og; on the site, compact
   provenance prose (inline links, normal line height) separate from a wrapping row of genuine
   44 px source and action links; no overlapping invisible hit areas. The 44 px target for
   buttons and navigation stays. Look at the result at 360 and 1280 and on og-home.png before
   you reply; the harness screenshots are part of done.

6. build.py:258 "Read how seats are calculated." stays visible after the unavailable home
   sentence in both unavailable forms (no polls, polls-present seats-unavailable), as draft 2
   requires; the disclosure may repeat it but not replace it.

7. screenshots.py:225 OG headline. Invariant: the OG card never claims a seat estimate the
   page withholds; one availability decision, computed once in the pipeline, feeds both the
   page and the card together with the selected poll's provenance. Share that function, do
   not duplicate the rule.

8. screenshots.py:221 per-route cards and og:image metadata: deferred to its own change
   (feed home, planned for next week). Do nothing here beyond leaving the template usable;
   state "deferred" in your reply.

Nits: blur the focused main after the focus test and capture focus separately (cheap, do it).
The unavailable OG card's empty lower half: deferred, do not fill it.

Done means: pytest green with no weakened assertion; refresh/build/verify; python
product/nz_election/tests/screenshots.py --out /tmp/ds-shots and --og-only --out /tmp/ds-og
pass including axe; bin/lint clean; list any check the sandbox could not run as a claim and I
will run it on the host.

--- Fresh review of PR #21 (review-nz-election-design, read-only, 2026-10-17 00:37Z) ---
- **Important**: [build.py:251](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/pipeline/build.py:251) crashes when the current 30-day window contains no polls, even with retained poll history. Read-only comparison: `73378ab empty window: rendered 22521 characters`; `HEAD empty window: ValueError min() iterable argument is empty`. Compute the range only for a nonempty window. This can block production builds.

- **Important**: Existing checks became weaker. [test_coalitions.py:149](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/test_coalitions.py:149) replaces full strip/table equality with figure equality and a caption substring, allowing missing or incorrect table rows. [test_increment_two_regressions.py:184](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/test_increment_two_regressions.py:184) removes numerical anchor and connector checks without equivalent checks for the new geometry. Restore those guarantees using the new markup. The other modified assertions preserve their intent or strengthen it.

- **Important**: [coalitions.mjs:89](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/web/coalitions.mjs:89) does not match [build.py:186](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/pipeline/build.py:186): accessible strip names, captions, table columns, disclosure structure and percentage precision differ. The client omits per-party base/overhang columns. Both correctly remove the invalid overhang `aria-label`, but that fix does not establish parity. Add a DOM/accessibility comparison using an overhang fixture.

- **Important**: [electorate_pages.py:18](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/pipeline/electorate_pages.py:18) assigns every source link the publisher inferred from the dataset. Consequently, the Representation Commission report is labelled “Stats NZ”; mixed candidate sources can be labelled “Electoral Commission”. Preserve each source’s identity. The visible paragraph also hides the original-source links and licences inside disclosure, contrary to the accepted source-note grammar.

- **Important**: [styles.css:3](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/web/styles.css:3) makes every prose link an inline block with 44 px height and vertical padding. The resulting triple spacing and separated retrieval date are a merge-blocking design defect, especially on the static OG card. First remove interactive padding in `.og`. For the website, separate compact provenance prose from a wrapping row of genuine 44 px source/action links; avoid overlapping invisible hit areas.

- **Important**: [build.py:258](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/pipeline/build.py:258) hides “Read how seats are calculated.” inside “Why seats are unavailable”. Draft 2 explicitly requires that link following the unavailable home sentence. Keep it visible in the polls-present, seats-unavailable form too.

- **Important**: [screenshots.py:225](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/screenshots.py:225) generates the OG headline directly from `default_scenario`, bypassing the page’s stale-data withholding. An overdue coherent bundle can therefore produce a seat estimate on the card while the page says none is available. Share the page’s availability decision and selected-poll provenance.

- **Important**: [screenshots.py:221](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/screenshots.py:221) renders only home and Wellington North cards into test artifacts. There is no published per-route card generation or `og:image` metadata. The template exists, but draft 2’s per-route sharing requirement is incomplete. Either deliver that integration or explicitly accept its deferral.

- **Nit**: [screenshots.py:103](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/screenshots.py:103) leaves the keyboard-focused main outline in baseline captures. Keep the real focus behavior, but explicitly blur after testing it and capture focus separately. OG uses a fresh page and replacement document, so this artifact does not taint its capture.

- **Nit**: [screenshots.py:227](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/tests/screenshots.py:227) leaves the unavailable OG card’s lower half empty. Follow-up, not a blocker: rebalance its typography and spacing, optionally include the latest poll date. Do not invent a seat graphic to fill space.

Verification was read-only; no full pytest/browser rerun. Budgets measure actual built bytes, not claimed constants: CSS is 10,609 bytes; the existing fixture transfers 17,484 bytes before the reserved font. Reconstructing `73378ab`’s generated CSS gives 24,779 bytes, so that budget fails on main. New token, identity and provenance requirements also distinguish main, although not every new assertion does; provenance checks only references, not attribution accuracy. Axe is 553,446 bytes, includes MPL-2.0, matches the documented SHA-256, and is absent from the inspected site output. No data captures, route registry or workflows changed; presentation and availability behavior did.

The 390 px screenshot **passes the unavailable-form five-second test**: the site identifies itself, clearly says there is no seat estimate, and names the poll source before scrolling. The host manifest measures the source-note bottom at 458.8 px at both phone widths. It does not establish the populated-number form’s quality. The first visual change should be source-note spacing, then moving available poll information ahead of the disabled explorer explanation. Desktop repeats the spacing defect; the electorate and election-night pages are readable but sparse. The attached election-night page is light, so it does not demonstrate the dark token treatment.

Important findings: 8