from quart import Quart, send_file, jsonify, safe_join
from quart_cors import cors
from networkx import nx
import asyncio

from utils import get_random_element

from const import *


# TODO refactor, since this is currently highly dependent
# maybe just use receiver main and mock the missing parts later on
from receiver_main import qr_factory, on_new_qr_code

app = Quart(__name__)
app = cors(app)

NOF_ADDRESSES = 10

RECEIVERS = [RECEIVER_1_ADDRESS, RECEIVER_2_ADDRESS, RECEIVER_3_ADDRESS, RECEIVER_4_ADDRESS, RECEIVER_5_ADDRESS,
             RECEIVER_6_ADDRESS, RECEIVER_7_ADDRESS, RECEIVER_8_ADDRESS]

PROVIDER_MAP = {address: 0 for address in RECEIVERS}


qrcode_file_name = 'current_qrcode.jpeg'
script_path = os.path.dirname(os.path.realpath(__file__))

shortest_paths = None
current_provider = None
current_id = None
track_loop_future = None


@app.before_serving
async def start_services():
    global shortest_paths, track_loop_future

    network = create_token_network_topology()
    shortest_paths = nx.single_source_shortest_path(network, SENDER_ADDRESS)
    track_loop_future = asyncio.ensure_future(run_track_loop())


@app.after_serving
async def end_services():
    track_loop_future.cancel()


def get_shortest_path_to(receiver_address):
    return shortest_paths[receiver_address]


@app.route('/api/1/path/current')
async def get_current_path():
    return jsonify(get_shortest_path_to(current_provider))


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


async def run_track_loop():
    global current_provider, current_id
    global PROVIDER_MAP

    while True:
        current_provider, current_id = get_random_element(PROVIDER_MAP)
        PROVIDER_MAP[current_provider] += 1
        qr_code = qr_factory(current_provider, current_id)
        # Display new QR Code on LCD
        on_new_qr_code(qr_code)
        await asyncio.sleep(5)


@app.route('/api/1/provider/current')
async def get_current_provider():

    data = {
        "address": current_provider,
        "identifier": current_id
    }
    return jsonify(data)


@app.route('/api/1/provider/qr/current')
def get_current_qr_code():
    # TODO generate QR code
    return send_file(safe_join(script_path, qrcode_file_name))


