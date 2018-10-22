import serial
import time
import asyncio
import logging

from utils import context_switch

log = logging.getLogger()


class ArduinoSerial:

    def __init__(self, port, baudrate, timeout):
        self._serial = None
        try:
            self._serial = serial.Serial(port, baudrate, timeout)  # open serial port
            # TODO check for initialisation instead of waiting?
            time.sleep(2)
        except serial.serialutil.SerialException:
            # TODO why are we passing this exception?
            pass

    def set_high(self):
        self._serial.write(b'1')

    def set_low(self):
        self._serial.write(b'0')

    # TODO return true if bit is high and false when bit is low
    @property
    def is_high(self):
        return NotImplementedError()

    @property
    def status(self):
        return self._serial.readline().decode('utf-8').strip()


class MockSerial:

    def __init__(self):
        self._bit_set = False

    def set_high(self):
        self._bit_set = True

    def set_low(self):
        self._bit_set = False

    @property
    def is_high(self):
        return self._bit_set

    @property
    def status(self):
        return '1' if self._bit_set is True else '0'


class TrackControl:

    def __init__(self, track_power_serial):
        self.track_power_serial = track_power_serial
        self._barrier_event = None
        self._barrier_task = None

    @property
    def is_powered(self):
        return self.track_power_serial.is_high

    @property
    def barrier_event(self):
        # can be awaited in a task like this:
        # `await track_control.barrier_event.wait()`
        if self._barrier_event is None:
            # make sure the event is instantiated when there is an event loop running
            assert asyncio.get_running_loop()
            self._barrier_event = asyncio.Event()
        return self._barrier_event

    def start(self):
        self._barrier_task = asyncio.create_task(self.run_barrier_loop())

    async def run_barrier_loop(self):
        while True:
            await asyncio.sleep(10)
            await self._trigger_barrier()

    async def _trigger_barrier(self):
        # set event so that all tasks waiting on it will continue
        self._barrier_event.set()
        # this context switch needs to happen, so that all tasks that are waiting
        # on the event can advance, before the event is reset again
        await context_switch()
        # reset immediately so that tasks can wait for the next trigger
        self._barrier_event.clear()

    def power_off(self):
        self.track_power_serial.set_low()
        log.debug("Serial read for track power is {}".format(self.track_power_serial.status))
        log.info("Turned power for train off")

    def power_on(self):
        self.track_power_serial.set_high()
        log.debug("Serial read for track power is {}".format(self.track_power_serial.status))
        log.info("Turned power for train on")



