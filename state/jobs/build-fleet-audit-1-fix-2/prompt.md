# Follow-up 2: Fleet Audit increment 1, two fresh-review findings

Same worktree `.worktrees/fleet-audit-1`, branch `change/fleet-audit-1`, on top of 29b2ff4
(now PR #1, CI green). A fresh-context review found two crash paths under malformed plist
input; the supervisor reproduced both on Python 3.12. Fix only these. Commit in the worktree;
never push. Do not edit `pytest.ini` or `.github/workflows/ci.yml`.

## 1. More plistlib exceptions escape `observe_plist` (Important)

`fleet_audit/plists.py` `observe_plist`: `plistlib.loads(b'<plist><key>x</key></plist>')`
raises `IndexError` and `plistlib.loads(b'<plist><date>x</date></plist>')` raises
`AttributeError`; both escape as a traceback so `declared` never reaches exit 3. The input is
untrusted bytes and the error message already keeps only the exception class name, so catch
`Exception` around the parse (keep the existing comment's reasoning; say in a comment why the
broad catch is right here) and produce the same `invalid_plist` error with
`{type(exc).__name__}: malformed plist`. Add both inputs to `test_plist_join_errors` with their
exact expected messages (`invalid plist: IndexError: malformed plist`,
`invalid plist: AttributeError: malformed plist`).

## 2. `Unsupported` KeepAlive payloads are not JSON-safe (Important)

A KeepAlive mapping may contain `<data>` (bytes) or `<date>` (datetime) values; `frozen`
leaves them as is, and `declared --json` then crashes in `json.dumps`
(`{'KeepAlive': {'x': b'a'}}` reproduces). Fix in `parse_plist`: accept a KeepAlive mapping as
`Unsupported` only when every nested value is bool, int, str, list or dict of the same; any
other value type is a field error `KeepAlive: invalid value` and the field becomes
`Unknown("invalid value")`, matching the other fields. Add to `test_plists.py`: bytes and
datetime values inside KeepAlive give one field error and `json.dumps(serialize(...))` succeeds;
the existing `SuccessfulExit` mapping fixture is still `Unsupported`. Never copy the raw
bytes or date into any message.

## Definition of done

Paste actual output of each:

1. From `product/fleet_audit/`: `uv run --with pytest pytest -q` with zero failures and the
   test count (expected 194 or more).
2. From `product/fleet_audit/`: `uv run python -m fleet_audit.acceptance registry --offline`
   last line `OK registry`.
3. From the worktree root: `bin/lint` exits 0.

Final message under 25 lines: files changed, the three outputs, and anything you could not do.
