# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Summarize an external full-detail GeoJSON using spherical Lambert equal-area metres."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline.geography import KINDS, PRODUCT, summary, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Full-detail FeatureCollection outside the repository')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve().is_relative_to(PRODUCT.parents[1]):
        parser.error('Full-detail input must be outside the repository')
    raw = args.input.read_bytes()
    collection = json.loads(raw)
    properties = collection['features'][0]['properties']
    kind = next(k for k, (prop, _) in KINDS.items() if prop in properties)
    validate(collection, kind)
    sha = hashlib.sha256(raw).hexdigest()
    result = dict(schema_version=1, kind=kind, input_sha256=sha,
                  projection='Spherical Lambert cylindrical equal-area; R=6371008.8 m; central meridian=173; standard parallel=-41; longitude unwrapped about 173',
                  features=[summary(f, KINDS[kind][0]) for f in collection['features']])
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('Input sha256: ' + sha)


if __name__ == '__main__':
    main()
