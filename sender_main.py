import time
import numpy
import requests
import pathlib

import requests
from PIL import Image
from PyV4L2Camera.camera import Camera
from PyV4L2Camera.controls import ControlIDs

from pyzbar.pyzbar import decode

from const import TOKEN_ADDRESS, RECEIVER_LIST


def start_scanning():
    camera = Camera('/dev/video0', 640, 240)
    controls = camera.get_controls()

    for control in controls:
        print(control.name)


    # Video setting options are:
    # options = [ControlIDs.AUTO_WHITE_BALANCE, ControlIDs.BACKLIGHT_COMPENSATION,
    #           ControlIDs.BLACK_LEVEL, ControlIDs.BLUE_BALANCE, ControlIDs.BRIGHTNESS,
    #           ControlIDs.CHROMA_AGC, ControlIDs.COLORFX, ControlIDs.COLOR_KILLER,
    #           ControlIDs.CONTRAST, ControlIDs.DO_WHITE_BALANCE, ControlIDs.EXPOSURE,
    #           ControlIDs.GAIN, ControlIDs.GAMMA, ControlIDs.HFLIP, ControlIDs.HUE,
    #           ControlIDs.HUE_AUTO, ControlIDs.POWER_LINE_FREQUENCY, ControlIDs.RED_BALANCE,
    #           ControlIDs.SATURATION, ControlIDs.SHARPNESS, ControlIDs.VFLIP,
    #           ControlIDs.WHITENESS, ControlIDs.WHITE_BALANCE_TEMPERATURE]

    camera.set_control_value(ControlIDs.BRIGHTNESS, 48)

    pathlib.Path('images').mkdir(parents=True, exist_ok=True)

    while True:
        start = time.monotonic()
        for _ in range(2):
            frame = camera.get_frame()

            # Decode the image
            im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                                 'RGB')

            # Convert the image to a numpy array and back to the pillow image
            arr = numpy.asarray(im)
            im = Image.fromarray(numpy.uint8(arr))
            # Display the image to show that everything works fine
            im.save(f"images/test{time.monotonic()}.jpg")
            try:
                data = decode(im)[0].data
                camera.close()
                return eval(data.decode('utf8'))
            except IndexError:
                print("Couldn't find any QR codes")
            print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))


def send_payment(address, nonce):
    print("Address = %s" % str(address))
    token_address = TOKEN_ADDRESS
    payment_url = 'http://localhost:5001/api/v1/payments/'
    print("Request URL is: %s" % (payment_url + token_address + "/" + str(address)))
    r = requests.post(payment_url + token_address + "/" + str(address),
                      json={"amount": 1, "identifier": nonce}
                      )
    if r.status_code == 200:
        # TODO querry payment history if nonce is used in PaymentSentSuccessfullEvent
        print("Payment successfull")
    else:
        print("Response = %s" % r.text)
        send_payment(address, nonce)


def get_channels():
    r = requests.get("http://localhost:5001/api/v1/channels")
    print(r.json())


def run():
    # We assume that Raiden is already started
    previous_receiver_info = (0, 0)
    while True:
        address_id, nonce = start_scanning()
        if (address_id, nonce) == previous_receiver_info:
            continue
        address = RECEIVER_LIST[address_id]
        send_payment(address, nonce)
        previous_receiver_info = (address_id, nonce)


if __name__ == "__main__":
    # get_channels()
    run()
