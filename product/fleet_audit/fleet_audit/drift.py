"""Independent three-way comparisons of requested, trusted evidence."""
from .models import Absent, Comparison, DriftFinding, JobRecord, Known, Unknown, Unsupported, Value
from .registry import calendar_error, valid_path


def normalize_calendar(value: object) -> Value[tuple[tuple[tuple[str, int], ...], ...]]:
    raw = value
    if isinstance(value, tuple):
        try:
            value = [dict(alternative) for alternative in value]
            if any(len(mapping) != len(alternative) for mapping, alternative in zip(value, raw)):
                return Unsupported(raw, 'duplicate calendar keys')
        except (TypeError, ValueError):
            return Unsupported(raw, 'invalid frozen calendar')
    error = calendar_error(value)
    if error is not None:
        return Unsupported(raw, error)
    alternatives = value if isinstance(value, list) else [value]
    return Known(tuple(sorted(set(tuple(sorted((key, 0 if key == 'Weekday' and val == 7 else val)
                                               for key, val in item.items())) for item in alternatives))))


def compare_job(job: JobRecord) -> tuple[tuple[Comparison, ...], tuple[DriftFinding, ...]]:
    observations = dict(job.observations)
    declaration = job.registry
    if declaration is None:
        return (), ()

    def observed(source, field):
        obs = observations.get(source)
        if obs is None or obs.status != 'attempted' or obs.error is not None or obs.data is None:
            return Unknown(source + ' unavailable')
        if source == 'service' and (not obs.data.structural_valid or job.loaded != Known(True)):
            return Unknown('loaded evidence untrusted')
        if field.startswith('schedule.'):
            return getattr(obs.data.schedule, field.split('.')[1])
        return getattr(obs.data, 'argv' if source == 'service' and field == 'arguments' else field)

    requested = [('program', Known(declaration.expected_program)),
                 ('arguments', Known(declaration.expected_arguments)),
                 ('working_directory', declaration.expected_working_directory)]
    requested.extend(('schedule.' + field, getattr(declaration.expected_schedule, field))
                     for field in ('interval_seconds', 'calendar', 'keep_alive', 'run_at_load'))
    comparisons, findings = [], []
    for field, expected in requested:
        if isinstance(expected, Absent):
            continue
        values = {'registry': expected, 'disk': observed('plist', field), 'loaded': observed('service', field)}
        for source, value in values.items():
            if isinstance(value, Known):
                if field == 'schedule.calendar':
                    values[source] = normalize_calendar(value.value)
                elif field in ('program', 'working_directory') and not valid_path(value.value):
                    values[source] = Unsupported(value.value, 'expected absolute normalized path')
        for left_source, right_source in (('registry', 'disk'), ('registry', 'loaded'), ('disk', 'loaded')):
            left, right = values[left_source], values[right_source]
            pair = left_source + '-to-' + right_source
            refs = tuple({'registry': 'registry', 'disk': 'plist', 'loaded': 'service'}[s]
                         for s in (left_source, right_source))
            if right_source == 'loaded' and job.loaded == Known(False):
                status = 'not_applicable'
            elif not isinstance(left, Known) or not isinstance(right, Known):
                status = 'unknown'
            else:
                status = 'equal' if left.value == right.value else 'different'
            comparisons.append(Comparison(field, pair, left, right, status, refs))
            if status == 'different':
                kind = 'wrong_schedule' if field.startswith('schedule.') else 'wrong_' + field
                reason = f'{field}: {left_source}={left.value} differs from {right_source}={right.value}'
                findings.append(DriftFinding(kind, field, pair, reason, refs))
    return tuple(comparisons), tuple(findings)
