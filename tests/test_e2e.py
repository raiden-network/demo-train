import subprocess
import random
import os

import pytest

from time import sleep

from const import (
    RECEIVER_1_ADDRESS,
    RECEIVER_2_ADDRESS,
    RECEIVER_3_ADDRESS,
    RECEIVER_4_ADDRESS,
    RECEIVER_5_ADDRESS,
    RECEIVER_6_ADDRESS,
    RECEIVER_7_ADDRESS,
    RECEIVER_8_ADDRESS,
    SENDER_ADDRESS,
    create_token_network_topology
)
from deployment import start_raiden_nodes, get_receiver_addresses
from sender_main import send_payment


"""
FIXME this are old tests - implement the new architecture changes to make them work again!
"""

receivers = [
    RECEIVER_1_ADDRESS,
    RECEIVER_2_ADDRESS,
    RECEIVER_3_ADDRESS,
    RECEIVER_4_ADDRESS,
    RECEIVER_5_ADDRESS,
    RECEIVER_6_ADDRESS,
    RECEIVER_7_ADDRESS,
    RECEIVER_8_ADDRESS
]


@pytest.mark.skip
def test_address_import():
    addresses = get_receiver_addresses()
    for address in addresses.values():
        assert address in receivers


# This test takes a couple of minutes
@pytest.mark.skip
def test_payment():
    # Starting the needed raiden nodes
    dictionary_sender = {1: SENDER_ADDRESS}
    dictionary_receiver = {}

    start_raiden_nodes(dictionary_sender,
                       key_store_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      'sender/key_storage/'))
    for i, address in enumerate(receivers):
        dictionary_receiver[i + 2] = address
    start_raiden_nodes(dictionary_receiver, delete_keystore=False)
    # Creating the token network
    network = create_token_network_topology()
    # Send Payment and check if it was received
    for i, address in enumerate(receivers):
        nonce = random.randint(1, 20)
        send_payment(address=address, nonce=nonce)
        # Wait for 5 seconds - This is needed to wait for the payment to succeed
        sleep(5)
        #assert query_for_payment(
        #    network,
        #    receiver_address=address,
        #    receiver_id=i + 2,
        #    nonce=nonce
        #)

    # Cleaning up the Database & killing running raiden instances
    subprocess.run(
        "rm -fr ~/.raiden",
        shell=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )

