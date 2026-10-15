"""Declared-only entry point."""
import argparse
import os
import sys
from pathlib import Path

from .files import LocalFiles
from .registry import join_plists, load_registry
from .reports import build_report, render_json, render_text


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def main(argv: list[str] | None = None) -> int:
    parser = Parser(prog="fleet-audit", description="Validate declarations and join disk plists; no live observation.")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    declared = commands.add_parser("declared", help="validate runbooks and their plist labels")
    declared.add_argument("directory", type=Path)
    declared.add_argument("--json", action="store_true", help="emit one JSON report")
    args = parser.parse_args(argv)
    uid = os.getuid()
    files = LocalFiles()
    registry = join_plists(load_registry(args.directory, uid, files), files)
    report = build_report(registry, f"gui/{uid}")
    if args.json:
        print(render_json(report))
    elif not registry.errors:
        print(render_text(report))
    for error in registry.errors:
        print(error.message, file=sys.stderr)
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
