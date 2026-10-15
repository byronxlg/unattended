"""Stable declaration and audit reports with explicit exit precedence."""
import json
import base64
from dataclasses import fields, is_dataclass

from .models import Absent, Known, Observation, Unknown, Unsupported


def serialize(value):
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
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
    if isinstance(registry, str):
        return audit_report(registry, domain)
    jobs = []
    for job in sorted(registry.jobs, key=lambda j: (j.project.project if j.project else 'scan', j.registry.id if j.registry else j.plist_path, j.plist_path)):
        item = serialize(job)
        item["observations"] = {name: serialize(obs) for name, obs in job.observations}
        for name in ("registry", "plist", "inventory", "service", "override", "output", "receipt"):
            item["observations"].setdefault(name, serialize(Observation("not_requested", None, (), None, None, None)))
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
        lines.append(f"{escaped(job['project']['project'] if job['project'] else 'scan')}/{escaped(job['registry']['id'] if job['registry'] else job['plist_path'])} "
                     f"{escaped(identity['domain'])}/{escaped(identity['label'] if identity['label'] is not None else 'no_label')} {escaped(job['verdict'])}: {escaped(job['reason'])}")
    if report["command"] != "declared":
        for job in report["jobs"]:
            lines.extend("drift: " + escaped(finding["reason"]) for finding in job["drift"])
            lines.extend("uncertainty: " + escaped(detail) for detail in job["uncertainties"])
        lines.extend("issue: " + escaped(issue) for issue in report["issues"])
        lines.append("summary: " + json.dumps(report["summary"], sort_keys=True))
        return "\n".join(lines)
    lines.extend('issue: ' + escaped(issue['message']) for issue in report['issues'])
    lines.append(f"summary: {len(report['jobs'])} declared, {len(report['issues'])} invalid-input errors")
    return "\n".join(lines)


def render_json(report):
    return json.dumps(report, ensure_ascii=True, sort_keys=True)


def audit_report(command, fleet):
    jobs, counts = [], {}
    for job in sorted(fleet.jobs, key=lambda j: (j.project.project if j.project else 'scan', j.registry.id if j.registry else j.plist_path, j.plist_path)):
        item = serialize(job)
        item['observations'] = {name: serialize(obs) for name, obs in job.observations}
        item['verdict'] = job.verdict.name
        item['rule_id'] = job.verdict.rule_id
        item['reason'] = job.verdict.reason
        item['evidence_refs'] = list(job.verdict.evidence_refs)
        counts[job.verdict.name] = counts.get(job.verdict.name, 0) + 1
        jobs.append(item)
    report = {'schema_version': 1, 'command': command, 'domain': fleet.domain,
              'observed_at': fleet.observed_at, 'jobs': jobs, 'issues': list(fleet.coverage.issues) or ([] if fleet.coverage.complete else ['incomplete coverage']),
              'summary': {'jobs': len(jobs), 'verdicts': counts,
                          'drift_findings': sum(len(j.drift) for j in fleet.jobs),
                          'uncertainties': sum(len(j.uncertainties) + (j.verdict.name == 'cannot_determine') for j in fleet.jobs),
                          'invalid_input_errors': 0}}
    report['exit_code'] = exit_code(report)
    return report


def exit_code(report):
    if report['summary'].get('invalid_input_errors', 0):
        return 3
    if any(isinstance(issue, dict) and issue.get('exit_code') == 3 for issue in report['issues']):
        return 3
    if any(isinstance(issue, dict) and issue.get('exit_code') == 1 for issue in report['issues']):
        return 1
    definite = {'failing', 'late', 'declared_not_loaded', 'loaded_disabled'}
    for job in report['jobs']:
        if job['verdict'] in definite or job['drift'] or (job['verdict'] == 'disabled' and (job['registry'] or {}).get('expected_enabled') is True):
            return 1
    if not report['jobs'] or report['issues'] or report['summary'].get('uncertainties', 0):
        return 2
    if any(job['verdict'] not in ('running', 'healthy_idle', 'disabled') or
           job['verdict'] == 'disabled' and (job['registry'] or {}).get('expected_enabled') is not False for job in report['jobs']):
        return 2
    return 0


def audit_fleet(fleet, files):
    from dataclasses import replace
    from .drift import compare_job
    from .output import observe_job
    from .verdicts import evaluate
    jobs = []
    for original in fleet.jobs:
        job = observe_job(original, files)
        comparisons, drift = compare_job(job)
        incomplete = tuple(f'{c.field}: {c.pair} comparison unknown' for c in comparisons if c.status == 'unknown')
        job = replace(job, comparisons=comparisons, drift=drift, uncertainties=job.uncertainties + incomplete)
        verdict = evaluate(job, fleet.coverage, 'audit')
        contract = job.registry.output
        ancillary = []
        if contract is not None:
            evidence = dict(job.observations).get('receipt' if contract.kind == 'ticks_jsonl' else 'output')
            if evidence is not None and evidence.data is not None:
                ancillary.extend(getattr(evidence.data, 'parsing_errors', ()))
                if evidence.data.age_seconds is None:
                    ancillary.append('unavailable or invalid evidence timestamp')
                if evidence.data.age_seconds is not None and evidence.data.age_seconds < 0:
                    ancillary.append('future evidence timestamp')
        jobs.append(replace(job, verdict=verdict, uncertainties=tuple(dict.fromkeys(job.uncertainties + tuple(ancillary)))))
    return replace(fleet, jobs=tuple(jobs))
