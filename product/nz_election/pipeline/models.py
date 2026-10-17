"""Shared typed failures and parser results."""
from dataclasses import dataclass, field


class ParseDrift(ValueError):
    code = "parse_drift"

    def __init__(self, reason, locator=""):
        self.reason = reason
        self.locator = locator
        # Source details remain private unless the parser supplies a position.
        self.public_locator = ""
        super().__init__(f"parse_drift: {reason}: {locator}")


@dataclass
class ParseResult:
    polls: list = field(default_factory=list)
    excluded_rows: list = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)


@dataclass
class DriftReport:
    polls: list
    diagnostics: dict
