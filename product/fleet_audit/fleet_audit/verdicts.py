"""Ordered audit rules: unknown evidence never proves a health predicate."""
from dataclasses import dataclass
from typing import Callable

from .models import Absent, DisabledState, Known, Verdict
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
    failures = tuple(f'cannot establish {name}: {" ".join(obs.source_command)} rc={obs.return_code}: {obs.error.message}' for name, obs in coverage.observations if obs.error)
    if not coverage.complete or failures:
        return Match(tuple(name for name, _ in coverage.observations), '; '.join(coverage.issues or failures or ('cannot establish coverage: inventory rc=None: incomplete coverage',)))
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


def coverage_failure(job, coverage):
    match = coverage_match(job, coverage)
    return Verdict('cannot_determine', 1, match.details, match.evidence_refs) if isinstance(match, Match) else None


def known(value, expected):
    return isinstance(value, Known) and type(value.value) is type(expected) and value.value == expected


def rule_match(number, job, coverage):
    observations = dict(job.observations)
    service = observations.get('service')
    data = service.data if service else None
    disabled = job.disabled.value if isinstance(job.disabled, DisabledState) else job.disabled
    origin = job.disabled.origin if isinstance(job.disabled, DisabledState) else 'unknown'
    loaded = known(job.loaded, True)
    absent = known(job.loaded, False)
    state = data.state if data else None
    pid = data.pid if data else None
    code = data.last_exit_code if data else None
    no_pid = isinstance(pid, Absent)
    idle = loaded and known(state, 'not running') and no_pid
    contract = job.registry.output
    evidence_name = 'receipt' if contract and contract.kind == 'ticks_jsonl' else 'output'
    observation = observations.get(evidence_name)
    evidence = observation.data if observation else None
    age = evidence.age_seconds if evidence else None
    refs = ('service',)
    detail = None
    if number == 2 and (not isinstance(disabled, Known) or type(disabled.value) is not bool):
        obs = observations.get('override')
        source = ' '.join(obs.source_command) if obs else 'override'
        detail = f'disabled state unknown: {source} rc={obs.return_code if obs else None}: {obs.error.message if obs and obs.error else "untrusted disabled state"}'
        refs = ('override', 'plist')
    elif number == 3 and loaded and known(disabled, True):
        detail = f'service loaded but disabled by {origin}; lookup rc=0'
        refs += ('override', 'plist')
    elif number == 4 and absent and known(disabled, True):
        detail = f'service absent, disabled by {origin}; expected_enabled={str(job.registry.expected_enabled).lower()}; lookup rc=113'
        refs += ('override', 'plist', 'registry')
    elif number == 5 and absent and known(disabled, False):
        detail = 'service absent; lookup rc=113; load history unknown'
    elif number == 6 and loaded and known(state, 'running') and isinstance(pid, Known) and type(pid.value) is int and pid.value > 0:
        detail = f'state running, pid={pid.value}; useful work not established'
    elif number == 7 and loaded and no_pid and (known(state, 'not running') or known(state, 'spawn scheduled')) and isinstance(code, Known) and type(code.value) is int and code.value != 0:
        text = data.last_exit_text.value if isinstance(data.last_exit_text, Known) else 'unknown'
        detail = f'state={state.value}, no pid; last exit={code.value} {text}'
    elif number == 8 and loaded and no_pid and known(state, 'spawn scheduled'):
        policy, policy_origin = data.schedule.keep_alive, 'loaded'
        if not isinstance(policy, Known):
            plist = observations.get('plist')
            policy = plist.data.schedule.keep_alive if plist and plist.error is None and plist.data else None
            policy_origin = 'disk'
        if known(policy, True):
            detail = f'KeepAlive=true ({policy_origin}), spawn scheduled, no pid; last exit={code.value if isinstance(code, Known) else "unknown"}'
            refs += ('plist',) if policy_origin == 'disk' else ()
    elif number == 9:
        details = list(job.uncertainties)
        details.extend(f'{name}: {obs.error.message}' for name, obs in observations.items() if obs.error)
        for name, obs in observations.items():
            if obs.data is not None:
                details.extend(f'{name}: {error.message}' for error in getattr(obs.data, 'field_errors', ()))
        if (known(state, 'running') and no_pid or isinstance(pid, Known) and not known(state, 'running')):
            details.append('contradictory pid/state')
        # Drift is not yet computed in increment 3; no missing comparison is treated as equal.
        # Existing explicit comparison uncertainty remains blocking evidence.
        details.extend('required comparison unknown' for c in job.comparisons if getattr(c, 'status', None) == 'unknown')
        details.extend(str(finding) for finding in job.drift)
        if details:
            detail = 'health unestablished: ' + '; '.join(dict.fromkeys(details))
            refs = tuple(observations)
    elif number == 10:
        problem = None
        if contract is None:
            problem = 'no freshness contract declared'
        elif evidence is None or age is None:
            problem = 'unavailable or invalid evidence timestamp'
        elif age < 0:
            problem = 'future evidence timestamp'
        elif getattr(evidence, 'parsing_errors', ()):
            problem = '; '.join(evidence.parsing_errors)
        if problem:
            detail = 'freshness unestablished: ' + problem
            refs = (evidence_name, 'registry')
    elif number == 11 and loaded and contract and age is not None and age > contract.max_age_seconds + job.registry.grace_seconds:
        detail = f'{contract.kind} {contract.path} age={age:g}s exceeds max_age={contract.max_age_seconds}s + grace={job.registry.grace_seconds}s; missed execution not established'
        refs = (evidence_name, 'registry')
    elif number == 12 and idle and contract and age is not None and 0 <= age <= contract.max_age_seconds + job.registry.grace_seconds and getattr(evidence, 'outcome', None) == 'failed':
        result = 'present' if evidence.result is not None else 'null'
        detail = f'receipt {contract.path} ts={evidence.ts} supervisor rc={evidence.rc if evidence.rc is not None else "unknown"}; result={result}'
        refs += ('receipt',)
    elif number == 13 and idle and known(code, 0) and contract and age is not None and 0 <= age <= contract.max_age_seconds:
        completed = contract.kind == 'ticks_jsonl' and getattr(evidence, 'outcome', None) == 'completed'
        sufficient = contract.kind == 'mtime' and contract.mtime_sufficient is True
        if completed or sufficient:
            detail = f'not running, last exit=0; {contract.path} age={age:g}s <= max_age={contract.max_age_seconds}s; evidence={"completed tick" if completed else "explicit mtime"}'
            refs += (evidence_name, 'registry')
    elif number == 14:
        if contract and age is not None and contract.max_age_seconds < age <= contract.max_age_seconds + job.registry.grace_seconds:
            problem = 'within grace'
        elif not idle:
            problem = 'idle state unestablished'
        elif not known(code, 0):
            problem = 'last exit zero unestablished'
        else:
            problem = 'completion unestablished'
        detail = 'health unestablished: ' + problem
        refs += (evidence_name,)
    return Match(refs, detail) if detail is not None else NoMatch()


def make_rule(number, name):
    return Rule(number, lambda job, coverage: rule_match(number, job, coverage),
                lambda match: Verdict(name, number, match.details, match.evidence_refs))


RULES = (Rule(1, coverage_match, lambda match: Verdict('cannot_determine', 1, match.details, match.evidence_refs)),) + tuple(
    make_rule(number, name) for number, name in enumerate((
        'cannot_determine', 'loaded_disabled', 'disabled', 'declared_not_loaded', 'running',
        'failing', 'failing', 'cannot_determine', 'cannot_determine', 'late', 'failing',
        'healthy_idle', 'cannot_determine'), start=2))


def evaluate(job, coverage, mode='audit'):
    if mode != 'audit':
        raise ValueError('only audit verdicts are implemented')
    for rule in RULES:
        match = rule.predicate(job, coverage)
        if isinstance(match, Match):
            return rule.verdict_builder(match)
    raise AssertionError('rule 14 must match')
