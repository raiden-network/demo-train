from track_control import ArduinoSerial, TrackControl, ArduinoTrackControl
from server import Server
import time
import asyncio
import subprocess
import os
import signal



arduino_serial = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
arduino_track_control = ArduinoTrackControl(arduino_serial)
track_control = TrackControl(arduino_track_control)
average_elements = 3

round_times = []
last_round_time = 0
last_trigger_time = time.time()

frontend = Server()


def running_average():
    if round_times:
        return (sum(round_times)) / len(round_times)
    else:
        return 0.


async def run_loop():
    global last_trigger_time, last_round_time, round_times
    while True:
        barrier_task = asyncio.create_task(track_control.wait_for_barrier_event())
        await barrier_task
        frontend.barrier_triggered()
        trigger_time = time.time()
    
        round_time = trigger_time - last_trigger_time
    
        round_times.append(round_time)
        if len(round_times) > average_elements:
            round_times.pop(0)
    
        print_string = f"""
        New round finished:
            - Running avg ({len(round_times)} elem.:       {running_average()})
            - Current time:                                     {round_time} 
            - Last time:                                        {last_round_time} 
            - Deviation last:                                   {round_time - last_round_time} 
            - Deviation avg:                                    {round_time - running_average()}
        """
        print(print_string)
        last_trigger_time = trigger_time
        last_round_time = round_time

async def main():
    run_task = asyncio.create_task(track_control.run())
    await asyncio.create_task(run_loop())


try:
    arduino_track_control.connect()
    print('Arduino connected')
    subpr = subprocess.Popen(
                        "DISPLAY=:0.0 "
                                    "/home/train/processing-3.4/processing-java "
                                                "--sketch=/home/train/demo-train/processing/sketchbook/railTrack --force --run",
                                                            shell=True,
                                                                        stdout=subprocess.DEVNULL,
                                                                                    stderr=subprocess.DEVNULL,
                                                                                    preexec_fn=os.setsid)
    time.sleep(5)
    frontend.connect()
    time.sleep(2)
    frontend.start()
    print('Frontend started')
    time.sleep(2)
    track_control.power_on()
    print('Powered on tracks')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except Exception as e:
    print(e)
    print("Received exit, exiting")
    track_control.power_off()
    arduino_serial._serial.close()
    os.killpg(os.getpgid(subpr.pid), signal.SIGTERM) 
