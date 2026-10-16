"""Manifest-checked inputs and field provenance for offline daily families."""
import json
from . import export
from .fixtures import ROOT, captures
from .refresh import PRODUCT, config


def inputs(paths, configs=()):
    raw = captures(paths=set(paths))
    entries = [e for e in json.loads((ROOT / 'manifest.json').read_text())['entries'] if e['path'] in raw]
    sources = [dict(id=e['path'], url=e['url'], revision=e['revision'], licence=e['licence'],
                    fetched_at=e['captured_at'], history_url=(
                        'https://en.wikipedia.org/w/index.php?title=Candidates_in_the_2026_New_Zealand_general_election_by_electorate&action=history'
                        if e['path'].startswith('wikipedia/candidates') else None)) for e in entries]
    hashes = {'fixtures/' + e['path']: e['sha256'] for e in entries}
    for name in ('electorates', *configs):
        hashes['config/' + name + '.json'] = export.digest((PRODUCT / 'config' / (name + '.json')).read_bytes())
    hashes['electorates.data'] = export.digest(export.canonical(config('electorates')).encode())
    return raw, sources, hashes


def refs(path, locator, fields):
    return [dict(field=f, source_id=path, locator=locator) for f in fields]


def acquired(sources, path):
    return next(s['fetched_at'] for s in sources if s['id'] == path)
