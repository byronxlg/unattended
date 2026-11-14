"""Pages acceptance still passes on a site built after polling close (incident 7 to 14 Nov 2026)."""
import subprocess
import sys
from pathlib import Path

from product.nz_election.pipeline import build, verify
from product.nz_election.pipeline.refresh import refresh

POST_CLOSE = '2026-11-08T06:01:00Z'


def test_verify_all_accepts_a_post_close_build(tmp_path):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-17T01:00:00Z')
    site = tmp_path / 'site'
    built = subprocess.run([sys.executable, str(Path(build.__file__)), '--data', str(data),
                            '--out', str(site / 'nz-election'), '--now', POST_CLOSE],
                           capture_output=True, text=True)
    assert built.returncode == 0, built.stderr
    result = subprocess.run([sys.executable, str(Path(verify.__file__)), 'all', '--data', str(data),
                             '--site', str(site)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith('PASS all\n')
