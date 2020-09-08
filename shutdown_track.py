from track_control import ArduinoSerial, ArduinoTrackControl, TrackControl


def main():
    ser = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
    tc = ArduinoTrackControl(ser)
    tc.connect()
    tc.power_off()


main()
