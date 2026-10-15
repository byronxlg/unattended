import ast
import copy
import importlib.metadata
import json
import os
from pathlib import Path

import pytest
import yaml

from fleet_audit import cli
from fleet_audit.acceptance import FIXTURES, FixtureFiles, prove_registry
from fleet_audit.files import LIMIT, LocalFiles, observed, read_regular
from fleet_audit.models import Absent, Error, Known, Unknown, Unsupported
from fleet_audit.registry import join_plists, load_registry, parse_frontmatter

BASE = yaml.safe_load((FIXTURES / 'registry-valid/fleet.md').read_text().split('---')[1])
MISSING = object()
CASES = []


def parse(obj):
    return parse_frontmatter('test.md', ('---\n' + yaml.safe_dump(obj, sort_keys=False) + '---\n').encode(), 501)


def changed(field, value):
    obj = copy.deepcopy(BASE)
    parts = field.split('.')
    target = obj
    for part in parts[:-1]:
        target = target['jobs'][0] if part == 'jobs[0]' else target.setdefault(part, {})
    if value is MISSING:
        target.pop(parts[-1], None)
    else:
        target[parts[-1]] = value
    return obj


def case(field, values, suffix):
    CASES.extend((field, value, suffix) for value in values)


for key in ('schema_version', 'project', 'owner', 'reviewed', 'jobs'):
    case(key, [MISSING], 'required field missing')
for key in ('id', 'label', 'plist_path', 'expected_program', 'expected_arguments'):
    case('jobs[0].' + key, [MISSING], 'required field missing')
case('schema_version', [0, 2, True, '1', 1.0], 'expected schema_version 1')
case('project', ['', 'Bad', '-bad', 1], 'expected project slug')
case('owner', ['', ' ', 1, 1.5, False], 'expected nonblank owner')
case('tier', ['urgent', 1], 'expected critical, standard, or experimental')
case('lifecycle', ['deleted', 1], 'expected active, paused, or retired')
case('reviewed', ['2026-02-30', '2026-1-01', 20261016], 'expected valid YYYY-MM-DD string')
case('jobs', [{}, 'no'], 'expected list')
case('jobs', [[]], 'expected nonempty job list')
case('jobs[0].id', ['', 'UPPER', 1], 'expected job slug')
case('jobs[0].scheduler', ['cron', 1], 'only launchd is supported')
case('jobs[0].host', ['remote', 1], 'only local host is supported')
case('jobs[0].domain', ['gui/502', 'system', 501], 'expected current-user gui/501')
case('jobs[0].label', ['', 'has space', 'a/b', 'a\x7f', 1], 'expected launchd label')
for key in ('plist_path', 'expected_program', 'expected_working_directory', 'output.path'):
    case('jobs[0].' + key, ['relative', '~/file', '$HOME/file', '/a/../b', '/a/./b', '/a//b', '/a/', '//a', '/a\x00', 2],
         'expected absolute normalized path')
case('jobs[0].expected_arguments', [[], {}, '/bin/sh', [1], [True]], 'expected nonempty argv array')
case('jobs[0].expected_arguments', [['/bin/sh', '\n'], ['/bin/sh', '\x7f']], 'argv contains control character')
for key in ('expected_enabled', 'output.mtime_sufficient', 'expected_schedule.keep_alive', 'expected_schedule.run_at_load'):
    case('jobs[0].' + key, ['yes', 1, 'false'], 'expected boolean')
case('jobs[0].grace_seconds', [-1, True, '1', 1.5], 'expected nonnegative integer')
case('jobs[0].grace_seconds', [0], 'grace_seconds requires output')
case('jobs[0].output', [[], False], 'expected evidence mapping')
case('jobs[0].expected_schedule', [[], 'daily'], 'expected schedule mapping')
case('jobs[0].expected_schedule', [{}], 'expected at least one schedule expectation')
case('jobs[0].output.kind', ['receipt', 1], 'expected mtime or ticks_jsonl')
for key in ('output.max_age_seconds', 'expected_schedule.interval_seconds'):
    case('jobs[0].' + key, [0, -1, True, '60', 1.5], 'expected positive integer')
case('jobs[0].expected_schedule.calendar', [[], 'daily', [1]], 'expected calendar mapping or nonempty list')
case('jobs[0].expected_schedule.calendar', [{}], 'calendar mapping must not be empty')
case('jobs[0].expected_schedule.calendar', [{'Year': 2026}], 'unknown calendar field Year')
for key, low, high in [('Minute', 0, 59), ('Hour', 0, 23), ('Day', 1, 31), ('Weekday', 0, 7), ('Month', 1, 12)]:
    case('jobs[0].expected_schedule.calendar', [{key: v} for v in (low-1, high+1, True, '1', 1.5)],
         f'expected {key} integer in {low}..{high}')
for key in ('uid', 'receipt', 'cron', 'unexpected'):
    for prefix in ('', 'jobs[0].', 'jobs[0].output.', 'jobs[0].expected_schedule.'):
        case(prefix + key, [1], 'unknown field')
case('jobs[0].output', [{'kind': 'mtime', 'max_age_seconds': 1}], 'required field missing')
case('jobs[0].output', [{'path': '/receipt', 'max_age_seconds': 1}], 'required field missing')
case('jobs[0].output', [{'path': '/receipt', 'kind': 'mtime'}], 'required field missing')
case('jobs[0].output', [{'path': '/receipt', 'kind': 'ticks_jsonl', 'max_age_seconds': 1, 'mtime_sufficient': True}],
     'mtime_sufficient requires kind mtime')
case('jobs[0].expected_schedule', [{'calendar': {'Hour': 1}}], 'calendar requires timezone local')
case('jobs[0].expected_schedule', [{'calendar': {'Hour': 1}, 'timezone': 'UTC'}], 'calendar requires timezone local')
case('jobs[0].expected_schedule', [{'timezone': 'local'}], 'timezone requires calendar')


@pytest.mark.parametrize('field,value,suffix', CASES)
def test_schema_rejection_matrix(field, value, suffix):
    result = parse(changed(field, value))
    matches = [e for e in result.errors if e.message.endswith(suffix)]
    assert matches, result.errors
    assert all(e.message.startswith(f'test.md:{e.field}: ') for e in result.errors)
    assert any(e.field == field or e.field.startswith(field + '.') for e in matches)

    raw = (FIXTURES / 'registry-valid/fleet.md').read_text()
    invalid = [
        (raw.replace("'2026-10-16'", '2026-10-16'), 'expected valid YYYY-MM-DD string'),
        (raw.replace('owner: Fixture owner', 'owner: null'), 'invalid frontmatter: nulls are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner: ~'), 'invalid frontmatter: nulls are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner:'), 'invalid frontmatter: nulls are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner: &owner Fixture owner\nother: *owner'), 'invalid frontmatter: aliases are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner: !!str Fixture owner'), 'invalid frontmatter: tags are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner: !custom Fixture owner'), 'invalid frontmatter: tags are not allowed'),
        (raw.replace('owner: Fixture owner', 'owner: a\nowner: b'), 'invalid frontmatter: duplicate key owner'),
        (raw.replace('owner: Fixture owner', 'owner: yes'), 'expected nonblank owner'),
        (raw.replace('owner: Fixture owner', 'owner: 2026-10-16'), 'expected nonblank owner'),
        (raw.replace('jobs:', 'jobs:').replace('- id: tick', '- expected_enabled: yes\n  id: tick'), 'expected boolean'),
        (raw.replace('- id: tick', '- expected_schedule: {keep_alive: null}\n  id: tick'), 'invalid frontmatter: nulls are not allowed'),
        ('---\n[]\n---\n', 'expected mapping'),
        (raw.replace('jobs:\n- id: tick', 'jobs:\n- not-a-mapping\n- id: tick'), 'expected mapping'),
    ]
    for text, message in invalid:
        errors = parse_frontmatter('test.md', text.encode(), 501).errors
        assert any(e.message == f'test.md:{e.field}: {message}' for e in errors), errors


def test_registry_defaults_and_metadata():
    for lifecycle in ('active', 'paused', 'retired'):
        obj = copy.deepcopy(BASE)
        obj['lifecycle'] = lifecycle
        result = parse(obj)
        assert not result.errors
        job = result.jobs[0].registry
        assert job.project.lifecycle == lifecycle
        assert job.project.tier == 'standard'
        assert job.project.reviewed == '2026-10-16'
        assert job.identity.domain == 'gui/501' and job.identity.host == 'local'
        assert job.scheduler == 'launchd'
        assert job.expected_enabled is True and job.grace_seconds == 0
        assert job.output is None
        assert isinstance(job.expected_schedule.run_at_load, Absent)
        assert isinstance(job.expected_working_directory, Absent)
    obj['jobs'][0].update(output={'path': '/receipt', 'kind': 'mtime', 'max_age_seconds': 60},
                          expected_schedule={'interval_seconds': 1, 'calendar': [{'Weekday': 7}], 'timezone': 'local',
                                             'keep_alive': False, 'run_at_load': True})
    result = parse(obj)
    assert not result.errors
    assert result.jobs[0].registry.output.mtime_sufficient is False
    assert result.jobs[0].registry.expected_schedule.keep_alive == Known(False)


def test_discovery_order_frontmatter_and_limits(tmp_path):
    files = LocalFiles()
    assert load_registry(tmp_path, 501, files).errors[0].message.endswith('no declared jobs')
    (tmp_path/'z').mkdir()
    (tmp_path/'z/z.md').write_text('ordinary prose')
    (tmp_path/'a.md').write_text('ordinary prose')
    (tmp_path/'linked').symlink_to(tmp_path/'z', target_is_directory=True)
    assert files.discover(tmp_path).data == (str(tmp_path/'a.md'), str(tmp_path/'z/z.md'))
    assert not parse_frontmatter('plain.md', b'# Plain\n---\nbody', 501).errors
    for text in (b'---\nowner: missing closer', b'---bad\n', b'---\nx: [\n---\n'):
        assert 'invalid frontmatter:' in parse_frontmatter('bad.md', text, 501).errors[0].message
    huge = json.loads((FIXTURES/'file-too-large.json').read_text())
    path = tmp_path/'large.md'
    path.write_bytes(huge['fill'].encode()*huge['bytes'])
    assert read_regular(str(path)).error.code == 'too_large'
    assert load_registry(tmp_path, 501, files).errors[0].code == 'too_large'
    path.write_bytes(b'x'*LIMIT)
    assert len(read_regular(str(path)).data) == LIMIT
    path.unlink()
    count = json.loads((FIXTURES/'discovery-limit.json').read_text())['markdown_files']
    for index in range(count - 2):
        (tmp_path/f'{index}.md').write_text('ordinary')
    assert files.discover(tmp_path).error.code == 'discovery'
    (tmp_path/'0.md').unlink()
    assert len(files.discover(tmp_path).data) == 1000
    assert json.loads((FIXTURES/'nonregular-file.json').read_text())['kind'] == 'fifo'
    fifo = tmp_path/'fifo'
    os.mkfifo(fifo)
    assert read_regular(str(fifo)).error.code == 'nonregular'
    assert read_regular(str(tmp_path)).error is not None


def test_duplicate_projects_jobs_and_identities():
    for scenario, suffix in [('registry-duplicate-project', 'duplicate project example'),
                             ('registry-duplicate-job', 'duplicate job id tick'),
                             ('registry-duplicate-identity', 'duplicate identity local/gui/501/com.unattended.tick')]:
        files = FixtureFiles(scenario)
        result = load_registry(FIXTURES/scenario, 501, files)
        assert any(e.message.endswith(suffix) for e in result.errors)
        before = list(files.reads)
        assert join_plists(result, files) == result
        assert files.reads == before
    obj = copy.deepcopy(BASE)
    obj['jobs'].append(dict(copy.deepcopy(obj['jobs'][0]), id='other', label='another.label'))
    assert not parse(obj).errors


def test_literal_paths_and_argv():
    obj = copy.deepcopy(BASE)
    obj['jobs'][0].update(expected_program='/does not exist/$LITERAL/~tool',
                          expected_working_directory='/does not exist/directory',
                          expected_arguments=['arbitrary argv zero', '', 'two words', '$HOME', '~'])
    result = parse(obj)
    assert not result.errors
    files = FixtureFiles()
    joined = join_plists(result, files)
    assert not joined.errors
    job = joined.jobs[0].registry
    assert job.expected_program == '/does not exist/$LITERAL/~tool'
    assert job.expected_arguments == ('arbitrary argv zero', '', 'two words', '$HOME', '~')
    assert files.reads == ['/fleet-fixtures/com.unattended.tick.plist']


def test_plist_join_errors():
    import plistlib
    cases = [(None, Error('missing', 'not found'), 'plist missing'),
             (None, Error('unreadable', 'denied'), 'plist unreadable: denied'),
             (None, Error('too_large', 'file exceeds 1048576 bytes'), 'plist unreadable: file exceeds 1048576 bytes'),
             (b'invalid', None, 'invalid plist: InvalidFileException: malformed plist'),
             (b'<plist><key>x</key></plist>', None, 'invalid plist: IndexError: malformed plist'),
             (b'<plist><date>x</date></plist>', None, 'invalid plist: AttributeError: malformed plist'),
             (plistlib.dumps({}), None, 'plist Label missing'),
             (plistlib.dumps({'Label': 'wrong'}), None, 'plist Label wrong differs from com.unattended.tick')]
    class FakeFiles:
        def read_regular(self, path, limit):
            assert limit == LIMIT
            return observed(content, ('read', path), error)
    for content, error, suffix in cases:
        result = join_plists(parse(BASE), FakeFiles())
        assert result.errors[0].message == 'test.md:jobs[0].plist_path: ' + suffix
    for name in ('com.google.keystone.agent', 'com.google.keystone.xpcservice'):
        obj = changed('jobs[0].plist_path', '/fleet-fixtures/' + name + '.plist')
        assert join_plists(parse(obj), FixtureFiles()).errors[0].message.endswith('plist Label missing')


def test_declared_entrypoint_and_no_collection(materialized, capsys, monkeypatch):
    monkeypatch.setattr(os, 'getuid', lambda: 501)
    assert cli.main(['declared', str(materialized/'registry-valid')]) == 0
    output = capsys.readouterr()
    assert output.out.count(' declared: ') == 1 and not output.err
    assert cli.main(['declared', str(materialized/'registry-valid'), '--json']) == 0
    report = json.loads(capsys.readouterr().out)
    assert set(report) == {'schema_version','command','domain','observed_at','jobs','issues','summary','exit_code'}
    assert report['jobs'][0]['observations']['service']['data'] is None
    assert cli.main(['declared', str(materialized/'registry-schema-errors')]) == 3
    output = capsys.readouterr()
    assert 'unknown field' in output.err and not output.out
    for args, code in [(['--help'], 0), (['audit'], 3), (['declared','--unknown'], 3)]:
        with pytest.raises(SystemExit) as exc:
            cli.main(args)
        assert exc.value.code == code
        capsys.readouterr()
    entry = next(e for e in importlib.metadata.distribution('fleet-audit').entry_points if e.name == 'fleet-audit')
    assert entry.load() is cli.main
    prove_registry()
    package = Path(cli.__file__).parent
    for source in package.glob('*.py'):
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.Import):
                assert all(alias.name != 'subprocess' or source.name == 'collect.py' for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                assert node.module != 'subprocess' or source.name == 'collect.py'
    assert (package/'collect.py').exists()
    with pytest.raises(AssertionError, match='Library'):
        Path('/Users/byron/Library/forbidden').read_bytes()
    import subprocess
    with pytest.raises(AssertionError, match='process'):
        subprocess.run(['true'])


def test_values_require_explicit_matching():
    for value in (Known(True), Known(False), Known(0), Absent('missing'), Unknown('failed'), Unsupported((), 'unsupported')):
        with pytest.raises(TypeError):
            bool(value)
        with pytest.raises(TypeError):
            not value
