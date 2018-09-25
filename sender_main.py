import time
import io

import requests
from PIL import Image
try:
    import picamera
except ModuleNotFoundError:
    pass
from pyzbar.pyzbar import decode

from const import TOKEN_ADDRESS


def start_scanning():
    stream = io.BytesIO()
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 10
    camera.start_preview()
    time.sleep(2)
    while True:
        start = time.monotonic()
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        image = Image.open(stream)
        try:
            data = decode(image)[0].data
            camera.close()
            return eval(data.decode('utf8'))
        except IndexError:
             print("Couldn't find any QR codes")
        print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))
        stream = io.BytesIO()


def send_payment(address, nonce):
    print("Address = %s" % str(address))
    token_address = TOKEN_ADDRESS
    payment_url = 'http://localhost:5001/api/1/payments/'
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
    r = requests.get("http://localhost:5001/api/1/channels")
    print(r.json())


def run():
    # We assume that Raiden is already started
    while True:
        address, nonce = start_scanning()
        send_payment(address, nonce)


if __name__ == "__main__":
    # get_channels()
    run()
