"""Pure calculations. Missing evidence never becomes a successful zero."""
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean
import re
import math

from .models import Indicator
from .sources import FAILURES, NZ, USAGE, day, number, timestamp



def mapping(value):
    return value if isinstance(value, dict) else {}


def sequence(value):
    return value if isinstance(value, list) else []


def text(value):
    return value if isinstance(value, str) else ""


def dt(value):
    stamp = timestamp(value)
    return datetime.fromisoformat(stamp) if stamp else None


def week(value):
    stamp = dt(value)
    if not stamp:
        return None
    year, wk, _ = stamp.astimezone(NZ).isocalendar()
    return f"{year}-W{wk:02}"


def compute(snapshot):
    s = snapshot
    out = []
    diagnostics = s.diagnostics
    diagnostics["calculation"] = {}
    counts = diagnostics["calculation"]

    def warn(code):
        counts[code] = counts.get(code, 0) + 1

    def delta(start, end, divisor=3600):
        a, b = dt(start), dt(end)
        if a is None or b is None:
            return None
        value = (b-a).total_seconds()/divisor
        if value < 0:
            warn("negative_interval")
            return None
        return value

    def series(samples, mode="mean", key="date"):
        buckets = defaultdict(list)
        for value, stamp in samples:
            date = week(stamp) if key == "week" else day(stamp)
            if date and value is not None:
                buckets[date].append(value)
        return [{key: date, "value": (sum(values) if mode == "sum" else
                 100*sum(values)/len(values) if mode == "percent" else mean(values)),
                 "n": len(values), "available": True, "note": ""}
                for date, values in sorted(buckets.items())]

    def emit(stage, name, definition, unit, samples=(), mode="mean",
             deps=(), note="", kind="lagging", available=True, reason="", dated=True):
        samples = [(v, t) for v, t in samples if v is not None]
        unavailable = [d.reason for d in deps if not d.available]
        available = available and not unavailable
        if not available:
            samples = []
            note = "not shown: " + (reason or "; ".join(sorted(set(unavailable))))
        n = len(samples)
        values = [v for v, _ in samples]
        value = (sum(values) if mode == "sum" else 100*sum(values)/len(values) if mode == "percent"
                 else mean(values)) if values else None
        if value is not None and not math.isfinite(value):
            warn("aggregate_overflow")
            value, n, available = None, 0, False
            note = "not shown: aggregate overflow"
        if available and not n:
            note = (note + "; " if note else "") + "no data (n=0)"
        skipped = sum(d.skipped + sum(d.warnings.values()) for d in deps)
        if skipped:
            note += f"; source diagnostics: {skipped}"
        ind = Indicator(stage, kind, name, definition, value, unit, n,
                        available, note, series(samples, mode) if dated and available else [])
        out.append(ind)
        return ind

    jobs, changes = s.jobs.data, s.changes.data
    fixes = defaultdict(list)
    for job in jobs:
        slug = text(job.get("change"))
        if job.get("kind") == "fix" and slug:
            fixes[slug].append(job)
    diagnostics["unattributed_jobs"] = sum(not text(j.get("change")) for j in jobs)
    hist = defaultdict(list)
    for record in s.history.data:
        hist[(text(record.get("slug")), text(record.get("artifact")))].append(record)

    def first(slug, artifact):
        adds = [r for r in hist[slug, artifact] if r.get("added") is True]
        return min(adds, key=lambda r: r.get("order", 0)) if adds else {}

    def stamp(slug, artifact):
        return first(slug, artifact).get("committed_at")

    def edits(slug, artifact, boundary):
        origin = first(slug, boundary)
        if not origin or not hist[slug, artifact]:
            return None
        # History order, not timestamps, decides the boundary even with skewed clocks.
        order = origin.get("order", 0)
        return len({text(r.get("sha")) for r in hist[slug, artifact]
                    if r.get("order", 0) > order and r.get("sha") != origin.get("sha")})

    emit("Plan", "conversation_to_intent", "First intent addition minus recorded conversation start",
         "hours", [(delta(c.get("started"), stamp(c["slug"], "intent")), stamp(c["slug"], "intent"))
                   for c in changes], deps=(s.changes, s.history), kind="leading")
    accepted = ("accepted", "building", "in_review", "merged", "reverted")
    emit("Plan", "intent_survival", "Accepted / decided intents, excluding open",
         "percent", [(int(c.get("outcome") in accepted), None) for c in changes
                     if c.get("outcome") in (*accepted, "closed")],
         mode="percent", deps=(s.changes,), dated=False)
    emit("Plan", "intent_changes_after_spec", "Distinct intent touches after first spec addition",
         "commits/change", [(edits(c["slug"], "intent", "spec"), None) for c in changes],
         deps=(s.changes, s.history), dated=False)
    emit("Design", "intent_to_spec", "First spec addition minus first intent addition",
         "hours", [(delta(stamp(c["slug"], "intent"), stamp(c["slug"], "spec")), stamp(c["slug"], "spec"))
                   for c in changes], deps=(s.changes, s.history), kind="leading")
    emit("Design", "spec_rework", "Distinct spec touches after first plan addition",
         "commits/change", [(edits(c["slug"], "spec", "plan"), None) for c in changes],
         deps=(s.changes, s.history), dated=False)

    attempts = [(c, number(c.get("attempts"), integer=True)) for c in changes]
    attempts = [(c, n) for c, n in attempts if n is not None and n >= 1]
    emit("Build", "first_pass_merge", "Merged changes with one attempt / merged changes with attempts",
         "percent", [(int(n == 1), None) for c, n in attempts if c.get("outcome") == "merged"],
         mode="percent", deps=(s.changes,), dated=False, kind="leading")
    prs_source = s.github.get("prs")
    linked = {p for c in changes for p in sequence(c.get("prs")) if isinstance(p, int) and not isinstance(p, bool)}
    prs = {p["number"]: p for p in prs_source.data if p.get("number") in linked}

    def final(c):
        numbers = sequence(c.get("prs"))
        if not numbers or any(not isinstance(p, int) or isinstance(p, bool) or p not in prs
                              or not timestamp(prs[p].get("merged_at")) for p in numbers):
            return None
        return max((prs[p]["merged_at"] for p in numbers), key=dt)

    completed = [(c, final(c)) for c in changes if c.get("outcome") in ("merged", "reverted")]
    completed = [(c, end) for c, end in completed if end]
    emit("Build", "plan_to_final_merge", "Final linked merge minus first plan addition (approval proxy)",
         "hours", [(delta(stamp(c["slug"], "plan"), end), end) for c, end in completed if c.get("outcome") == "merged"],
         deps=(s.changes, s.history, prs_source), kind="leading")
    rework = {c["slug"]: n-1+len(fixes[c["slug"]]) for c, n in attempts}
    cycles = emit("Build", "rework_cycles", "Attempts minus one plus distinct fix jobs",
                  "cycles/change", [(v, None) for v in rework.values()], deps=(s.changes, s.jobs),
                  note="May double count review passes and inflate planned increments", dated=False)
    cycles.series = [{"change": c["slug"], "value": rework[c["slug"]], "n": 1,
                      "attempt_cycles": n-1, "fix_jobs": len(fixes[c["slug"]]),
                      "available": True, "note": ""} for c, n in attempts]
    emit("Build", "plan_match", "True explicit plan_match / recorded merged verdicts",
         "percent", [(int(c["plan_match"]), None) for c in changes
                     if c.get("outcome") == "merged" and isinstance(c.get("plan_match"), bool)],
         mode="percent", deps=(s.changes,), dated=False)
    emit("CLAUDE.md", "repeated_mistakes", "Sum of distinct occurrences beyond the first in each recorded class",
         "repeat occurrences", [(max(len({v for v in sequence(m.get("occurrences")) if isinstance(v, str)})-1, 0), m.get("ts"))
                                for m in s.mistakes.data], mode="sum", deps=(s.mistakes,),
         note="Coverage is recorded mistakes only", kind="leading")

    intervals = []
    for job in jobs:
        a, b = dt(job.get("started")), dt(job.get("ended"))
        if a and b:
            if b < a:
                warn("negative_job_interval")
            elif b > a:
                intervals.append((a, b))

    def concurrency(pairs):
        events = sorted([(a, 1) for a, b in pairs]+[(b, -1) for a, b in pairs])
        active = peak = 0
        area = union = 0.0
        previous = None
        for moment, change in events:
            elapsed = (moment-previous).total_seconds() if previous else 0
            if active:
                union += elapsed
                area += elapsed*active
            active += change
            peak = max(peak, active)
            previous = moment
        return peak, area/union if union else None

    peak, avg = concurrency(intervals)
    for name, value, definition in [("peak_jobs", peak, "Peak simultaneous active job intervals"),
                                     ("mean_jobs", avg, "Time-weighted jobs over union of active intervals")]:
        ind = emit("Parallel", name, definition, "jobs", [(value, None)] if intervals else [],
                   deps=(s.jobs,), kind="leading", dated=False)
        ind.n = len(intervals)
        daily = defaultdict(list)
        for a, b in intervals:
            cursor = a
            while cursor < b:
                local = cursor.astimezone(NZ)
                try:
                    tomorrow = datetime.combine(local.date()+timedelta(days=1), datetime.min.time(), NZ)
                except (ValueError, OverflowError):
                    warn("calendar_boundary")
                    tomorrow = b
                end = min(b, tomorrow)
                daily[local.date().isoformat()].append((cursor, end))
                cursor = end
        ind.series = [{"date": date, "value": concurrency(pairs)[0 if name == "peak_jobs" else 1],
                       "n": len(pairs), "available": True, "note": ""} for date, pairs in sorted(daily.items())]
    emit("Parallel", "review_quality_held", "Review quality during overlap", "boolean",
         available=False, reason="structured quality evidence is not shown", kind="leading")
    merged_prs = [p for p in prs.values() if timestamp(p.get("merged_at"))]
    weekly = emit("Parallel", "weekly_merges", "Distinct linked merged PRs per Pacific/Auckland ISO week",
                  "PRs/week", [(1, p["merged_at"]) for p in merged_prs], mode="sum", deps=(prs_source,))
    weekly.series = series([(1, p["merged_at"]) for p in merged_prs], "sum", "week") if weekly.available else []
    weekly.value = mean([r["value"] for r in weekly.series]) if weekly.series else None
    for name, samples, mode, unit in [
        ("weekly_completed_changes", [(1, end) for c, end in completed], "sum", "changes/week"),
        ("weekly_rework", [(rework[c["slug"]], end) for c, end in completed if c["slug"] in rework], "mean", "cycles/change")]:
        ind = emit("Parallel", name, "Completed changes grouped by final merge week", unit,
                   samples, mode=mode, deps=(prs_source, s.changes, s.jobs))
        ind.series = series(samples, mode, "week") if ind.available else []
        if mode == "sum":
            ind.value = mean([r["value"] for r in ind.series]) if ind.series else None

    built = {text(j.get("change")) for j in jobs if j.get("kind") == "build"}
    built_prs = {p for c in changes if c["slug"] in built for p in sequence(c.get("prs")) if isinstance(p, int)}
    check_deps, ci_samples = [prs_source, s.jobs], []
    for n, pr in sorted(prs.items()):
        if n not in built_prs:
            continue
        src = s.github.get(f"checks:{n}")
        check_deps.append(src)
        groups = defaultdict(list)
        invalid_group = False
        for check in src.data:
            app = text(mapping(check.get("app")).get("slug"))
            name = text(check.get("name"))
            if not app or not name or not timestamp(check.get("started_at")):
                warn("invalid_check_group")
                invalid_group = True
                continue
            groups[app, name].append(check)
        first_checks = [min(values, key=lambda r: (dt(r["started_at"]), r["id"])) for values in groups.values()]
        if not invalid_group and first_checks and all(r.get("status") == "completed" and isinstance(r.get("conclusion"), str) for r in first_checks):
            ci_samples.append((int(all(r.get("conclusion") == "success" for r in first_checks)), pr.get("created_at")))
    emit("Test", "first_pass_ci", "PRs whose earliest check in every app/name group succeeded",
         "percent", ci_samples, mode="percent", deps=check_deps, kind="leading",
         note="Final stored PR head proxy; original implementation head is not shown")
    review_deps, comment_deps = [prs_source], [prs_source]
    reviews, comments = {}, {}
    review_times, first_times = [], []
    for n, pr in sorted(prs.items()):
        rev, com = s.github.get(f"reviews:{n}"), s.github.get(f"comments:{n}")
        review_deps.append(rev)
        comment_deps.append(com)
        reviews[n] = [r for r in rev.data if r.get("state") != "PENDING" and timestamp(r.get("submitted_at"))]
        comments[n] = [r for r in com.data if r.get("in_reply_to_id") is None and timestamp(r.get("created_at"))]
        times = [r["submitted_at"] for r in reviews[n]]
        if times:
            end = min(times, key=dt)
            review_times.append((delta(pr.get("created_at"), end, 60), end))
        times += [r["created_at"] for r in comments[n]]
        if times:
            end = min(times, key=dt)
            first_times.append((delta(pr.get("created_at"), end, 60), end))
    emit("Test", "review_time", "First submitted non-pending review minus PR creation",
         "minutes", review_times, deps=review_deps,
         note="Submitted-review latency proxy; supervisor identity and effort are not recorded")

    post_fixes = {c["slug"]: [j for j in fixes[c["slug"]] if timestamp(j.get("started")) and dt(j["started"]) > dt(end)]
                  for c, end in completed}
    failure_samples = [(int(c.get("outcome") == "reverted" or bool(post_fixes[c["slug"]])), end) for c, end in completed]
    failure_deps = (prs_source, s.changes, s.jobs)
    emit("Test", "change_failure_rate", "Completed changes reverted or fixed strictly after final merge",
         "percent", failure_samples, mode="percent", deps=failure_deps,
         note="Conservative change-level proxy; pre-completion fixes excluded")

    eval_rows = s.evals.data
    emit("Evals", "eval_pass_rate", "True eval results / boolean results", "percent",
         [(int(r["passed"]), r.get("ts")) for r in eval_rows if isinstance(r.get("passed"), bool)],
         mode="percent", deps=(s.evals,), kind="leading")
    eval_groups = defaultdict(list)
    for r in eval_rows:
        if text(r.get("eval")) and timestamp(r.get("ts")):
            eval_groups[r["eval"]].append(r)
    eval_latency = []
    for rows in eval_groups.values():
        row = min(rows, key=lambda r: dt(r["ts"]))
        incidents = sorted((r["incident_at"] for r in rows if timestamp(r.get("incident_at"))), key=dt)
        if incidents:
            eval_latency.append((delta(incidents[0], row["ts"]), row["ts"]))
    emit("Evals", "incident_to_eval", "First result timestamp per eval minus incident_at",
         "hours", eval_latency, deps=(s.evals,), kind="leading")
    for name, unit in [("regressions_ci", "events"), ("regressions_after_merge", "events"), ("regressions_ci_share", "percent")]:
        emit("Evals", name, "Structured regression detection", unit, available=False, reason="no structured source yet")
    emit("Deploy", "first_review", "Earliest submitted review or root comment minus PR creation",
         "minutes", first_times, deps=review_deps+comment_deps, kind="leading",
         note="Same-supervisor-run creation and review can yield minutes by construction; not independent response speed")
    emit("Deploy", "human_free_resolution", "Comments resolved without human branch edits", "percent",
         available=False, reason="REST comments do not establish resolution or branch-editor identity", kind="leading")
    emit("Deploy", "agent_resolution_proxy", "Merged commented PRs / PRs with root review comments",
         "percent", [(int(bool(prs[n].get("merged_at"))), None) for n in comments if comments[n] and "merged_at" not in prs[n].get("_invalid_fields", [])],
         mode="percent", deps=comment_deps, dated=False, kind="leading",
         note="Assumes merged comments were agent-resolved; human-free editing is not verified")
    emit("Deploy", "defects_caught", "Unique defects caught before merge", "defects",
         available=False, reason="review findings lack structured severity and identity")
    emit("Deploy", "defects_escaped", "Unique defects escaped after merge", "defects",
         available=False, reason="fix jobs do not establish unique defects")
    caught = [(sum(dt(r["created_at"]) < dt(pr["merged_at"]) for r in comments.get(n, [])), pr["merged_at"])
              for n, pr in prs.items() if timestamp(pr.get("merged_at"))]
    emit("Deploy", "pre_merge_comments", "Root review comments submitted before merge (activity proxy)",
         "comments", caught, mode="sum", deps=comment_deps)
    emit("Deploy", "post_merge_fixes", "Attributed fix jobs starting after final change merge (activity proxy)",
         "jobs", [(len(post_fixes[c["slug"]]), end) for c, end in completed],
         mode="sum", deps=failure_deps)

    gates = s.github.get("gates")
    closed, opened = [], []
    for gate in gates.data:
        if "closed_at" in gate.get("_invalid_fields", []):
            continue
        end = gate.get("closed_at")
        if end:
            closed.append((delta(gate.get("created_at"), end), end))
        else:
            opened.append((delta(gate.get("created_at"), s.head.committed_at), s.head.committed_at))
        for value in (gate.get("created_at"), end):
            if timestamp(value) and s.head.committed_at and dt(value) > dt(s.head.committed_at):
                warn("gate_event_after_head")
    emit("Gates", "closed_gate_wait", "Closed needs-byron issue lifetime", "hours",
         closed, deps=(gates,), kind="leading", note="Issue lifetime proxies label-addition and gate wait")
    emit("Gates", "open_gate_age", "Open needs-byron issue age censored at HEAD time", "hours",
         opened, deps=(gates,), kind="leading", note="HEAD is a deterministic censor, not an API observation cutoff")
    ci = s.github.get("ci.yml")
    failed_runs = [r for r in ci.data if r.get("status") == "completed" and r.get("conclusion") in FAILURES]
    bodies = [text(g.get("body")) for g in gates.data]
    emit("CI/CD", "unpaged_failure_proxy", "Terminal failed CI runs without a run URL in a gate / failed CI runs",
         "percent", [(int(not any(re.search(re.escape(text(r.get("html_url"))) + r"(?![A-Za-z0-9_/])", body) for body in bodies))
                      if text(r.get("html_url")) else None, r.get("updated_at")) for r in failed_runs],
         mode="percent", deps=(ci, gates), kind="leading",
         note="Absence of a linked gate does not establish triage")
    emit("CI/CD", "human_free_triage", "Pipeline failures triaged without human intervention", "percent",
         available=False, reason="absence of paging does not establish triage", kind="leading")

    pages = s.github.get("pages.yml")
    deploy_deps, deploys = [pages], {}
    missing_details = False
    deploy_note = ("Successful Pages runs imply a successful deploy job under pages.yml's "
                   "build -> deploy dependency; run updated_at proxies deploy completed_at")
    for run in pages.data:
        if run.get("conclusion") == "cancelled":
            continue
        key = f"jobs:{run['id']}"
        if key in s.github.sources:
            src = s.github.sources[key]
            deploy_deps.append(src)
            for job in src.data:
                if job.get("name") == "deploy" and job.get("status") == "completed" and timestamp(job.get("completed_at")):
                    deploys[f"job:{job['id']}"] = {**job, "head_sha": run.get("head_sha")}
        elif run.get("conclusion") == "success":
            if timestamp(run.get("updated_at")):
                deploys[f"run:{run['id']}"] = dict(
                    id=run["id"], conclusion="success", completed_at=run["updated_at"],
                    head_sha=run.get("head_sha"))
            else:
                warn("invalid_successful_run_completion")
                missing_details = True
        elif run.get("conclusion") in FAILURES:
            missing_details = True
    deployments = sorted(deploys.values(), key=lambda r: (dt(r["completed_at"]), str(r["id"])))
    good = [d for d in deployments if d.get("conclusion") == "success"]
    dates = sorted({day(r.get("created_at")) for r in pages.data if day(r.get("created_at"))})
    frequency_samples = []
    if dates:
        cursor, last = datetime.fromisoformat(dates[0]).date(), datetime.fromisoformat(dates[-1]).date()
        daily = defaultdict(int)
        for d in good:
            daily[day(d["completed_at"])] += 1
        last = max(last, max((datetime.fromisoformat(d).date() for d in daily), default=last))
        while cursor <= last:
            frequency_samples.append((daily[cursor.isoformat()], datetime.combine(cursor, datetime.min.time().replace(hour=12), NZ).isoformat()))
            if cursor == last:
                break
            cursor += timedelta(days=1)
    emit("CI/CD", "deployment_frequency", "Successful Pages deploy jobs / observed calendar days, including zero days",
         "deployments/day", frequency_samples, deps=deploy_deps, note=deploy_note,
         available=not missing_details, reason="missing deploy evidence")
    lead = []
    for pr in merged_prs:
        sha = text(pr.get("merge_commit_sha"))
        matches = [d for d in good if sha and d.get("head_sha") == sha and dt(d["completed_at"]) >= dt(pr["merged_at"])]
        if matches:
            end = matches[0]["completed_at"]
            lead.append((delta(pr["merged_at"], end), end))
    emit("CI/CD", "deployment_lead_time", "First successful deploy of exact merge SHA minus merge",
         "hours", lead, deps=deploy_deps+[prs_source], note=deploy_note,
         available=not missing_details, reason="missing deploy evidence")
    emit("CI/CD", "dora_change_failure_rate", "Change-level failure proxy, same cohort as Test change failure rate",
         "percent", failure_samples, mode="percent", deps=failure_deps)
    episode, recovery = None, []
    for deploy in deployments:
        if deploy.get("conclusion") in FAILURES and episode is None:
            episode = deploy["completed_at"]
        elif deploy.get("conclusion") == "success" and episode is not None:
            recovery.append((delta(episode, deploy["completed_at"]), deploy["completed_at"]))
            episode = None
    emit("CI/CD", "restore_time", "First failed deploy to next successful deploy; consecutive failures form one episode",
         "hours", recovery, deps=deploy_deps,
         available=not missing_details, reason="missing deploy evidence",
         note=deploy_note + f"; pipeline recovery, not service restoration; open episodes excluded: {int(episode is not None)}")
    emit("Maintain", "breach_to_intent", "Band breach to first intent addition", "hours",
         available=False, reason="no structured source yet", kind="leading")
    findings = [c for c in changes if c.get("origin") == "finding"]
    decided = [c for c in findings if c.get("outcome") in ("merged", "closed", "reverted")]
    emit("Maintain", "findings_to_fixes", "Merged finding changes / decided finding changes", "percent",
         [(int(c.get("outcome") == "merged"), None) for c in decided],
         mode="percent", deps=(s.changes,), dated=False,
         note=f"Pending findings excluded: {len(findings)-len(decided)}")
    emit("Maintain", "repeat_incidents", "Later finding changes sharing explicit incident identifiers",
         "repeat incidents", available=False, reason="no structured source yet")

    for field in (*USAGE, "total_tokens"):
        samples = []
        for job in jobs:
            usage = mapping(job.get("usage"))
            if field == "total_tokens":
                a, b = number(usage.get("input_tokens")), number(usage.get("output_tokens"))
                value = a+b if a is not None and b is not None else None
            else:
                value = number(usage.get(field))
            samples.append((value, job.get("ended")))
        emit("Cost", field, "Reported ledger usage; resumed-thread context may overlap",
             "tokens", samples, mode="sum", deps=(s.jobs,),
             note="Total tokens = input + output; cache and reasoning are components")
    snapshots = []
    for job in jobs:
        windows = mapping(job.get("rate_limits"))
        for label in ("primary", "secondary"):
            window = mapping(windows.get(label))
            value = number(window.get("used_percent"))
            if window.get("window_minutes") == 10080 and value is not None and timestamp(job.get("ended")):
                snapshots.append((job["ended"], text(job.get("id")), value, window.get("resets_at")))
                break
    snapshots.sort(key=lambda r: (dt(r[0]), r[1]))
    window = emit("Cost", "weekly_window", "Latest observed 10080-minute window per NZ day",
                  "percent", [(r[2], r[0]) for r in snapshots], deps=(s.jobs,),
                  note="Snapshot, not consumption; reset drops are not negative usage")
    window.value = snapshots[-1][2] if snapshots else None
    latest, sample_counts = {}, defaultdict(int)
    for ended, ident, value, resets in snapshots:
        date = day(ended)
        sample_counts[date] += 1
        latest[date] = {"date": date, "value": value, "resets_at": resets,
                        "available": True, "note": ""}
    window.series = [{**row, "n": sample_counts[date]} for date, row in sorted(latest.items())]
    for field, unit in (("cost_usd", "USD"), ("turns", "turns")):
        samples, runs = [], []
        for tick in s.ticks.data:
            supervisor = mapping(tick.get("supervisor"))
            if supervisor.get("ran") is True:
                value = number(supervisor.get(field))
                if value is not None:
                    samples.append((value, tick.get("ts")))
                    runs.append({"ts": tick.get("ts"), "line": tick.get("_line"),
                                 "value": value, "n": 1, "available": True, "note": ""})
        ind = emit("Cost", f"supervisor_{field}", "Mean per reported run, including failed and zero-valued runs",
                   unit, samples, deps=(s.ticks,))
        ind.series = series(samples, "sum")
        detail = emit("Cost", f"supervisor_{field}_runs", "Reported supervisor values keyed by timestamp and source line",
                      unit, samples, deps=(s.ticks,), mode="sum")
        detail.series = sorted(runs, key=lambda r: (timestamp(r["ts"]) is not None, dt(r["ts"]), r["line"] or 0))
    wall = emit("Cost", "wall_time", "Final linked merge minus change started, not summed job time",
                "hours/change", [(delta(c.get("started"), end), end) for c, end in completed],
                deps=(s.changes, prs_source))
    per_change = []
    for c, end in completed:
        value = delta(c.get("started"), end)
        if value is not None:
            per_change.append({"change": c["slug"], "value": value, "n": 1, "available": True, "note": ""})
    detail = emit("Cost", "wall_time_by_change", "Elapsed wall time per completed change",
                  "hours/change", [(r["value"], None) for r in per_change], deps=(s.changes, prs_source))
    detail.series = per_change if detail.available else []
    durations = defaultdict(list)
    for job in jobs:
        value = number(job.get("duration_s"))
        slug = text(job.get("change"))
        if value is not None and slug:
            durations[slug].append(value)
    job_time = emit("Cost", "job_time", "Sum of valid attributed job durations, distinct from elapsed wall time",
                    "job-seconds", [(v, j.get("ended")) for j in jobs
                                    if text(j.get("change")) and (v := number(j.get("duration_s"))) is not None],
                    mode="sum", deps=(s.jobs,))
    job_time.series = [{"change": slug, "value": sum(values), "n": len(values),
                        "available": True, "note": ""} for slug, values in sorted(durations.items())]
    return out
