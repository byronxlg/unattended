"""Every declared return remains readable within the phone viewport."""
from pathlib import Path
import subprocess

from product.nz_election.tests.test_home import populated


def test_funding_returns_fit_phone(populated, tmp_path):
    _, site = populated
    result = subprocess.run(
        ['uv', 'run', str(Path(__file__).with_name('funding_rows_browser.py')),
         '--site', str(site.parent), '--out', str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
