"""Undeclared LaunchAgent discovery and stat-only evidence."""
from dataclasses import replace
from pathlib import Path

from .models import Coverage, FleetObservation, Identity, JobRecord, Known, Observation, Verdict
from .plists import observe_plist
from .output import observe_output
from .verdicts import evaluate


def scan_plists(directory, files, domain=None):
    if domain is None:
        import os
        domain = f'gui/{os.getuid()}'
    discovery = files.discover_plists(Path(directory))
    jobs = []
    for path in sorted(discovery.data or ()):
        plist = observe_plist(path, files)
        label = plist.data.label.value if plist.data is not None and isinstance(plist.data.label, Known) else None
        if (label is not None and label.startswith('com.apple.') or
                label is None and Path(path).name.startswith('com.apple.')):
            continue
        observations = (('discovery', discovery), ('plist', plist),
                        ('registry', Observation('not_applicable', None, (), None, None, None)))
        jobs.append(JobRecord(Identity('local', domain, label), None, None, path, observations))
    issues = (discovery.error.message,) if discovery.error else ()
    if not jobs:
        issues += ('cannot establish coverage: no discoverable jobs',)
    return FleetObservation(domain, discovery.observed_at, tuple(jobs),
                            Coverage(not issues, issues, (('discovery', discovery),)))


def scan_fleet(discovered, files, commands):
    from .collect import collect_jobs
    fleet = collect_jobs(discovered.jobs, discovered.domain, commands)
    coverage = replace(fleet.coverage, complete=fleet.coverage.complete and discovered.coverage.complete,
                       issues=discovered.coverage.issues + fleet.coverage.issues,
                       observations=discovered.coverage.observations + fleet.coverage.observations)
    cache, jobs = {}, []
    for job in fleet.jobs:
        observations = dict(job.observations)
        observations['output'] = Observation('not_requested', None, (), None, None, None)
        observations['receipt'] = Observation('not_applicable', None, (), None, None, None)
        plist = observations['plist']
        if plist.data is not None:
            paths = sorted({value.value for value in (plist.data.stdout_path, plist.data.stderr_path)
                            if isinstance(value, Known)})
            for index, path in enumerate(paths):
                if path not in cache:
                    cache[path] = observe_output(path, files)
                observations[f'output:{index}'] = cache[path]
        errors = tuple(f'{name}: {obs.error.message}' for name, obs in observations.items() if obs.error)
        if plist.data is not None:
            errors += tuple(f'plist: {error.message}' for error in plist.data.field_errors)
        job = replace(job, observations=tuple(observations.items()), uncertainties=errors)
        verdict = evaluate(job, coverage, 'scan')
        if job.identity.label is None:
            verdict = Verdict('cannot_determine', 1,
                              'cannot establish identity: plist Label missing or unreadable; filename is not identity',
                              ('plist',))
        jobs.append(replace(job, verdict=verdict))
    return replace(fleet, jobs=tuple(jobs), coverage=coverage)
