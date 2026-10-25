"""Aggregate acceptance distinguishes optional and required night checks."""
import subprocess
import sys
from pathlib import Path

import pytest

from product.nz_election.pipeline import night, verify
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.refresh import refresh


SCRIPT = Path(verify.__file__)


@pytest.fixture
def bundle(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-17T01:00:00Z')
    return data


def run_verify(data, *options):
    return subprocess.run([sys.executable, str(SCRIPT), 'all', '--data', str(data), *options],
                          capture_output=True, text=True)


def test_absent_optional_families_are_reported(bundle):
    result = run_verify(bundle)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ''
    assert [line for line in result.stdout.splitlines() if line.startswith('SKIP')] == [
        'SKIP night: family absent (night/index.json)',
        'SKIP waterfall: family absent (night/index.json)',
    ]
    assert 'PASS night\n' not in result.stdout
    assert 'PASS waterfall\n' not in result.stdout
    assert result.stdout.endswith('PASS all\n')


@pytest.mark.parametrize('required', ['night', 'waterfall', 'night,waterfall'])
def test_absent_required_family_fails(bundle, required):
    result = run_verify(bundle, '--require', required)
    assert result.returncode != 0
    assert result.stderr == 'FAIL all: MISSING_NIGHT_FAMILY\n'
    assert 'PASS all' not in result.stdout
    assert f'SKIP {required.split(",")[0]}:' not in result.stdout


def test_present_required_families_are_verified(bundle):
    daily_refresh(bundle, loaders={'night': night.load})
    result = run_verify(bundle, '--require', 'night,waterfall')
    assert result.returncode == 0, result.stderr
    assert result.stderr == ''
    assert 'PASS night\nPASS waterfall\n' in result.stdout
    assert 'SKIP' not in result.stdout
    assert result.stdout.endswith('PASS all\n')


@pytest.mark.parametrize('name', ['', 'null', '[]', '{}', 'true', '1.5', '9' * 1000,
                                   'ｎight', 'night,', 'night,private-token', 'all'])
def test_invalid_requirement_is_redacted(name, capsys):
    with pytest.raises(SystemExit) as raised:
        verify.cli(['all', '--require', name])
    assert str(raised.value) == 'FAIL all: CAMPAIGN_DATA'
    assert capsys.readouterr().out == ''


def test_required_check_names_accept_existing_checks():
    args = verify.parse_args(['all', '--require', 'polls,thresholds'])
    assert args.require == 'polls,thresholds'
