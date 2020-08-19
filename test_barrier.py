import asyncio
import time

from track_control import (
    ArduinoSerial,
    TrackControl,
    ArduinoTrackControl,
    BarrierEventTaskFactory,
    BarrierLoopTaskRunner
)


async def barrier_trigger_print(ser):
    tc = TrackControl(ArduinoTrackControl(ser))
    etf = BarrierEventTaskFactory(tc)
    ltf = BarrierLoopTaskRunner(tc)
    ltf.start()

    while True:
        task = etf.create_await_event_task()
        done, pending = await asyncio.wait([task])
        print(f'{time.time()}: Triggered Barrier')

ser = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
asyncio.run(barrier_trigger_print(ser))
