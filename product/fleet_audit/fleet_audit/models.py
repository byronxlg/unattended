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
    disabled: Value[bool] = Unknown("not requested")
    comparisons: tuple = ()
    drift: tuple = ()
    verdict: str = "declared"
    uncertainties: tuple = ()


@dataclass(frozen=True)
class RegistryResult:
    jobs: tuple[JobRecord, ...]
    errors: tuple[ValidationError, ...]
    discovery: Observation[tuple[str, ...]]
