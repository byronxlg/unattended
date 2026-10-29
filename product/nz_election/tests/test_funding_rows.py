"""Every declared return remains readable within the phone viewport."""
import os
from pathlib import Path
import signal
import subprocess

from product.nz_election.tests.test_home import populated


def test_funding_returns_fit_phone(populated, tmp_path):
    _, site = populated
    process = subprocess.Popen(
        ['uv', 'run', str(Path(__file__).with_name('funding_rows_browser.py')),
         '--site', str(site.parent), '--out', str(tmp_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        # Kill the session's process group even if the parent exited with pipes still open.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        raise AssertionError(f'Funding browser exceeded 300 s; process group killed.\n{stdout}{stderr}') from None
    assert process.returncode == 0, stdout + stderr
