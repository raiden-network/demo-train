from track_control import ArduinoSerial, TrackControl, ArduinoTrackControl
import time
import asyncio


current_trigger = time.time()

arduino_serial = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
arduino_track_control = ArduinoTrackControl(arduino_serial)
track_control = TrackControl(arduino_serial)
average_elements = 10

round_times = []
last_round_time = 0
last_trigger_time = time.time()


def running_average():
    if round_times:
        return (sum(round_times)) / len(round_times)
    else:
        return 0.


while True:
    barrier_task = asyncio.create_task(track_control.wait_for_barrier_event())
    asyncio.run(barrier_task)
    trigger_time = time.time()

    round_time = trigger_time - last_trigger_time

    round_times.append(round_time)
    if len(round_times) > average_elements:
        round_times.pop(0)

    print_string = """
    New round finished:
        - Running avg ({average_elements} elem.:    {running_average()})
        - Current time:                             {round_time} 
        - Last time:                                {last_round_time} 
        - Deviation last:                           {round_time - last_round_time} 
        - Deviation avg:                            {round_time - running_average()}
    """
    print(print_string)
    last_trigger_time = trigger_time
