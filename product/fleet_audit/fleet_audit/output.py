"""Output evidence uses its own observation time, never the report clock."""
from dataclasses import replace
from datetime import datetime

from .models import Observation


def age(stamp, observed_at):
    if stamp is None or observed_at is None:
        return None
    return (datetime.fromisoformat(observed_at) - datetime.fromisoformat(stamp)).total_seconds()


def observe_output(path, files):
    obs = files.stat_output(path)
    if obs.data is not None:
        obs = replace(obs, data=replace(obs.data, age_seconds=age(obs.data.mtime, obs.observed_at)))
    return obs


def observe_job(job, files):
    from .receipts import parse_receipt, read_tail
    contract = job.registry.output
    observations = dict(job.observations)
    observations['output'] = Observation('not_applicable', None, (), None, None, None)
    observations['receipt'] = Observation('not_applicable', None, (), None, None, None)
    if contract is not None:
        observations['output'] = observe_output(contract.path, files)
        if contract.kind == 'ticks_jsonl':
            observations['receipt'] = parse_receipt(read_tail(contract.path, files))
    errors = tuple(f'{name}: {obs.error.message}' for name, obs in observations.items() if obs.error)
    return replace(job, observations=tuple(observations.items()), uncertainties=tuple(dict.fromkeys(job.uncertainties + errors)))
