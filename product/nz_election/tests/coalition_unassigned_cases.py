"""Synthetic inputs for unavailable-allocation transition regressions."""
from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.seats import project


def unassigned_inputs(no_eligible=False):
    votes = dict(a=0, b=0, others=100) if no_eligible else dict(a=239, b=1, others=0)
    average = trend([dict(id='regression', revision='1', fieldwork_end='2026-10-17',
                          shares=votes, scale=1)], ['2026-10-17'])[0]
    seats = project(average)
    seats['assumptions']['electorate_wins'] = {}
    return average, seats
