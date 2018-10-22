import pytest
import json

from app import TrainApp
import asyncio

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

from utils import context_switch


@pytest.fixture
def train_app(raiden, track_control, network_topology):
    train_app = TrainApp(track_control, [raiden], network_topology)
    return train_app


# HACK
# FIXME, when using the same endpoint as in other tests, the aiohttp fake_raiden cannot
# double bind the port - probably due to a missing teardown in other tests
@pytest.fixture
def api_endpoint():
    return 'http://127.0.0.1:5005'


async def test_query_for_started_fake_raiden(fake_raiden, raiden, api_endpoint, address):
    result = await raiden.query_for_started()
    assert result is True


async def test_track_loop(fake_raiden, token_address, sender_address, train_app, raiden):
    # make a payment we're not waiting for
    fake_raiden.make_payment(token_address, sender_address, 123, 2)

    train_app.start()
    await context_switch()

    assert train_app.track_control.is_powered

    nonce = train_app.current_nonce
    provider_address = train_app.current_provider_address

    # we only have one provider, its RaidenNode instance and the corresponding FakeRaiden instance:
    assert provider_address == fake_raiden.address == raiden.address

    # make the payment manually on the fake-raiden instance of the provider
    fake_raiden.make_payment(token_address, sender_address, nonce, 1)
    await asyncio.sleep(1)

    assert train_app.current_nonce == nonce + 1
    assert train_app.track_control.is_powered

    train_app.stop()
