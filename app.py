import asyncio
import random
import subprocess
import sys
import time
from typing import List, Optional

import code128

from const import BAR_CODE_FILE_PATH, RECEIVER_LIST
from deployment import start_raiden_nodes
from raiden import RaidenNode, RaidenNodeMock
from server import Server
from track_control import (
    TrackControl,
    ArduinoSerial,
    ArduinoTrackControl,
    MockArduinoTrackControl,
    BarrierEventTaskFactory,
    BarrierLoopTaskRunner
)
from network import NetworkTopology
import logging

log = logging.getLogger()

ADDRESS_MAP = {address: index for index, address in enumerate(RECEIVER_LIST)}


class BarcodeHandler():
    _address_map = ADDRESS_MAP

    def save_barcode(self, address, nonce):
        address, nonce = self._process_args(address, nonce)
        self._save_barcode(address, nonce)

    def _process_args(self, address, nonce):
        address = self._address_map[address]
        return address, nonce

    def _save_barcode(self, address, nonce):
        barcode = code128.image(str(address) + "," + str(nonce))
        factor = 4
        barcode = barcode.resize((int(barcode.width * factor), int(barcode.height * factor)))
        barcode.save(str(BAR_CODE_FILE_PATH))


class TrainApp:

    def __init__(self, track_control: TrackControl, raiden_nodes: List[RaidenNode],
                 network_topology: NetworkTopology,
                 barcode_handler: Optional[BarcodeHandler] = None):
        self.track_control = track_control
        self.raiden_nodes = raiden_nodes
        self.network_topology = network_topology
        self.barcode_handler = barcode_handler
        self._track_loop = None
        self._current_provider = None
        self._provider_nonces = {provider.address: 0 for provider in self.raiden_nodes}
        self._barrier_ltr = None
        self._barrier_etf = None

    def start(self):
        """
        NOTE: it's necessary that the asyncio related instantiations are done at runtime,
        because we need a running loop!
        :return:
        """
        self._barrier_ltr = BarrierLoopTaskRunner(self.track_control)
        self._barrier_etf = BarrierEventTaskFactory(self.track_control)
        self._barrier_ltr.start()
        self._track_loop = asyncio.create_task(self.run())

    # FIXME make awaitable so that errors can raise
    # FIXME handle gracefully
    def stop(self):
        try:
            self._track_loop.cancel()
            self._barrier_ltr.stop()
        except asyncio.CancelledError:
            pass

    async def run(self):
        # TODO make sure that every neccessary task is running:
        # (barrier_etf, barrier_ltr instantiated, etc)
        log.info("Track loop started")
        # Starting frontend
        subprocess.Popen(
            "DISPLAY=:0.0 "
            "/home/train/processing-3.4/processing-java "
            "--sketch=/home/train/demo-train/processing/sketchbook/railTrack --force --run",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log.info("Started subprocess for Frontend")
        time.sleep(5)
        server = Server()
        time.sleep(2)
        server.start()
        time.sleep(2)
        self.track_control.power_on()
        while True:
            # Pick a random receiver
            self._set_next_provider()
            provider = self._current_provider
            server.new_receiver(ADDRESS_MAP[self.current_provider_address])
            current_nonce = self.current_nonce

            # Sleeping 4 s to make sure that the train completely passed the light barrier
            time.sleep(4)

            payment_received_task = asyncio.create_task(
                provider.ensure_payment_received(
                    sender_address=self.network_topology.sender_address,
                    token_address=self.network_topology.token_address,
                    nonce=current_nonce, poll_interval=0.05)
            )
            barrier_event_task = self._barrier_etf.create_await_event_task()
            log.info('Waiting for payment to provider={}, nonce={}'.format(provider.address,
                                                                           current_nonce))
            # await both awaitables but return when one of them is finished first
            done, pending = await asyncio.wait([payment_received_task, barrier_event_task],
                                               return_when=asyncio.FIRST_COMPLETED)
            payment_successful = False
            if payment_received_task in done:
                if payment_received_task.result() is True:
                    payment_successful = True
                    server.payment_received()
            else:
                assert barrier_event_task in done
                assert payment_received_task in pending
                # cancel the payment received task
                for task in pending:
                    task.cancel()

            if payment_successful is True:
                log.info("Payment received")
                assert barrier_event_task in pending
                await barrier_event_task
                server.barrier_triggered()
                # increment the nonce after the barrier was triggered
                self._increment_nonce_for_current_provider()
            else:
                log.info("Payment not received before next barrier trigger")
                self.track_control.power_off()
                server.payment_missing()

                payment_received_task = asyncio.create_task(
                    provider.ensure_payment_received(
                        sender_address=self.network_topology.sender_address,
                        token_address=self.network_topology.token_address,
                        nonce=self.current_nonce,
                        poll_interval=0.05)
                )
                await payment_received_task
                if payment_received_task.result() is True:
                    self._increment_nonce_for_current_provider()
                    self.track_control.power_on()
                    server.payment_received()
                    log.info("Payment received, turning track power on again")
                else:
                    # this shouldn't happen
                    # FIXME remove assert in production code
                    assert False

    def _on_new_provider(self):
        if self.barcode_handler is not None:
            self.barcode_handler.save_barcode(self.current_provider_address, self.current_nonce)

    def _set_next_provider(self):
        self._current_provider = random.choice(self.raiden_nodes)
        self._on_new_provider()

    @property
    def current_provider_address(self):
        return self._current_provider.address

    @property
    def current_nonce(self):
        return self._provider_nonces[self.current_provider_address]

    def _increment_nonce_for_current_provider(self):
        self._provider_nonces[self.current_provider_address] += 1

    @classmethod
    def build_app(cls, network: NetworkTopology):
        raiden_node_cls = RaidenNode
        arduino_serial = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
        # arduino_serial = ArduinoSerial(port='/dev/cu.usbmodem1421', baudrate=9600, timeout=.1)
        arduino_track_control = ArduinoTrackControl(arduino_serial)
        arduino_track_control.connect()

        # TODO for mock nodes, we should skip the deployment script
        # FIXME asyncio.run() is not the correct method
        try:
            raiden_nodes_dict = asyncio.run(
                start_raiden_nodes(raiden_node_cls, receivers=network.receivers))
        except (asyncio.TimeoutError, TimeoutError):
            log.info(
                'Not all raiden nodes could get started, check the log files for more info. Shutting down')
            sys.exit()
        raiden_nodes = list(raiden_nodes_dict.values())
        track_control = TrackControl(arduino_track_control)

        barcode_handler = BarcodeHandler()
        return cls(track_control, raiden_nodes, network, barcode_handler)
