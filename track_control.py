import serial
import time
import asyncio


class TrackControl:

    def __init__(self):
        self.arduino_serial = None
        try:
            self.arduino_serial = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)  # open serial port
            # TODO check for initialisation instead of waiting?
            time.sleep(2)
        except serial.serialutil.SerialException:
            # TODO let raise?
            pass

        self._is_powered = False

    @property
    def is_powered(self):
        return self._is_powered

    def power_off(self):
        self.arduino_serial.write(b'0')  # set Arduino output pin 13 low
        print(self.arduino_serial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status
        print("Turned power for train off")
        self._is_powered = False

    def power_on(self):
        self.arduino_serial.write(b'1')  # set Arduino output pin 13 high
        print(self.arduino_serial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status
        print("Turned power for train on")
        self._is_powered = True

    async def next_barrier_trigger(self):
        # waits until the next time the barrier is passed and then returns true
        # TODO see how we can wait for this asynchronously on the arduino!
        await asyncio.sleep(2)
        return True


class TrackControlMock:

    def __init__(self):
        self._is_powered = False

    @property
    def is_powered(self):
        return self._is_powered

    def power_off(self):
        print("Turned power for train off")
        self._is_powered = False

    def power_on(self):
        print("Turned power for train on")
        self._is_powered = True

    async def next_barrier_trigger(self):
        # waits until the next time the barrier is passed and then returns true
        # TODO see how we can wait for this asynchronously on the arduino!
        await asyncio.sleep(10)
        return True
