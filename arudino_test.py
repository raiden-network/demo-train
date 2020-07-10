from track_control import ArduinoSerial, ArduinoTrackControl
from time import sleep
import logging

log = logging.getLogger()


arduino_serial = ArduinoSerial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)
# arduino_serial = ArduinoSerial(port='/dev/cu.usbmodem1421', baudrate=9600, timeout=.1)
arduino_track_control = ArduinoTrackControl(arduino_serial)
if arduino_track_control.connect():
    print("Connection successfull")
sleep(5)
arduino_track_control.power_on()
sleep(5)
arduino_track_control.power_off()