"""The data branch accepts only host-independent, lexically ordered instants."""
from copy import deepcopy
import json
import os
import time

import pytest

from product.nz_election.pipeline import export
from product.nz_election.pipeline.build import build, local_time
from product.nz_election.pipeline.publish import publish
from product.nz_election.pipeline.refresh import refresh, utc_now
from product.nz_election.tests.test_pipeline import fail, git, make_bundle, repository


@pytest.fixture(scope='module')
def envelopes(tmp_path_factory):
    return export.validate_bundle(make_bundle(tmp_path_factory.mktemp('canonical')))


@pytest.mark.parametrize('value', [
    '2026-10-17T01:00:00.100000Z', '2026-10-17T01:00:00.000000Z',
    '2026-10-17T01:00:00', '2026-10-17T01:00:00+00:00',
    '2026-10-17T14:00:00+13:00', '2026-10-17 01:00:00Z',
    '20261017T010000Z', '2026-02-30T01:00:00Z', '', 123,
])
def test_noncanonical_instants_rejected(envelopes, value):
    env = deepcopy(envelopes['averages'])
    env['generated_at'] = value
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        export.validate_envelope(env, 'averages')


@pytest.mark.parametrize('stem,path', [
    ('polls', ('fetched_at',)), ('polls', ('source', 0, 'fetched_at')),
    ('seats', ('generated_at',)), ('status', ('data', 0, 'observed_at')),
    ('status', ('data', 0, 'last_attempt_at')), ('status', ('data', 0, 'last_success_at')),
    ('manifest', ('data', 0, 'observed_at')),
])
def test_each_operational_field_validated(envelopes, stem, path):
    env = deepcopy(envelopes[stem])
    target = env
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = '2026-10-17T01:00:00.100000Z'
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        export.validate_envelope(env, stem)


def test_manifest_acquisition_ranges_and_nested_sources_validated(envelopes):
    for filename, path in [('polls.json', ('fetched_at',)),
                           ('polls.json', ('source_ref', 0, 'fetched_at')),
                           ('status.json', ('observation_start',)),
                           ('status.json', ('observation_end',))]:
        env = deepcopy(envelopes['manifest'])
        target = next(row for row in env['data'] if row['path'] == filename)
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = '2026-10-17T01:00:00'
        with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
            export.validate_envelope(env, 'manifest')


def test_fractional_failed_attempt_rejected_before_publication(tmp_path):
    bundle = make_bundle(tmp_path)
    remote = repository(tmp_path, bundle)
    before = git(remote, 'rev-parse', 'data').stdout
    refresh(bundle, now='2026-10-17T01:00:00Z', parse=fail)
    path = bundle / 'status.json'
    env = json.loads(path.read_text())
    env['data'][0]['last_attempt_at'] = '2026-10-17T01:00:00.100000Z'
    # Simulate untrusted branch bytes without using the guarded producer.
    path.write_text(json.dumps(env))
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        publish(bundle, remote)
    assert git(remote, 'rev-parse', 'data').stdout == before


def test_build_manifest_instants_validated(tmp_path):
    out = build(tmp_path / 'missing', tmp_path / 'output', built='2026-10-17T01:00:00Z')
    original = json.loads((out / 'build-manifest.json').read_text())
    for key in ('built_at', 'observed_at'):
        env = deepcopy(original)
        env['data'][key] = '2026-10-17T01:00:00'
        with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
            export.validate_envelope(env, 'build-manifest')


def test_producers_reject_noncanonical_times(tmp_path, envelopes):
    bad = '2026-10-17T01:00:00.100000Z'
    for operation in (
        lambda: refresh(tmp_path / 'data', now=bad),
        lambda: build(tmp_path / 'missing', tmp_path / 'output', built=bad),
        lambda: export.inventory(tmp_path, None, 'sha', bad),
        lambda: export.envelope([], [], None, 'sha', inputs={}, method='v1', generated=bad),
    ):
        with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
            operation()
    assert not (tmp_path / 'data').exists() and not (tmp_path / 'output').exists()
    env = deepcopy(envelopes['polls'])
    env['source'][0]['fetched_at'] = bad
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        export.envelope([], env['source'], None, 'sha')
    with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
        export.csv_bytes(env)
    assert export.timestamp(utc_now())


def test_poll_dates_stay_date_only(envelopes):
    export.validate_envelope(envelopes['polls'], 'polls')
    for key in ('observed_at', 'fieldwork_start', 'fieldwork_end'):
        env = deepcopy(envelopes['polls'])
        env['data'][0][key] = '2026-10-17T01:00:00Z'
        with pytest.raises(ValueError, match='INVALID_DATE'):
            export.validate_envelope(env, 'polls')


def test_local_time_independent_of_host_timezone():
    previous = os.environ.get('TZ')
    try:
        for zone in ('UTC', 'Pacific/Auckland'):
            os.environ['TZ'] = zone
            time.tzset()
            assert local_time('2026-10-17T01:00:00Z') == '2:00 pm, Saturday 17 October 2026 NZDT'
            assert local_time('2026-07-01T01:00:00Z') == '1:00 pm, Wednesday 1 July 2026 NZST'
            with pytest.raises(ValueError, match='INVALID_TIMESTAMP'):
                local_time('2026-10-17T01:00:00')
    finally:
        if previous is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = previous
        time.tzset()
