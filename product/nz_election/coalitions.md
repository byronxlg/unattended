# Retired coalition explorer

The interactive explorer left all routes in PR #71 (170bf94). Its client, controls,
browser checks and synthetic screenshot states are now retired. The contract
below is historical.

Replacement invariants: polls answers render on the server; legacy fragments resolve
even without data; rendered tables keep provenance, unique region names and keyboard
access. Python coalition calculations, build.strip and TOP labels remain. Night
still imports allocator.mjs through night-seats.mjs. Share-state interaction and
client/server strip parity no longer apply because no explorer is rendered.

## Replacement checks

| Retired check | Current invariant |
| --- | --- |
| verify_coalitions explorer markup | Script-free polls, no fieldset, preserved explorer/source IDs; static majority and server calculations still checked |
| home_checks legacy inventory | All legacy IDs exist with or without data; published poll IDs still resolve; home and polls need no client scripts |
| landmark_checks client startup adapter | All 81 rendered routes retain image roles, provenance, unique region names and named keyboard-scroll targets |
| Client strip parity and browser states | No client strip or controls remain; server strip/TOP tests stay, staged modules and allowlist are pinned |
| Screenshot explorer states | Live data-availability states remain; static-text comparison now includes all polls content |

## Historical coalition explorer contract

The explorer uses only the published averages and seats envelopes. Its fingerprint is
SHA-256 of the concatenated averages.json and seats.json hexadecimal SHA-256 hashes.
The page pins both file hashes and the browser checks the downloaded bytes before enabling
controls. A saved state with another fingerprint is rejected with a visible warning.

Share URLs use `#coalition=<percent-encoded canonical JSON>`, bounded to 8192 characters.
The JSON object has exactly `version` (1), `mode` (`unchecked`), `fingerprint` (64 lowercase
hexadecimal characters), `selected` (distinct named party IDs), and `counts` (every named
party ID mapped to a canonical ASCII decimal string from "0" to "71"). Counts total at
most 71. Canonical JSON uses sorted object keys, no whitespace and literal Unicode.
Requiring canonical JSON also rejects duplicate object keys. Others is never selectable.
Reset removes the hash and restores the published electorate counts with no selection.

## Invariant enforcers

| Brief | Enforcement |
| --- | --- |
| 1. Static first | `build.polls_page` retains `strip`; hidden disabled fieldset; `verify_coalitions`, `test_static_content_preserved`, JS-disabled `coalitions_browser.py` |
| 2. Script allowlist | `scripts.validate_scripts` permits only `coalitions.mjs` and `allocator.mjs` at same-origin `PREFIX` paths, with exactly `type="module"` and `src`, no inline content or other scripts. This is a filename allowlist, not a module hash check. `build.py` copies these `product/nz_election/web/*.mjs` bytes from the PR-reviewed code checkout. Enforced before publishing, by `verify_polls`, `test_build`, the screenshot harness and `test_script_allowlist`. |
| 3. Exact arithmetic | `coalitions.scenario` and `coalitions.mjs` call `entitlement`; `test_scenario_python_js_parity` compares canonical output bytes |
| 4. Conditional majority | Both scenario functions keep occupied House, vacancies and definitive majority null; `test_unknown_capacity_stays_conditional`; real-candidate vacancy allocation in `test_real_candidate_vacancies` and `verify_coalitions` |
| 5. Empty selection, electorate limits | `inputs`, `validate`, Reset handler; `test_no_preselected_coalition`, browser checks |
| 6. Untrusted hash | `decode` and `validate` in both implementations; `test_invalid_state_error_parity`, fingerprint test and browser rejection checks; dynamic content uses `textContent` |
| 7. Incomplete inputs | `inputs`, pinned download hashes, fail-closed initialization; `test_incomplete_average_disables_explorer`, module/data failure browser checks |
| 8. Accessibility | Existing strip classes and new control CSS; browser keyboard, focus, contrast, live-region, reduced-motion and overflow assertions |
| 9. Screenshots | Six routes and 12 baseline images unchanged; six additional states at two sizes give 12 state images, 24 images overall |

## Departures and review limits

- `intent/nz-election/plan-m2.md` is absent from this checkout. The build brief and spec
  requirement 4 govern this implementation; no intent files were changed.
- The existing screenshot harness must allow the module and compare static content outside
  the explorer. This deliberately replaces its M1-only script prohibition, alongside the
  named `test_build` and verifier assertions. Existing injection tests remain untouched.
- The coalition vacancy screenshot shows unknown capacity and possible vacancies, not an
  invented definitive count. Real captured candidate IDs exercise exhausted-list allocation
  in tests; no checked-capacity UI ships without verified 2026 candidates.
- Chromium cannot start in this sandbox (Mach-port permission denied). The supervisor must
  run both browser commands and inspect phone and desktop images before acceptance.
