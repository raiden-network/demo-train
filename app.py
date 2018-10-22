import asyncio
import random
import sys
from typing import List

from const import SENDER_ADDRESS, TOKEN_ADDRESS, DEFAULT_CONFIG_FILE
from deployment import start_raiden_nodes
from raiden import RaidenNode, RaidenNodeMock
from track_control import TrackControl, ArduinoSerial, MockSerial
from network import NetworkTopology
import logging

from utils import wait_for_event

log = logging.getLogger()


class TrainApp:

    def __init__(self, track_control: TrackControl, raiden_nodes: List[RaidenNode],
                 network_topology: NetworkTopology):
        self.track_control = track_control
        self.raiden_nodes = raiden_nodes
        self.network_topology = network_topology
        self._track_loop = None
        self._current_provider = None
        self._provider_nonces = {provider.address: 0 for provider in self.raiden_nodes}

    def start(self):
        self._track_loop = asyncio.create_task(self.run())

    # FIXME make awaitable so that errors can raise
    # FIXME handle gracefully
    def stop(self):
        try:
            self._track_loop.cancel()
        except asyncio.CancelledError:
            pass

    async def run(self):
        log.debug("Track loop started")
        self.track_control.power_on()
        while True:
            # Pick a random receiver
            self._choose_and_set_next_provider()
            provider = self._current_provider
            current_nonce = self.current_nonce

            # Generate barcode with current provider address and nonce
            # barcode_code = barcode_factory(const.RECEIVER_LIST.index(self.current_provider_address), current_nonce)
            # on_new_bar_code(barcode_code, BAR_CODE_FILE_PATH)

            payment_received_task = asyncio.create_task(
                provider.ensure_payment_received(sender_address=self.network_topology.sender_address,
                                                 token_address=self.network_topology.token_address,
                                                 nonce=current_nonce, poll_interval=0.05)
            )
            barrier_event_task = asyncio.create_task(wait_for_event(self.track_control.barrier_event))
            log.info('Waiting for payment to provider={}, nonce={}'.format(provider.address, current_nonce))

            # await both awaitables but return when one of them is finished first
            done, pending = await asyncio.wait([payment_received_task, barrier_event_task],
                                               return_when=asyncio.FIRST_COMPLETED)
            payment_successful = False
            if payment_received_task in done:
                if payment_received_task.result() is True:
                    payment_successful = True
            # cancel the pending task(s), we don't need it anymore
            for task in pending:
                task.cancel()

            if payment_successful is True:
                log.info("Payment received")
                self._increment_nonce_for_current_provider()
            else:
                log.info("Payment not received before next barrier trigger")
                self.track_control.power_off()

                payment_received_task = asyncio.create_task(
                    provider.ensure_payment_received(sender_address=SENDER_ADDRESS,
                                                     token_address=TOKEN_ADDRESS,
                                                     nonce=current_nonce,
                                                     poll_interval=0.05)
                )
                await payment_received_task
                if payment_received_task.result() is True:
                    self.track_control.power_on()
                else:
                    # this shouldn't happen
                    # FIXME remove assert in production code
                    assert False

    def _choose_and_set_next_provider(self):
        self._current_provider = random.choice(self.raiden_nodes)

    @property
    def current_provider_address(self):
        return self._current_provider.address

    @property
    def current_nonce(self):
        return self._provider_nonces[self.current_provider_address]

    def _increment_nonce_for_current_provider(self):
        self._provider_nonces[self.current_provider_address] += 1

    @classmethod
    def build_app(cls, network: NetworkTopology, mock_arduino=False, mock_raiden=False,
                  config_file=None):
        raiden_node_cls = RaidenNode
        if mock_arduino:
            log.debug('Mocking Arduino serial')
            serial_track_power = MockSerial()
        else:
            serial_track_power = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
        if mock_raiden:
            raiden_node_cls = RaidenNodeMock
            log.debug('Mocking RaidenNode')

        # TODO for mock nodes, we should skip the deployment script
        # FIXME asyncio.run() is not the correct method
        try:
            raiden_nodes_dict = asyncio.run(start_raiden_nodes(raiden_node_cls, receivers=network.receivers,
                                                           config_file=config_file))
        except (asyncio.TimeoutError, TimeoutError):
            log.info('Not all raiden nodes could get started, check the log files for more info. Shutting down')
            sys.exit()
        raiden_nodes = list(raiden_nodes_dict.values())
        track_control = TrackControl(serial_track_power)

        return cls(track_control, raiden_nodes, network)
