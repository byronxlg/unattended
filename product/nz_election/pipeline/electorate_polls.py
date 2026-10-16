"""Local poll tables kept separate from national and demographic measures."""
from decimal import Decimal, InvalidOperation
import re
from . import daily_sources as ds
from . import poll_parser as p
from .models import ParseDrift
from .refresh import config

PATH = 'wikipedia/polls-2026.wikitext'


def parse(text, acquired):
    if not isinstance(text, str) or len(text.encode()) > p.LIMIT:
        raise ParseDrift('local_size_limit')
    registry = {r['name']: r for r in config('electorates')}
    result, selected = [], 0
    for section, line, body in p.tables(text):
        if not section or section[0] != 'Electorate polling':
            continue
        selected += 1
        if len(section) != 3 or section[1] not in {'General electorates', 'Māori electorates'}:
            raise ParseDrift('local_section')
        chunks = p.split_markup(body, '\n|-')
        header = [p.clean(v) for a, v in p.row_cells(chunks[0])]
        if (header[:4] != ['Date', 'Polling organisation', 'Sample size', ''] or header[-1] != 'Lead'
                or not header[4:-1] or len(set(header[4:-1])) != len(header[4:-1])
                or set(header[4:-1]) - {'NAT', 'LAB', 'GRN', 'ACT', 'NZF', 'TPM', 'OPP', 'IND', 'Others'}):
            raise ParseDrift('local_headers')
        carry = {}
        for index, chunk in enumerate(chunks[1:], 1):
            cells, source = [], iter(p.row_cells(chunk))
            for column in range(len(header)):
                if column in carry:
                    attrs, value, remaining = carry.pop(column)
                    if remaining > 1:
                        carry[column] = attrs, value, remaining - 1
                else:
                    item = next(source, None)
                    if item is None:
                        raise ParseDrift('local_width')
                    attrs, value = item
                    attr = p.attributes(attrs)
                    if 'colspan' in attr or ('rowspan' in attr and (column > 2 or attr['rowspan'] != '2')):
                        raise ParseDrift('local_merge')
                    if 'rowspan' in attr:
                        carry[column] = attrs, value, 1
                cells.append((attrs, value))
            if next(source, None) is not None:
                raise ParseDrift('local_width')
            visible = p.clean(cells[0][1])
            if re.fullmatch(r'[A-Za-z]{3} 2026', visible):
                start = end = None
            else:
                start, end = p.dates(*reversed(cells[0]))
            measure = {'party vote': 'party_vote', 'electorate vote': 'candidate_vote'}.get(p.clean(cells[3][1]).lower())
            if not measure:
                raise ParseDrift('local_measure')
            shares = {}
            for name, (_, value) in zip(header[4:-1], cells[4:-1]):
                visible_value = p.clean(value.replace('{{n/a}}', ''))
                approximate = visible_value.startswith('~')
                number = visible_value.lstrip('~')
                if number in ('', '-', 'N/A'):
                    shares[name] = dict(value=None, approximate=False)
                    continue
                try:
                    decimal = Decimal(number)
                    if not decimal.is_finite() or not 0 <= decimal <= 100 or decimal.as_tuple().exponent < -2:
                        raise InvalidOperation
                except InvalidOperation:
                    raise ParseDrift('local_share') from None
                shares[name] = dict(value=int(decimal * 100), approximate=approximate)
            sample = p.clean(cells[2][1]).replace(',', '')
            if sample and (not sample.isascii() or not sample.isdigit() or int(sample) < 1):
                raise ParseDrift('local_sample')
            electorate = registry.get(section[-1])
            refs = ds.refs(PATH, f'table:{line}/row:{index}', ['shares', 'measure', 'fieldwork_start', 'fieldwork_end', 'sample'])
            result.append(dict(id=f'local-{line}-{index}', poll_id=f'local-{line}-{index}',
                               electorate_id=electorate['id'] if electorate else None,
                               pollster=p.clean(cells[1][1]), fieldwork_start=start, fieldwork_end=end,
                               observed_at=end or acquired, sample=int(sample) if sample else None,
                               measure=measure, shares=shares, scale=100,
                               reference_urls=sorted(set(re.findall(r'https?://[^\s|<>}\]]+', cells[1][1]))),
                               boundary_basis=dict(source_name=section[-1], basis='2026 electorate polling; source does not specify boundary version',
                                                   mapping='exact registry name' if electorate else 'Unresolved', fieldwork_label=visible),
                               source_ref=refs))
        if carry:
            raise ParseDrift('local_unfinished_merge')
    if 'Electorate polling' in text and not selected:
        raise ParseDrift('local_missing_tables')
    return result


def load():
    raw, sources, hashes = ds.inputs({PATH})
    return {'electorate-polls': parse(raw[PATH].decode(), ds.acquired(sources, PATH))}, sources, hashes
