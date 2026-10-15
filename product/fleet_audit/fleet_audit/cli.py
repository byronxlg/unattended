"""Declaration validation and bounded audit entry points."""
import argparse
import os
import re
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
    parser = Parser(prog="fleet-audit", description="Validate declarations or audit launchd state and freshness.")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    declared = commands.add_parser("declared", help="validate runbooks and their plist labels")
    declared.add_argument("directory", type=Path)
    declared.add_argument("--json", action="store_true", help="emit one JSON report")
    audit = commands.add_parser("audit", help="audit declared jobs and freshness")
    audit.add_argument("directory", type=Path)
    audit.add_argument("--domain")
    audit.add_argument("--fixture", type=Path)
    audit.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == 'audit':
        try:
            report = run_audit(args)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            return 3
        print(render_json(report) if args.json else render_text(report))
        return report['exit_code']
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


def run_audit(args):
    from .collect import LiveCommands, collect_jobs
    from .reports import audit_fleet
    from .snapshot import load_snapshot, replay
    if args.fixture:
        snapshot = load_snapshot(args.fixture)
        if args.domain is not None and args.domain != snapshot.manifest.domain:
            raise ValueError('domain mismatch')
        return replay(snapshot, 'audit')
    domain = args.domain or f'gui/{os.getuid()}'
    if not re.fullmatch(r'gui/\d+', domain) or domain != f'gui/{os.getuid()}':
        raise ValueError('audit requires current-user domain')
    files = LocalFiles()
    registry = join_plists(load_registry(args.directory, os.getuid(), files), files)
    if registry.errors:
        return build_report(registry, domain) | {'command': 'audit'}
    fleet = collect_jobs(registry.jobs, domain, LiveCommands())
    return build_report('audit', audit_fleet(fleet, files))


if __name__ == "__main__":
    raise SystemExit(main())
