"""Bounded EC archive parser. Source local timestamps remain unconverted."""
from datetime import datetime
from decimal import Decimal
import re
import xml.etree.ElementTree as ET
from .export import canonical, digest

MAX_BYTES = 2_000_000
COUNT_FIELDS = {'votes', 'party_seats', 'candidate_seats', 'total_seats', 'list_no',
                'total_voting_places_counted', 'total_votes_cast', 'total_electorates_final',
                'total_minimal_votes', 'total_special_votes', 'total_registered_parties'}


def count(value):
    if type(value) is not str or not re.fullmatch(r'0|[1-9][0-9]{0,8}', value):
        raise ValueError('XML_COUNT')
    return int(value)


def percent(value):
    if type(value) is not str or not re.fullmatch(r'[0-9]{1,3}(?:\.[0-9]{1,2})?', value) or Decimal(value) > 100:
        raise ValueError('XML_PERCENT')
    return value


def document(raw, tag):
    if type(raw) is not bytes or not raw or len(raw) > MAX_BYTES:
        raise ValueError('XML_DOCUMENT')
    try:
        text = raw.decode('utf-8-sig')
        if re.search(r'<!DOCTYPE|<!ENTITY', text, re.I):
            raise ValueError
        root = ET.fromstring(text)
        if root.tag != tag:
            raise ValueError
        return root
    except (ValueError, ET.ParseError):
        raise ValueError('XML_DOCUMENT') from None


def fields(node, required):
    if len(node) != len(required) or {x.tag for x in node} != set(required):
        raise ValueError('XML_FIELDS')
    result = {}
    for child in node:
        if child.tag in COUNT_FIELDS:
            count(child.text)
        if len(child) or child.attrib or not child.text or not child.text.strip():
            raise ValueError('XML_FIELDS')
        result[child.tag] = child.text
    return result


def records(root, tag, attr, required):
    result = {}
    for node in root:
        if node.tag != tag or set(node.attrib) != {attr}:
            raise ValueError('XML_REFERENCE')
        ident = node.get(attr)
        count(ident)
        if ident in result:
            raise ValueError('XML_REFERENCE')
        result[ident] = fields(node, required)
    if not result:
        raise ValueError('XML_REFERENCE')
    return result


def references(parties, electorates, candidates):
    refs = dict(
        parties=records(document(parties, 'parties'), 'party', 'p_no', ['abbrev', 'short_name', 'party_name', 'registered']),
        electorates=records(document(electorates, 'electorates'), 'electorate', 'e_no', ['electorate_name']),
        candidates=records(document(candidates, 'candidates'), 'candidate', 'c_no', ['candidate_name', 'electorate', 'party', 'list_no']))
    ranks = set()
    for c in refs['candidates'].values():
        rank = count(c['list_no'])
        if (c['party'] not in refs['parties'] and not (c['party'] == '0')) or (c['electorate'] != '0' and c['electorate'] not in refs['electorates']):
            raise ValueError('XML_REFERENCE')
        key = (c['party'], rank)
        if rank and key in ranks:
            raise ValueError('XML_REFERENCE')
        if rank:
            ranks.add(key)
    if any(p['registered'] not in {'yes', 'no'} for p in refs['parties'].values()):
        raise ValueError('XML_REFERENCE')
    return dict(refs, reference_version=digest(canonical(refs).encode()))


def election(raw, refs):
    root = document(raw, 'election')
    local = root.get('updated')
    try:
        if set(root.attrib) != {'updated'} or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d', local or ''):
            raise ValueError
        datetime.fromisoformat(local)
    except ValueError:
        raise ValueError('XML_TIMESTAMP') from None
    if [n.tag for n in root] != ['statistics', 'partystatus']:
        raise ValueError('XML_FIELDS')
    stats = fields(root[0], ['total_voting_places_counted', 'percent_voting_places_counted', 'total_votes_cast',
                            'percent_votes_cast', 'total_electorates_final', 'percent_electorates_final',
                            'total_minimal_votes', 'total_special_votes', 'total_registered_parties'])
    stats = {k: percent(v) if k.startswith('percent_') else count(v) for k, v in stats.items()}
    parties = records(root[1], 'party', 'p_no', ['votes', 'percent_votes', 'party_seats', 'candidate_seats', 'total_seats'])
    parties = {p: {k: percent(v) if k == 'percent_votes' else count(v) for k, v in row.items()} for p, row in parties.items()}
    if set(parties) - refs['parties'].keys():
        raise ValueError('XML_REFERENCE')
    valid = sum(p['votes'] for p in parties.values())
    if valid > stats['total_votes_cast'] or stats['total_electorates_final'] > len(refs['electorates']):
        raise ValueError('XML_TOTAL')
    for row in parties.values():
        # EC supplies truncated percentage strings, not a denominator of votes cast.
        if row['total_seats'] != row['party_seats'] + row['candidate_seats']:
            raise ValueError('XML_TOTAL')
        if not valid and (Decimal(row['percent_votes']) or row['total_seats']):
            raise ValueError('XML_TOTAL')
        if valid and abs(Decimal(row['percent_votes']) - Decimal(100 * row['votes']) / valid) > Decimal(1).scaleb(-len(row['percent_votes'].partition('.')[2])):
            raise ValueError('XML_TOTAL')
    return dict(reference_version=refs['reference_version'], source_updated_local=local,
                statistics=stats, party_results=parties, valid_party_votes=valid,
                reported_house=sum(p['total_seats'] for p in parties.values()))
