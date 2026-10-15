import json
import plistlib
from dataclasses import replace

from fleet_audit.acceptance import FIXTURES
from fleet_audit.models import Absent, Known, Unknown, Unsupported
from fleet_audit.plists import parse_plist
from fleet_audit.reports import serialize


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
