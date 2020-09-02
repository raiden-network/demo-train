import asyncio
import random
import subprocess
import sys
import time
from typing import List, Optional

import code128

from const import BAR_CODE_FILE_PATH, RECEIVER_LIST, POST_BARRIER_WAIT_TIME
from deployment import start_raiden_nodes
from raiden import RaidenNode, RaidenNodeMock
from server import Server
from track_control import (
    TrackControl,
    ArduinoSerial,
    ArduinoTrackControl,
    MockArduinoTrackControl
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
        self._barrier_loop_task = None
        self._possible_providers = None
        self._frontend = Server()

    def start(self):
        """
        NOTE: it's necessary that the asyncio related instantiations are done at runtime,
        because we need a running loop!
        :return:
        """
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
        self._frontend.connect()
        time.sleep(2)
        self._frontend.start()
        time.sleep(2)

        self._barrier_loop_task = asyncio.create_task(self.track_control.run_barrier_loop())
        self._track_loop = asyncio.create_task(self.run())

    # FIXME make awaitable so that errors can raise
    # FIXME handle gracefully
    def stop(self):
        self.track_control.power_off()
        try:
            self._track_loop.cancel()
        except asyncio.CancelledError:
            pass

    def _prepare_cycle(self):
        self._set_next_provider()
        self._frontend.new_receiver(ADDRESS_MAP[self.current_provider_address])

    async def _process_cycle(self, provider, nonce):
        payment_received_task = asyncio.create_task(
            provider.ensure_payment_received(
                sender_address=self.network_topology.sender_address,
                token_address=self.network_topology.token_address,
                nonce=nonce, poll_interval=0.05)
        )
        barrier_event_task = asyncio.create_task(self.track_control.wait_for_barrier_event())

        log.info(f'Waiting for payment to provider={provider.address}, nonce={nonce}')
        pending_tasks = [payment_received_task, barrier_event_task]
        while True:
            # Wait for payment and for barrier events, but return when one of them is finished first
            done, pending_tasks = await asyncio.wait(pending_tasks,
                                                return_when=asyncio.FIRST_COMPLETED)

            if payment_received_task in done:
                if payment_received_task.result() is True:
                    log.info("Payment received")
                    self._frontend.payment_received()
                    if not self.track_control.is_powered:
                        # we have shut down the power before!
                        self.track_control.power_on()
                        log.info("Turning track power on.")
                        # wait so that the train can move out of the barrier after a power on
                        # (where the train is standing close to the barrier!)
                        await asyncio.sleep(POST_BARRIER_WAIT_TIME)

                    if barrier_event_task in pending_tasks:
                        # wait for the barrier to stay in sync
                        await barrier_event_task
                        await asyncio.sleep(POST_BARRIER_WAIT_TIME)
                        assert barrier_event_task.done()
                        pending_tasks.remove(barrier_event_task)
                        assert len(pending_tasks) == 0
                        # only at this point we can call this cycle complete!
                        break
                else:
                    # this code path is not expected to be executed,
                    # but we would need to restart waiting for the payment
                    payment_received_task = asyncio.create_task(
                        provider.ensure_payment_received(
                            sender_address=self.network_topology.sender_address,
                            token_address=self.network_topology.token_address,
                            nonce=nonce, poll_interval=0.05)
                    )
            else:
                assert barrier_event_task in done
                log.debug("Barrier was triggered.")
                self._frontend.barrier_triggered()
                assert payment_received_task in pending_tasks
                log.info("Payment not received before barrier trigger")
                self.track_control.power_off()
                log.info("Shut off track power")
                self._frontend.payment_missing()

    async def run(self):
        # TODO make sure that every neccessary task is running:
        # (barrier_etf, barrier_ltr instantiated, etc)
        
        self._prepare_cycle()
        barrier_task = asyncio.create_task(self.track_control.wait_for_barrier_event())
        self.track_control.power_on()
        log.info("Track loop started")

        # Just wait for the trigger to sync up, then sleep a little until the train is passed
        # this is the extra round to sync up, the train will not pay the same addres/nonce
        # combination twice, even if it happens to see the barcode twice
        await barrier_task
        log.info("Syncing finished, the first round was free!")
        assert barrier_task.done()
        await asyncio.sleep(POST_BARRIER_WAIT_TIME)

        # now the paid round begins!
        while True:
            await self._process_cycle(self._current_provider, self.current_nonce)
            self._increment_nonce_for_current_provider()
            self._prepare_cycle()


    def _on_new_provider(self):
        if self.barcode_handler is not None:
            self.barcode_handler.save_barcode(self.current_provider_address, self.current_nonce)

    def set_possible_providers(self, nodes):
        if not set(nodes).issubset(set(self.raiden_nodes)):
            raise ValueError("Possible providers have to be known raiden nodes.")
        self._possible_providers = nodes

    def _set_next_provider(self): 
        nodes_to_choose_from = self._possible_providers or self.raiden_nodes
        self._current_provider = random.choice(nodes_to_choose_from)
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
    def build_app(cls, network: NetworkTopology, mock_arduino=False, mock_raiden=False,
                  config_file=None, possible_receiver_addresses=None):
        raiden_node_cls = RaidenNode
        if mock_arduino:
            log.debug('Mocking Arduino serial')
            arduino_track_control = MockArduinoTrackControl()
        else:
            arduino_serial = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
            # arduino_serial = ArduinoSerial(port='/dev/cu.usbmodem1421', baudrate=9600, timeout=.1)
            arduino_track_control = ArduinoTrackControl(arduino_serial)
            log.debug('Connecting to Arduino serial.')
            arduino_track_control.connect()

        if mock_raiden:
            raiden_node_cls = RaidenNodeMock
            log.debug('Mocking RaidenNode')

        # TODO for mock nodes, we should skip the deployment script
        try:
            raiden_nodes_dict = asyncio.run(
                start_raiden_nodes(raiden_node_cls, receivers=network.receivers,
                                   config_file=config_file))
        except (asyncio.TimeoutError, TimeoutError):
            log.info(
                'Not all raiden nodes could get started, check the log files for more info. Shutting down')
            sys.exit()
        raiden_nodes = list(raiden_nodes_dict.values())
        # TODO 
        track_control = TrackControl(arduino_track_control)

        barcode_handler = BarcodeHandler()

        obj = cls(track_control, raiden_nodes, network, barcode_handler)
        if possible_receiver_addresses is not None:
            possible_receiver_nodes = [raiden_nodes_dict[addr] for addr in possible_receiver_addresses]
            obj.set_possible_providers(possible_receiver_nodes)
        return obj
