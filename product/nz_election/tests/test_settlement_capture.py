"""The preparation CLI never exposes untrusted bundle text in failure output."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from product.nz_election.pipeline import export, settlement_capture

SENTINEL = 'UNTRUSTED_SETTLEMENT_SENTINEL'


def bad_timestamp():
    envelope = export.envelope({}, [], 'offline-verification', 'a' * 40)
    envelope['data'] = {SENTINEL: {'generated_at': 'bad timestamp'}}
    return json.dumps(envelope)


@pytest.mark.parametrize('raw', ['', 'null', '42', '[]', bad_timestamp(), '1.5',
                                  str(10**100), json.dumps(SENTINEL + '\x00')],
                         ids=['empty', 'null', 'number', 'list', 'timestamp-key',
                              'float', 'huge', 'unusual-string'])
def test_cli_sanitizes_malformed_bundle(tmp_path, raw):
    data = tmp_path / 'data'
    data.mkdir()
    for name in ('manifest.json', 'status.json'):
        (data / name).write_text(raw)
    for name in ('manifest.csv', 'status.csv', 'LICENCES.md'):
        (data / name).write_text('')
    out = tmp_path / 'capture.json'
    result = subprocess.run([sys.executable, '-B', str(Path(settlement_capture.__file__)),
                             '--data', str(data), '--out', str(out)], capture_output=True, text=True)
    assert result.returncode != 0
    assert result.stdout == ''
    assert SENTINEL not in result.stdout + result.stderr
    assert result.stderr == 'NIGHT_CAPTURE_PREP_FAILED\n'
    assert not out.exists()
