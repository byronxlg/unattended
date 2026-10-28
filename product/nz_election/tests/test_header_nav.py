"""Navigation regressions without changing the protected no-JavaScript harness."""
from pathlib import Path
import subprocess

import pytest

from product.nz_election.pipeline.scripts import HEADER_INIT, validate_scripts
from product.nz_election.tests.test_design import built_design  # noqa: F401


def test_header_nav_browser(built_design, tmp_path):
    _, site = built_design
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('header_nav_browser.py')),
                             str(site), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS header navigation:' in result.stdout


def test_header_inline_handler_validation():
    from html import escape
    assert validate_scripts(f'<body onload="{escape(HEADER_INIT, quote=True)}"></body>')
    for source in ('alert(1)', HEADER_INIT + '\nalert(1)'):
        with pytest.raises(ValueError, match='UNSAFE_SCRIPT'):
            validate_scripts(f'<body onload="{escape(source, quote=True)}"></body>')
    with pytest.raises(ValueError, match='UNSAFE_SCRIPT'):
        validate_scripts(f'<img onload="{escape(HEADER_INIT, quote=True)}">')
