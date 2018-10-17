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
        self.arduino_serial.write(bytes([0]))  # Sets Arduino pin 3 LOW
        print(self.arduino_serial.readline().decode(
            'utf-8').strip())  # get Arduino output pin 13 status
        print("Turned power for train off")
        self._is_powered = False

    def power_on(self):
        self.arduino_serial.write(bytes([1]))  # Sets Arduino pin 3 HIGH
        print(self.arduino_serial.readline().decode(
            'utf-8').strip())  # get Arduino output pin 13 status
        print("Turned power for train on")
        self._is_powered = True

    async def next_barrier_trigger(self):
        self.arduino_serial.write(bytes([2]))  # Triggers a series of distance measurements
        self.arduino_serial.flush()  # Make sure arduino reads the above command
        while True:
            data = self.arduino_serial.readline()
            try:
                data = float(data.decode().strip())
            except ValueError:
                data = 100
            if data < 20:  # If something passes closer than 20cm
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
