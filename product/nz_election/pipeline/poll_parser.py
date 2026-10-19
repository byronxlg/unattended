"""Bounded structural scanner for revision-pinned national poll tables."""
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import html
import re

from .models import ParseDrift, ParseResult, DriftReport

LIMIT = 2 * 1024 * 1024
# Allow publication within a week of fieldwork without accepting arbitrary date drift.
MAX_RELEASE_LAG_DAYS = 7


def attributes(text):
    """Consume every attribute so quoting cannot hide a merge or sort value."""
    values = {}
    token = re.compile(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+))")
    position = 0
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        match = token.match(text, position)
        if match is None:
            raise ParseDrift('invalid_attributes', text)
        key = match[1].lower()
        if key in values:
            raise ParseDrift('duplicate_attribute', key)
        values[key] = next(value for value in match.groups()[1:] if value is not None)
        position = match.end()
        if position < len(text) and not text[position].isspace():
            raise ParseDrift('invalid_attributes', text)
    for key in ('rowspan', 'colspan'):
        if key in values and not re.fullmatch(r'[1-9][0-9]*', values[key]):
            raise ParseDrift('unexplained_merge', text)
    return values


def reference_at(text, start):
    opening = re.match(r"<ref\b((?:\"[^\"]*\"|'[^']*'|[^'\">])*)>", text[start:], re.I)
    if opening is None:
        raise ParseDrift('invalid_ref')
    raw = opening[1].rstrip()
    use = raw.endswith('/')
    attrs = attributes(raw[:-1] if use else raw)
    end = start + opening.end()
    if use:
        if not attrs.get('name'):
            raise ParseDrift('unknown_named_ref')
        return end, attrs, None
    closing = re.search(r'</ref\s*>', text[end:], re.I)
    if closing is None:
        raise ParseDrift('unclosed_ref')
    content = text[end:end + closing.start()]
    if re.search(r'<ref\b', content, re.I):
        raise ParseDrift('nested_ref')
    return end + closing.end(), attrs, content


def references(text):
    position = 0
    while match := re.search(r'<!--|<ref\b|</ref\b', text[position:], re.I):
        start = position + match.start()
        if match[0] == '<!--':
            end = text.find('-->', start + 4)
            if end < 0:
                raise ParseDrift('unclosed_comment')
            position = end + 3
            continue
        if match[0].lower().startswith('</'):
            raise ParseDrift('unexpected_ref_close')
        end, attrs, content = reference_at(text, start)
        yield start, end, attrs, content
        position = end


def split_markup(text, separator):
    """Separators inside templates, links and citations are not table syntax."""
    result, start, i, stack = [], 0, 0, []
    while i < len(text):
        if len(stack) > 64:
            raise ParseDrift("nesting_limit")
        if text.startswith('<!--', i):
            end = text.find('-->', i + 4)
            if end < 0:
                raise ParseDrift("unclosed_comment")
            i = end + 3
            continue
        if re.match(r'<ref\b', text[i:], re.I):
            i, _, _ = reference_at(text, i)
            continue
        pair = text[i:i + 2]
        if pair in ('{{', '[['):
            stack.append('}}' if pair == '{{' else ']]')
            i += 2
        elif stack and text.startswith(stack[-1], i):
            i += len(stack.pop())
        elif text[i] == '[' and not stack:
            stack.append(']')
            i += 1
        elif not stack and text.startswith(separator, i):
            result.append(text[start:i])
            i += len(separator)
            start = i
        else:
            i += 1
    if stack:
        raise ParseDrift("unclosed_markup")
    return result + [text[start:]]


def clean(text):
    for start, end, _, _ in reversed(list(references(text))):
        text = text[:start] + text[end:]
    out, i = '', 0
    while i < len(text):
        if text.startswith('{{', i):
            start, depth = i + 2, 1
            i += 2
            while i < len(text) and depth:
                if text.startswith('{{', i):
                    depth += 1
                    i += 2
                elif text.startswith('}}', i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            if depth:
                raise ParseDrift("unclosed_template")
            template = text[start:i - 2]
            if template.split('|')[0].strip().lower() not in ('efn', 'refn'):
                raise ParseDrift("unknown_template", template[:80])
        else:
            out += text[i]
            i += 1
    out = re.sub(r'\[\[([^\[\]]+)\]\]', lambda m: m[1].split('|')[-1], out)
    out = re.sub(r'\[(https?://[^\s\]]+)\s+([^\]]+)\]', r'\2', out)
    out = re.sub(r'<[^>]+>', '', out)
    return html.unescape(out.replace("'''", '').replace("''", '')).strip()


def cell(raw):
    parts = split_markup(raw, '|')
    if len(parts) > 1 and re.search(r'(?:style|rowspan|colspan|data-sort-value|data-sort-type|align|class)\s*=', parts[0], re.I):
        attributes(parts[0])
        return parts[0], '|'.join(parts[1:])
    return '', raw


def tables(text):
    section, body, start, depth = [], [], 0, 0
    for line_no, line in enumerate(text.splitlines(), 1):
        heading = re.fullmatch(r'(={2,6})\s*(.*?)\s*\1\s*', line)
        if heading and not depth:
            level = len(heading[1])
            section = [(n, s) for n, s in section if n < level] + [(level, heading[2].strip())]
        if line.startswith('{|'):
            if depth:
                raise ParseDrift("nested_table", str(line_no))
            depth, start, body = 1, line_no, []
        elif line.startswith('|}') and depth:
            yield [s for _, s in section], start, '\n'.join(body)
            depth = 0
        elif depth:
            body.append(line)
    if depth:
        raise ParseDrift("unclosed_table")


def row_cells(row):
    chunks = split_markup(row, '\n')
    pieces = []
    for line in chunks:
        if line.startswith(('!', '|')) and not line.startswith('|+'):
            marker = line[0]
            pieces.extend(split_markup(line[2:] if line.startswith(marker * 2) else line[1:], '!!' if marker == '!' else '||'))
        elif pieces:
            pieces[-1] += '\n' + line
    return [cell(p) for p in pieces]


MONTHS = {m: i for i, m in enumerate(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'), 1)}


def dates(value, attrs):
    if not isinstance(value, str) or not isinstance(attrs, str):
        raise ParseDrift("invalid_dates")
    value = clean(value)
    normalized = value.replace('\u2013', '-').replace('\u2014', '-')
    m = re.fullmatch(r'(?:(\d{1,2})(?:\s+([A-Za-z]+))?\s*-\s*)?(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', normalized)
    if not m:
        raise ParseDrift("invalid_dates", value)
    try:
        end = date(int(m[5]), MONTHS[m[4][:3]], int(m[3]))
        start = date(end.year, MONTHS[(m[2] or m[4])[:3]], int(m[1] or m[3]))
    except (ValueError, KeyError):
        raise ParseDrift("invalid_dates", value) from None
    sort = attributes(attrs).get('data-sort-value')
    if sort is not None:
        try:
            sort_date = date.fromisoformat(sort)
            if sort_date.isoformat() != sort:
                raise ValueError
        except ValueError:
            raise ParseDrift('invalid_dates', value + ' / ' + sort) from None
    if start > end or (sort is not None and not 0 <= (sort_date - end).days <= MAX_RELEASE_LAG_DAYS):
        raise ParseDrift("invalid_dates", value + ' / ' + (sort if sort else ''))
    return start.isoformat(), end.isoformat()


def parse_polls(wikitext, revision, mapping, identities):
    position = {'locator': ''}
    try:
        return _parse_polls(wikitext, revision, mapping, identities, position)
    except ParseDrift as exc:
        # Only scanner-generated positions are safe for public diagnostics.
        exc.public_locator = position['locator']
        raise


def _parse_polls(wikitext, revision, mapping, identities, position):
    if len(wikitext.encode()) > LIMIT:
        raise ParseDrift("size_limit")
    result, selected, seen = ParseResult(), 0, set()
    refs = {}
    for _, _, attrs, content in references(wikitext):
        key = attrs.get('name')
        if key is not None and content is not None:
            if key in refs and refs[key] != content:
                raise ParseDrift("conflicting_named_ref", key)
            refs[key] = content
    signature = ['Date', 'Polling organisation', 'Sample size', 'NAT', 'LAB', 'GRN', 'ACT', 'NZF', 'TPM', 'OPP', 'Others', 'Lead']
    for section, line, body in tables(wikitext):
        if section != ['Party vote', 'Table of polls']:
            result.excluded_rows.append(dict(reason='non_national_table', locator=f'line:{line}', section=section))
            continue
        position['locator'] = f'line:{line}'
        selected += 1
        rows = split_markup(body, '\n|-')
        header_found = False
        carry = {}
        for index, row in enumerate(rows):
            locator = f'table:{line}/row:{index}'
            position['locator'] = locator
            cells = row_cells(row)
            if not cells:
                continue
            if cells[0][1].lstrip().startswith('Date'):
                labels = []
                for attrs, value in cells:
                    label = clean(value)
                    span = attributes(attrs).get('colspan')
                    if 'rowspan' in attributes(attrs):
                        raise ParseDrift('unexplained_merge', locator)
                    if span:
                        expansion = mapping.get('header_expansions', {}).get(label, [])
                        if len(expansion) != int(span):
                            raise ParseDrift('unexplained_merge', locator)
                        labels.extend(expansion)
                    else:
                        labels.append(label)
                if labels != signature:
                    raise ParseDrift("unknown_headers", locator)
                header_found = True
                continue
            if not header_found:
                raise ParseDrift("unknown_headers", locator)
            if len(cells) == 1 and attributes(cells[0][0]).get('colspan') == '12' and not clean(cells[0][1]):
                result.excluded_rows.append(dict(reason='separator', locator=locator))
                continue
            if len(cells) == 2 and attributes(cells[1][0]).get('colspan') == '11':
                result.excluded_rows.append(dict(reason='event', locator=locator, text=cells[1][1]))
                continue
            expanded = []
            source = iter(cells)
            for column in range(12):
                if column in carry:
                    attrs, value, remaining = carry[column]
                    expanded.append((attrs, value))
                    if remaining == 1:
                        del carry[column]
                    else:
                        carry[column] = (attrs, value, remaining - 1)
                    continue
                entry = next(source, None)
                if entry is None:
                    raise ParseDrift("unexplained_width", locator)
                attrs, value = entry
                parsed = attributes(attrs)
                if 'colspan' in parsed:
                    raise ParseDrift('unexplained_merge', locator)
                if 'rowspan' in parsed:
                    span = int(parsed['rowspan'])
                    if column > 2 or span < 2 or span > 100:
                        raise ParseDrift("unexplained_merge", locator)
                    carry[column] = (attrs, value, span - 1)
                expanded.append(entry)
            if next(source, None) is not None:
                raise ParseDrift("unexplained_width", locator)
            cells = expanded
            # Historical rows are outside the M1 2026 history contract.
            visible = clean(cells[0][1])
            if re.search(r'\b202[3-5]\b', visible):
                result.excluded_rows.append(dict(reason='outside_2026', locator=locator))
                continue
            date_attrs = cells[0][0]
            sort = attributes(date_attrs).get('data-sort-value')
            start, end = dates(cells[0][1], date_attrs)
            documented_exception = False
            for exception in mapping.get('date_exceptions', []):
                if (exception['visible'] == visible
                        and sort and exception['sort'] == sort
                        and exception['pollster'] == clean(cells[1][1])
                        and exception.get('source') and exception.get('reason')):
                    documented_exception = True
                    result.diagnostics.setdefault('date_exceptions', []).append(
                        dict(exception, locator=locator, kind='documented-exception'))
            if sort is not None and sort != end and not documented_exception:
                result.diagnostics.setdefault('date_exceptions', []).append(dict(
                    locator=locator, kind='release-date', visible=visible, sort=sort, pollster=clean(cells[1][1]),
                    source='https://en.wikipedia.org/w/index.php?oldid=' + str(revision),
                    reason=f'Sort date is within {MAX_RELEASE_LAG_DAYS} days after fieldwork; '
                           'release-date convention accepted, visible fieldwork dates retained.'))
            if end[:4] != '2026':
                raise ParseDrift("invalid_dates", locator)
            label = clean(cells[1][1])
            pollster = mapping['pollsters'].get(label)
            if not pollster:
                raise ParseDrift("unknown_pollster", label)
            sample = clean(cells[2][1]).replace(',', '')
            if sample in ('', '-', '\u2013', 'N/A', '?'):
                sample = None
            elif sample.isdigit() and int(sample) > 0:
                sample = int(sample)
            else:
                raise ParseDrift("invalid_sample", locator)
            shares = {}
            for header, (_, raw) in zip(signature[3:11], cells[3:11]):
                party = mapping['headers'].get(header)
                if party is None:
                    raise ParseDrift("unknown_party_mapping", header)
                value = clean(raw).rstrip('%').strip()
                if value in ('', '-', '\u2013', 'N/A'):
                    shares[party] = None
                    continue
                try:
                    number = Decimal(value)
                    if not number.is_finite() or number < 0 or number > 100:
                        raise InvalidOperation
                except InvalidOperation:
                    raise ParseDrift("invalid_shares", locator) from None
                shares[party] = number
            citation_text = row
            for _, _, attrs, content in references(row):
                if content is None:
                    name = attrs['name']
                    if name not in refs:
                        raise ParseDrift("unknown_named_ref", name)
                    citation_text += '\n' + refs[name]
            urls = sorted(set(re.findall(r'https?://[^\s|<>\]{}"\x27]+', citation_text)))
            key = '|'.join((pollster, start, end))
            identity = identities.get(key, {})
            if 'surveys' in identity:
                matches = [s for s in identity['surveys']
                           if s.get('revision') == revision and s.get('source_ref') == locator]
                if len(matches) != 1:
                    raise ParseDrift('ambiguous_duplicates', locator)
                identity = matches[0]
            discriminator = identity.get('discriminator', '')
            poll_id = identity.get('id', 'poll-' + hashlib.sha256((key + '|' + discriminator).encode()).hexdigest()[:20])
            if poll_id in seen:
                raise ParseDrift("ambiguous_duplicates", locator)
            seen.add(poll_id)
            result.polls.append(dict(id=poll_id, fieldwork_start=start, fieldwork_end=end,
                                     pollster=pollster, sample=sample, shares=shares,
                                     reference_urls=urls, reference_text=citation_text,
                                     source_ref=locator, revision=revision, history=[]))
        if carry:
            raise ParseDrift("unexplained_merge", 'unterminated rowspan')
        position['locator'] = ''
    if selected != 1 or not result.polls:
        raise ParseDrift("national_table_count", str(selected))
    result.diagnostics.update(poll_count=len(result.polls), excluded_count=len(result.excluded_rows))
    return result


def compare_revisions(previous, current, review):
    old = {p['id']: p for p in previous}
    new = {p['id']: deepcopy(p) for p in current.polls}
    if len(old) != len(previous) or len(new) != len(current.polls):
        raise ParseDrift('ambiguous_duplicates')
    removed = sorted(old.keys() - new.keys())
    for poll_id in removed:
        decision = review.get('removals', {}).get(poll_id, {})
        revision = str(current.polls[0]['revision']) if current.polls else ''
        if not decision.get('reason') or decision.get('revision') != revision:
            raise ParseDrift('missing_previous_polls', poll_id)
    fields = ('fieldwork_start', 'fieldwork_end', 'pollster', 'sample', 'shares', 'reference_urls')
    for poll_id in old.keys() & new.keys():
        new[poll_id]['history'] = deepcopy(old[poll_id].get('history', []))
        if any(old[poll_id][k] != new[poll_id][k] for k in fields):
            history = {k: deepcopy(v) for k, v in old[poll_id].items() if k != 'history'}
            new[poll_id]['history'].append(history)
    return DriftReport(list(new.values()), dict(old_count=len(old), new_count=len(new),
                       added_ids=sorted(new.keys() - old.keys()), removed_ids=removed))
