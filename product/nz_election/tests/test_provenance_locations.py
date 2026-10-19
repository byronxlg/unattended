"""Detailed evidence belongs on the one-click Methods target."""
from product.nz_election.pipeline.provenance_checks import check_site
from product.nz_election.tests.test_home import populated


def test_provenance_locations(populated):
    envs, site = populated
    assert check_site(site, envs) == 72
