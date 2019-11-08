import subprocess
import asyncio
import aiohttp
import logging

from os import PathLike

log = logging.getLogger()


class RaidenNode:

    def __init__(self, address: str, api_endpoint: str, config_file: PathLike):
        self.address = address
        self.config_file = config_file
        self.api_endpoint = api_endpoint
        self._raiden_process = None

    def __repr__(self):
        return "{}<address={}, api-endpoint={}>".format(self.__class__.__name__, self.address, self.api_endpoint)

    def start(self):
        # start the subprocess
        # FIXME better stripping of http:// in api-address
        raiden = "raiden"\
                 + " --address " + str(self.address) \
                 + " --api-address " + str(self.api_endpoint[7:])
        if self.config_file is not None:
            raiden += " --config-file " + str(self.config_file)
        # TODO determine if still neccessary
        raiden += "&"
        log.info("Starting {}".format(self))
        with open(f'./raiden_{self.address[:10]}.log', 'w') as logfile:
            self._raiden_process = subprocess.Popen(
                raiden,
                shell=True,
                stdout=logfile,
                stderr=logfile
            )

    def stop(self):
        log.info("Stopping {}".format(self))
        self._raiden_process.terminate()

    async def query_for_started(self):
        url = self.api_endpoint + "/api/v1/address"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    if response.status == 200:
                        if data["our_address"] == self.address:
                            return True
                        raise ValueError("Address doesn't match expected address")
                    else:
                        # no 200 OK means the Raiden Node is somehow not available
                        # TODO handle different connection errors
                        log.info("Node not available: {}".format(self))
                        return False
            # If Raiden not online it will raise a ClientConnectorError
            except aiohttp.ClientConnectorError:
                return False

    async def ensure_is_started(self, poll_interval=1):
        # poll the raiden api and check if the process is started
        # use a future, multiple futures can be gathered

        # runs infinitely, when the task/future isn't scheduled with a timeout!
        while True:
            if await self.query_for_started() is True:
                return True
            await asyncio.sleep(poll_interval)

    async def query_for_payment_received(self, sender_address, token_address, nonce):

        url = self.api_endpoint + "/api/v1/payments/{}/{}".format(token_address, sender_address)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if response.status == 200:
                    for event in data:
                        if event["event"] == "EventPaymentReceivedSuccess" and \
                           event["amount"] == 1 and \
                           event["identifier"] == nonce:
                            return True
                    # Event not found in event list:
                    return False
                else:
                    # no 200 OK means the Raiden Node is somehow not available
                    # TODO handle different connection errors
                    # This should probably raise an exception, since the node is unhealthy or
                    # something in the query is wrong
                    log.info("Node not available: {}".format(self))
                    return False

    async def ensure_payment_received(self,
                                      sender_address,
                                      token_address,
                                      nonce,
                                      poll_interval=1):
        while True:
            received = await self.query_for_payment_received(sender_address, token_address, nonce)
            if received is True:
                return True
            await asyncio.sleep(poll_interval)


class RaidenNodeMock(RaidenNode):
    # TODO instead of mocking the node in-process, rather use the FakeRaiden server in the background
    # to allow actual network requests and the logic of the RaidenNode
    """
    this is mainly to provide the same interface as a raiden node without actually starting
    a subprocess and querying the raiden api
    """

    def __init__(self, address: str, api_endpoint: str, config_file: PathLike):
        super(RaidenNodeMock, self).__init__(address, api_endpoint, config_file)
        self._started = False

    def start(self):
        # don't start the raiden subprocess, but
        # TODO rather start the FakeRaiden server
        self._started = True

    def stop(self):
        # TODO stop the FakeRaiden server
        self._started = False

    async def query_for_started(self):
        # TODO remove
        await asyncio.sleep(0.1)
        return self._started

    async def query_for_payment_received(self, sender_address, token_address, nonce):
        # TODO remove
        await asyncio.sleep(0.1)
        # always say the payment was received for now
        return True
