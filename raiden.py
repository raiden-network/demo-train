import subprocess
import asyncio
import aiohttp

from os import PathLike


class RaidenNode:

    def __init__(self, address: str, keystore_path: PathLike, password_file: PathLike, eth_rpc_endpoint: str,
                 api_endpoint: str, matrix_server: str):
        self.address = address
        self.keystore_path = keystore_path
        self.password_file = password_file
        self.eth_rpc_endpoint = eth_rpc_endpoint
        self.api_endpoint = api_endpoint
        self.matrix_server = matrix_server
        self._raiden_process = None

    def start(self):
        # start the subprocess
        # FIXME better stripping of http:// in api-address
        raiden = "raiden --keystore-path " + str(self.keystore_path) \
                 + " --eth-rpc-endpoint " + self.eth_rpc_endpoint \
                 + " --address " + str(self.address) \
                 + " --password-file " + str(self.password_file) \
                 + " --api-address " + str(self.api_endpoint[7:]) \
                 + " --no-web-ui --accept-disclaimer"\
                 + " --matrix-server={}&".format(self.matrix_server)
        print(
            "Starting Raiden Node for address %s on Port %s" %
            (self.address, self.api_endpoint)
        )
        self._raiden_process = subprocess.Popen(
            raiden,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self):
        print(
            "Stopping Raiden Node for address %s on Port %s" %
            (self.address, self.api_endpoint)
        )
        self._raiden_process.terminate()

    async def query_for_started(self):
        url = self.api_endpoint + "/api/1/address"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    if response.status == 200:
                        if data["our_address"] == self.address:
                            return True
                        # wrong address, this shouldn't happen
                        # TODO remove assert for production
                        assert False
                    else:
                        # no 200 OK means the Raiden Node is somehow not available
                        # TODO handle different connection errors
                        print("Raiden client not available.")
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

        url = self.api_endpoint + "/api/1/payments/{}/{}".format(token_address, sender_address)
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
                    print("Raiden client not available.")
                    return False

    async def ensure_payment_received(self,
                                      sender_address,
                                      token_address,
                                      nonce,
                                      poll_interval=1,
                                      mocking=False):
        # If we mock this should return true
        if mocking:
            while True:
                await self.query_for_payment_received(sender_address, token_address, nonce)
                return True

        else:
            while True:
                received = await self.query_for_payment_received(sender_address, token_address, nonce)
                if received:
                    return True
                await asyncio.sleep(poll_interval)


class RaidenNodeMock(RaidenNode):
    """
    this is mainly to provide the same interface as a raiden node without actually starting
    a subprocess and querying the raiden api
    """

    def __init__(self, address: str, keystore_path: PathLike, password_file: PathLike, eth_rpc_endpoint: str,
                 api_endpoint: str, matrix_server: str):
        super(RaidenNodeMock, self).__init__(address, keystore_path, password_file, eth_rpc_endpoint,
                                             api_endpoint, matrix_server)
        self._started = False

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    async def query_for_started(self):
        await asyncio.sleep(0.1)
        return self._started

    async def query_for_payment_received(self, sender_address, token_address, nonce):
        await asyncio.sleep(0.1)
        # TODO enable to set a received payment externally
        # always say the payment was received for now
        return True

