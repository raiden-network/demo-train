import json
import logging
import os
import random
import subprocess
import requests
from socket import error as socket_error
from time import sleep

import qrcode
from ethereum.utils import checksum_encode

from const import TOKEN_ADDRESS, SENDER_ADDRESS, KEYSTOREPATHRECEIVER, ETH_RPC_ENDPOINT, \
    PASSWORDFILE

log = logging.getLogger(__name__)


def get_receiver_addresses():
    """"Puts all addresses in our KeyStorePath in a dict with key 'receiver_id' """
    KeyStorePath = KEYSTOREPATHRECEIVER
    addresses = {}

    for i, f in enumerate(os.listdir(KeyStorePath)):
        fullpath = os.path.join(KeyStorePath, f)
        if os.path.isfile(fullpath):
            try:
                with open(fullpath) as data_file:
                    data = json.load(data_file)
                    addresses[i + 1] = checksum_encode(str(data['address']))

            except (
                    IOError,
                    json.JSONDecodeError,
                    KeyError,
                    OSError,
                    UnicodeDecodeError,
            ) as ex:
                # Invalid file - skip
                if f.startswith('UTC--'):
                    # Should be a valid account file - warn user
                    msg = 'Invalid account file'
                    if isinstance(ex, IOError) or isinstance(ex, OSError):
                        msg = 'Can not read account file (errno=%s)' % ex.errno
                    if isinstance(ex, json.decoder.JSONDecodeError):
                        msg = 'The account file is not valid JSON format'
                    log.warning(msg, path=fullpath, ex=ex)
    print("Addresses are %s" % addresses)
    return addresses


def starting_raiden_nodes(receivers):
    print("Removing old Raiden Databases")
    subprocess.run(
        "rm -fr ~/.raiden",
        shell=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )

    for receiver_id, address in list(receivers.items()):
        raiden = "raiden --keystore-path " + KEYSTOREPATHRECEIVER \
                 + " --eth-rpc-endpoint " + ETH_RPC_ENDPOINT \
                 + " --address " + str(address) \
                 + " --password-file " + str(PASSWORDFILE) \
                 + " --api-address 127.0.0.1:500" + str(receiver_id) \
                 + " --no-web-ui --accept-disclaimer &"
        print(
            "Starting Raiden Node for address %s on Port %s" %
            (address, ("500" + str(receiver_id)))
        )
        subprocess.Popen(
            raiden,
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
    # Sleeping until raiden Nodes are online
    print("Waiting for Raiden Nodes to start up. This takes ~ 45s")
    sleep(45)
    print("Raiden nodes are started")


def display_qr_code(qr_code):
    # TODO this should push the QR-Code to the display
    qr_code.show()


def querry_for_payment(receiver_id, nonce):
    token_address = TOKEN_ADDRESS
    sender_address = SENDER_ADDRESS
    event_url = "http://localhost:500" + str(receiver_id) + "/api/1/payments/" \
                + token_address + '/' + sender_address
    try:
        r = requests.get(event_url)
        print("Querring URL %s" % event_url)
        print("Request response is: %s" % r.json())
        for data in r.json():
            if data["event"] == "EventPaymentReceivedSuccess" and \
                    data["amount"] == 1 and \
                    data["identifier"] == nonce:
                return True
        return False
    except socket_error:
        # TODO handle connection errors
        print("Couldn't send to Raiden client.")
        print("URL was: %s" % event_url)
        return False


def await_barrier_input():
    # TODO this function awaits the input of the light barrier
    print("Waiting for light barrier trigger")
    sleep(5)
    print("Light barrier was triggered")


def turn_leds_green():
    # TODO Turn LEDs green and start subprocess which turns them red once the train passed
    sleep(0.5)
    print("Turning all LEDs green")


def turn_off_power():
    # TODO
    print("Turning power for train off")


def turn_on_power():
    # TODO
    print("Turning power for train on")


def run(receivers, nonce=1):
    while True:
        # Pick a random receiver
        receiver_id, address = random.choice(list(receivers.items()))
        # TODO: Overwrite old displayed QR code with new one
        # Generate QR code with receiver address
        qr_code = qrcode.make((address, nonce))
        # Display new QR Code on LCD
        display_qr_code(qr_code)
        # Waiting till train passes light barrier
        await_barrier_input()
        # Check if payment was received
        if querry_for_payment(receiver_id, nonce):
            nonce += 1
            print("Payment received")
            turn_leds_green()

        else:
            turn_off_power()
            while True:
                if querry_for_payment(receiver_id, nonce):
                    break
                # TODO remove this sleep
                sleep(1)
            turn_on_power()
            turn_leds_green()


if __name__ == "__main__":
    receivers = get_receiver_addresses()
    starting_raiden_nodes(receivers)
    run(receivers)
