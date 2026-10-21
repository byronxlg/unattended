# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check packaged night files without a page or network dependency."""
from pathlib import Path
import json
import sys
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import night


def check(root):
    night.validate(root)
    index = json.loads((Path(root) / 'night/index.json').read_text())['data']
    replay = next(s for s in index if s['sequence_id'] == 'illustrative-2023')
    end = json.loads((Path(root) / replay['snapshot_paths'][-1]).read_text())['data'][0]
    assert end['valid_party_votes'] == 2851211
    assert end['reported_house'] == 122
    assert end['mode'] == night.LABEL
    return end


if __name__ == '__main__':
    check(Path(sys.argv[1]))
    print('PASS night smoke: 2851211 valid party votes; House 122')
