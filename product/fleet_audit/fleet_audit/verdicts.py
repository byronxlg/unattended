"""Increment 2 implements only the rule-1 coverage guard."""
from dataclasses import dataclass
from typing import Callable

from .models import Known, Verdict
from .registry import valid_label


@dataclass(frozen=True)
class Match:
    evidence_refs: tuple[str, ...]
    details: str


@dataclass(frozen=True)
class NoMatch:
    pass


@dataclass(frozen=True)
class Rule:
    id: int
    predicate: Callable
    verdict_builder: Callable


def coverage_match(job, coverage):
    if not coverage.complete:
        return Match(tuple(name for name, _ in coverage.observations), '; '.join(coverage.issues))
    if not valid_label(job.identity.label) or job.identity.host != 'local':
        return Match(('registry',), 'cannot establish identity: registry rc=None: unusable identity')
    service = dict(job.observations).get('service')
    if (not isinstance(job.loaded, Known) or service is None or service.data is None
            or not service.data.structural_valid or service.error is not None):
        source = ' '.join(service.source_command) if service else 'service'
        rc = service.return_code if service else None
        error = service.error.message if service and service.error else 'untrusted service response'
        return Match(('service',), f'cannot establish loaded: {source} rc={rc}: {error}')
    return NoMatch()


RULES = (Rule(1, coverage_match, lambda match: Verdict('cannot_determine', 1, match.details, match.evidence_refs)),)


def coverage_failure(job, coverage):
    for rule in RULES:
        match = rule.predicate(job, coverage)
        if isinstance(match, Match):
            return rule.verdict_builder(match)
    return None
