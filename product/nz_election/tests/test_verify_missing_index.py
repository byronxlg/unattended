"""Missing required families take precedence over stale inventory and site errors."""
import subprocess
import sys
from pathlib import Path

import pytest

from product.nz_election.pipeline import night, verify
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.refresh import refresh


SCRIPT = Path(verify.__file__)


@pytest.fixture(scope='module')
def missing_index(tmp_path_factory):
    root = tmp_path_factory.mktemp('missing-night-index')
    data = root / 'data'
    refresh(data, now='2026-10-17T01:00:00Z')
    daily_refresh(data, loaders={'night': night.load})
    site = build(data, root / 'site' / 'nz-election')
    for bundle in (data, site / 'data'):
        assert 'night/index.json' in (bundle / 'manifest.json').read_text()
        (bundle / 'night/index.json').unlink()
    return {'data': data, 'site': site, 'site-parent': site.parent}


@pytest.mark.parametrize('check,required', [
    ('all', 'night,waterfall'), ('waterfall', None), ('night', None),
    ('polls', 'waterfall'),
])
@pytest.mark.parametrize('source', ['data', 'site', 'site-parent'])
def test_required_missing_index_precedes_validation(missing_index, check, required, source):
    option = '--data' if source == 'data' else '--site'
    args = [check, option, str(missing_index[source])]
    if required is not None:
        args += ['--require', required]
    result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stderr == f'FAIL {check}: MISSING_NIGHT_FAMILY\n'
    assert result.stdout == ''
