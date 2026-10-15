from __future__ import annotations
"""Immutable records with explicit evidence presence and trust."""
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


class ExplicitValue:
    def __bool__(self):
        raise TypeError("Value requires explicit variant matching")


@dataclass(frozen=True)
class Known(ExplicitValue, Generic[T]):
    value: T


@dataclass(frozen=True)
class Absent(ExplicitValue):
    reason: str


@dataclass(frozen=True)
class Unknown(ExplicitValue):
    reason: str


@dataclass(frozen=True)
class Unsupported(ExplicitValue):
    raw: object
    reason: str


type Value[T] = Known[T] | Absent | Unknown | Unsupported


@dataclass(frozen=True)
class Error:
    code: str
    message: str


@dataclass(frozen=True)
class ValidationError:
    file: str
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class Observation(Generic[T]):
    status: str
    observed_at: str | None
    source_command: tuple[str, ...]
    return_code: int | None
    error: Error | None
    data: T | None


@dataclass(frozen=True)
class Identity:
    host: str
    domain: str
    label: str


@dataclass(frozen=True)
class Project:
    project: str
    owner: str
    tier: str
    lifecycle: str
    reviewed: str
    runbook_path: str


@dataclass(frozen=True)
class Schedule:
    interval_seconds: Value[int]
    calendar: Value[tuple]
    timezone: Value[str]
    keep_alive: Value[bool]
    run_at_load: Value[bool]


@dataclass(frozen=True)
class OutputContract:
    path: str
    kind: str
    max_age_seconds: int
    mtime_sufficient: bool


@dataclass(frozen=True)
class Declaration:
    identity: Identity
    project: Project
    id: str
    scheduler: str
    plist_path: str
    expected_program: str
    expected_arguments: tuple[str, ...]
    expected_working_directory: Value[str]
    expected_schedule: Schedule
    expected_enabled: bool
    output: OutputContract | None
    grace_seconds: int


@dataclass(frozen=True)
class PlistData:
    path: str
    present_keys: tuple[str, ...]
    label: Value[str]
    program: Value[str]
    arguments: Value[tuple[str, ...]]
    working_directory: Value[str]
    schedule: Schedule
    disabled: Value[bool]
    stdout_path: Value[str]
    stderr_path: Value[str]
    environment_keys: Value[tuple[str, ...]]
    field_errors: tuple[Error, ...]


@dataclass(frozen=True)
class JobRecord:
    identity: Identity
    project: Project
    registry: Declaration
    plist_path: str
    observations: tuple[tuple[str, Observation], ...]
    loaded: Value[bool] = Unknown("not requested")
    disabled: Value[bool] | DisabledState = Unknown("not requested")
    comparisons: tuple = ()
    drift: tuple = ()
    verdict: str | Verdict | None = "declared"
    uncertainties: tuple = ()


@dataclass(frozen=True)
class RegistryResult:
    jobs: tuple[JobRecord, ...]
    errors: tuple[ValidationError, ...]
    discovery: Observation[tuple[str, ...]]


@dataclass(frozen=True)
class CommandData:
    argv: tuple[str, ...]
    stdout: str
    stderr: str
    timed_out: bool
    truncated: bool
    duration_seconds: float | None


@dataclass(frozen=True)
class DomainData:
    domain: str
    labels: tuple[str, ...]
    complete: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ServiceData:
    identity: Identity
    loaded: Value[bool]
    state: Value[str]
    pid: Value[int]
    runs: Value[int]
    last_exit_code: Value[int]
    last_exit_text: Value[str]
    program: Value[str]
    argv: Value[tuple[str, ...]]
    working_directory: Value[str]
    plist_path: Value[str]
    schedule: Schedule
    properties: Value[tuple[str, ...]]
    missing_fields: tuple[str, ...]
    warnings: tuple[str, ...]
    structural_valid: bool


@dataclass(frozen=True)
class OverrideData:
    entries: tuple[tuple[str, bool], ...]
    complete: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class DisabledState:
    value: Value[bool]
    origin: str
    entry: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class Verdict:
    name: str
    rule_id: int
    reason: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class Coverage:
    complete: bool
    issues: tuple[str, ...]
    observations: tuple[tuple[str, Observation], ...]


@dataclass(frozen=True)
class FleetObservation:
    domain: str
    observed_at: str | None
    jobs: tuple[JobRecord, ...]
    coverage: Coverage


@dataclass(frozen=True)
class Manifest:
    format_version: int
    capture_clock: str
    domain: str
    macos_label: str
    indexes: dict
    provenance: dict


@dataclass(frozen=True)
class Snapshot:
    manifest: Manifest
    runbooks: dict
    plists: dict
    commands: dict
    stats: dict
    receipts: dict
    expected: dict
