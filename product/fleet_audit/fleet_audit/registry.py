"""Strict version-one declarations and disk plist joins."""
import re
import unicodedata
from dataclasses import replace
from datetime import date
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, TagToken

from .files import LIMIT, FileSource
from .models import (Absent, Declaration, Identity, JobRecord, Known, Observation,
                     OutputContract, Project, RegistryResult, Schedule, ValidationError)
from .plists import observe_plist


class RejectedScalar:
    """A YAML implicit type outside the schema scalar vocabulary."""


class Scalar(str):
    def __new__(cls, value, style):
        result = super().__new__(cls, value)
        result.style = style
        return result


def restricted_yaml(text):
    for token in yaml.scan(text, Loader=yaml.BaseLoader):
        if isinstance(token, AliasToken):
            raise ValueError("aliases are not allowed")
        if isinstance(token, TagToken):
            raise ValueError("tags are not allowed")

    def convert(node):
        if isinstance(node, MappingNode):
            result = {}
            for key, value in node.value:
                key = convert(key)
                if not isinstance(key, str):
                    raise ValueError("mapping keys must be strings")
                if key in result:
                    raise ValueError(f"duplicate key {key}")
                result[key] = convert(value)
            return result
        if isinstance(node, SequenceNode):
            return [convert(value) for value in node.value]
        if not isinstance(node, ScalarNode):
            raise ValueError("expected mapping")
        value = node.value
        if node.style is None:
            if value.lower() in ("null", "~", ""):
                raise ValueError("nulls are not allowed")
            if value in ("true", "false"):
                return value == "true"
            if re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
                return int(value)
            for tag, pattern in yaml.SafeLoader.yaml_implicit_resolvers.get(value[:1], []):
                if tag != "tag:yaml.org,2002:str" and pattern.match(value):
                    return RejectedScalar()
        return Scalar(value, node.style)

    return convert(yaml.compose(text, Loader=yaml.BaseLoader))


def controls(value):
    return any(unicodedata.category(c) == "Cc" for c in value)


def valid_path(value):
    return (isinstance(value, str) and value.startswith("/") and not controls(value)
            and (value == "/" or all(p not in ("", ".", "..") for p in value[1:].split("/"))))


def calendar_error(value):
    alternatives = value if isinstance(value, list) else [value]
    if not alternatives or any(not isinstance(v, dict) for v in alternatives):
        return "expected calendar mapping or nonempty list"
    bounds = {"Minute": (0, 59), "Hour": (0, 23), "Day": (1, 31), "Weekday": (0, 7), "Month": (1, 12)}
    for item in alternatives:
        if not item:
            return "calendar mapping must not be empty"
        for key, val in item.items():
            if key not in bounds:
                return f"unknown calendar field {key}"
            low, high = bounds[key]
            if type(val) is not int or not low <= val <= high:
                return f"expected {key} integer in {low}..{high}"
    return None


def freeze_calendar(value):
    return tuple(tuple(sorted(v.items())) for v in (value if isinstance(value, list) else [value]))


def empty_discovery():
    return Observation("not_requested", None, (), None, None, None)


class Validator:
    def __init__(self, path, uid):
        self.path, self.uid, self.errors = path, uid, []

    def error(self, field, message, code="schema"):
        self.errors.append(ValidationError(self.path, field, code, f"{self.path}:{field}: {message}"))

    def mapping(self, value, field, allowed, required):
        if not isinstance(value, dict):
            self.error(field, "expected mapping")
            return False
        for key in value:
            if key not in allowed:
                self.error(f"{field}.{key}" if field else key, "unknown field")
        for key in required:
            if key not in value:
                self.error(f"{field}.{key}" if field else key, "required field missing")
        return True

    def check(self, obj, key, prefix, predicate, message):
        if key in obj and not predicate(obj[key]):
            self.error(f"{prefix}.{key}" if prefix else key, message)

    def schedule(self, obj, field):
        allowed = ("interval_seconds", "calendar", "timezone", "keep_alive", "run_at_load")
        if not isinstance(obj, dict):
            self.error(field, "expected schedule mapping")
            return
        self.mapping(obj, field, allowed, ())
        if not any(k in obj for k in ("interval_seconds", "calendar", "keep_alive", "run_at_load")):
            self.error(field, "expected at least one schedule expectation")
        self.check(obj, "interval_seconds", field, positive, "expected positive integer")
        for key in ("keep_alive", "run_at_load"):
            self.check(obj, key, field, boolean, "expected boolean")
        if "calendar" in obj:
            error = calendar_error(obj["calendar"])
            if error:
                self.error(field + ".calendar", error)
            if obj.get("timezone") != "local":
                self.error(field + ".timezone", "calendar requires timezone local")
        elif "timezone" in obj:
            self.error(field + ".timezone", "timezone requires calendar")

    def output(self, obj, field):
        if not isinstance(obj, dict):
            self.error(field, "expected evidence mapping")
            return
        self.mapping(obj, field, ("path", "kind", "max_age_seconds", "mtime_sufficient"),
                     ("path", "kind", "max_age_seconds"))
        self.check(obj, "path", field, valid_path, "expected absolute normalized path")
        self.check(obj, "kind", field, lambda v: v in ("mtime", "ticks_jsonl"), "expected mtime or ticks_jsonl")
        self.check(obj, "max_age_seconds", field, positive, "expected positive integer")
        self.check(obj, "mtime_sufficient", field, boolean, "expected boolean")
        if obj.get("mtime_sufficient") is True and obj.get("kind") != "mtime":
            self.error(field + ".mtime_sufficient", "mtime_sufficient requires kind mtime")

    def validate(self, obj):
        required = ("schema_version", "project", "owner", "reviewed", "jobs")
        if not self.mapping(obj, "", required + ("tier", "lifecycle"), required):
            return
        self.check(obj, "schema_version", "", lambda v: type(v) is int and v == 1, "expected schema_version 1")
        self.check(obj, "project", "", slug, "expected project slug")
        self.check(obj, "owner", "", lambda v: isinstance(v, str) and bool(v.strip()), "expected nonblank owner")
        self.check(obj, "tier", "", lambda v: v in ("critical", "standard", "experimental"),
                   "expected critical, standard, or experimental")
        self.check(obj, "lifecycle", "", lambda v: v in ("active", "paused", "retired"),
                   "expected active, paused, or retired")
        self.check(obj, "reviewed", "", reviewed, "expected valid YYYY-MM-DD string")
        if "jobs" not in obj:
            return
        if not isinstance(obj["jobs"], list):
            self.error("jobs", "expected list")
            return
        if not obj["jobs"]:
            self.error("jobs", "expected nonempty job list")
        ids = set()
        for index, job in enumerate(obj["jobs"]):
            field = f"jobs[{index}]"
            required = ("id", "label", "plist_path", "expected_program", "expected_arguments")
            allowed = required + ("scheduler", "host", "domain", "expected_working_directory",
                                  "expected_schedule", "expected_enabled", "output", "grace_seconds")
            if not self.mapping(job, field, allowed, required):
                continue
            self.check(job, "id", field, slug, "expected job slug")
            if slug(job.get("id")):
                if job["id"] in ids:
                    self.error(field + ".id", f"duplicate job id {job['id']}", "duplicate")
                ids.add(job["id"])
            self.check(job, "scheduler", field, lambda v: v == "launchd", "only launchd is supported")
            self.check(job, "host", field, lambda v: v == "local", "only local host is supported")
            self.check(job, "domain", field, lambda v: v == f"gui/{self.uid}", f"expected current-user gui/{self.uid}")
            self.check(job, "label", field, valid_label, "expected launchd label")
            for key in ("plist_path", "expected_program", "expected_working_directory"):
                self.check(job, key, field, valid_path, "expected absolute normalized path")
            if "expected_arguments" in job:
                argv = job["expected_arguments"]
                if not isinstance(argv, list) or not argv or any(not isinstance(a, str) for a in argv):
                    self.error(field + ".expected_arguments", "expected nonempty argv array")
                elif any(controls(a) for a in argv):
                    self.error(field + ".expected_arguments", "argv contains control character")
            self.check(job, "expected_enabled", field, boolean, "expected boolean")
            self.check(job, "grace_seconds", field, lambda v: type(v) is int and v >= 0, "expected nonnegative integer")
            if "grace_seconds" in job and "output" not in job:
                self.error(field + ".grace_seconds", "grace_seconds requires output")
            if "expected_schedule" in job:
                self.schedule(job["expected_schedule"], field + ".expected_schedule")
            if "output" in job:
                self.output(job["output"], field + ".output")


def positive(value):
    return type(value) is int and value > 0


def boolean(value):
    return type(value) is bool


def slug(value):
    return isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value) is not None


def valid_label(value):
    return isinstance(value, str) and bool(value) and not controls(value) and not any(c.isspace() or c == "/" for c in value)


def reviewed(value):
    if not isinstance(value, Scalar) or value.style not in ("'", '"') or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def expectation(obj, key):
    return Known(obj[key]) if key in obj else Absent("no expectation")


def parse_frontmatter(path: str, content: bytes, uid: int) -> RegistryResult:
    validator = Validator(path, uid)
    discovery = empty_discovery()
    try:
        text = content.decode("utf-8")
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            if lines and lines[0].startswith("---"):
                raise ValueError("opening delimiter must be ---")
            return RegistryResult((), (), discovery)
        if "---" not in lines[1:]:
            raise ValueError("closing delimiter missing")
        obj = restricted_yaml("\n".join(lines[1:lines.index("---", 1)]))
    except (ValueError, RecursionError, yaml.YAMLError) as exc:
        validator.error("frontmatter", f"invalid frontmatter: {exc}", "frontmatter")
        return RegistryResult((), tuple(validator.errors), discovery)
    validator.validate(obj)
    if validator.errors:
        return RegistryResult((), tuple(validator.errors), discovery)
    project = Project(obj["project"], obj["owner"], obj.get("tier", "standard"),
                      obj.get("lifecycle", "active"), obj["reviewed"], path)
    jobs = []
    for job in obj["jobs"]:
        schedule = job.get("expected_schedule", {})
        output = job.get("output")
        declaration = Declaration(
            Identity(job.get("host", "local"), job.get("domain", f"gui/{uid}"), job["label"]),
            project, job["id"], job.get("scheduler", "launchd"), job["plist_path"],
            job["expected_program"], tuple(job["expected_arguments"]),
            expectation(job, "expected_working_directory"),
            Schedule(expectation(schedule, "interval_seconds"),
                     Known(freeze_calendar(schedule["calendar"])) if "calendar" in schedule else Absent("no expectation"),
                     expectation(schedule, "timezone"), expectation(schedule, "keep_alive"), expectation(schedule, "run_at_load")),
            job.get("expected_enabled", True),
            OutputContract(output["path"], output["kind"], output["max_age_seconds"], output.get("mtime_sufficient", False))
            if output is not None else None, job.get("grace_seconds", 0))
        jobs.append(JobRecord(declaration.identity, project, declaration, declaration.plist_path,
                              (("registry", Observation("attempted", None, ("parse_frontmatter", path), None, None, declaration)),)))
    return unique(RegistryResult(tuple(jobs), (), discovery))


def unique(result):
    errors = list(result.errors)
    projects, identities, indexes = {}, set(), {}
    for job in result.jobs:
        project = job.project
        index = indexes.get(project.runbook_path, 0)
        indexes[project.runbook_path] = index + 1
        field = f"jobs[{index}]"
        if project.project in projects and projects[project.project] != project.runbook_path:
            error = ValidationError(project.runbook_path, "project", "duplicate",
                                    f"{project.runbook_path}:project: duplicate project {project.project}")
            if error not in errors:
                errors.append(error)
        projects[project.project] = project.runbook_path
        if job.identity in identities:
            identity = job.identity
            field += ".label"
            errors.append(ValidationError(project.runbook_path, field, "duplicate",
                          f"{project.runbook_path}:{field}: duplicate identity {identity.host}/{identity.domain}/{identity.label}"))
        identities.add(job.identity)
    return replace(result, errors=tuple(dict.fromkeys(errors)))


def discover_runbooks(directory: Path, files: FileSource):
    return files.discover(directory)


def load_registry(directory: Path, uid: int, files: FileSource) -> RegistryResult:
    discovery = discover_runbooks(directory, files)
    jobs, errors = [], []
    if discovery.error is not None:
        errors.append(ValidationError(str(directory), "discovery", discovery.error.code,
                                     f"{directory}:discovery: {discovery.error.message}"))
    else:
        for path in discovery.data:
            content = files.read_regular(path, LIMIT)
            if content.error is not None:
                errors.append(ValidationError(path, "frontmatter", content.error.code,
                                             f"{path}:frontmatter: {content.error.message}"))
                continue
            result = parse_frontmatter(path, content.data, uid)
            jobs.extend(replace(job, observations=(("registry", replace(content, data=job.registry,
                                                                      source_command=("parse_frontmatter", path))),))
                        for job in result.jobs)
            errors.extend(result.errors)
    if not jobs and not errors:
        errors.append(ValidationError(str(directory), "jobs", "empty", f"{directory}:jobs: no declared jobs"))
    return unique(RegistryResult(tuple(jobs), tuple(errors), discovery))


def join_plists(registry: RegistryResult, files: FileSource) -> RegistryResult:
    if registry.errors:
        return registry
    jobs, errors, indexes = [], [], {}
    for job in registry.jobs:
        path = job.project.runbook_path
        index = indexes.get(path, 0)
        indexes[path] = index + 1
        field = f"jobs[{index}].plist_path"
        observation = observe_plist(job.plist_path, files)
        message = None
        if observation.error is not None:
            error = observation.error
            message = ("plist missing" if error.code == "missing" else
                       f"invalid plist: {error.message}" if error.code == "invalid_plist" else
                       f"plist unreadable: {error.message}")
        elif not isinstance(observation.data.label, Known):
            message = "plist Label missing"
        elif observation.data.label.value != job.identity.label:
            message = f"plist Label {observation.data.label.value} differs from {job.identity.label}"
        elif observation.data.field_errors:
            message = "invalid plist: " + "; ".join(e.message for e in observation.data.field_errors)
        if message:
            errors.append(ValidationError(path, field, "plist", f"{path}:{field}: {message}"))
        jobs.append(replace(job, observations=job.observations + (("plist", observation),)))
    return replace(registry, jobs=tuple(jobs), errors=tuple(errors))
