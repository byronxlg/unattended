"""Real captured national sequences, plus explicitly synthetic unreported details."""
from datetime import datetime, timedelta, timezone
import json
from xml.sax.saxutils import escape
from product.nz_election.pipeline import fixtures, xml_parser


class Clock:
    def __init__(self):
        self.seconds = 0
        self.origin = datetime(2026, 11, 7, 6, tzinfo=timezone.utc)
    def now(self):
        return self.origin + timedelta(seconds=self.seconds)
    def monotonic(self):
        return self.seconds
    def sleep(self, seconds):
        self.seconds += seconds


def captures(demo=False, observation=1):
    prefix = 'ec-mediademo-xml/' if demo else 'ec-2026-media-xml/'
    paths = {e['path'] for e in json.loads((fixtures.ROOT / 'manifest.json').read_text())['entries'] if e['path'].startswith(prefix)}
    raw = {p.removeprefix(prefix): b for p, b in fixtures.captures(paths=paths).items()}
    if demo:
        raw['election.xml'] = raw[f'election-obs{observation}.xml']
    refs = xml_parser.references(*(raw[n + '.xml'] for n in ('parties', 'electorates', 'candidates')))
    for ident in refs['electorates']:
        path = f'e{int(ident):02}/e{int(ident):02}.xml'
        if path in raw:
            continue
        candidates = [c for c, row in refs['candidates'].items() if row['electorate'] == ident]
        # Missing captured details are synthetic zeros, never represented as official captures.
        stats = dict(total_voting_places=0, total_voting_places_counted=0, percent_voting_places_counted=0,
                     total_votes_cast=0, percent_votes_cast=0, total_party_informals=0, total_candidate_informals=0,
                     total_registered_parties=len(refs['parties']), total_candidates=len(candidates))
        raw[path] = (f'<electorate e_no="{ident}" final="true" updated="2026-10-22T00:00:00"><statistics>' +
            ''.join(f'<{k}>{v}</{k}>' for k, v in stats.items()) + '</statistics><partyvotes>' +
            ''.join(f'<party p_no="{escape(p)}"><votes>0</votes></party>' for p in refs['parties']) + '</partyvotes><candidatevotes>' +
            ''.join(f'<candidate c_no="{c}"><votes>0</votes></candidate>' for c in candidates) + '</candidatevotes></electorate>').encode()
    return raw
