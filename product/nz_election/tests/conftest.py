"""Shared offline inputs; synthetic cases stay outside immutable captures."""
import json
from pathlib import Path
import pytest
from product.nz_election.pipeline.fixtures import captures, golden

PRODUCT = Path(__file__).resolve().parents[1]


@pytest.fixture
def official():
    return golden()


@pytest.fixture
def mapping():
    return json.loads((PRODUCT / 'config/party-map.json').read_text())


@pytest.fixture
def wikitext():
    return captures()['wikipedia/polls-2026.wikitext'].decode()
