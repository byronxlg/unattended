"""Labelled synthetic reported ties, based on one hash-checked zero-state capture."""
import xml.etree.ElementTree as ET
from product.nz_election.pipeline import fixtures, xml_parser


def reported_tie(tied_count=2, final=True):
    prefix = 'ec-2026-media-xml/'
    raw = fixtures.captures(paths={prefix + n + '.xml' for n in ('parties', 'electorates', 'candidates')} | {prefix + 'e01/e01.xml'})
    refs = xml_parser.references(*(raw[prefix + n + '.xml'] for n in ('parties', 'electorates', 'candidates')))
    root = ET.fromstring(raw[prefix + 'e01/e01.xml'])
    root.set('final', 'true' if final else 'false')
    for tag, value in [('total_voting_places', '1' if final else '2'), ('total_voting_places_counted', '1'),
                       ('total_votes_cast', str(100 * tied_count))]:
        root.find('statistics/' + tag).text = value
    tied = []
    for candidate in list(root.find('candidatevotes'))[:tied_count]:
        candidate.find('votes').text = '100'
        tied.append(candidate.get('c_no'))
    return ET.tostring(root), refs, sorted(tied)


def dom_tree(raw):
    # Node has no DOMParser. This adapter supplies the DOM shape only; real XML decoding
    # and DOMParser parity remain covered by night_browser.py in Chromium.
    def node(element):
        return dict(tag=element.tag, attrs=element.attrib, text=element.text, children=[node(c) for c in element])
    return node(ET.fromstring(raw))
