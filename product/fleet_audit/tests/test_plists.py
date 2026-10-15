import json
import plistlib
import struct
from dataclasses import replace
from datetime import datetime

import pytest

from fleet_audit.acceptance import FIXTURES, FixtureFiles
from fleet_audit.files import LIMIT, observed
from fleet_audit.models import Absent, Error, Known, Unknown, Unsupported
from fleet_audit.plists import parse_plist
from fleet_audit.registry import join_plists, load_registry
from fleet_audit.reports import build_report, serialize


def test_xml_binary_presence_and_environment_keys():
    xml = parse_plist('xml', (FIXTURES/'plist-xml.plist').read_bytes())
    binary = parse_plist('binary', (FIXTURES/'plist-binary.plist').read_bytes())
    assert replace(xml, path='binary') == binary
    assert not xml.field_errors
    assert xml.arguments == Known(('/path with spaces/tool', '', 'arg with spaces'))
    assert xml.program == Known('/path with spaces/tool')
    assert isinstance(xml.schedule.keep_alive, Unsupported)
    assert isinstance(xml.environment_keys, Absent)
    assert 'Program' not in xml.present_keys
    assert xml.schedule.run_at_load == Known(True)
    assert xml.disabled == Known(False) and 'Disabled' not in xml.present_keys
    env = parse_plist('environment', (FIXTURES/'plist-environment-keys.plist').read_bytes())
    assert env.environment_keys == Known(('SYNTHETIC_KEY',))
    assert 'EnvironmentVariables' in env.present_keys
    assert 'synthetic-marker-not-a-secret' not in json.dumps(serialize(env))
    for environment in ({'KEY': 'another-secret'}, {'KEY': ['invalid-secret']}):
        parsed = parse_plist('env', plistlib.dumps({'EnvironmentVariables': environment}))
        assert 'secret' not in repr(parsed)
    only_program = parse_plist('program', plistlib.dumps({'Program': '/bin/sh'}))
    assert isinstance(only_program.arguments, Absent)
    assert only_program.schedule.keep_alive == Known(False)
    bad = parse_plist('invalid', plistlib.dumps({'StartInterval': True, 'Disabled': 1, 'RunAtLoad': 'yes'}))
    assert len(bad.field_errors) == 3
    assert isinstance(bad.schedule.interval_seconds, Unknown)
    for name in ('com.unattended.tick', 'com.google.GoogleUpdater.wake', 'com.google.keystone.agent', 'com.google.keystone.xpcservice'):
        real = json.loads((FIXTURES/(name+'.json')).read_text())
        assert real['source_commit'] == '18c8e8c'
        reconstructed = plistlib.loads((FIXTURES/(name+'.plist')).read_bytes())
        assert reconstructed == real['declared']
    tick = parse_plist('tick', (FIXTURES/'com.unattended.tick.plist').read_bytes())
    assert tick.schedule.run_at_load == Known(True)
    assert tick.schedule.interval_seconds == Known(600)


@pytest.mark.parametrize('value', [b'a', datetime(2026, 10, 16)])
@pytest.mark.parametrize('nesting', ['direct', 'list', 'dict'])
def test_keep_alive_rejects_non_json_values(value, nesting):
    nested = {'direct': value, 'list': [value], 'dict': {'nested': value}}[nesting]
    content = plistlib.dumps({'KeepAlive': {'x': nested}})
    parsed = parse_plist('invalid-policy', content)
    assert parsed.schedule.keep_alive == Unknown('invalid value')
    assert parsed.field_errors == (Error('plist_field', 'KeepAlive: invalid value'),)
    report = json.loads(json.dumps(serialize(parsed)))
    assert report['schedule']['keep_alive'] == {
        'status': 'unknown', 'value': None, 'reason': 'invalid value'}
    assert report['field_errors'] == [{'code': 'plist_field', 'message': 'KeepAlive: invalid value'}]


def test_recursive_binary_plist_join_error(monkeypatch):
    content = b'bplist00\xa1\x00\x08' + struct.pack('>6xBBQQQ', 1, 1, 1, 0, 10)
    try:
        value = plistlib.loads(content)
    except RecursionError:
        pass
    else:
        assert isinstance(value, list) and value[0] is value

        # Python 3.12 caches this cyclic array instead of raising during loading.
        def recursive_load(data):
            assert data == content
            raise RecursionError('synthetic parser recursion')

        monkeypatch.setattr(plistlib, 'loads', recursive_load)

    class FakeFiles:
        def read_regular(self, path, limit):
            assert path == '/fleet-fixtures/com.unattended.tick.plist'
            assert limit == LIMIT
            return observed(content, ('read', path))

    registry = load_registry(FIXTURES/'registry-valid', 501, FixtureFiles())
    result = join_plists(registry, FakeFiles())
    assert len(result.errors) == 1
    assert result.errors[0].message.endswith('invalid plist: RecursionError: malformed plist')
    assert build_report(result, 'gui/501')['exit_code'] == 3
