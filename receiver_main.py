import json
import serial
import time
import random
import subprocess
import requests
import networkx as nx
from socket import error as socket_error
from time import sleep, monotonic

import qrcode
from ethereum.utils import checksum_encode

from const import *


ArduinoSerial = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)  # open serial port
time.sleep(2)


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
    print("Addresses are %s" % addresses)
    return addresses


def starting_raiden_nodes(receivers, key_store_path=KEYSTOREPATHRECEIVER, delete_keystore=True):
    if delete_keystore:
        print("Removing old Raiden Databases")
        subprocess.run(
            "rm -fr ~/.raiden",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )

    for receiver_id, address in list(receivers.items()):
        # FIXME setting the matrix server manually is just a hotfix for matrix issues
        raiden = "raiden --keystore-path " + key_store_path \
                 + " --eth-rpc-endpoint " + ETH_RPC_ENDPOINT \
                 + " --address " + str(address) \
                 + " --password-file " + str(PASSWORDFILE) \
                 + " --api-address 127.0.0.1:500" + str(receiver_id) \
                 + " --no-web-ui --accept-disclaimer"\
                 + " --matrix-server=https://transport02.raiden.network &"
        print(
            "Starting Raiden Node for address %s on Port %s" %
            (address, ("500" + str(receiver_id)))
        )
        subprocess.Popen(
            raiden,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Waiting until all Raiden nodes are live
    # TODO Find a more elegant way to check if raiden nodes are online
    start_time = monotonic()
    for receiver_id, address in list(receivers.items()):
        url = "http://localhost:500"+str(receiver_id)+"/api/1/address"
        while True:
            try:
                r = requests.get(url)
                if r.json()["our_address"] == address:
                    break
            except socket_error:
                sleep(1)
            if monotonic() - start_time > 300:
                raise TimeoutError("It took more than 5 minutes to start the Raiden Nodes")

    print("Raiden nodes are started")


def display_qr_code(qr_code):
    # TODO this should push the QR-Code to the display
    qr_code.show()


def querry_for_payment(network, receiver_address, receiver_id, nonce):
    token_address = TOKEN_ADDRESS
    sender_address = SENDER_ADDRESS
    event_url = "http://localhost:500" + str(receiver_id) + "/api/1/payments/" \
                + token_address + '/' + sender_address
    # TODO This needs to be provided to the Frontend
    print(nx.shortest_path(network, source=sender_address, target=receiver_address))
    try:
        r = requests.get(event_url)
        # print("Querring URL %s" % event_url)
        # print("Request response is: %s" % r.json())
        for data in r.json():
            if data["event"] == "EventPaymentReceivedSuccess" and \
                    data["amount"] == 1 and \
                    data["identifier"] == nonce:
                return True
        return False
    except socket_error:
        # TODO handle connection errors
        print("Raiden client not available.")
        # print("URL was: %s" % event_url)
        return False


def create_token_network_topology():
    # This is hardcoded. To see the topology checkout Images/Network_topology.png
    G = nx.Graph()
    G.add_edge(SENDER_ADDRESS, RECEIVER_1_ADDRESS)
    G.add_edges_from([
        (RECEIVER_1_ADDRESS, RECEIVER_2_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_5_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_8_ADDRESS)
    ])
    G.add_edge(RECEIVER_2_ADDRESS, RECEIVER_3_ADDRESS)
    G.add_edge(RECEIVER_3_ADDRESS, RECEIVER_4_ADDRESS)
    G.add_edge(RECEIVER_5_ADDRESS, RECEIVER_6_ADDRESS)
    G.add_edge(RECEIVER_6_ADDRESS, RECEIVER_7_ADDRESS)

    """Belows code can be used to debug the Graph"""
    # plt.subplot(121)
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    return G


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
    ArduinoSerial.write(b'0')  # set Arduino output pin 13 low
    print(ArduinoSerial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status
    print("Turning power for train off")


def turn_on_power():
    ArduinoSerial.write(b'1')  # set Arduino output pin 13 high
    print(ArduinoSerial.readline().decode('utf-8').strip())  # get Arduino output pin 13 status
    print("Turning power for train on")


def run(receivers, network, nonce=1):
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
        if querry_for_payment(network, address, receiver_id, nonce):
            nonce += 1
            print("Payment received")
            turn_leds_green()

        else:
            turn_off_power()
            while True:
                if querry_for_payment(network, address, receiver_id, nonce):
                    break
                # TODO remove this sleep
                sleep(1)
            turn_on_power()
            turn_leds_green()


if __name__ == "__main__":
    receivers = get_receiver_addresses()
    network = create_token_network_topology()
    starting_raiden_nodes(receivers)
    run(receivers, network)
