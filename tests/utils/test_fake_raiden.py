import pytest
import aiohttp

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


# HACK
# FIXME, when using the same endpoint as in other tests, the aiohttp fake_raiden cannot
# double bind the port - probably due to a missing teardown in other tests
@pytest.fixture
def api_endpoint():
    return 'http://127.0.0.1:5005'


async def test_make_payment(fake_raiden, token_address, sender_address, api_endpoint):
    fake_raiden.make_payment(token_address, sender_address, 123, 2)
    assert len(fake_raiden.payments[(token_address, sender_address)]) == 1

    expected_result = [{"event": "EventPaymentReceivedSuccess", "amount": 2, "identifier": 123}]

    url = api_endpoint + "/api/1/payments/{}/{}".format(token_address, sender_address)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            assert response.status == 200
            assert data == expected_result


async def test_make_succesive_payments(fake_raiden, token_address, sender_address):
    fake_raiden.make_payment(token_address, sender_address, 123, 2)
    fake_raiden.make_payment(token_address, sender_address, 0, 1)
    assert len(fake_raiden.payments[(token_address, sender_address)]) == 2

