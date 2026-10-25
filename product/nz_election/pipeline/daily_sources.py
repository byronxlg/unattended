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


def live_loaders(acquire=None, *, now=None, event=None):
    """Acquire in memory; failures propagate to atomic last-good family retention."""
    from . import fetch, markets, candidates, baseline, enrolment, electorate_polls, advance, night
    from .sunsets import require_collection
    transport = acquire or fetch.acquire
    def acquire(**kwargs):
        require_collection('daily', now() if callable(now) else now, event)
        return transport(**kwargs)
    messages = {}

    def market_loader():
        results = {}
        for event in markets.events():
            path = 'polymarket/' + event['slug'] + '.json'
            result = acquire(url=fetch.gamma_url(event['slug']))
            markets.parse(result['raw'], event['slug'], event['family'], result['fetched_at'])
            results[path] = result
        def live_inputs(paths, configs):
            # Validate committed evidence before selecting live replacements.
            raw, sources, hashes = inputs(paths, configs)
            for source in sources:
                path = source['id']
                result = results[path]
                raw[path] = result['raw']
                source.update(fetched_at=result['fetched_at'], revision=None)
                hashes.pop('fixtures/' + path)
                hashes['live/' + path] = export.digest(raw[path])
            return raw, sources, hashes
        payload = markets.load(live_inputs)
        messages['markets'] = 'Live Gamma observations. Amounts in USD per supervisor review.'
        return payload

    def candidate_loader():
        result = acquire(url=fetch.CANDIDATE_URL)
        def live_inputs(paths, configs):
            raw, sources, hashes = inputs(set(paths) | {candidates.WIKI}, configs)
            # Reviewed claims cannot silently acquire new revision provenance.
            if candidates.WIKI in paths and raw[candidates.WIKI].decode() != result['wikitext']:
                raise ValueError('CANDIDATE_REVISION_REVIEW_REQUIRED')
            raw[candidates.WIKI] = result['wikitext'].encode()
            source = next(s for s in sources if s['id'] == candidates.WIKI)
            source.update(fetched_at=result['fetched_at'], revision=result['revision'],
                          url='https://en.wikipedia.org/w/index.php?oldid=' + result['revision'])
            hashes.pop('fixtures/' + candidates.WIKI)
            hashes['live/' + candidates.WIKI] = export.digest(raw[candidates.WIKI])
            return raw, sources, hashes
        payload = candidates.load(live_inputs)
        messages['candidates'] = ('Live Wikipedia candidate revision acquired; official EC spine from committed captures. '
                                  'Supplemental identities still require reviewed mappings.')
        return payload

    loaders = {'candidates': candidate_loader, 'baseline-2023': baseline.load, 'enrolment': enrolment.load,
            'electorate-polls': electorate_polls.load, 'markets': market_loader, 'night': night.load, 'advance': advance.load}
    def guarded(loader):
        def load():
            require_collection('daily', now() if callable(now) else now, event)
            return loader()
        return load
    return {name: guarded(loader) for name, loader in loaders.items()}, messages
