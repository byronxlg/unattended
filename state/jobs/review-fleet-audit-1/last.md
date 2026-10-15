Two malformed-input paths crash instead of producing structured validation reports. Offline acceptance returned OK registry; the pytest command was blocked by sandbox restrictions on the uv cache.

Full review comments:

- [P2] Handle additional malformed XML plist exceptions - /Users/byron/repos/unattended/.worktrees/fleet-audit-1/product/fleet_audit/fleet_audit/plists.py:64-67
  Malformed XML plists can raise exceptions outside this handler: `<plist><key>x</key></plist>` raises `IndexError`, and `<plist><date>x</date></plist>` raises `AttributeError` on Python 3.12. Both escape `observe_plist`, causing `declared` to terminate with a traceback instead of reporting invalid input and returning 3. Normalize these parser failures into the existing sanitized `invalid_plist` observation.

- [P2] Make unsupported KeepAlive payloads JSON-safe - /Users/byron/repos/unattended/.worktrees/fleet-audit-1/product/fleet_audit/fleet_audit/plists.py:39-40
  A KeepAlive mapping containing a plist data or date value is retained without validation, but `frozen` leaves bytes and datetime objects unchanged. Consequently, `declared --json` crashes in `json.dumps` rather than emitting a report; a mapping such as `{'x': b'a'}` reproduces this. Either reject these values as invalid plist fields or encode them into a JSON-safe unsupported representation.