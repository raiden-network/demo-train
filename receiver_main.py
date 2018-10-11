import const

import asyncio
import random
import networkx as nx

from track_control import TrackControl, TrackControlMock
from raiden import RaidenNode, RaidenNodeMock
from typing import List

import code128

from quart import Quart, jsonify, send_file, safe_join
from quart_cors import cors

from const import get_receiver_addresses, SHORTEST_PATHS, CODE_FILE_NAME, SCRIPT_PATH, \
    BAR_CODE_FILE_PATH, \
    create_token_network_topology, SENDER_ADDRESS, TOKEN_ADDRESS
from deployment import start_raiden_nodes

app = Quart(__name__)
app = cors(app)

track_loop_future = None
current_provider = None
mocking = False

# TODO the nonce should be counted PER PROVIDER
current_nonce = None


def on_new_bar_code(bar_code, file_path):
    factor = 4
    bar_code = bar_code.resize((int(bar_code.width * factor), int(bar_code.height * factor)))
    bar_code.save(str(file_path))


def get_shortest_path_to(receiver_address):
    return SHORTEST_PATHS[receiver_address]


def barcode_factory(address, nonce):
    return code128.image("(" + str(address) + "," + str(nonce) + ")")


async def run_track_loop(raiden_receivers: List[RaidenNode], track_control, nonce=1, mocking=False):
    # This should be the only function writing to the global variables!
    global current_provider, current_nonce
    print("Track loop started")

    track_control.power_on()
    while True:
        # Pick a random receiver
        receiver = random.choice(raiden_receivers)
        current_provider = receiver.address
        current_nonce = nonce
        # Generate barcode with receiver address
        barcode_code = barcode_factory(const.RECEIVER_LIST.index(receiver.address), nonce)
        on_new_bar_code(barcode_code, BAR_CODE_FILE_PATH)

        payment_received_task = asyncio.create_task(
            receiver.ensure_payment_received(sender_address=SENDER_ADDRESS,
                                             token_address=TOKEN_ADDRESS,
                                             nonce=current_nonce, poll_interval=0.05,
                                             mocking=mocking)
        )
        await track_control.next_barrier_trigger()

        payment_successful = False

        # don't wait for the task to finish, we want to know the result/ no result now
        if payment_received_task.done():
            payment_successful = payment_received_task.result()
        else:
            payment_received_task.cancel()

        if payment_successful is True:
            nonce += 1
            print("Payment received")
        else:
            print("Payment not received before next barrier trigger")
            track_control.power_off()

            payment_received_task = asyncio.create_task(
                receiver.ensure_payment_received(sender_address=SENDER_ADDRESS,
                                                 token_address=TOKEN_ADDRESS,
                                                 poll_interval=0.05,
                                                 mocking=mocking)
            )
            await payment_received_task
            if payment_received_task.result():
                track_control.power_on()
            else:
                # this shouldn't happen
                # FIXME remove assert in production code
                assert False


@app.route('/api/1/provider/current')
async def get_current_provider():
    # to leave interface as is, just send a 0 indentifier for now,
    # we don't need the identifier now
    data = {
        "address": current_provider,
        "identifier": current_nonce
    }
    return jsonify(data)


@app.route('/api/1/provider/qr/current')
def get_current_qr_code():
    return send_file(safe_join(SCRIPT_PATH, CODE_FILE_NAME))


@app.route('/api/1/_debug/')
async def show_debug_info():
    return str(track_loop_future)


#@app.route('/api/1/path/current')
#async def get_current_path():
#    return jsonify(get_shortest_path_to(current_provider))


@app.before_serving
async def start_services():
    global track_loop_future

    track_control_cls = TrackControl
    raiden_node_cls = RaidenNode

    if mocking is True:
        track_control_cls = TrackControlMock
        raiden_node_cls = RaidenNodeMock
        print('Run mocked Raiden Nodes and Track control instances')

    receivers = get_receiver_addresses()
    network = create_token_network_topology()
    const.SHORTEST_PATHS = nx.single_source_shortest_path(network, SENDER_ADDRESS)

    raiden_nodes = await start_raiden_nodes(raiden_node_cls, receivers)
    raiden_receivers = [node for node in raiden_nodes.values() if
                        node.address is not SENDER_ADDRESS]
    track_control = track_control_cls()

    track_loop_future = asyncio.ensure_future(
        run_track_loop(raiden_receivers, track_control, mocking=mocking)
                                              )
    print('Initialization completed')


@app.after_serving
async def end_services():
    track_loop_future.cancel()


def build_app(mock=False):
    global mocking
    mocking = bool(mock)
    return app
