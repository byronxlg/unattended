"""The only live command adapter; bounded, sequential, read-only collection."""
import os
import re
import selectors
import subprocess
import time
from dataclasses import replace
from datetime import datetime, timezone
from typing import Protocol

from .launchctl_parse import parse_domain, parse_service, redact_environment
from .models import CommandData, Coverage, Error, FleetObservation, Observation
from .overrides import effective_disabled, parse_overrides
from .verdicts import coverage_failure


class CommandSource(Protocol):
    def run(self, argv: tuple[str, ...]) -> Observation[CommandData]: ...


def run_bounded(argv, timeout_seconds=10, max_bytes=4194304):
    if (len(argv) != 3 or argv[0] != '/bin/launchctl' or argv[1] not in ('print', 'print-disabled')
            or not re.fullmatch(r'gui/\d+(?:/[^\s/\x00-\x1f\x7f]+)?', argv[2])
            or (argv[1] == 'print-disabled' and argv[2].count('/') != 1)):
        raise ValueError('unsupported command')
    if not 0 < timeout_seconds <= 10 or not 0 < max_bytes <= 4194304:
        raise ValueError('invalid command bounds')
    stamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    start = time.monotonic()
    streams = [bytearray(), bytearray()]
    process, error, rc, timed_out, truncated = None, None, None, False, False
    try:
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                                   shell=False)
        with selectors.DefaultSelector() as selector:
            for index, stream in enumerate((process.stdout, process.stderr)):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, index)
            while selector.get_map():
                remaining = timeout_seconds - (time.monotonic() - start)
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(argv, timeout_seconds)
                for key, _ in selector.select(remaining):
                    room = max_bytes - sum(map(len, streams))
                    chunk = os.read(key.fileobj.fileno(), min(65536, room + 1))
                    if not chunk:
                        selector.unregister(key.fileobj)
                    elif len(chunk) > room:
                        streams[key.data].extend(chunk[:room])
                        truncated = True
                        error = Error('output_limit', 'combined command output limit exceeded')
                        break
                    else:
                        streams[key.data].extend(chunk)
                if truncated:
                    break
            if truncated:
                process.kill()
                rc = process.wait()
            else:
                rc = process.wait(timeout=max(0, timeout_seconds - (time.monotonic() - start)))
    except subprocess.TimeoutExpired:
        timed_out, error = True, Error('timeout', 'command deadline exceeded')
    except OSError as exc:
        error = Error('command_io', type(exc).__name__)
    finally:
        if process is not None:
            if process.poll() is None:
                process.kill()
            process.wait()
            for stream in (process.stdout, process.stderr):
                stream.close()
    data = CommandData(tuple(argv), *(redact_environment(bytes(s).decode('utf-8', errors='replace')) for s in streams),
                       timed_out, truncated, time.monotonic() - start)
    return Observation('attempted', stamp, tuple(argv), None if timed_out else rc, error, data)


class LiveCommands:
    run = staticmethod(run_bounded)


def collect_jobs(jobs, domain, source):
    inventory = parse_domain(source.run(('/bin/launchctl', 'print', domain)), domain)
    services = [parse_service(source.run(('/bin/launchctl', 'print', f'{domain}/{job.identity.label}')), job.identity)
                for job in jobs]
    overrides = parse_overrides(source.run(('/bin/launchctl', 'print-disabled', domain)))
    globals_ = (('inventory', inventory), ('override', overrides))
    issues = tuple(f'cannot establish {name}: {" ".join(obs.source_command)} rc={obs.return_code}: {obs.error.message}'
                   for name, obs in globals_ if obs.error is not None)
    if not jobs and not issues:
        issues = ('cannot establish coverage: no discoverable jobs',)
    coverage = Coverage(not issues, issues, globals_)
    observed = []
    for job, service in zip(jobs, services):
        disabled = effective_disabled(job.identity.label, dict(job.observations).get('plist'), overrides)
        job = replace(job, loaded=service.data.loaded, disabled=disabled,
                      observations=job.observations + globals_ + (('service', service),))
        observed.append(replace(job, verdict=coverage_failure(job, coverage)))
    return FleetObservation(domain, inventory.observed_at, tuple(observed), coverage)
