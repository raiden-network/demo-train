import pytest
import json
import asyncio

from utils import random_address


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture
def nonce():
    return 1


@pytest.fixture()
def poll_interval():
    return 0.01


async def test_query_for_started(mock_aioresponse, raiden, api_endpoint, address):
    data = {"our_address": address}
    mock_aioresponse.get(api_endpoint + '/api/v1/address', status=200, body=json.dumps(data))
    result = await raiden.query_for_started()
    assert result is True


async def test_query_for_started_wrong_address(mock_aioresponse, raiden, api_endpoint, address):
    wrong_address = random_address()
    # this would be a miracle:
    assert not address == wrong_address
    data = {"our_address": wrong_address}
    mock_aioresponse.get(api_endpoint + '/api/v1/address', status=200, body=json.dumps(data))
    with pytest.raises(ValueError):
        await raiden.query_for_started()


async def test_query_for_started_wrong_status(mock_aioresponse, raiden, api_endpoint, address):
    mock_aioresponse.get(api_endpoint + '/api/v1/address', status=500, body='')
    result = await raiden.query_for_started()
    assert result is False


async def test_query_for_payment_received(mock_aioresponse, raiden, api_endpoint, sender_address, token_address, nonce):
    correct_event = {"event": "EventPaymentReceivedSuccess", "amount": 1, "identifier": nonce}
    other_event = {"event": "EventPaymentReceivedSuccess", "amount": 1, "identifier": 123}
    data = [other_event, correct_event]
    mock_aioresponse.get(api_endpoint + '/api/v1/payments/{}/{}'.format(token_address, sender_address),
                         status=200, body=json.dumps(data))
    result = await raiden.query_for_payment_received(sender_address, token_address, nonce)
    assert result is True


async def test_query_for_payment_received_not_found(mock_aioresponse, raiden, api_endpoint, sender_address,
                                                    token_address, nonce):
    other_event = {"event": "EventPaymentReceivedSuccess", "amount": 1, "identifier": 123}
    data = [other_event]
    mock_aioresponse.get(api_endpoint + '/api/v1/payments/{}/{}'.format(token_address, sender_address),
                         status=200, body=json.dumps(data))
    result = await raiden.query_for_payment_received(sender_address, token_address, nonce)
    assert result is False


async def test_query_for_payment_received_wrong_status(mock_aioresponse, raiden, api_endpoint, sender_address,
                                                       token_address, nonce):
    mock_aioresponse.get(api_endpoint + '/api/v1/payments/{}/{}'.format(token_address, sender_address),
                         status=500, body='')
    result = await raiden.query_for_payment_received(sender_address, token_address, nonce)
    assert result is False


async def test_ensure_payment_received(mock_aioresponse, raiden, sender_address, token_address, nonce, api_endpoint,
                                       poll_interval):

    # set a response that doens't return the correct payment first
    other_event = {"event": "EventPaymentReceivedSuccess", "amount": 1, "identifier": 123}
    correct_event = {"event": "EventPaymentReceivedSuccess", "amount": 1, "identifier": nonce}
    data = [other_event]

    # the first 10 queries will not return the correct event
    for _ in range(10):
        mock_aioresponse.get(api_endpoint + '/api/v1/payments/{}/{}'.format(token_address, sender_address),
                             status=200, body=json.dumps(data))

    ensure_payment_task = asyncio.create_task(raiden.ensure_payment_received(sender_address, token_address, nonce,
                                                                             poll_interval=poll_interval))

    # make sure we can do something else concurrently, in this case, set the correct response
    data.append(correct_event)
    # query 11 will include the correct event
    mock_aioresponse.get(api_endpoint + '/api/v1/payments/{}/{}'.format(token_address, sender_address),
                         status=200, body=json.dumps(data))

    result = await ensure_payment_task
    assert result is True


async def test_ensure_is_started(mock_aioresponse, address, raiden, api_endpoint, poll_interval):

    data = {"our_address": address}

    # the first 10 queries will return a wrong status code
    for _ in range(10):
        mock_aioresponse.get(api_endpoint + '/api/v1/address', status=500, body='')

    ensure_started_task = asyncio.create_task(raiden.ensure_is_started(poll_interval=poll_interval))

    # make sure we can do something else concurrently, in this case, set the correct response
    mock_aioresponse.get(api_endpoint + '/api/v1/address', status=200, body=json.dumps(data))

    result = await ensure_started_task
    assert result is True
