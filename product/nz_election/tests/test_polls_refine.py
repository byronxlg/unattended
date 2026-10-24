"""Reader abbreviations in the shared legacy and social seat strip."""
from product.nz_election.pipeline.build import strip


def test_strip_uses_top_reader_abbreviation():
    counts = dict(nat=43, lab=35, grn=15, act=9, nzf=7, tpm=4, opp=7)
    html = strip(dict(seats=counts, entitlements=counts,
                      assumed_house=120, assumed_majority=61, overhang=0))
    assert '<span>TOP</span>' in html
    assert 'OPP' not in html
    for party in ('NAT', 'LAB', 'GRN', 'ACT', 'NZF', 'TPM'):
        assert f'<span>{party}</span>' in html
