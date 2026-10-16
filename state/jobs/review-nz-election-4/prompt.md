Fresh-context review of branch change/nz-election-4 against main (merge-base 307febd), for
https://github.com/byronxlg/unattended/pull/12 (NZ election increment 4, coalition explorer),
HEAD 7dca242. Worktree .worktrees/nz-election-4, read-only. Follow REVIEW.md. Important or Nit,
at most five nits, nothing bin/lint reports. Do not approve.

Context: this increment adds the first JavaScript to the product: product/nz_election/web/
coalitions.mjs, a progressive-enhancement module on the polls page, allowlisted by hash through
pipeline/scripts.py. It recomputes seats in the browser from the published averages.json and
seats.json with the same exact integer Sainte-Lague arithmetic as pipeline/allocator.py, lets a
reader pick parties and assume electorate wins, and shares state through a `#coalition=` URL
fragment. Python twin: pipeline/coalitions.py (scenario, decode, validate). Contract and the
engineer's enforcer table: product/nz_election/coalitions.md. Spec: intent/nz-election/spec.md
requirement 4. Plan: intent/nz-election/plan-m2.md, section Increment 4 and the nine invariants
(static first, script allowlist, exact arithmetic, conditional majority, empty selection and
electorate limits, untrusted hash, incomplete inputs, accessibility, screenshots). The engineer's
report is state/jobs/nz-election-4/last.md in the main checkout (not the worktree), if readable.

Scope, in this order:
1. Untrusted input in coalitions.mjs and coalitions.py: `git diff 307febd..7dca242 --
   product/nz_election/web/coalitions.mjs product/nz_election/pipeline/coalitions.py`. The hash
   fragment is attacker-controlled. Walk decode and validate on both sides for every field:
   canonical JSON requirement (does the JS actually re-serialise and compare bytes, or only
   parse?), duplicate keys, prototype keys (__proto__, constructor) as party IDs or object keys,
   non-string counts, leading zeros, "-0", Unicode digits, percent-decoding errors, fragments
   over 8192 characters, a fingerprint for other data. Is any decoded value ever written with
   innerHTML or into an attribute? Does an invalid state leave the page in the static state with a
   visible warning, and is the warning text itself static?
2. Arithmetic parity: coalitions.mjs and coalitions.py both call the entitlement allocator.
   Confirm no Number arithmetic touches seat counts or quotients on the JS side (BigInt
   throughout, including the unassigned count and House size). Does test_scenario_python_js_parity
   compare canonical bytes across a set of scenarios that includes overhang, a party under
   threshold with an electorate, every party selected, no party selected, and counts summing to
   exactly 71? Would the parity test fail if the JS silently used Number for one path?
3. Conditional majority: the published M1 data keeps occupied_house, vacancies and majority
   null when list capacity is unchecked. Does the explorer ever print a definitive majority or a
   definitive House size? Read the two coalition screenshots (artifacts/nz-election/screenshots/
   coalition-edit-*.png and coalition-vacancy-*.png in the worktree) and check the wording.
4. Static first and the allowlist: build.py and the hidden disabled fieldset with JS off;
   scripts.validate_scripts (what exactly is hashed, how a mismatch fails, whether it runs before
   publishing in refresh.py and in verify_polls); the replaced M1 assertions in test_build.py and
   screenshots.py (`git diff 307febd..7dca242 -- '*test*'`): are the replacements at least as
   strong (no inline scripts, no scripts outside the allowlist, no external origins)? Did any
   existing test other than those named assertions change?
5. Accessibility against spec requirement 4 and the plan's invariant 8, judged from
   coalitions_browser.py and the screenshots: keyboard reachability, 3px focus, 44px targets on
   the checkboxes and inputs at 390px, live region announcing the recomputed summary, reduced
   motion, overflow at 390px, colour not the only carrier of selection.
6. Byte budget: size of coalitions.mjs and the CSS added; the plan's budget for the polls page.

Host run stands at 7dca242: 252 passed, bin/lint ok, refresh and build and verify all PASS
(including PASS coalitions), coalitions_browser.py PASS, screenshots PASS 6 routes 12 baseline
images plus 12 state images. The supervisor looked at the four coalition images. Chromium does
not start in your sandbox; reason from the code and read the PNGs.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
