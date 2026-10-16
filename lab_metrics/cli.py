"""Command entry point, collection and atomic output."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from .compute import compute
from .models import Snapshot
from .render import render_document
from .sources import (read_artifact_history, read_changes, read_evals, read_github,
                      read_head, read_jobs, read_mistakes, read_ticks)

ROOT = Path(__file__).resolve().parent.parent


def collect(root):
    head = read_head(root)
    jobs = read_jobs(root / "state/ledger.jsonl")
    ticks = read_ticks(root / "state/ticks.jsonl")
    changes = read_changes(root / "state/changes.yaml")
    mistakes = read_mistakes(root / "state/mistakes.jsonl")
    evals = read_evals(root / "evals/results.jsonl")
    history = read_artifact_history(root, [r["slug"] for r in changes.data])
    numbers = sorted({p for c in changes.data for p in c["prs"]})
    github = read_github("byronxlg/unattended", numbers, time.monotonic()+45)
    sources = dict(jobs=jobs, ticks=ticks, changes=changes, mistakes=mistakes,
                   evals=evals, history=history, **github.sources)
    diagnostics = {"sources": {
        name: dict(available=src.available, reason=src.reason, skipped=src.skipped, warnings=src.warnings)
        for name, src in sorted(sources.items())},
        "skipped": sum(src.skipped for src in sources.values())}
    if head.committed_at is None:
        diagnostics["invalid_head_timestamp"] = 1
    return Snapshot(head, jobs, ticks, changes, mistakes, evals, history, github, diagnostics)


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".metrics-", delete=False) as file:
            name = file.name
            file.write(data)
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute lab indicators from read-only evidence")
    parser.add_argument("--json", choices=["-"], help="JSON to stdout without writing")
    args = parser.parse_args(argv)
    snapshot = collect(ROOT)
    indicators = compute(snapshot)
    data = render_document(snapshot.head, indicators, snapshot.diagnostics)
    if args.json == "-":
        try:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except BrokenPipeError:
            # A bounded preview consumer may close stdout early.
            sys.stdout = open(os.devnull, "w")
        return 0
    atomic_write(ROOT / "site/data/metrics.json", data)
    document = json.loads(data)
    unavailable = sum(not i.available for i in indicators)
    print(f"metrics: {len(indicators)} indicators, {unavailable} unavailable, {document['diagnostics'].get('skipped', 0)} skipped")
    return 0
