import asyncio
import logging
import subprocess
from os import PathLike

import aiohttp

log = logging.getLogger()


class RaidenNode:

    def __init__(self, address: str, api_endpoint: str, config_file: PathLike):
        self.address = address
        self.config_file = config_file
        self.api_endpoint = api_endpoint
        self._raiden_process = None

    def __repr__(self):
        return "{}<address={}, api-endpoint={}>".format(self.__class__.__name__, self.address,
                                                        self.api_endpoint)

    def start(self):
        # start the subprocess
        # FIXME better stripping of http:// in api-address
        raiden = "nodejs" + \
                 " /home/train/demo-train/light-client/raiden-cli/build/index.js" + \
                 " --ethNode " + "http://parity.goerli.ethnodes.brainbot.com:8545" + \
                 " --store " + f"./store_{self.address}" + \
                 " --password " + "raiden" + \
                 " --port " + self.api_endpoint[-4:] + \
                 " --privateKey " + f"./receiver/key_storage/UTC--{self.address} &"
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
                            log.info(f"Succesfully started node {self.address}")
                            return True
                        raise ValueError("Address doesn't match expected address")
                    else:
                        # no 200 OK means the Raiden Node is somehow not available
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
                                int(event["amount"]) == 1 and \
                                int(event["identifier"]) == nonce:
                            return True
                    # Event not found in event list:
                    return False
                else:
                    # no 200 OK means the Raiden Node is somehow not available
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
