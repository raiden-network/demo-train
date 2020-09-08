import asyncio
import time
import signal

from track_control import (
    ArduinoSerial,
    TrackControl,
    ArduinoTrackControl,
)


async def barrier_trigger_print(track_control):

    while True:
        task = asyncio.create_task(track_control.wait_for_barrier_event())
        done, pending = await asyncio.wait([task])
        print(f'{time.time()}: Triggered Barrier')
        asyncio.sleep(0.0001)


async def shutdown(signal, loop):
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks)
    loop.stop()


def main():
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    try:
        ser = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
        tc = TrackControl(ArduinoTrackControl(ser))
        asyncio.run(barrier_trigger_print(tc))

    finally:
        loop.close()


main()
