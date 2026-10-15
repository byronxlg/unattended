"""Shared source and output contracts."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceResult:
    available: bool = True
    reason: str = ""
    data: list[dict] = field(default_factory=list)
    skipped: int = 0
    warnings: dict[str, int] = field(default_factory=dict)

    def warn(self, code):
        self.warnings[code] = self.warnings.get(code, 0) + 1


@dataclass
class Head:
    sha: str
    committed_at: str | None


@dataclass
class GitHubSnapshot:
    sources: dict[str, SourceResult] = field(default_factory=dict)

    def get(self, key):
        return self.sources.get(key, SourceResult(False, "source not fetched"))


@dataclass
class Snapshot:
    head: Head
    jobs: SourceResult
    ticks: SourceResult
    changes: SourceResult
    mistakes: SourceResult
    evals: SourceResult
    history: SourceResult
    github: GitHubSnapshot
    diagnostics: dict = field(default_factory=dict)


@dataclass
class Indicator:
    stage: str
    kind: str
    name: str
    definition: str
    value: Any
    unit: str
    n: int
    available: bool = True
    note: str = ""
    series: list[dict] = field(default_factory=list)
