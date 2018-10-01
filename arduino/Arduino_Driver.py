import serial
import time

ArduinoSerial = serial.Serial('COM4', 9600, timeout=.1)  # open serial port
time.sleep(2)


def power_on():
    ArduinoSerial.write(b'1')  # set Arduino output pin 13 high
    print(ArduinoSerial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status


def power_off():
    ArduinoSerial.write(b'0')  # set Arduino output pin 13 low
    print(ArduinoSerial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status


def exit():
    ArduinoSerial.write(b'0')  # set Arduino output pin 13 low and quit
    ArduinoSerial.close()  # close serial port
    quit()


time.sleep(5)
power_on()
print("Sleeping 10s")
time.sleep(10)
print("turning power off")
power_off()
