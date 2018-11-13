import pytest
import asyncio

from app import TrainApp
from utils import context_switch

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


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


async def test_track_loop(fake_raiden, token_address, sender_address, train_app, raiden, track_control):
    # make a payment we're not waiting for
    fake_raiden.make_payment(token_address, sender_address, 123, 2)

    train_app.start()
    await context_switch()

    # test internals for now
    assert train_app._barrier_ltr.is_running
    assert train_app._barrier_etf is not None
    assert not train_app._track_loop.done()

    assert train_app.track_control == track_control
    assert track_control.is_powered

    # we only have one provider, its RaidenNode instance and the corresponding FakeRaiden instance:
    assert train_app.current_provider_address == raiden.address
    assert train_app.current_nonce == 0

    nonce = train_app.current_nonce

    # make the payment manually on the fake-raiden instance of the provider
    fake_raiden.make_payment(token_address, sender_address, nonce, 1)

    # sleep for longer than a "context_switch()", since we have a poll-interval set and we are doing real networking
    await asyncio.sleep(0.1)

    # Payment should be succesful, track still powered
    # the nonce is not yet increased since we are still waiting for the barrier to trigger
    assert train_app.current_nonce == 0
    assert train_app.track_control.is_powered

    track_control.trigger_barrier()

    await context_switch()

    # The barrier was triggered, so now we incremented the nonce and are waiting for the next payment
    # the provider address is still the same, since there are no other nodes to choose from
    assert train_app.current_nonce == 1
    assert train_app.current_provider_address == raiden.address
    assert train_app.track_control.is_powered

    train_app.stop()


async def test_track_loop_barrier_triggered(fake_raiden, token_address, sender_address, train_app, raiden, track_control):
    # make a payment we're not waiting for
    fake_raiden.make_payment(token_address, sender_address, 123, 2)

    train_app.start()
    await context_switch()

    assert train_app.track_control == track_control
    assert track_control.is_powered

    nonce = train_app.current_nonce
    provider_address = train_app.current_provider_address

    # we only have one provider, its RaidenNode instance:
    assert provider_address == raiden.address
    assert nonce == 0

    track_control.trigger_barrier()
    await context_switch()

    # we triggered the barrier before paying, so the nonce shouldn't be increased and
    # the track should be powered off
    assert train_app.current_nonce == nonce
    assert not train_app.track_control.is_powered

    # now make the correct payment
    fake_raiden.make_payment(token_address, sender_address, nonce, 1)

    # sleep for longer than a "context_switch()", since we have a poll-interval set and we are doing real networking
    await asyncio.sleep(1)
    # The payment was made in the end so now we incremented the nonce and are waiting for the next payment
    # the provider address is still the same, since there are no other nodes to choose from
    assert train_app.current_nonce == nonce + 1
    assert train_app.current_provider_address == raiden.address
    assert train_app.track_control.is_powered

    train_app.stop()
