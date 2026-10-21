"""Captured archives and hostile XML use the same reusable parser."""
import pytest
from product.nz_election.pipeline import xml_parser as xml
from product.nz_election.pipeline.fixtures import captures


@pytest.fixture(scope='module')
def raw():
    return captures()


def refs(raw, year='2023'):
    return xml.references(*(raw[f'ec-{year}-xml/{n}.xml'] for n in ('parties', 'electorates', 'candidates')))


def test_xml_archives_2017_2020_2023(raw):
    for year, seats, votes, house in [('2017', 71, 2591896, 120), ('2020', 72, 2886420, 120), ('2023', 72, 2851211, 122)]:
        reference = refs(raw, year)
        result = xml.election(raw[f'ec-{year}-xml/election.xml'], reference)
        assert len(reference['electorates']) == seats
        assert result['valid_party_votes'] == votes
        assert result['reported_house'] == house
        assert result['statistics']['total_votes_cast'] != votes


@pytest.mark.parametrize('change', ['unknown-party', 'unknown-electorate', 'duplicate'])
def test_xml_reference_integrity(raw, change):
    candidates = raw['ec-2023-xml/candidates.xml']
    if change == 'unknown-party':
        candidates = candidates.replace(b'<party>16</party>', b'<party>999</party>', 1)
    elif change == 'unknown-electorate':
        candidates = candidates.replace(b'<electorate>35</electorate>', b'<electorate>999</electorate>', 1)
    else:
        candidates = candidates.replace(b'c_no="68"', b'c_no="30"')
    with pytest.raises(ValueError, match='^XML_REFERENCE$'):
        xml.references(raw['ec-2023-xml/parties.xml'], raw['ec-2023-xml/electorates.xml'], candidates)


@pytest.mark.parametrize('value', ['', None, [], {}, True, 1.5, 10**100, '1.0', '-1', '01', '１２', '1e3', '9999999999'])
def test_xml_rejects_malformed_counts(value):
    with pytest.raises(ValueError, match='^XML_COUNT$'):
        xml.count(value)


@pytest.mark.parametrize('value', [b'', None, [], {}, True, 1.5, 10**100, 'weird', b'x' * (xml.MAX_BYTES + 1),
                                      b'<!DOCTYPE election [<!ENTITY x "12">]><election/>'])
def test_xml_rejects_entities_and_oversize(value):
    with pytest.raises(ValueError, match='^XML_DOCUMENT$'):
        xml.document(value, 'election')


def test_xml_totals_and_timestamp(raw):
    reference = refs(raw)
    source = raw['ec-2023-xml/election.xml']
    for before, after, code in [(b'<votes>246473', b'<votes>99999999', 'XML_TOTAL'),
                                 (b'<votes>246473', b'<votes>1.5', 'XML_COUNT'),
                                 (b'2024-11-10T00:00:00', b'2024-99-10T00:00:00', 'XML_TIMESTAMP')]:
        with pytest.raises(ValueError, match='^' + code + '$'):
            xml.election(source.replace(before, after), reference)
