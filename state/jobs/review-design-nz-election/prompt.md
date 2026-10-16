Read-only critique of intent/nz-election/design.md (draft 1, the design brief for the NZ election
web app). You are the second designer on this brief: your job is to find what will fail when it is
built, not to restate it. Do not change files.

Read first: intent/nz-election/design.md; intent/nz-election/spec.md "Design" section and lines
270 to 280 (accessibility); product/nz_election/web/styles.css and templates/base.html and
polls.html (what exists today, 8 KB CSS, system sans, seat strip); config/party-colours.json
(seven sampled fills with evidence); product/nz_election/AGENTS.md Design rules; REVIEW.md pass 4.
Byron's steer is in the "Design and marketing track" section of intent/nz-election/intent.md.

Judge, with evidence from the files:
1. The five-second test: from the 390 px wireframe, does the first viewport really hold the site
   name, the home sentence (two lines at 32 px?), the strip with its label lane and the provenance
   line? Estimate the pixel height of each from the type scale and the existing strip CSS
   (.strip min-height 104 px on phones plus the lane height) and say what falls below the fold.
2. Contrast: compute the contrast ratio of every pairing the brief claims (grey #5A5A5A on
   #FFFFFF, rule #C8C8C8 boundary on white, night grey #A9B2BF on #0F1A2B, night rule #3A4658 on
   night paper, tick #F58220 as a mark on white and on night paper, focus #005EA8 and #7CC4FF).
   Report any below 4.5:1 for text or 3:1 for boundaries, and which party fills from
   config/party-colours.json fall under 3:1 against either paper so an outline is required.
3. The font decision: the budget is a 45 KB woff2 subset of Bricolage Grotesque for display only.
   Does the spec's "no font CDN" constraint and the first-view budget of 100 KB survive it with
   the current HTML and CSS sizes (measure site output if a build exists under site/nz-election,
   otherwise the templates)? Is a display-only face at four sizes worth 45 KB, or should the brief
   spend it elsewhere? Give a recommendation and the reasoning.
4. The home sentence: is "National-led bloc 63 seats, Labour-led 57" an editorial claim the site
   cannot source? Propose the exact sentence form for the three cases (majority, no majority, no
   data) that uses only the allocator's party totals and the explorer's default scenario.
5. Provenance chip: does the pattern scale to a table with 71 rows (one chip per row would be
   noise)? Propose where the chip sits for tables, strips, single numbers and the map.
6. States and copy: any state the brief misses that the pipeline already produces (read
   publish.py status handling and the templates' state blocks); any copy that names system
   internals.
7. Anything in the brief that is a generic default rather than a choice for this subject, and
   anything that contradicts spec.md or AGENTS.md.

Report: findings as Important (would produce a defect or a failed review round if built as
written) or Nit, each with file:line or a computed value, and "Important findings: N" as the last
line.
