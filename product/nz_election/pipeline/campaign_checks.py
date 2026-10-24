"""Campaign invariants over reviewed snapshots and the routes that consume them.

Donation facts are reviewed index transcriptions, not archived source bytes. The
scorecard includes 2017 as well as the required 2020 and 2023 national polls.
Neither family is currently exported in the daily data bundle.
"""
from collections import Counter
from datetime import date
from functools import wraps
import gzip
import json
import re
from decimal import Decimal

from . import donations, pollster_scorecard, snapshots
from .content_checks import Tree, Node
from ..tools.check_visible_text import check_absent_text


DONATION_ROWS = 'CAMPAIGN_DONATION_ROWS'
DONATION_DATES = 'CAMPAIGN_DONATION_DATES'
DONATION_INDEX = 'CAMPAIGN_DONATION_INDEX'
NO_TOTAL_FUNDING = 'CAMPAIGN_NO_TOTAL_FUNDING'
FINAL_POLL = 'CAMPAIGN_FINAL_POLL'
OFFICIAL_ERRORS = 'CAMPAIGN_OFFICIAL_ERRORS'
COVERAGE = 'CAMPAIGN_COVERAGE'
PROVENANCE = 'CAMPAIGN_PROVENANCE'
ABSENT = 'CAMPAIGN_ABSENT'
ADVANCE = 'CAMPAIGN_ADVANCE'
DATA = 'CAMPAIGN_DATA'
CODES = frozenset({DONATION_ROWS, DONATION_DATES, DONATION_INDEX, NO_TOTAL_FUNDING,
                   FINAL_POLL, OFFICIAL_ERRORS, COVERAGE, PROVENANCE, ABSENT, ADVANCE, DATA})
INPUT_ERRORS = (ValueError, TypeError, LookupError, AttributeError, ArithmeticError,
                OSError, StopIteration)


class CampaignError(ValueError):
    """A typed boundary prevents upstream strings impersonating owned codes."""

    def __init__(self, code):
        self.code = code if code in CODES else DATA
        super().__init__(self.code)


def report_failure(check):
    """No ordinary exception may cross the campaign reporting boundary."""
    @wraps(check)
    def checked(*args, **kwargs):
        try:
            return check(*args, **kwargs)
        except CampaignError:
            raise
        except Exception:
            raise CampaignError(DATA) from None
    return checked


def guard(code):
    def decorate(check):
        @wraps(check)
        def checked(*args, **kwargs):
            try:
                return check(*args, **kwargs)
            except CampaignError:
                raise
            except INPUT_ERRORS:
                raise CampaignError(code) from None
        return checked
    return decorate


@guard(DATA)
def validate_bundle(directory):
    from . import export
    return export.validate_bundle(directory)


def require(condition, invariant):
    """Only owned invariant codes cross the campaign reporting boundary."""
    if not condition:
        raise CampaignError(invariant)


@guard(NO_TOTAL_FUNDING)
def no_total_funding(value):
    """Allow the funding disclaimer, never a derived funding field or claim."""
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r'[^a-z]', '', key.lower())
            require(not ('total' in normalized and 'funding' in normalized),
                    NO_TOTAL_FUNDING)
            no_total_funding(item)
    elif isinstance(value, list):
        for item in value:
            no_total_funding(item)
    elif isinstance(value, str):
        text = re.sub(r'<[^>]*>', ' ', value)
        require(not re.search(r'\btotal\s+(?:party\s+)?funding\s*(?:is|of|:|=)?\s*(?:NZD|\$|[0-9])', text, re.I),
                NO_TOTAL_FUNDING)


def checked_load(loader, path, fallback, codes):
    try:
        return loader(path)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        code = str(error).split(':')[0]
        raise CampaignError(codes.get(code, fallback)) from None


# Exact EC short names in the archived 2020/2023 party reference files.
EC_PARTIES = {
    'ACT New Zealand': 'act', 'Advance NZ': 'advance',
    'Aotearoa Legalise Cannabis Party': 'alcp', 'Green Party': 'grn',
    'HeartlandNZ': 'heartland', 'Labour Party': 'lab', 'Māori Party': 'tpm',
    'Te Pāti Māori': 'tpm', 'National Party': 'nat', 'New Conservative': 'con',
    'New Conservatives': 'con', 'New Zealand First Party': 'nzf',
    'NZ Outdoors Party': 'nzof', 'ONE Party': 'one', 'Social Credit': 'social-credit',
    'Sustainable New Zealand Party': 'sustainable', 'TEA Party': 'tea',
    'The Opportunities Party (TOP)': 'opp', 'Vision New Zealand': 'vision',
    'Animal Justice Party': 'animal-justice', 'DemocracyNZ': 'democracynz',
    'Freedoms NZ': 'freedoms', 'Leighton Baker': 'leighton-baker',
    'New Nation Party': 'new-nation', 'NZ Loyal': 'loyal', 'NewZeal': 'newzeal',
    'Women’s Rights Party': 'womens-rights',
}


@guard(OFFICIAL_ERRORS)
def check_official(data):
    from .fixtures import captures
    from .xml_parser import document
    paths = {f'ec-{year}-xml/{name}.xml' for year in (2020, 2023)
             for name in ('parties', 'election')}
    raw = captures(paths=paths)
    for result in data['official_results']:
        year = result['year']
        if year not in (2020, 2023):
            continue
        parties = document(raw[f'ec-{year}-xml/parties.xml'], 'parties')
        labels = {r.attrib['p_no']: r.findtext('short_name') for r in parties}
        election = document(raw[f'ec-{year}-xml/election.xml'], 'election')
        votes = {}
        for row in election.findall('./partystatus/party'):
            label = labels[row.attrib['p_no']]
            require(label in EC_PARTIES, OFFICIAL_ERRORS)
            votes[EC_PARTIES[label]] = row.findtext('votes')
        require({p['party_id']: p['votes'] for p in result['parties']} == votes,
                OFFICIAL_ERRORS)


@guard(FINAL_POLL)
def check_candidate_sources(data, directory):
    from .poll_parser import tables, split_markup, cell, clean, MONTHS
    observed = Counter()
    for source in data['sources']:
        raw = json.loads(gzip.decompress((directory / source['capture']).read_bytes()))
        text = next(iter(raw['query']['pages'].values()))['revisions'][0]['slots']['main']['*']
        for section, _, body in tables(text):
            if not (section[0].startswith('Party vote') and section[-1] in {
                    'Individual polls', 'UMR and Curia polls', 'Nationwide polling'}):
                continue
            for row in split_markup(body, '\n|-')[1:]:
                cells = []
                for chunk in split_markup(row, '\n'):
                    if chunk.startswith('|') and not chunk.startswith('|+'):
                        cells.extend(split_markup(chunk[1:], '||'))
                if len(cells) < 6:
                    continue
                label_index = 0 if source['year'] == 2017 else 1
                label = clean(cell(cells[label_index])[1])
                if re.fullmatch(r'20[0-9]{2} election result', label):
                    continue
                fieldwork = clean(cell(cells[1 - label_index])[1])
                observed[source['year'], label, fieldwork] += 1
    actual = Counter((r['year'], r['pollster'], r['fieldwork_label']) for r in data['candidates'])
    require(actual == observed, FINAL_POLL)
    for row in data['candidates']:
        if row.get('fieldwork_precision') == 'day':
            # Only the end is used for selection; retain source typos in starts
            # and disjoint fieldwork spans without silently correcting them.
            match = re.search(r'([0-9]{1,2}) ([A-Za-z]+) ([0-9]{4})$', row['fieldwork_label'])
            require(match and match[2][:3] in MONTHS and any(d in row['fieldwork_label'] for d in ('-', '–')),
                    FINAL_POLL)
            end = date(int(match[3]), MONTHS[match[2][:3]], int(match[1])).isoformat()
            require(row['fieldwork_end'] == end, FINAL_POLL)


@report_failure
def check_snapshots(directory=None):
    directory = snapshots.SNAPSHOTS if directory is None else directory
    donation_path = directory / 'donations.json'
    poll_path = directory / 'pollster-record.json'
    rows = checked_load(donations.load_donations, donation_path, DONATION_ROWS, {
        **{k: DONATION_INDEX for k in ('donations_count_mismatch', 'donations_skip_invalid')},
        **{k: DONATION_DATES for k in ('donations_date_invalid', 'donations_date_order', 'donations_date_exception')},
    })
    donation_data = json.loads(donation_path.read_text())
    no_total_funding(donation_data)
    for row in rows:
        for field in ('received', 'disclosed'):
            # Retrieval is not evidence for an observation date. A coincident date
            # needs an explicit reviewed note explaining the source observation.
            if field in row and row[field] == row['retrieved_at'][:10]:
                require(snapshots._text(row.get('date_note')) and row[field] in row['date_note'],
                        DONATION_DATES)
    records = checked_load(pollster_scorecard.load_pollster_record, poll_path, FINAL_POLL, {
        **{'scorecard_' + k: OFFICIAL_ERRORS for k in ('official', 'error', 'mean', 'decimal')},
        **{'scorecard_' + k: COVERAGE for k in ('coverage', 'absent_comparable_input', 'skip')},
    })
    require({2020, 2023} <= {r['year'] for r in records}, COVERAGE)
    require(all(r['source_locator'].startswith('National party vote table ') for r in records),
            FINAL_POLL)
    poll_data = json.loads(poll_path.read_text())
    no_total_funding(poll_data)
    check_official(poll_data)
    try:
        check_candidate_sources(poll_data, directory)
    except (ValueError, KeyError, TypeError, IndexError, StopIteration):
        raise CampaignError(FINAL_POLL) from None
    return rows, records


def descendants(node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from descendants(child)


@guard(ABSENT)
def check_markup(html, rows, year='2026'):
    try:
        check_absent_text(html, 'campaign parties')
    except ValueError:
        raise CampaignError(ABSENT) from None
    tree = Tree(html)
    no_total_funding(tree.root.text)
    notes = {n.attrs.get('id'): n for n in tree.nodes
             if 'source-note' in n.attrs.get('class', '').split()}
    def sourced(note):
        return any(link.tag == 'a' and link.attrs.get('href')
                   for action in descendants(note)
                   if action.tag == 'p' and 'source-actions' in action.attrs.get('class', '').split()
                   for link in descendants(action))
    for node in tree.nodes:
        no_total_funding(node.attrs)
        if node.tag == 'figure':
            refs = node.attrs.get('aria-describedby', '').split()
            require(refs and all(ref in notes and notes[ref].text.strip() and sourced(notes[ref]) for ref in refs),
                    PROVENANCE)
    blocks = [n for n in tree.nodes if 'party-donations' in n.attrs.get('class', '').split()]
    from .parties_page import ordered, largest_donors
    from .build import observation_label
    groups = {p: [r for r in rows if r['party_id'] == p and r.get('received', '')[:4] == year]
              for p in ordered([])}
    groups = {p: group for p, group in groups.items() if group}
    require(len(blocks) == len(groups), ABSENT)
    for party, group in groups.items():
        sections = [n for n in tree.nodes if n.tag == 'section' and n.attrs.get('id') == party]
        require(len(sections) == 1, ABSENT)
        matches = [n for n in descendants(sections[0]) if n in blocks]
        require(len(matches) == 1, ABSENT)
        block = matches[0]
        total = sum((Decimal(r['amount_nzd']) for r in group), Decimal(0))
        require(block.attrs.get('data-total') == f'{total:.2f}'
                and block.attrs.get('data-count') == str(len(group))
                and f'NZD {total:,.2f}' in block.text
                and f'{len(group)} declared returns' in block.text,
                ABSENT)
        actions = [n for n in descendants(block) if n.tag == 'p'
                   and 'source-actions' in n.attrs.get('class', '').split()]
        require(any(n.tag == 'a' and n.attrs.get('href') == group[0]['source_url']
                    for action in actions for n in descendants(action))
                and 'Copyright Electoral Commission' in block.text
                and 'not total party funding' in block.text,
                PROVENANCE)
        donors = largest_donors(group)
        amounts = re.findall(r'NZD ([0-9][0-9,]*(?:\.[0-9]+)?)', block.text)
        require(amounts == ['20,000', f'{total:,.2f}']
                + [f'{donor["amount"]:,.2f}' for _, donor in donors],
                ABSENT)
        for name, donor in donors:
            require(name + f': NZD {donor["amount"]:,.2f}' in block.text,
                    ABSENT)
            require(all(observation_label(day) in block.text for day in donor['dates']),
                    ABSENT)
