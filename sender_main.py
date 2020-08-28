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


def start_scanning(camera=None):

    """ Video settings """
    #controls = camera.get_controls()
    #for control in controls:
    #    print(control.name)
    # Video setting options are:
    # options = [ControlIDs.AUTO_WHITE_BALANCE, ControlIDs.BACKLIGHT_COMPENSATION,
    #           ControlIDs.BLACK_LEVEL, ControlIDs.BLUE_BALANCE, ControlIDs.BRIGHTNESS,
    #           ControlIDs.CHROMA_AGC, ControlIDs.COLORFX, ControlIDs.COLOR_KILLER,
    #           ControlIDs.CONTRAST, ControlIDs.DO_WHITE_BALANCE, ControlIDs.EXPOSURE,
    #           ControlIDs.GAIN, ControlIDs.GAMMA, ControlIDs.HFLIP, ControlIDs.HUE,
    #           ControlIDs.HUE_AUTO, ControlIDs.POWER_LINE_FREQUENCY, ControlIDs.RED_BALANCE,
    #           ControlIDs.SATURATION, ControlIDs.SHARPNESS, ControlIDs.VFLIP,
    #           ControlIDs.WHITENESS, ControlIDs.WHITE_BALANCE_TEMPERATURE]

    pathlib.Path('images').mkdir(parents=True, exist_ok=True)

    while True:
        start = time.monotonic()
        frame = camera.get_frame()

        # Decode the image
        im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                                 'RGB')
        im = im.crop((100, 200, im.width - 100, im.height - 150)).rotate(3)
        # im = im.crop((100, 200, im.width - 100, im.height - 150))

        # enhancer = ImageEnhance.Sharpness(im)

        # im = enhancer.enhance(2)


        #thresh = 130
        #fn = lambda x: 255 if x > thresh else 0
        #im = im.convert('L').point(fn, mode='1')

        # Convert the image to a numpy array and back to the pillow image
        # arr = numpy.asarray(im)
        # im = Image.fromarray(numpy.uint8(arr))
        # Display the image to show that everything works fine

        im.save(f"images/test{time.monotonic()}.jpg")
        try:
            data = decode(im)[0].data
            print(data)
            return tuple(int(i) for i in data.decode('utf8').split(","))
        except IndexError:
            print("Couldn't find any QR codes")
            print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))
        except ValueError:
            print("Decodation of the QR code failed due to wrong result")


def send_payment(address, nonce):
    print("Address = %s" % str(address))
    token_address = TOKEN_ADDRESS
    payment_url = 'http://localhost:5001/api/v1/payments/'
    print("Request URL is: %s" % (payment_url + token_address + "/" + str(address)))
    r = requests.post(payment_url + token_address + "/" + str(address),
                      json={"amount": 1, "identifier": str(nonce)}
                      )
    if r.status_code == 200:
        # TODO querry payment history if nonce is used in PaymentSentSuccessfullEvent
        print("Payment successfull")
    else:
        # FIXME we need a backoff strategy, this will recursively fire a
        # lot of requests if the payment never goes through and will never stop.
        print("Response = %s" % r.text)
        send_payment(address, nonce)


def get_channels():
    r = requests.get("http://localhost:5001/api/v1/channels")
    print(r.json())


def run():
    # We assume that Raiden is already started
    previous_receiver_info = (0, 0)
    camera = Camera('/dev/video0', 1024, 576)
    camera.set_control_value(ControlIDs.CONTRAST, 10)
    camera.set_control_value(ControlIDs.SATURATION, 10)
    while True:
        address_id, nonce = start_scanning(camera)
        if (address_id, nonce) == previous_receiver_info:
            continue
        address = RECEIVER_LIST[address_id]
        send_payment(address, nonce)
        previous_receiver_info = (address_id, nonce)


if __name__ == "__main__":
    # get_channels()
    run()
