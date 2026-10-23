"""Guard repeated home markup with complete electorate and seat populations."""
from copy import deepcopy

from product.nz_election.pipeline.build import config, home_presentation
from product.nz_election.pipeline.home import hero
from product.nz_election.pipeline.snapshot_views import map_graphic
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401


def test_full_electorate_map_byte_budget(populated):
    envs = deepcopy(populated[0])
    # Small captures leave most tiles unnamed by result. Populate every predecessor
    # so repeated result labels cost as much as they do on the live data branch.
    envs['baseline-2023']['data'] = [
        dict(old_electorate_id=identity, old_name=row['name'], candidate_votes=[
            dict(name='Winner', party='National Party', votes=23456),
            dict(name='Runner up', party='Labour Party', votes=12345)])
        for identity, row in {i: row for row in config('electorates') for i in row['baseline_ids']}.items()
    ]
    html = map_graphic(envs, hexagons=True)
    assert html.count('<a href=') == 71
    assert html.count('<title>') == 71
    assert html.count('<tr>') == 72
    assert len(html.encode()) < 28_500


def test_seat_metadata_byte_budget(populated):
    envs, _ = populated
    presentation = home_presentation(envs, NOW)
    html = hero(envs, NOW, presentation)
    assert html.count('class="seat"') == presentation['result']['assumed_house']
    assert len(html.encode()) < 6_000
