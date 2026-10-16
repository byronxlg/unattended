"""Original 2023 electorate results, never reallocated to successor boundaries."""
import csv
import io
import re
import xml.etree.ElementTree as ET
from . import daily_sources as ds
from .fixtures import ROOT

PARTY = 'ec-2023/party-votes.csv'
XML = 'ec-2023-xml/electorates.xml'


def csv_rows(raw):
    return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))


def candidate_votes(raw, number):
    rows = csv_rows(raw)
    if len(rows) < 4 or not re.search(r'\b' + str(number) + r'\b', rows[1][0]):
        raise ValueError('INVALID_BASELINE_SCHEMA')
    headers = rows[2]
    if headers[-2:] != ['Total Valid Candidate Votes', 'Informal Candidate Votes']:
        raise ValueError('INVALID_BASELINE_SCHEMA')
    if number == 39:
        if 'Port Waikato' not in rows[1][0] or not any('cancel' in c.lower() for r in rows for c in r):
            raise ValueError('INVALID_DEFERRED_CONTEST')
        return None
    start = [i for i, r in enumerate(rows) if r and r[0] == 'Electorate Candidate Valid Votes']
    totals = [r for r in rows if len(r) == len(headers) and r[1].endswith(' Total')]
    if len(start) != 1 or len(totals) != 1:
        raise ValueError('INVALID_BASELINE_TOTAL')
    result = []
    for line, row in enumerate(rows[start[0]+1:], start[0]+2):
        if not row:
            continue
        if len(row) != 4 or not row[2].isdigit():
            raise ValueError('INVALID_BASELINE_TOTAL')
        result.append(dict(name=row[0], party=row[1], votes=int(row[2]), locator='CSV row:' + str(line)))
    if [r['name'] for r in result] != headers[2:-2] or [r['votes'] for r in result] != list(map(int, totals[0][2:-2])):
        raise ValueError('BASELINE_TOTAL_MISMATCH')
    if sum(r['votes'] for r in result) != int(totals[0][-2]):
        raise ValueError('BASELINE_TOTAL_MISMATCH')
    return result


def load():
    paths = {PARTY, XML} | {f'ec-2023/candidate-votes-by-voting-place-{n}.csv' for n in range(1, 73)
                           if (ROOT / f'ec-2023/candidate-votes-by-voting-place-{n}.csv').is_file()}
    raw, sources, hashes = ds.inputs(paths, ('electorate-correspondence',))
    parties = csv_rows(raw[PARTY])
    header = parties[1]
    if header[0] != 'Electorate' or header[-3:] != ['Total Valid Party Votes', 'Informal Party Votes', 'Total Party Votes Counted']:
        raise ValueError('INVALID_BASELINE_SCHEMA')
    party_rows = {r[0]: (i, r) for i, r in enumerate(parties, 1) if len(r) == len(header)}
    result = []
    for old in ET.fromstring(raw[XML]):
        number, name = int(old.get('e_no')), old.findtext('electorate_name')
        line, party = party_rows[name]
        votes = [dict(name=p, votes=int(v), source_ref=ds.refs(PARTY, f'CSV row:{line}/column:{i}', ['votes']))
                 for i, (p, v) in enumerate(zip(header[1:-3], party[1:-3]), 2)]
        if sum(v['votes'] for v in votes) != int(party[-3]):
            raise ValueError('BASELINE_TOTAL_MISMATCH')
        path = f'ec-2023/candidate-votes-by-voting-place-{number}.csv'
        candidates = candidate_votes(raw[path], number) if path in raw else None
        if candidates is not None:
            for c in candidates:
                c['source_ref'] = ds.refs(path, c.pop('locator'), ['name', 'party', 'votes'])
        reason = 'Contest deferred; no general-election candidate baseline.' if number == 39 else 'Missing candidate capture.' if candidates is None else None
        refs = ds.refs(PARTY, f'CSV row:{line}', ['party_votes', 'old_name'])
        result.append(dict(id=f'ec-2023-{number}', old_electorate_id=number, old_name=name, election_date='2023-10-14',
                           result_as_of='2023-11-03', observed_at='2023-11-03', party_votes=votes, candidate_votes=candidates,
                           field_sources=dict(party_votes=refs, candidate_votes=(ds.refs(path, 'electorate total', ['candidate_votes']) if path in raw else []),
                                              candidate_status=reason), source_ref=refs))
    return {'baseline-2023': result}, sources, hashes
