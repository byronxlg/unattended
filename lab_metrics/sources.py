"""Read-only evidence collection with bounded subprocesses."""
import json
import math
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from .models import GitHubSnapshot, Head, SourceResult

FAILURES = ("failure", "timed_out", "action_required", "startup_failure")

NZ = ZoneInfo("Pacific/Auckland")
USAGE = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
         "output_tokens", "reasoning_output_tokens")


def timestamp(value, result=None):
    if value is None:
        return None
    try:
        dt = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError()
        dt = dt.astimezone(timezone.utc)
        dt.astimezone(NZ)
        return dt.isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError, AttributeError, OverflowError):
        if result is not None:
            result.warn("invalid_timestamp")
        return None


def number(value, result=None, integer=False):
    if value is None:
        return None
    try:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError()
        n = float(value)
        if not math.isfinite(n) or n < 0 or (integer and not n.is_integer()):
            raise ValueError()
        return int(n) if integer else n
    except (ValueError, TypeError, OverflowError):
        if result is not None:
            result.warn("invalid_number")
        return None


def day(value):
    stamp = timestamp(value)
    return datetime.fromisoformat(stamp).astimezone(NZ).date().isoformat() if stamp else None


def normalize(row, result, depth=0):
    if depth > 20:
        result.warn("excessive_nesting")
        return {}
    out = {}
    for key, value in row.items():
        if key in ("last_message", "result", "notes", "_invalid_fields"):
            continue
        if key in ("usage", "rate_limits", "supervisor", "head", "app", "user", "check_suite") and value is not None and not isinstance(value, dict):
            result.warn("invalid_" + key)
            out[key] = None
            continue
        if key in ("occurrences", "reasons", "prs") and value is not None and not isinstance(value, list):
            result.warn("invalid_" + key)
            out[key] = []
            continue
        if key in ("ran", "killed", "passed", "plan_match") and value is not None and not isinstance(value, bool):
            result.warn("invalid_" + key)
            out[key] = None
            continue
        if key in ("kind", "change", "outcome", "origin", "eval", "name", "state", "status", "conclusion", "sha", "merge_commit_sha", "body", "html_url") and value is not None and not isinstance(value, str):
            result.warn("invalid_" + key)
            out[key] = None
            continue
        if key in ("started", "ended", "ts", "incident_at", "submitted_at", "created_at",
                   "closed_at", "merged_at", "started_at", "completed_at", "updated_at",
                   "run_started_at", "committed_at", "detected_at"):
            out[key] = timestamp(value, result)
            if value is not None and out[key] is None:
                out.setdefault("_invalid_fields", []).append(key)
        elif key in ("duration_s", "duration_ms", "cost_usd", "used_percent") or key in USAGE:
            out[key] = number(value, result)
        elif key in ("attempts", "turns", "jobs_running", "window_minutes", "resets_at",
                     "number", "run_attempt"):
            out[key] = number(value, result, integer=True)
        elif isinstance(value, dict):
            out[key] = normalize(value, result, depth+1)
        elif isinstance(value, list):
            out[key] = [normalize(v, result, depth+1) if isinstance(v, dict) else v for v in value]
        else:
            out[key] = value
    return out


def records(rows, identity, result=None):
    result = result if result is not None else SourceResult()
    seen, conflicts = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            result.skipped += 1
            result.warn("invalid_record")
            continue
        ident = row.get(identity)
        if (isinstance(ident, bool) or not isinstance(ident, (str, int)) or not str(ident)
                or (identity == "slug" and (not isinstance(ident, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", ident)))):
            result.skipped += 1
            result.warn("missing_identity")
            continue
        record = normalize(row, result)
        if ident in seen:
            result.skipped += 1
            if seen[ident] != record:
                conflicts.add(ident)
                result.warn("conflicting_identity")
        seen[ident] = record
    result.skipped += len(conflicts)
    result.data = [seen[k] for k in sorted(seen, key=str) if k not in conflicts]
    return result


def read_jsonl(path, identity, optional=False, dedup=True):
    result = SourceResult()
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        if optional:
            return SourceResult(False, "missing optional evidence")
        raise
    rows = []
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (ValueError, RecursionError):
            result.skipped += 1
            result.warn("invalid_json")
            continue
        if not dedup and isinstance(row, dict) and row.get(identity):
            row["_line"] = line_no
            row["_identity"] = str(line_no)
        rows.append(row)
    return records(rows, identity if dedup else "_identity", result)


def read_jobs(path):
    return read_jsonl(path, "id")


def read_ticks(path):
    return read_jsonl(path, "ts", dedup=False)


def read_mistakes(path):
    return read_jsonl(path, "mistake", dedup=False)


def read_evals(path):
    return read_jsonl(path, "eval", optional=True, dedup=False)


def read_changes(path):
    try:
        doc = yaml.safe_load(path.read_text())
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        raise ValueError("malformed changes YAML") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("changes"), list):
        raise ValueError("changes YAML requires a changes list")
    result = records(doc["changes"], "slug")
    for row in result.data:
        prs = row.get("prs", [])
        if not isinstance(prs, list):
            result.warn("invalid_prs")
            prs = []
        valid = [number(p, result, integer=True) for p in prs]
        row["prs"] = sorted({p for p in valid if p is not None and p > 0})
    return result


def git(root, args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True, timeout=8).stdout


def read_head(root):
    parts = git(root, ["show", "-s", "--format=%H%x09%cI", "HEAD"]).strip().split("\t")
    if len(parts) != 2:
        return Head("", None)
    sha, stamp = parts
    return Head(sha if re.fullmatch("[0-9a-fA-F]+", sha) else "", timestamp(stamp))


def read_artifact_history(root, slugs):
    result = SourceResult()
    try:
        ordered = git(root, ["rev-list", "--reverse", "--topo-order", "HEAD"]).splitlines()
    except (OSError, subprocess.SubprocessError):
        return SourceResult(False, "git history unavailable")
    positions = {sha: i for i, sha in enumerate(ordered)}
    valid_slugs = []
    for slug in slugs:
        if not isinstance(slug, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
            result.warn("invalid_slug")
        else:
            valid_slugs.append(slug)
    for slug in sorted(set(valid_slugs)):
        for artifact in ("intent", "spec", "plan"):
            path = f"intent/{slug}/{artifact}.md"
            try:
                args = ["log", "HEAD", "--reverse", "--topo-order", "--format=%H%x09%cI"]
                additions = git(root, [*args, "--diff-filter=A", "--", path]).splitlines()
                touches = git(root, [*args, "--", path]).splitlines()
            except (OSError, subprocess.SubprocessError):
                return SourceResult(False, "git history unavailable")
            first = additions[0].split("\t")[0] if additions else None
            seen = set()
            for order, line in enumerate(touches):
                parts = line.split("\t")
                if len(parts) != 2:
                    result.warn("invalid_git_record")
                    continue
                sha, stamp = parts
                if sha in seen:
                    continue
                seen.add(sha)
                result.data.append(dict(slug=slug, artifact=artifact, sha=sha,
                                        committed_at=timestamp(stamp, result),
                                        added=sha == first, order=positions.get(sha, order)))
    return result


class Client:
    def __init__(self, repo, deadline):
        self.repo, self.deadline = repo, deadline
        self.cache = {}
        self.stopped = None

    def read(self, endpoint, collection=None, identity="id"):
        if endpoint in self.cache:
            return self.cache[endpoint]
        result = self._read(endpoint, collection, identity)
        self.cache[endpoint] = result
        return result

    def _read(self, endpoint, collection, identity):
        if self.stopped:
            return SourceResult(False, self.stopped)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            return SourceResult(False, "github budget exhausted")
        endpoint += ("&" if "?" in endpoint else "?") + "per_page=100"
        try:
            proc = subprocess.run(["gh", "api", "--method", "GET",
                                   f"/repos/{self.repo}/{endpoint}", "--paginate", "--slurp"],
                                  capture_output=True, text=True, timeout=min(8, remaining))
        except FileNotFoundError:
            self.stopped = "gh missing"
            return SourceResult(False, self.stopped)
        except subprocess.TimeoutExpired:
            self.stopped = "github timeout"
            return SourceResult(False, self.stopped)
        except OSError:
            self.stopped = "github process unavailable"
            return SourceResult(False, self.stopped)
        if proc.returncode:
            error = proc.stderr.lower()
            reason = ("github authentication unavailable" if "auth" in error or "401" in error
                      else "github rate exhausted" if "rate limit" in error
                      else "github permission denied" if "403" in error
                      else "github unavailable")
            self.stopped = reason
            return SourceResult(False, reason)
        try:
            pages = json.loads(proc.stdout)
            if not isinstance(pages, list) or not pages:
                raise ValueError()
            rows = []
            for page in pages:
                data = page.get(collection) if collection and isinstance(page, dict) else page
                if not isinstance(data, list):
                    raise ValueError()
                for row in data:
                    if not isinstance(row, dict) or not isinstance(row.get(identity), int) or isinstance(row.get(identity), bool):
                        raise ValueError()
                rows.extend(data)
        except (ValueError, TypeError, RecursionError):
            return SourceResult(False, "invalid github pages")
        return records(rows, identity)


def read_prs(repo, deadline):
    return Client(repo, deadline).read("pulls?state=all", identity="number")


def read_reviews(repo, number, deadline):
    return Client(repo, deadline).read(f"pulls/{number}/reviews")


def read_review_comments(repo, number, deadline):
    return Client(repo, deadline).read(f"pulls/{number}/comments")


def read_checks(repo, sha, deadline):
    return Client(repo, deadline).read(f"commits/{sha}/check-runs?filter=all", "check_runs")


def read_workflow_runs(repo, workflow, deadline):
    return Client(repo, deadline).read(f"actions/workflows/{workflow}/runs", "workflow_runs")


def read_run_jobs(repo, run_id, deadline):
    return Client(repo, deadline).read(f"actions/runs/{run_id}/jobs?filter=all", "jobs")


def read_gates(repo, deadline):
    result = Client(repo, deadline).read("issues?state=all&labels=needs-byron", identity="number")
    result.data = [r for r in result.data if "pull_request" not in r]
    return result


def read_github(repo, pr_numbers, deadline):
    client = Client(repo, deadline)
    snap = GitHubSnapshot()

    def batch(specs):
        # Deduplicating endpoint work also avoids concurrent cache writes for shared heads.
        unique = list(dict.fromkeys((endpoint, collection, identity)
                                    for key, endpoint, collection, identity in specs))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = {}
            for offset in range(0, len(unique), 2):
                chunk = unique[offset:offset+2]
                if client.stopped or time.monotonic() >= deadline:
                    reason = client.stopped or "github budget exhausted"
                    results.update({item: SourceResult(False, reason) for item in unique[offset:]})
                    break
                futures = [(item, pool.submit(client.read, *item)) for item in chunk]
                for item, future in futures:
                    results[item] = future.result()
        for key, endpoint, collection, identity in specs:
            snap.sources[key] = results[endpoint, collection, identity]

    batch([
        ("prs", "pulls?state=all", None, "number"),
        ("gates", "issues?state=all&labels=needs-byron", None, "number"),
        ("ci.yml", "actions/workflows/ci.yml/runs", "workflow_runs", "id"),
        ("pages.yml", "actions/workflows/pages.yml/runs", "workflow_runs", "id"),
    ])
    details = []
    for pr in snap.get("prs").data:
        n = pr["number"]
        if n not in pr_numbers:
            continue
        details.extend([(f"reviews:{n}", f"pulls/{n}/reviews", None, "id"),
                        (f"comments:{n}", f"pulls/{n}/comments", None, "id")])
        head = pr.get("head")
        sha = head.get("sha") if isinstance(head, dict) else None
        if isinstance(sha, str) and re.fullmatch("[0-9a-fA-F]+", sha):
            details.append((f"checks:{n}", f"commits/{sha}/check-runs?filter=all", "check_runs", "id"))
    for run in snap.get("pages.yml").data:
        if run.get("conclusion") not in FAILURES:
            continue
        details.append((f"jobs:{run['id']}", f"actions/runs/{run['id']}/jobs?filter=all", "jobs", "id"))
    batch(details)
    snap.get("gates").data = [r for r in snap.get("gates").data if "pull_request" not in r]
    return snap
