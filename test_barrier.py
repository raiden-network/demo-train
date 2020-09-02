import asyncio
import time

from track_control import (
    ArduinoSerial,
    TrackControl,
    ArduinoTrackControl,
)


async def barrier_trigger_print(ser):
    # FIXME tests do not run
    tc = TrackControl(ArduinoTrackControl(ser))

    while True:
        done, pending = await asyncio.wait([task])
        print(f'{time.time()}: Triggered Barrier')

ser = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
asyncio.run(barrier_trigger_print(ser))
