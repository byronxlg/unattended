"""Stable declared reports without live service observations."""
import json
from dataclasses import fields, is_dataclass

from .models import Absent, Known, Observation, Unknown, Unsupported


def serialize(value):
    if isinstance(value, Known):
        return {"status": "known", "value": serialize(value.value)}
    if isinstance(value, (Absent, Unknown, Unsupported)):
        result = {"status": type(value).__name__.lower(), "value": None, "reason": value.reason}
        if isinstance(value, Unsupported):
            result["raw"] = serialize(value.raw)
        return result
    if is_dataclass(value):
        return {f.name: serialize(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(v) for v in value]
    return value


def build_report(registry, domain):
    jobs = []
    for job in sorted(registry.jobs, key=lambda j: (j.project.project, j.registry.id, j.plist_path)):
        item = serialize(job)
        item["observations"] = {name: serialize(obs) for name, obs in job.observations}
        for name in ("service", "override", "output", "receipt"):
            item["observations"][name] = serialize(Observation("not_requested", None, (), None, None, None))
        item["reason"] = ("invalid registry or plist join" if registry.errors else
                          f"joined plist {job.plist_path}; live state not observed")
        item["evidence_refs"] = [name for name, _ in job.observations]
        jobs.append(item)
    return {"schema_version": 1, "command": "declared", "domain": domain,
            "observed_at": registry.discovery.observed_at, "jobs": jobs,
            "issues": serialize(registry.errors),
            "summary": {"jobs": len(jobs), "verdicts": {"declared": len(jobs)},
                        "drift_findings": 0, "uncertainties": 0, "invalid_input_errors": len(registry.errors)},
            "exit_code": 3 if registry.errors or not jobs else 0}


def escaped(text):
    return json.dumps(str(text), ensure_ascii=True)[1:-1]


def render_text(report):
    lines = []
    for job in report["jobs"]:
        identity = job["identity"]
        lines.append(f"{escaped(job['project']['project'])}/{escaped(job['registry']['id'])} "
                     f"{escaped(identity['domain'])}/{escaped(identity['label'])} declared: {escaped(job['reason'])}")
    lines.append(f"summary: {len(report['jobs'])} declared, {len(report['issues'])} invalid-input errors")
    return "\n".join(lines)


def render_json(report):
    return json.dumps(report, ensure_ascii=True, sort_keys=True)
