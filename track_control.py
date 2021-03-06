import serial
import time
import asyncio
import logging
from typing import List, Optional

from enum import Enum

log = logging.getLogger()


# // 0: request Sensor Data/'ACK Signal'
# // 1: power Track off
# // 2: power Track on
# // 3: turn barrier measuring off
# // 4: turn barrier measuring on
class OutMessage(Enum):
    ACK = 0
    REQUEST_SENSOR = 1
    POWER_OFF = 2
    POWER_ON = 3
    DISTANCE_MEASURE_OFF = 4
    DISTANCE_MEASURE_ON = 5

    @classmethod
    def encode(cls, message: 'OutMessage'):
        encoded = None
        # ACK is not implemented at the moment,
        # so for now this is equivalent to a sensor request
        if message is cls.ACK:
            encoded = bytes([0])
        elif message is cls.REQUEST_SENSOR:
            encoded = bytes([0])
        elif message is cls.POWER_OFF:
            encoded = bytes([1])
        elif message is cls.POWER_ON:
            encoded = bytes([2])
        elif message is cls.DISTANCE_MEASURE_OFF:
            encoded = bytes([3])
        elif message is cls.DISTANCE_MEASURE_ON:
            encoded = bytes([4])
        else:
            ValueError('Message not known')
        return encoded


# // 0: not measuring,
# // 1: object is not close,
# // 2: object is close
class BarrierState(Enum):
    NOT_MEASURING = 0
    OBJECT_NOT_CLOSE = 1
    OBJECT_CLOSE = 2

    @staticmethod
    def decode(byte):
        decoded = None
        if byte == bytes([0]):
            decoded = BarrierState.NOT_MEASURING
        elif byte == bytes([1]):
            decoded = BarrierState.OBJECT_NOT_CLOSE
        elif byte == bytes([2]):
            decoded = BarrierState.OBJECT_CLOSE
        else:
            print('can;t decode')
            raise ValueError('Can\'t decode data')
        return decoded


# // 0: Power is Off,
# // 1: Power is On
class PowerState(Enum):
    POWER_OFF = 0
    POWER_ON = 1

    @staticmethod
    def decode(byte):
        decoded = None
        if byte == bytes([0]):
            decoded = PowerState.POWER_OFF
        elif byte == bytes([1]):
            decoded = PowerState.POWER_ON
        else:
            print('can;t decode')
            raise ValueError('Can\'t decode data')
        return decoded


class ArduinoSerial:

    def __init__(self, port, baudrate, timeout):
        self._serial = serial.Serial(port, baudrate, timeout=timeout)  # open serial port
        time.sleep(2)

    def do_handshake(self):
        self._wait_for_read(b'H')
        send_value = OutMessage.encode(OutMessage.ACK)
        self._serial.write(send_value)
        # wait for ACK from Arduino
        self._wait_for_read(b'A', allowed_prepending=[b'H'])
        log.debug('Handshake with Arduino succesful')
        return True

    def send_message(self, message):
        send_value = OutMessage.encode(message)
        log.debug(f'Send message to Arduino: {message}<{send_value}>')
        self._serial.write(send_value)
        # wait for ACK from Arduino
        self._wait_for_read(b'A')
        log.debug('Got ACK from Arduino')

    def read_bytes(self, nof_bytes):
        values = []
        for _ in range(nof_bytes):
            val = self._serial.read()
            if val is b'':
                raise ValueError('No bytes to read')
            values.append(val)
        log.debug(f"Read bytes from Arduino: {values}")
        return tuple(values)

    def _wait_for_read(self, expected, max_tries: Optional[int]=None, allowed_prepending: Optional[List]=None):
        val = self._serial.read()
        tried = 0
        if allowed_prepending is None:
            allowed_prepending = []
        allowed_prepending_signals = {b'', *allowed_prepending}

        while val in allowed_prepending_signals:
            val = self._serial.read()
            if max_tries is not None:
                tried += 1
                if tried > max_tries:
                    break
            time.sleep(0.05)

        was_expected = bool(val == expected)
        if was_expected is False:
            raise ValueError(f'Unexpected serial read from Arduino! Expected {expected}, got {val}.')


class ArduinoTrackControl:

    def __init__(self, serial: ArduinoSerial):
        self._serial = serial
        self._barrier_state = None
        self._power_state = None

    @property
    def barrier_state(self):
        return self._barrier_state

    @property
    def power_state(self):
        return self._power_state

    def connect(self):
        return self._serial.do_handshake()

    def power_on(self):
        self._serial.send_message(OutMessage.POWER_ON)

    def power_off(self):
        self._serial.send_message(OutMessage.POWER_OFF)

    def start_measure(self):
        self._serial.send_message(OutMessage.DISTANCE_MEASURE_ON)

    def stop_measure(self):
        self._serial.send_message(OutMessage.DISTANCE_MEASURE_OFF)

    def update_sensor_data(self):
        self._serial.send_message(OutMessage.REQUEST_SENSOR)
        power_byte, barrier_byte = self._serial.read_bytes(2)
        self._power_state = PowerState.decode(power_byte)
        self._barrier_state = BarrierState.decode(barrier_byte)


class MockArduinoTrackControl:

    def __init__(self):
        self._barrier_state = None
        self._power_state = None

    @property
    def barrier_state(self):
        return self._barrier_state

    @property
    def power_state(self):
        return self._power_state

    def connect(self):
        return True

    def power_on(self):
        self._power_state = PowerState.POWER_ON

    def power_off(self):
        self._power_state = PowerState.POWER_OFF

    def start_measure(self):
        # start with not triggering
        pass

    def stop_measure(self):
        self._barrier_state = BarrierState.NOT_MEASURING

    def update_sensor_data(self):
        # we don't communicate with arduino, so do nothing here
        pass

    def mock_set_barrier_trigger(self):
        """
        only for setting the barrier state manually in the mock class,
        """
        self._barrier_state = BarrierState.OBJECT_CLOSE

    def mock_unset_barrier_trigger(self):
        """
        only for unsetting the barrier state manually in the mock class
        """
        self._barrier_state = BarrierState.OBJECT_NOT_CLOSE


class EventTaskFactory:

    async def await_event(self):
        raise NotImplementedError

    def create_await_event_task(self):
        return asyncio.create_task(self.await_event())


class LoopTaskRunner:

    def is_running(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class BarrierEventTaskFactory(EventTaskFactory):

    def __init__(self, track_control: 'TrackControl'):
        self._track_control = track_control

    async def await_event(self):
        event = asyncio.Event()
        self._track_control.register_barrier_event(event)
        await event.wait()
        self._track_control.unregister_barrier_event(event)


class BarrierLoopTaskRunner(LoopTaskRunner):

    def __init__(self, track_control: 'TrackControl'):
        self._track_control = track_control
        self._barrier_task = None

    def is_running(self):
        return not self._barrier_task.done()

    def start(self):
        self._barrier_task = asyncio.create_task(self._track_control.run_barrier_loop())

    def stop(self):
        # TODO implement
        pass


class TrackControl:

    def __init__(self, arduino_track_control):
        # the ArduinoTrackControl is assumed to be connected already!
        self.arduino_track_control = arduino_track_control
        self._barrier_events = set()
        # sleep for x seconds when barrier was triggered
        self._barrier_sleep_time = 4.

    @property
    def is_powered(self):
        return bool(self.arduino_track_control.power_state is PowerState.POWER_ON)

    @property
    def _any_event_is_waiting(self):
        for event in self._barrier_events:
            if not event.is_set():
                return True
        return False

    def register_barrier_event(self, event: asyncio.Event):
        if not event.is_set():
            self._barrier_events.add(event)
        else:
            raise Exception('Tried to register an Event that is aleady set')

    def unregister_barrier_event(self, event: asyncio.Event):
        self._barrier_events.remove(event)

    def remove_all_barrier_events(self):
        self._barrier_events = set()

    async def run_barrier_loop(self):
        while True:
            if self._any_event_is_waiting:
                self.arduino_track_control.start_measure()
                while True:
                    self.arduino_track_control.update_sensor_data()
                    barrier_state = self.arduino_track_control.barrier_state
                    if barrier_state is BarrierState.OBJECT_CLOSE:
                        self.trigger_barrier()
                        self.arduino_track_control.stop_measure()
                        await asyncio.sleep(self._barrier_sleep_time)
                    else:
                        await asyncio.sleep(0.1)
                    # break out of loop to trigger measure again
                    break
            else:
                await asyncio.sleep(0.1)

    def trigger_barrier(self):
        for event in self._barrier_events:
            event.set()

    def power_off(self):
        self.arduino_track_control.power_off()
        self.arduino_track_control.update_sensor_data()
        # assert not self.arduino_track_control.is_powered()
        log.info("Turned power for train off")

    def power_on(self):
        self.arduino_track_control.power_on()
        self.arduino_track_control.update_sensor_data()
        # assert self.arduino_track_control.is_powered()
        log.info("Turned power for train on")
