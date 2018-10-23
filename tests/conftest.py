import os

import pytest
import networkx as nx
from aioresponses import aioresponses

from raiden import RaidenNodeMock, RaidenNode
from tests.utils.fake_raiden import FakeRaiden
from track_control import TrackControl, MockSerial
from network import NetworkTopology
from utils import random_address


@pytest.fixture
def sender_address():
    return random_address()


@pytest.fixture
def token_address():
    return random_address()


@pytest.fixture
def address():
    return random_address()


@pytest.fixture
def api_endpoint():
    return 'http://127.0.0.1:5001'


@pytest.fixture
def default_raiden_config_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raiden_config_tests.toml')


@pytest.fixture
def raiden_mock(address, api_endpoint, default_raiden_config_file):
    raiden = RaidenNodeMock(address, api_endpoint, default_raiden_config_file)
    return raiden


@pytest.fixture
def raiden(address, api_endpoint, default_raiden_config_file):
    raiden = RaidenNode(address, api_endpoint, default_raiden_config_file)
    return raiden


@pytest.fixture
def track_control():
    return TrackControl(track_power_serial=MockSerial())


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture()
def network_topology(sender_address, address, token_address):
    g = nx.Graph()
    g.add_edge(sender_address, address)
    return NetworkTopology(g, sender_address, address, token_address)


@pytest.fixture()
async def fake_raiden(event_loop, address, api_endpoint):
    port = int(api_endpoint.split(":")[2])
    fake_raiden = FakeRaiden(loop=event_loop, address=address, port=port)
    await fake_raiden.start()
    yield fake_raiden
    await fake_raiden.stop()
