# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Official candidacies with explicit reviewed supplemental identity joins."""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import daily_sources as ds
from product.nz_election.pipeline.refresh import config, PRODUCT

SHEET = 'ec-2026/wayback-electorate-candidates.xlsx'
PDF = 'ec-2026/wayback-party-lists.pdf'
WIKI = 'wikipedia/candidates-2026.wikitext'
WD = 'wikidata/candidacies-2026.sparql.json'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def nfc(value):
    return unicodedata.normalize('NFC', value)


def spreadsheet(raw):
    if not isinstance(raw, bytes) or len(raw) > 2_000_000:
        raise ValueError('INVALID_CANDIDATE_SHEET')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            if (len(infos) > 100 or len({i.filename for i in infos}) != len(infos)
                    or sum(i.file_size for i in infos) > 8_000_000
                    or any(i.file_size > 2_000_000 or i.flag_bits & 1 for i in infos)):
                raise ValueError('INVALID_CANDIDATE_SHEET')
            def xml(path):
                p = PurePosixPath(path)
                if p.is_absolute() or '..' in p.parts:
                    raise ValueError('INVALID_CANDIDATE_SHEET')
                data = archive.read(path)
                if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
                    raise ValueError('INVALID_CANDIDATE_SHEET')
                return ET.fromstring(data)
            book = xml('xl/workbook.xml')
            sheets = book.findall('s:sheets/s:sheet', NS)
            if len(sheets) != 1:
                raise ValueError('INVALID_CANDIDATE_SHEET')
            relations = {r.get('Id'): r for r in xml('xl/_rels/workbook.xml.rels')}
            relation = relations[sheets[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            if relation.get('TargetMode') == 'External':
                raise ValueError('INVALID_CANDIDATE_SHEET')
            strings = [''.join(n.itertext()) for n in xml('xl/sharedStrings.xml')]
            records = []
            for row in xml('xl/' + relation.get('Target')).findall('s:sheetData/s:row', NS):
                cells = {}
                for cell in row:
                    match = re.fullmatch(r'([A-Z]+)([1-9][0-9]*)', cell.get('r', ''))
                    if not match or match[1] in cells or cell.find('s:f', NS) is not None:
                        raise ValueError('INVALID_CANDIDATE_SHEET')
                    value = cell.findtext('s:v', '', NS)
                    if cell.get('t') == 's':
                        if not re.fullmatch(r'[0-9]{1,6}', value):
                            raise ValueError('INVALID_CANDIDATE_SHEET')
                        value = strings[int(value)]
                    elif cell.get('t') == 'inlineStr':
                        value = ''.join(cell.find('s:is', NS).itertext())
                    cells[match[1]] = value
                if cells:
                    records.append((int(row.get('r')), cells))
            header = records[0][1]
            if set(header.values()) != {'Electorate', 'Party', 'Name'} or len(header) != 3:
                raise ValueError('INVALID_CANDIDATE_SHEET')
            result = []
            for number, cells in records[1:]:
                if set(cells) != set(header) or any(not v.strip() for v in cells.values()):
                    raise ValueError('INVALID_CANDIDATE_SHEET')
                result.append(dict(row=number, **{header[k]: v for k, v in cells.items()}))
            if not result or len(result) > 5000 or len({r['row'] for r in result}) != len(result):
                raise ValueError('INVALID_CANDIDATE_SHEET')
            return result
    except (zipfile.BadZipFile, ET.ParseError, KeyError, IndexError, TypeError, AttributeError, ValueError):
        raise ValueError('INVALID_CANDIDATE_SHEET') from None


def apply_mappings(rows, mappings):
    by_id = {r['id']: r for r in rows}
    conflicts = []
    for mapping in mappings:
        if not mapping.get('reviewer') or not mapping.get('evidence'):
            raise ValueError('UNREVIEWED_CANDIDATE_MAPPING')
        row = by_id[mapping['candidate_id']]
        if mapping['electorate_id'] != row['electorate_id'] or mapping['party_id'] != row['party_id']:
            raise ValueError('CANDIDATE_MAPPING_MISMATCH')
        for field, claims in mapping['claims'].items():
            if field not in {'name', 'party_id', 'list_rank', 'wikidata_id', 'wikipedia_url', 'person_id'}:
                raise ValueError('INVALID_CANDIDATE_CLAIM')
            if any(not c.get('source_id') or not c.get('locator') for c in claims):
                raise ValueError('INVALID_CANDIDATE_CLAIM')
            all_claims = ([dict(value=row[field], **row['field_sources'][field][0])] if row[field] is not None else []) + claims
            if len({json.dumps(c['value'], sort_keys=True) for c in all_claims}) > 1:
                identity = 'conflict-' + str(len(conflicts) + 1)
                conflicts.append(dict(id=identity, person_id=row['person_id'], electorate_id=row['electorate_id'],
                                      field=field, claims=all_claims, resolution='Unresolved', review_ref=mapping['evidence'],
                                      source_ref=claims, observed_at=row['observed_at']))
                row['conflict_ids'].append(identity)
            elif claims:
                row[field] = claims[0]['value']
                row['field_sources'][field] = claims
        row['join_status'] = 'Unresolved' if row['conflict_ids'] else 'Reviewed'
    return conflicts


def load():
    mappings = config('candidate-mappings')['mappings']
    supplemental = {claim['source_id'] for mapping in mappings for claims in mapping['claims'].values() for claim in claims}
    if supplemental - {WIKI, WD}:
        raise ValueError('INVALID_SUPPLEMENTAL_SOURCE')
    raw, sources, hashes = ds.inputs({SHEET, PDF} | supplemental, ('electorate-aliases', 'candidate-mappings', 'ec-party-lists-2026'))
    aliases = config('electorate-aliases')
    registry = {r['id']: r['name'] for r in config('electorates')}
    if any(nfc(name) != nfc(registry.get(identity, '')) for name, identity in aliases.items()):
        raise ValueError('INVALID_ELECTORATE_ALIAS')
    rows = []
    def candidate(identity, name, party, electorate, rank, path, locator):
        fields = ds.refs(path, locator, ('name', 'party_id', 'electorate_id', 'list_rank', 'person_id'))
        return dict(id=identity, person_id=None, name=name, party_id=party, electorate_id=electorate,
                    list_rank=rank, wikidata_id=None, wikipedia_url=None, join_status='Unavailable: identity review pending',
                    conflict_ids=[], field_sources={f['field']: [f] for f in fields}, source_ref=fields,
                    observed_at=ds.acquired(sources, path))
    for row in spreadsheet(raw[SHEET]):
        rows.append(candidate('ec-row-' + str(row['row']), row['Name'], row['Party'], aliases.get(nfc(row['Electorate'])),
                              None, SHEET, 'Candidates!row:' + str(row['row'])))
    lists = []
    transcription = config('ec-party-lists-2026')
    from product.nz_election.pipeline.export import digest
    if digest(raw[PDF]) != transcription['source']['sha256']:
        raise ValueError('PARTY_LIST_HASH_MISMATCH')
    for index, party in enumerate(transcription['parties'], 1):
        ids = []
        for rank, entry in enumerate(party['candidates'], 1):
            if entry['rank'] != rank:
                raise ValueError('INVALID_LIST_RANK')
            identity = f'ec-list-{index}-{rank}'
            ids.append(identity)
            loc = entry['locator']
            locator = f'page:{loc["page"]}/column:{loc["column"]}/line:{loc["line"]}'
            rows.append(candidate(identity, entry['name'], party['party_name'], None, rank, PDF, locator))
        refs = ds.refs(PDF, 'party:' + party['party_name'], ('party_id', 'candidate_ids', 'complete', 'review_ref'))
        lists.append(dict(id='list-' + str(index), party_id=party['party_name'], candidate_ids=ids, complete=False,
                          review_ref='Rank transcription reviewed; identity review pending. Capacity unchecked.',
                          source_ref=refs, field_sources=refs, observed_at=ds.acquired(sources, PDF)))
    conflicts = apply_mappings(rows, mappings)
    return {'candidates': rows, 'party-lists': lists, 'candidate-review': conflicts}, sources, hashes


def propose(out):
    out = Path(out).resolve()
    if out.is_relative_to((PRODUCT / 'config').resolve()):
        raise ValueError('PROPOSAL_MUST_BE_OUTSIDE_CONFIG')
    raw, _, _ = ds.inputs({SHEET, WIKI, WD})
    # The statement capture has identifiers but no labels, so it cannot prove a name agreement.
    from product.nz_election.pipeline.poll_parser import clean, split_markup
    boxes = []
    text = raw[WIKI].decode()
    for section in re.split(r'^===([^=\n]+)===\s*$', text, flags=re.M)[1:][::2]:
        start = text.index('===' + section + '===')
        end = text.find('\n===', start + len(section) + 6)
        body = text[start:end if end >= 0 else len(text)]
        for match in re.finditer(r'\{\{NZ election box candidate\b', body):
            pos, depth = match.end(), 1
            while pos < len(body) and depth:
                if body[pos:pos+2] == '{{':
                    depth += 1
                    pos += 2
                elif body[pos:pos+2] == '}}':
                    depth -= 1
                    pos += 2
                else:
                    pos += 1
            fields = {}
            for part in split_markup(body[match.end():pos-2], '|'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    if key.strip() in {'party', 'candidate'}:
                        fields[key.strip()] = clean(value)
            if {'party', 'candidate'} <= fields.keys():
                boxes.append((nfc(fields['candidate']), nfc(fields['party']), nfc(section.strip()),
                              f'offset:{start + match.start()}'))
    proposed = []
    for row in spreadsheet(raw[SHEET]):
        matches = [b for b in boxes if b[:3] == (nfc(row['Name']), nfc(row['Party']), nfc(row['Electorate']))]
        if len(matches) == 1:
            proposed.append(dict(ec_row=row['row'], name=row['Name'], party=row['Party'], electorate=row['Electorate'],
                                 ec_locator=f'Candidates!row:{row["row"]}', wikipedia_locator=matches[0][3],
                                 revision='1380178146', reviewed=False))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(schema='candidate-proposals-v1', proposals=proposed,
                                  notes='Exact NFC triple only. Wikidata has no labels; no label agreements can be established.'), ensure_ascii=False, indent=2) + '\n')
    return len(proposed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['propose-mappings'])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(f'PASS proposals: {propose(args.out)} rows')
